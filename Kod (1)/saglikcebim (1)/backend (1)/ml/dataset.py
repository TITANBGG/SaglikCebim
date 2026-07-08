"""
SağlıkCebim - Göğüs X-ray Dataset Sınıfı
NIH ChestX-ray14 veri seti için PyTorch Dataset.
"""

import os

import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
from torch.utils.data import Dataset


class ChestXrayDataset(Dataset):
    """NIH ChestX-ray14 veri seti."""

    CLASSES = [
        "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration",
        "Mass", "Nodule", "Pneumonia", "Pneumothorax",
        "Consolidation", "Edema", "Emphysema", "Fibrosis",
        "Pleural_Thickening", "Hernia",
    ]

    def __init__(self, csv_path, image_dir, image_list_path=None, transform=None,
                 apply_clahe=False, cache_dir=None):
        """
        Args:
            csv_path: Data_Entry_2017_v2020.csv dosya yolu
            image_dir: Görüntülerin bulunduğu klasör
            image_list_path: train_val_list.txt veya test_list.txt (opsiyonel)
            transform: torchvision.transforms (opsiyonel)
            apply_clahe: CLAHE ön-işleme uygula (cache yoksa)
            cache_dir: Pre-cache dizini (varsa buradan okur, CLAHE atlanır)
        """
        self.image_dir = image_dir
        self.cache_dir = cache_dir
        self.transform = transform
        self.apply_clahe = apply_clahe

        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()

        if image_list_path and os.path.exists(image_list_path):
            with open(image_list_path, "r") as f:
                valid_images = {line.strip() for line in f if line.strip()}
            df = df[df["Image Index"].isin(valid_images)].reset_index(drop=True)

        self.image_names = df["Image Index"].values
        self.labels = self._encode_labels(df["Finding Labels"].values)

    def _encode_labels(self, findings):
        """Multi-label encoding: 'Pneumonia|Edema' → [0,0,...,1,...,1,...,0]"""
        encoded = np.zeros((len(findings), len(self.CLASSES)), dtype=np.float32)
        for i, finding_str in enumerate(findings):
            if finding_str == "No Finding":
                continue
            for finding in finding_str.split("|"):
                finding = finding.strip()
                if finding in self.CLASSES:
                    encoded[i, self.CLASSES.index(finding)] = 1.0
        return encoded

    def _apply_clahe(self, image):
        """Grayscale'e çevir → CLAHE uygula → RGB'ye dönüştür."""
        gray = image.convert("L")
        arr = np.array(gray)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        result = clahe.apply(arr)
        enhanced = Image.fromarray(result)
        return enhanced.convert("RGB")

    def __len__(self):
        return len(self.image_names)

    def __getitem__(self, idx):
        img_name = self.image_names[idx]

        # Cache varsa oradan oku (zaten CLAHE + median blur + 256x256)
        if self.cache_dir:
            cache_path = os.path.join(self.cache_dir, img_name)
            if os.path.exists(cache_path):
                image = Image.open(cache_path).convert("RGB")
            else:
                # Cache'de yoksa orijinalden oku
                img_path = os.path.join(self.image_dir, img_name)
                image = Image.open(img_path).convert("RGB")
                if self.apply_clahe:
                    image = self._apply_clahe(image)
        else:
            img_path = os.path.join(self.image_dir, img_name)
            image = Image.open(img_path).convert("RGB")
            if self.apply_clahe:
                image = self._apply_clahe(image)

        if self.transform:
            image = self.transform(image)

        label = self.labels[idx]
        return image, label

    def get_class_frequencies(self):
        """Her sınıfın pozitif örnek sayısını döndür."""
        pos_counts = self.labels.sum(axis=0)
        return {cls: int(cnt) for cls, cnt in zip(self.CLASSES, pos_counts)}

    def get_pos_weights(self):
        """BCE pos_weight için ağırlıklar (negatif/pozitif oranı)."""
        pos_counts = self.labels.sum(axis=0)
        neg_counts = len(self.labels) - pos_counts
        weights = neg_counts / (pos_counts + 1e-5)
        return weights.astype(np.float32)
