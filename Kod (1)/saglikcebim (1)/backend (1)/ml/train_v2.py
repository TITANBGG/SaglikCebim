"""
SağlıkCebim - Göğüs X-ray Model Eğitim Scripti V2
Büyük iyileştirmeler: Focal Loss, EfficientNet-B4, CLAHE, Class Weights,
Cosine Annealing, Güçlü Augmentation, Label Smoothing.

Kullanım:
    python train_v2.py
    python train_v2.py --config configs/chestxray_v2_config.yaml
    python train_v2.py --resume ../models/chestxray_v2_best.pt
"""

import argparse
import logging
import os
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
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


# =====================================================================
# FOCAL LOSS — BCE'den çok daha iyi: kolay örneklere az, zor örneklere
# çok odaklanır. Nadir sınıflar için kritik.
# =====================================================================
class FocalLoss(nn.Module):
    """Focal Loss for multi-label classification.
    
    Lin et al., "Focal Loss for Dense Object Detection", ICCV 2017.
    FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)
    """
    def __init__(self, gamma=2.0, alpha=None, pos_weight=None, label_smoothing=0.0):
        super().__init__()
        self.gamma = gamma
        self.alpha = alpha  # per-class alpha weights
        self.pos_weight = pos_weight
        self.label_smoothing = label_smoothing

    def forward(self, logits, targets):
        # Label smoothing
        if self.label_smoothing > 0:
            targets = targets * (1 - self.label_smoothing) + 0.5 * self.label_smoothing

        # BCE loss (per element)
        bce = F.binary_cross_entropy_with_logits(logits, targets, reduction='none')
        
        # p_t
        probs = torch.sigmoid(logits)
        p_t = probs * targets + (1 - probs) * (1 - targets)
        
        # Focal modulation
        focal_weight = (1 - p_t) ** self.gamma
        loss = focal_weight * bce

        # Alpha weighting (per-class)
        if self.alpha is not None:
            alpha_t = self.alpha * targets + (1 - self.alpha) * (1 - targets)
            loss = alpha_t * loss

        # Pos weight
        if self.pos_weight is not None:
            weight = self.pos_weight * targets + (1 - targets)
            loss = weight * loss

        return loss.mean()


# =====================================================================
# MODEL FABRİKASI
# =====================================================================
def build_model(backbone="efficientnet_b4", num_classes=14, pretrained=True, dropout=0.4):
    """Model oluştur — EfficientNet-B4 veya DenseNet-121."""
    if backbone == "efficientnet_b4":
        weights = models.EfficientNet_B4_Weights.DEFAULT if pretrained else None
        model = models.efficientnet_b4(weights=weights)
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(in_features, num_classes),
        )
        logger.info(f"Model: EfficientNet-B4 ({sum(p.numel() for p in model.parameters()) / 1e6:.1f}M param)")
    elif backbone == "densenet121":
        weights = models.DenseNet121_Weights.DEFAULT if pretrained else None
        model = models.densenet121(weights=weights)
        in_features = model.classifier.in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(in_features, num_classes),
        )
        logger.info(f"Model: DenseNet-121 ({sum(p.numel() for p in model.parameters()) / 1e6:.1f}M param)")
    elif backbone == "densenet169":
        weights = models.DenseNet169_Weights.DEFAULT if pretrained else None
        model = models.densenet169(weights=weights)
        in_features = model.classifier.in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(in_features, num_classes),
        )
        logger.info(f"Model: DenseNet-169 ({sum(p.numel() for p in model.parameters()) / 1e6:.1f}M param)")
    else:
        raise ValueError(f"Bilinmeyen backbone: {backbone}")
    
    return model


# =====================================================================
# EĞİTİM FONKSİYONLARI
# =====================================================================
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
            # Gradient clipping — kararlılık için
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad()

        running_loss += loss.item() * accum_steps
        avg_loss = running_loss / (i + 1)
        pbar.set_postfix(loss=f"{avg_loss:.4f}")

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

    # Per-class AUROC
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


