"""Optimal threshold analizi."""
import sys, os
sys.path.insert(0, '.')
from app.services.radiology.preprocessing import load_image, prepare_for_inference
from app.services.radiology.model import predict

img_dir = 'data/chestxray14/images'
test_images = sorted(os.listdir(img_dir))[:20]

for img_name in test_images:
    path = os.path.join(img_dir, img_name)
    image, _ = load_image(path)
    tensor = prepare_for_inference(image)
    results = predict(tensor, threshold=0.2)
    positives = [r for r in results if r['positive']]
    if positives:
        parts = [f"{p['class']}({p['confidence']:.2f})" for p in positives]
        print(f"{img_name}: {', '.join(parts)}")
    else:
        top = results[0]
        print(f"{img_name}: no finding>0.2, top={top['class']}({top['confidence']:.3f})")
