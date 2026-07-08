"""
SağlıkCebim - Model Değerlendirme Scripti
Eğitilmiş modelin detaylı performans analizi.

Kullanım:
    python evaluate.py --model ../models/chestxray_best.pt
"""

import argparse
import logging

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from torch.amp import autocast
from torch.utils.data import DataLoader
from torchvision import models

from augmentation import get_val_transforms
from dataset import ChestXrayDataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_model(checkpoint_path, device):
    """Eğitilmiş modeli yükle."""
    checkpoint = torch.load(checkpoint_path, map_location=device)
    config = checkpoint["config"]
    model_cfg = config["model"]

    model = models.densenet121(weights=None)
    in_features = model.classifier.in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=model_cfg["dropout"]),
        nn.Linear(in_features, model_cfg["num_classes"]),
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model = model.to(device)
    model.eval()
    return model, config


def find_optimal_thresholds(labels, predictions):
    """Her sınıf için Youden's J statistic ile optimal threshold bul."""
    thresholds = []
    for i in range(labels.shape[1]):
        if labels[:, i].sum() == 0:
            thresholds.append(0.5)
            continue
        fpr, tpr, thresh = roc_curve(labels[:, i], predictions[:, i])
        j_scores = tpr - fpr
        best_idx = np.argmax(j_scores)
        thresholds.append(float(thresh[best_idx]))
    return thresholds


def find_f1_optimal_thresholds(labels, predictions, min_threshold=0.05):
    """Her sınıf için F1-optimal threshold bul (precision-recall dengesi)."""
    from sklearn.metrics import precision_recall_curve
    thresholds = []
    for i in range(labels.shape[1]):
        if labels[:, i].sum() == 0:
            thresholds.append(0.5)
            continue
        precision, recall, thresh = precision_recall_curve(labels[:, i], predictions[:, i])
        # precision/recall have n+1 elements, thresh has n elements
        p = precision[:-1]
        r = recall[:-1]
        f1_scores = np.where(
            (p + r) > 0,
            2 * p * r / (p + r),
            0,
        )
        best_idx = np.argmax(f1_scores)
        best_thr = max(float(thresh[best_idx]), min_threshold)
        thresholds.append(best_thr)
    return thresholds


def main():
    parser = argparse.ArgumentParser(description="Model Değerlendirme")
    parser.add_argument("--model", type=str, required=True, help="Model checkpoint yolu")
    parser.add_argument("--config", type=str, default=None, help="Config dosyası (opsiyonel)")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Cihaz: {device}")

    model, config = load_model(args.model, device)
    data_cfg = config["data"]
    train_cfg = config["training"]

    image_size = data_cfg.get("image_size", 224)
    transform = get_val_transforms(image_size, config)

    image_dir = data_cfg["data_dir"]
    import os
    image_subdir = os.path.join(image_dir, "images")
    if not os.path.isdir(image_subdir):
        image_subdir = image_dir

    test_dataset = ChestXrayDataset(
        csv_path=data_cfg["image_list"],
        image_dir=image_subdir,
        image_list_path=data_cfg.get("test_list"),
        transform=transform,
    )
    import platform
    num_workers = 0 if platform.system() == "Windows" else train_cfg["num_workers"]
    test_loader = DataLoader(
        test_dataset,
        batch_size=train_cfg["batch_size"],
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )

    logger.info(f"Test seti: {len(test_dataset)} görüntü")

    # Tahminler
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

    # AUROC
    class_names = ChestXrayDataset.CLASSES
    logger.info("=" * 60)
    logger.info("SINIF BAZLI AUROC")
    logger.info("=" * 60)

    aurocs = []
    for i, name in enumerate(class_names):
        if all_labels[:, i].sum() > 0:
            auc = roc_auc_score(all_labels[:, i], all_preds[:, i])
            aurocs.append(auc)
            logger.info(f"  {name:25s}: {auc:.4f}")
        else:
            aurocs.append(0.0)
            logger.info(f"  {name:25s}: N/A (örneksiz)")

    logger.info(f"\n  Ortalama AUROC: {np.mean(aurocs):.4f}")

    # Optimal threshold'lar
    thresholds = find_optimal_thresholds(all_labels, all_preds)
    logger.info("\n" + "=" * 60)
    logger.info("OPTİMAL THRESHOLD'LAR")
    logger.info("=" * 60)
    for name, thr in zip(class_names, thresholds):
        logger.info(f"  {name:25s}: {thr:.3f}")

    # Binary classification raporu
    binary_preds = (all_preds > np.array(thresholds)).astype(int)
    logger.info("\n" + "=" * 60)
    logger.info("SINIFLANDIRMA RAPORU")
    logger.info("=" * 60)
    report = classification_report(
        all_labels, binary_preds, target_names=class_names, zero_division=0
    )
    logger.info("\n" + report)

    # Threshold'ları kaydet
    threshold_data = {name: float(thr) for name, thr in zip(class_names, thresholds)}
    import json
    threshold_path = args.model.replace(".pt", "_thresholds.json")
    with open(threshold_path, "w") as f:
        json.dump(threshold_data, f, indent=2)
    logger.info(f"Youden's J Threshold'lar kaydedildi: {threshold_path}")

    # F1-optimal threshold'lar
    f1_thresholds = find_f1_optimal_thresholds(all_labels, all_preds, min_threshold=0.05)
    logger.info("\n" + "=" * 60)
    logger.info("F1-OPTİMAL THRESHOLD'LAR")
    logger.info("=" * 60)
    for name, thr in zip(class_names, f1_thresholds):
        logger.info(f"  {name:25s}: {thr:.3f}")

    # F1-optimal classification raporu
    f1_binary_preds = (all_preds > np.array(f1_thresholds)).astype(int)
    logger.info("\n" + "=" * 60)
    logger.info("F1-OPTİMAL SINIFLANDIRMA RAPORU")
    logger.info("=" * 60)
    f1_report = classification_report(
        all_labels, f1_binary_preds, target_names=class_names, zero_division=0
    )
    logger.info("\n" + f1_report)

    # F1-optimal threshold'ları kaydet
    f1_threshold_data = {name: float(thr) for name, thr in zip(class_names, f1_thresholds)}
    f1_threshold_path = args.model.replace(".pt", "_thresholds.json")
    with open(f1_threshold_path, "w") as f:
        json.dump(f1_threshold_data, f, indent=2)
    logger.info(f"F1-optimal threshold'lar kaydedildi: {f1_threshold_path}")


if __name__ == "__main__":
    main()