# =====================================================================
# ANA FONKSİYON
# =====================================================================
def main():
    parser = argparse.ArgumentParser(description="Göğüs X-ray Model Eğitimi V2")
    parser.add_argument(
        "--config", type=str, default="configs/chestxray_v2_config.yaml",
        help="Konfigürasyon dosyası yolu",
    )
    parser.add_argument(
        "--resume", type=str, default=None,
        help="Checkpoint dosyası yolu (eğitime devam)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    model_cfg = config["model"]
    data_cfg = config["data"]
    train_cfg = config["training"]
    output_cfg = config["output"]

    # Dizinler
    model_dir = Path(output_cfg["model_dir"])
    log_dir = Path(output_cfg["log_dir"])
    model_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_dir / "training_v2.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(file_handler)

    # Cihaz
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Cihaz: {device}")
    if device.type == "cuda":
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
        logger.info(f"VRAM: {vram_gb:.1f} GB")

    # ========== VERİ SETLERİ ==========
    image_size = data_cfg.get("image_size", 224)
    apply_clahe = data_cfg.get("apply_clahe", True)
    train_transform = get_train_transforms(image_size, config)
    val_transform = get_val_transforms(image_size, config)

    image_dir = data_cfg["data_dir"]
    image_subdir = os.path.join(image_dir, "images")
    if not os.path.isdir(image_subdir):
        image_subdir = image_dir

    cache_dir = data_cfg.get("cache_dir")
    if cache_dir:
        cache_dir = os.path.join(os.path.dirname(__file__), cache_dir) if not os.path.isabs(cache_dir) else cache_dir
        logger.info(f"Cache dizini: {cache_dir}")

    train_dataset = ChestXrayDataset(
        csv_path=data_cfg["image_list"],
        image_dir=image_subdir,
        image_list_path=data_cfg.get("train_list"),
        transform=train_transform,
        apply_clahe=apply_clahe,
        cache_dir=cache_dir,
    )

    # Sınıf ağırlıklarını hesapla
    class_freqs = train_dataset.get_class_frequencies()
    pos_weights_np = train_dataset.get_pos_weights()
    logger.info("Sınıf dağılımı:")
    for cls, cnt in class_freqs.items():
        total = len(train_dataset)
        pct = cnt / total * 100
        logger.info(f"  {cls:25s}: {cnt:6d} ({pct:.1f}%)")

    # Train/val split
    val_ratio = data_cfg.get("val_split", 0.15)
    val_size = int(len(train_dataset) * val_ratio)
    train_size = len(train_dataset) - val_size
    train_subset, val_subset = random_split(
        train_dataset,
        [train_size, val_size],
        generator=torch.Generator().manual_seed(42),
    )

    # Val subset: augmentation yok ama CLAHE var
    val_subset.dataset = ChestXrayDataset(
        csv_path=data_cfg["image_list"],
        image_dir=image_subdir,
        image_list_path=data_cfg.get("train_list"),
        transform=val_transform,
        apply_clahe=apply_clahe,
        cache_dir=cache_dir,
    )

    test_dataset = ChestXrayDataset(
        csv_path=data_cfg["image_list"],
        image_dir=image_subdir,
        image_list_path=data_cfg.get("test_list"),
        transform=val_transform,
        apply_clahe=apply_clahe,
        cache_dir=cache_dir,
    )

    num_workers = 0 if os.name == "nt" else train_cfg.get("num_workers", 4)

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

    logger.info(f"Eğitim: {train_size} | Validasyon: {val_size} | Test: {len(test_dataset)}")

    # ========== MODEL ==========
    model = build_model(
        backbone=model_cfg.get("backbone", "efficientnet_b4"),
        num_classes=model_cfg["num_classes"],
        pretrained=model_cfg["pretrained"],
        dropout=model_cfg.get("dropout", 0.4),
    )
    model = model.to(device)

    # ========== LOSS ==========
    loss_cfg = train_cfg.get("loss", {})
    loss_type = loss_cfg.get("type", "focal")
    
    if loss_type == "focal":
        gamma = loss_cfg.get("gamma", 2.0)
        label_smoothing = loss_cfg.get("label_smoothing", 0.05)
        use_pos_weight = loss_cfg.get("use_pos_weight", True)
        
        # pos_weight: nadir sınıflara daha fazla ağırlık
        pos_weight = None
        if use_pos_weight:
            # Cap pos_weight to avoid extreme values
            pw = np.clip(pos_weights_np, 1.0, 50.0)
            pos_weight = torch.tensor(pw, dtype=torch.float32).to(device)
            logger.info(f"Pos weights (capped 1-50): {dict(zip(ChestXrayDataset.CLASSES, pw.tolist()))}")
        
        criterion = FocalLoss(
            gamma=gamma,
            pos_weight=pos_weight,
            label_smoothing=label_smoothing,
        )
        logger.info(f"Loss: Focal (gamma={gamma}, label_smoothing={label_smoothing})")
    else:
        pos_weight = torch.tensor(np.clip(pos_weights_np, 1.0, 50.0), dtype=torch.float32).to(device)
        criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
        logger.info("Loss: Weighted BCEWithLogitsLoss")

    # Eval criterion (always unweighted BCE for fair comparison)
    eval_criterion = nn.BCEWithLogitsLoss()

    # ========== OPTIMIZER ==========
    opt_cfg = train_cfg["optimizer"]
    
    # Differential learning rate: backbone daha düşük, head daha yüksek
    base_lr = opt_cfg["lr"]
    backbone_lr = base_lr * opt_cfg.get("backbone_lr_mult", 0.1)
    
    backbone_params = []
    head_params = []
    for name, param in model.named_parameters():
        if "classifier" in name or "fc" in name:
            head_params.append(param)
        else:
            backbone_params.append(param)
    
    optimizer = torch.optim.AdamW([
        {"params": backbone_params, "lr": backbone_lr},
        {"params": head_params, "lr": base_lr},
    ], weight_decay=opt_cfg.get("weight_decay", 1e-4))
    
    logger.info(f"Optimizer: AdamW (backbone_lr={backbone_lr:.2e}, head_lr={base_lr:.2e})")

    # ========== SCHEDULER ==========
    sch_cfg = train_cfg.get("scheduler", {})
    sch_type = sch_cfg.get("type", "cosine")
    epochs = train_cfg["epochs"]
    warmup_epochs = sch_cfg.get("warmup_epochs", 3)
    
    if sch_type == "cosine":
        # Cosine annealing with warm restarts
        scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer,
            T_0=sch_cfg.get("T_0", 10),
            T_mult=sch_cfg.get("T_mult", 2),
            eta_min=sch_cfg.get("min_lr", 1e-7),
        )
        logger.info(f"Scheduler: CosineAnnealingWarmRestarts (T_0={sch_cfg.get('T_0', 10)})")
    else:
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode="max",
            factor=sch_cfg.get("factor", 0.1),
            patience=sch_cfg.get("patience", 3),
            min_lr=sch_cfg.get("min_lr", 1e-7),
        )

    # Mixed precision
    scaler = GradScaler("cuda", enabled=train_cfg.get("mixed_precision", True))
    accum_steps = train_cfg.get("gradient_accumulation_steps", 2)

    # ========== EĞİTİM DÖNGÜSÜ ==========
    best_auroc = 0.0
    patience_counter = 0
    patience = train_cfg.get("early_stopping_patience", 10)
    start_epoch = 0

    # Resume
    if args.resume:
        ckpt = torch.load(args.resume, map_location=device, weights_only=False)
        model.load_state_dict(ckpt["model_state_dict"])
        if "optimizer_state_dict" in ckpt:
            try:
                optimizer.load_state_dict(ckpt["optimizer_state_dict"])
            except Exception:
                logger.warning("Optimizer state yüklenemedi, sıfırdan başlanıyor")
        best_auroc = ckpt.get("best_auroc", 0.0)
        start_epoch = ckpt.get("epoch", 0)
        logger.info(f"Checkpoint: epoch {start_epoch}, AUROC: {best_auroc:.4f}")

    logger.info("=" * 70)
    logger.info("EĞİTİM V2 BAŞLIYOR")
    logger.info(f"  Backbone: {model_cfg.get('backbone', 'efficientnet_b4')}")
    logger.info(f"  CLAHE: {apply_clahe}")
    logger.info(f"  Epochs: {epochs}")
    logger.info(f"  Batch size: {train_cfg['batch_size']} x {accum_steps} accum = {train_cfg['batch_size'] * accum_steps} effective")
    logger.info("=" * 70)

    # Warmup için başlangıç LR değerlerini kaydet
    initial_lrs = [pg["lr"] for pg in optimizer.param_groups]

    for epoch in range(start_epoch, epochs):
        start = time.time()

        # Warmup: İlk birkaç epoch'ta lr'yi kademeli artır
        if epoch < warmup_epochs:
            warmup_factor = (epoch + 1) / warmup_epochs
            for pg, init_lr in zip(optimizer.param_groups, initial_lrs):
                pg["lr"] = init_lr * warmup_factor

        train_loss = train_one_epoch(
            model, train_loader, criterion, optimizer, scaler, device, accum_steps
        )
        val_loss, val_auroc, class_aurocs = evaluate(model, val_loader, eval_criterion, device)

        # Scheduler step
        if sch_type == "cosine":
            scheduler.step(epoch + 1)
        else:
            scheduler.step(val_auroc)

        elapsed = time.time() - start
        current_lr = optimizer.param_groups[-1]["lr"]

        logger.info(
            f"Epoch {epoch + 1}/{epochs} | "
            f"Train: {train_loss:.4f} | "
            f"Val: {val_loss:.4f} | "
            f"AUROC: {val_auroc:.4f} | "
            f"LR: {current_lr:.2e} | "
            f"{elapsed:.0f}s"
        )

        # Per-class AUROC log (her 5 epoch'ta)
        if (epoch + 1) % 5 == 0 or val_auroc > best_auroc:
            for cls, auc in class_aurocs.items():
                logger.info(f"    {cls:25s}: {auc:.4f}")

        # En iyi model kaydet
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
            logger.info(f"  ✓ Yeni en iyi model (AUROC: {best_auroc:.4f})")
        else:
            patience_counter += 1
            logger.info(f"  İyileşme yok ({patience_counter}/{patience})")
            if patience_counter >= patience:
                logger.info(f"  Early stopping: {patience} epoch iyileşme yok.")
                break

    # ========== TEST ==========
    logger.info("=" * 70)
    logger.info("TEST SETİ DEĞERLENDİRMESİ")
    logger.info("=" * 70)

    best_ckpt = torch.load(model_dir / output_cfg["best_model_name"], map_location=device, weights_only=False)
    model.load_state_dict(best_ckpt["model_state_dict"])

    test_loss, test_auroc, test_class_aurocs = evaluate(model, test_loader, eval_criterion, device)
    logger.info(f"Test AUROC (ortalama): {test_auroc:.4f}")
    for cls, auc in test_class_aurocs.items():
        logger.info(f"  {cls:25s}: {auc:.4f}")

    # Threshold hesapla ve kaydet
    logger.info("Optimal threshold'lar hesaplanıyor...")
    _compute_and_save_thresholds(model, test_loader, device, model_dir, output_cfg)

    logger.info("=" * 70)
    logger.info("EĞİTİM TAMAMLANDI")
    logger.info(f"En iyi Val AUROC: {best_auroc:.4f}")
    logger.info(f"Test AUROC: {test_auroc:.4f}")
    logger.info("=" * 70)


