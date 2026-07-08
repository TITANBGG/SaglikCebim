"""
SağlıkCebim - Eğitim Verisi Pre-Cache Scripti
112K resmi önceden işleyerek eğitimi 5x hızlandırır.

Pipeline:
  1024x1024 PNG → Grayscale → Median Blur → CLAHE → 256x256 PNG

Kullanım:
    python prepare_cache.py
"""

import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm

# Yollar
SRC_DIR = Path("../data/chestxray14/images")
CACHE_DIR = Path("../data/chestxray14/images_cached")
CACHE_SIZE = 256  # Augmentation için yeterli (224 + crop margin)


def process_single_image(args):
    """Tek resmi işle: grayscale → median blur → CLAHE → resize → kaydet."""
    src_path, dst_path = args

    if dst_path.exists():
        return True  # Zaten işlenmiş, atla

    try:
        # OpenCV ile oku (grayscale direkt)
        img = cv2.imread(str(src_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            return False

        # Median blur — salt-and-pepper gürültüyü temizle, kenarları koru
        img = cv2.medianBlur(img, 3)

        # CLAHE — kontrast normalizasyonu
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        img = clahe.apply(img)

        # 256x256'ya resize
        img = cv2.resize(img, (CACHE_SIZE, CACHE_SIZE), interpolation=cv2.INTER_AREA)

        # Kaydet (grayscale PNG — küçük dosya)
        cv2.imwrite(str(dst_path), img)
        return True
    except Exception as e:
        return False


def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Kaynak dosyaları listele
    src_files = sorted(SRC_DIR.glob("*.png"))
    if not src_files:
        src_files = sorted(SRC_DIR.glob("*.jpg")) + sorted(SRC_DIR.glob("*.jpeg"))

    if not src_files:
        print(f"HATA: {SRC_DIR} altinda resim bulunamadi!")
        return

    # Zaten işlenmiş olanları kontrol et
    existing = set(f.name for f in CACHE_DIR.glob("*.png"))
    remaining = [(f, CACHE_DIR / f.name) for f in src_files if f.name not in existing]

    total = len(src_files)
    done = total - len(remaining)

    print(f"Toplam: {total} resim")
    print(f"Zaten islenmis: {done}")
    print(f"Islenecek: {len(remaining)}")
    print(f"Cache dizini: {CACHE_DIR.resolve()}")
    print(f"Hedef boyut: {CACHE_SIZE}x{CACHE_SIZE}")
    print("=" * 60)

    if not remaining:
        print("Tum resimler zaten cache'de! Islem tamamlandi.")
        return

    start = time.time()

    # Paralel islem — CPU cekirdeklerini kullan
    num_workers = min(os.cpu_count() or 4, 8)
    print(f"Islemci sayisi: {num_workers}")

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(process_single_image, args): args for args in remaining}

        success = 0
        fail = 0
        pbar = tqdm(as_completed(futures), total=len(remaining), desc="Pre-cache", unit="img")
        for future in pbar:
            result = future.result()
            if result:
                success += 1
            else:
                fail += 1
            pbar.set_postfix(ok=success + done, fail=fail)

    elapsed = time.time() - start
    speed = len(remaining) / elapsed if elapsed > 0 else 0

    print("=" * 60)
    print(f"Tamamlandi!")
    print(f"  Basarili: {success + done}/{total}")
    print(f"  Basarisiz: {fail}")
    print(f"  Sure: {elapsed:.0f} saniye ({elapsed / 60:.1f} dakika)")
    print(f"  Hiz: {speed:.0f} resim/saniye")

    # Cache boyutu
    cache_size_gb = sum(f.stat().st_size for f in CACHE_DIR.glob("*.png")) / 1e9
    print(f"  Cache boyutu: {cache_size_gb:.1f} GB")


if __name__ == "__main__":
    main()
