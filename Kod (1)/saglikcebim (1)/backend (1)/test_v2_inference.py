"""V2 model end-to-end inference testi."""
import sys
import os

sys.path.insert(0, ".")

from app.services.radiology.model import (
    load_model, predict, DEFAULT_MODEL_PATH, THRESHOLDS_PATH, _load_thresholds
)
from app.services.radiology.preprocessing import load_image, prepare_for_inference

print(f"Model path: {DEFAULT_MODEL_PATH}")
print(f"Threshold path: {THRESHOLDS_PATH}")
print(f"Model exists: {DEFAULT_MODEL_PATH.exists()}")
print(f"Threshold exists: {THRESHOLDS_PATH.exists()}")

# Load thresholds
t = _load_thresholds()
print(f"Thresholds loaded: {len(t)} classes")
for k, v in t.items():
    print(f"  {k}: {v:.4f}")

# Load model
model, device = load_model()
print(f"\nModel loaded on: {device}")

# Test with a real image
test_img_path = "data/chestxray14/images/00000001_000.png"
if os.path.exists(test_img_path):
    image, meta = load_image(test_img_path)
    tensor = prepare_for_inference(image)
    print(f"Tensor shape: {tensor.shape}")

    results = predict(tensor)
    print(f"\nSonuclar ({len(results)} sinif):")
    for r in results:
        status = "POZITIF" if r["positive"] else "-"
        conf = r["confidence"] * 100
        cls = r["class"]
        print(f"  {cls:<22} {conf:5.1f}%  {status}")
else:
    print("Test image not found at:", test_img_path)