def _compute_and_save_thresholds(model, test_loader, device, model_dir, output_cfg):
    """F1-optimal threshold'ları otomatik hesapla ve kaydet."""
    import json
    from sklearn.metrics import precision_recall_curve

    model.eval()
    all_labels = []
    all_preds = []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            with autocast("cuda", enabled=(device.type == "cuda")):
                outputs = model(images)
            all_preds.append(torch.sigmoid(outputs).cpu().numpy())
            all_labels.append(labels.numpy())

    all_preds = np.concatenate(all_preds, axis=0)
    all_labels = np.concatenate(all_labels, axis=0)

    thresholds = {}
    for i, cls in enumerate(ChestXrayDataset.CLASSES):
        if all_labels[:, i].sum() == 0:
            thresholds[cls] = 0.5
            continue
        precision, recall, thresh = precision_recall_curve(all_labels[:, i], all_preds[:, i])
        p = precision[:-1]
        r = recall[:-1]
        f1 = np.where((p + r) > 0, 2 * p * r / (p + r), 0)
        best_idx = np.argmax(f1)
        thresholds[cls] = max(float(thresh[best_idx]), 0.05)

    threshold_path = model_dir / output_cfg["best_model_name"].replace(".pt", "_thresholds.json")
    with open(threshold_path, "w") as f:
        json.dump(thresholds, f, indent=2)
    logger.info(f"Threshold'lar kaydedildi: {threshold_path}")
    for cls, thr in thresholds.items():
        logger.info(f"  {cls:25s}: {thr:.3f}")


def load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    main()
