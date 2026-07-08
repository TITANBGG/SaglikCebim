"""Per-class threshold test script."""
import sys
import os
sys.path.insert(0, '.')

from app.services.radiology.preprocessing import load_image, prepare_for_inference
from app.services.radiology.model import predict, _load_thresholds

# Per-class threshold'ları göster
thresholds = _load_thresholds()
print("=== Per-Class Thresholds (min 0.05 uygulanmış) ===")
for cls, thr in thresholds.items():
    print(f"  {cls:25s}: {thr:.4f}")

# Test görüntüleri ile dene
img_dir = "data/chestxray14/images"
test_images = [
    "00000001_000.png",  # Cardiomegaly
    "00000003_000.png",  # Hernia
    "00000004_000.png",  # Mass|Nodule
    "00000005_000.png",  # No Finding
    "00000002_000.png",  # No Finding
]
print()
print("=== Test Sonuçları (per-class threshold) ===")
for img_name in test_images:
    path = os.path.join(img_dir, img_name)
    if not os.path.exists(path):
        continue
    image, _ = load_image(path)
    tensor = prepare_for_inference(image)
    results = predict(tensor)  # per-class threshold kullanacak
    positives = [r for r in results if r["positive"]]
    if positives:
        findings = ", ".join([f"{p['class']}({p['confidence']:.3f})" for p in positives[:5]])
        print(f"{img_name}: {findings}")
    else:
        top = results[0]
        print(f"{img_name}: (no finding, top: {top['class']} {top['confidence']:.3f})")
