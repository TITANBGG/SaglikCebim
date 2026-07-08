"""
SağlıkCebim - Göğüs X-ray Model Eğitim Scripti
NIH ChestX-ray14 veri seti üzerinde DenseNet-121 fine-tuning.

Kullanım:
    python train.py
    python train.py --config configs/chestxray_config.yaml
"""

import argparse
import logging
import os
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import yaml
from sklearn.metrics import roc_auc_score
from torch.amp import GradScaler, autocast
from torch.utils.data import DataLoader, random_split
from torchvision import models
from tqdm import tqdm

from augmentation import get_train_transforms, get_val_transforms
from dataset import ChestXrayDataset

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_model(num_classes=14, pretrained=True, dropout=0.5):
    """DenseNet-121 tabanlı multi-label sınıflandırıcı."""
    weights = models.DenseNet121_Weights.DEFAULT if pretrained else None
    model = models.densenet121(weights=weights)

    # Son sınıflandırıcıyı değiştir
    in_features = model.classifier.in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=dropout),
        nn.Linear(in_features, num_classes),
    )
    return model


def train_one_epoch(model, loader, criterion, optimizer, scaler, device, accum_steps=1):
    """Bir epoch eğitim."""
    model.train()
    running_loss = 0.0
    optimizer.zero_grad()
    total = len(loader)

    pbar = tqdm(enumerate(loader), total=total, desc="  Egitim", unit="batch")
    for i, (images, labels) in pbar:
        images = images.to(device)
        labels = labels.to(device)

        with autocast("cuda"):
            outputs = model(images)
            loss = criterion(outputs, labels) / accum_steps

        scaler.scale(loss).backward()

        if (i + 1) % accum_steps == 0:
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad()

        running_loss += loss.item() * accum_steps
        avg_loss = running_loss / (i + 1)
        pbar.set_postfix(loss=f"{avg_loss:.4f}")

        # Her 500 batch'te log dosyasina yaz
        if (i + 1) % 500 == 0:
            pct = (i + 1) / total * 100
            logger.info(f"  Batch {i+1}/{total} ({pct:.0f}%) | Loss: {avg_loss:.4f}")

    return running_loss / total


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    """Validasyon seti üzerinde değerlendirme."""
    model.eval()
    running_loss = 0.0
    all_labels = []
    all_preds = []

    pbar = tqdm(loader, desc="  Validasyon", unit="batch")
    for images, labels in pbar:
        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)
        loss = criterion(outputs, labels)

        running_loss += loss.item()
        all_preds.append(torch.sigmoid(outputs).cpu().numpy())
        all_labels.append(labels.cpu().numpy())

    avg_loss = running_loss / len(loader)
    all_preds = np.concatenate(all_preds, axis=0)
    all_labels = np.concatenate(all_labels, axis=0)

    # Her sınıf için AUROC hesapla
    aurocs = []
    class_names = ChestXrayDataset.CLASSES
    for i, name in enumerate(class_names):
        if all_labels[:, i].sum() > 0:
            auc = roc_auc_score(all_labels[:, i], all_preds[:, i])
            aurocs.append(auc)
        else:
            aurocs.append(0.0)

    mean_auroc = np.mean(aurocs)
    return avg_loss, mean_auroc, dict(zip(class_names, aurocs))


