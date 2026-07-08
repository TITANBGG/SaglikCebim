"""Sistem neleri buluyor, neleri kaçırıyor — detaylı analiz."""
import sys, os
sys.path.insert(0, '.')
import pandas as pd
from app.services.radiology.preprocessing import load_image, prepare_for_inference
from app.services.radiology.model import predict, _load_thresholds, CLASSES

csv_path = "data/chestxray14/Data_Entry_2017_v2020.csv"
test_list_path = "data/chestxray14/test_list.txt"
img_dir = "data/chestxray14/images"

df = pd.read_csv(csv_path)
with open(test_list_path, "r") as f:
    test_images = [line.strip() for line in f if line.strip()]

# Her siniftan ornekler bul
print("="*80)
print("HER SINIF ICIN ORNEK ANALIZ (test setinden)")
print("="*80)

thresholds = _load_thresholds()

# Her sinif icin: gercek pozitif ornekler bul ve test et
for cls in CLASSES:
    # Bu sinifa ait test goruntuleri
    cls_images = []
    for img_name in test_images:
        row = df[df["Image Index"] == img_name]
        if row.empty:
            continue
        labels = row.iloc[0]["Finding Labels"]
        if cls in labels.split("|"):
            cls_images.append((img_name, labels))
        if len(cls_images) >= 10:
            break

    if not cls_images:
        print(f"\n{cls}: Test setinde ornek yok!")
        continue

    detected = 0
    total = len(cls_images)
    print(f"\n{'='*60}")
    print(f" {cls} (threshold: {thresholds[cls]:.3f}) — {total} ornek test ediliyor")
    print(f"{'='*60}")

    for img_name, true_labels in cls_images:
        path = os.path.join(img_dir, img_name)
        if not os.path.exists(path):
            continue
        image, _ = load_image(path)
        tensor = prepare_for_inference(image)
        results = predict(tensor)

        # Bu sinif icin sonuc
        cls_result = next(r for r in results if r["class"] == cls)
        is_detected = cls_result["positive"]
        conf = cls_result["confidence"]

        if is_detected:
            detected += 1
            status = "BULDU"
        else:
            status = "KACIRDI"

        # Diger bulunan seyler
        other_pos = [r for r in results if r["positive"] and r["class"] != cls]
        other_str = ""
        if other_pos:
            other_str = " | Diger: " + ", ".join(f"{r['class']}({r['confidence']:.2f})" for r in other_pos[:3])

        print(f"  {status:8s} {img_name} conf={conf:.3f} (gercek: {true_labels}){other_str}")

    rate = detected / total * 100
    emoji = "✓" if rate >= 50 else "✗"
    print(f"  → {emoji} Tespit: {detected}/{total} (%{rate:.0f})")

# Normal goruntuler (No Finding)
print(f"\n{'='*60}")
print(f" NO FINDING (Normal) - False positive analizi")
print(f"{'='*60}")

normal_images = []
for img_name in test_images:
    row = df[df["Image Index"] == img_name]
    if row.empty:
        continue
    if row.iloc[0]["Finding Labels"] == "No Finding":
        normal_images.append(img_name)
    if len(normal_images) >= 20:
        break

correct = 0
for img_name in normal_images:
    path = os.path.join(img_dir, img_name)
    if not os.path.exists(path):
        continue
    image, _ = load_image(path)
    tensor = prepare_for_inference(image)
    results = predict(tensor)
    positives = [r for r in results if r["positive"]]

    if not positives:
        correct += 1
        print(f"  DOGRU   {img_name} — Bulgu yok (dogru)")
    else:
        fp_str = ", ".join(f"{r['class']}({r['confidence']:.2f})" for r in positives[:4])
        print(f"  YANLIS  {img_name} — False positive: {fp_str}")

print(f"  → Normal dogruluk: {correct}/{len(normal_images)} (%{correct/len(normal_images)*100:.0f})")

# Ozet tablo
print(f"\n{'='*80}")
print("GENEL OZET")
print(f"{'='*80}")
print(f"{'Sinif':25s} {'Threshold':>10s} {'25K Test AUROC':>15s}")
print("-"*55)
aurocs = {
    "Atelectasis": 0.7678, "Cardiomegaly": 0.8739, "Effusion": 0.8245,
    "Infiltration": 0.6896, "Mass": 0.8210, "Nodule": 0.7569,
    "Pneumonia": 0.7250, "Pneumothorax": 0.8589, "Consolidation": 0.7484,
    "Edema": 0.8427, "Emphysema": 0.9082, "Fibrosis": 0.8178,
    "Pleural_Thickening": 0.7746, "Hernia": 0.9007,
}
for cls in CLASSES:
    thr = thresholds[cls]
    auc = aurocs.get(cls, 0)
    quality = "IYI" if auc >= 0.85 else ("ORTA" if auc >= 0.75 else "ZAYIF")
    print(f"  {cls:25s} {thr:10.3f} {auc:12.4f}   {quality}")