def main():
    parser = argparse.ArgumentParser(description="Göğüs X-ray Model Eğitimi")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/chestxray_config.yaml",
        help="Konfigürasyon dosyası yolu",
    )
    parser.add_argument(
        "--resume",
        type=str,
        default=None,
        help="Checkpoint dosyası yolu (eğitime devam etmek için)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    model_cfg = config["model"]
    data_cfg = config["data"]
    train_cfg = config["training"]
    output_cfg = config["output"]

    # Dizinleri oluştur
    model_dir = Path(output_cfg["model_dir"])
    log_dir = Path(output_cfg["log_dir"])
    model_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Dosya logger
    file_handler = logging.FileHandler(log_dir / "training.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(file_handler)

    # Cihaz
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Cihaz: {device}")
    if device.type == "cuda":
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    # Veri setleri
    image_size = data_cfg.get("image_size", 224)
    train_transform = get_train_transforms(image_size, config)
    val_transform = get_val_transforms(image_size, config)

    image_dir = data_cfg["data_dir"]
    # NIH veri setinde görüntüler images_001/ ... images_012/ altında
    # Tek klasöre çıkarıldığını varsayıyoruz: data_dir/images/
    image_subdir = os.path.join(image_dir, "images")
    if not os.path.isdir(image_subdir):
        image_subdir = image_dir

    train_dataset = ChestXrayDataset(
        csv_path=data_cfg["image_list"],
        image_dir=image_subdir,
        image_list_path=data_cfg.get("train_list"),
        transform=train_transform,
    )

    # Train/val split
    val_ratio = data_cfg.get("val_split", 0.15)
    val_size = int(len(train_dataset) * val_ratio)
    train_size = len(train_dataset) - val_size
    train_subset, val_subset = random_split(
        train_dataset,
        [train_size, val_size],
        generator=torch.Generator().manual_seed(42),
    )

    # Val subset'e augmentation yok
    val_subset.dataset = ChestXrayDataset(
        csv_path=data_cfg["image_list"],
        image_dir=image_subdir,
        image_list_path=data_cfg.get("train_list"),
        transform=val_transform,
    )

    test_dataset = ChestXrayDataset(
        csv_path=data_cfg["image_list"],
        image_dir=image_subdir,
        image_list_path=data_cfg.get("test_list"),
        transform=val_transform,
    )

    # Windows uyumluluğu: num_workers sorun çıkarırsa 0 kullan
    num_workers = 0 if os.name == "nt" else train_cfg["num_workers"]

    train_loader = DataLoader(
        train_subset,
        batch_size=train_cfg["batch_size"],
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
    )
    val_loader = DataLoader(
        val_subset,
        batch_size=train_cfg["batch_size"],
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=train_cfg["batch_size"],
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )

    logger.info(f"Eğitim seti: {train_size} görüntü")
    logger.info(f"Validasyon seti: {val_size} görüntü")
    logger.info(f"Test seti: {len(test_dataset)} görüntü")

    # Model
    model = build_model(
        num_classes=model_cfg["num_classes"],
        pretrained=model_cfg["pretrained"],
        dropout=model_cfg["dropout"],
    )
    model = model.to(device)
    logger.info(f"Model: DenseNet-121 ({sum(p.numel() for p in model.parameters()) / 1e6:.1f}M parametre)")

    # Loss, optimizer, scheduler
    criterion = nn.BCEWithLogitsLoss()

    opt_cfg = train_cfg["optimizer"]
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=opt_cfg["lr"],
        weight_decay=opt_cfg.get("weight_decay", 0),
    )

    sch_cfg = train_cfg["scheduler"]
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="max",
        factor=sch_cfg["factor"],
        patience=sch_cfg["patience"],
        min_lr=sch_cfg.get("min_lr", 1e-7),
    )

    # Mixed precision
    scaler = GradScaler("cuda", enabled=train_cfg.get("mixed_precision", True))
    accum_steps = train_cfg.get("gradient_accumulation_steps", 1)

    # Eğitim döngüsü
    best_auroc = 0.0
    patience_counter = 0
    patience = train_cfg.get("early_stopping_patience", 5)
    start_epoch = 0

    # Resume desteği
    if args.resume:
        ckpt = torch.load(args.resume, map_location=device)
        model.load_state_dict(ckpt["model_state_dict"])
        optimizer.load_state_dict(ckpt["optimizer_state_dict"])
        best_auroc = ckpt.get("best_auroc", 0.0)
        start_epoch = ckpt.get("epoch", 0)
        logger.info(f"Checkpoint yuklendi: epoch {start_epoch}, AUROC: {best_auroc:.4f}")

    logger.info("=" * 60)
    logger.info("EĞİTİM BAŞLIYOR")
    logger.info("=" * 60)

    for epoch in range(start_epoch, train_cfg["epochs"]):
        start = time.time()

        train_loss = train_one_epoch(
            model, train_loader, criterion, optimizer, scaler, device, accum_steps
        )
        val_loss, val_auroc, class_aurocs = evaluate(model, val_loader, criterion, device)

        scheduler.step(val_auroc)
        elapsed = time.time() - start
        current_lr = optimizer.param_groups[0]["lr"]

        logger.info(
            f"Epoch {epoch + 1}/{train_cfg['epochs']} | "
            f"Train Loss: {train_loss:.4f} | "
            f"Val Loss: {val_loss:.4f} | "
            f"Val AUROC: {val_auroc:.4f} | "
            f"LR: {current_lr:.2e} | "
            f"Süre: {elapsed:.0f}s"
        )

        # En iyi modeli kaydet
        if val_auroc > best_auroc:
            best_auroc = val_auroc
            patience_counter = 0
            save_path = model_dir / output_cfg["best_model_name"]
            torch.save({
                "epoch": epoch + 1,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "best_auroc": best_auroc,
                "class_aurocs": class_aurocs,
                "config": config,
            }, save_path)
            logger.info(f"  ✓ En iyi model kaydedildi (AUROC: {best_auroc:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                logger.info(f"  Early stopping: {patience} epoch iyileşme yok.")
                break

    # Test seti değerlendirmesi
    logger.info("=" * 60)
    logger.info("TEST SETİ DEĞERLENDİRMESİ")
    logger.info("=" * 60)

    # En iyi modeli yükle
    checkpoint = torch.load(model_dir / output_cfg["best_model_name"], map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])

    test_loss, test_auroc, test_class_aurocs = evaluate(model, test_loader, criterion, device)
    logger.info(f"Test AUROC (ortalama): {test_auroc:.4f}")
    logger.info("-" * 40)
    for cls_name, auc_val in test_class_aurocs.items():
        logger.info(f"  {cls_name:25s}: {auc_val:.4f}")

    logger.info("=" * 60)
    logger.info("EĞİTİM TAMAMLANDI")
    logger.info(f"En iyi model: {model_dir / output_cfg['best_model_name']}")
    logger.info(f"En iyi Val AUROC: {best_auroc:.4f}")
    logger.info(f"Test AUROC: {test_auroc:.4f}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
