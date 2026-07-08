"""Kapsamlı performans testi - CLAHE preprocessing + per-class threshold."""
import sys
import os
import pandas as pd
sys.path.insert(0, '.')

from app.services.radiology.preprocessing import load_image, prepare_for_inference
from app.services.radiology.model import predict, _load_thresholds, CLASSES

# Ground truth labels
csv_path = "data/chestxray14/Data_Entry_2017_v2020.csv"
test_list_path = "data/chestxray14/test_list.txt"
img_dir = "data/chestxray14/images"

# CSV ve test listesi yükle
df = pd.read_csv(csv_path)
with open(test_list_path, "r") as f:
    test_images = [line.strip() for line in f if line.strip()]

# İlk 100 test görüntüsü ile değerlendir
N = 100
test_subset = test_images[:N]

thresholds = _load_thresholds()
print(f"Test: {N} görüntü, per-class threshold")
print()

tp = {c: 0 for c in CLASSES}  # True positive
fp = {c: 0 for c in CLASSES}  # False positive
fn = {c: 0 for c in CLASSES}  # False negative
tn = {c: 0 for c in CLASSES}  # True negative

for i, img_name in enumerate(test_subset):
    path = os.path.join(img_dir, img_name)
    if not os.path.exists(path):
        continue

    # Ground truth
    row = df[df["Image Index"] == img_name]
    if row.empty:
        continue
    labels_str = row.iloc[0]["Finding Labels"]
    true_labels = set(labels_str.split("|"))

    # Prediction
    image, _ = load_image(path)
    tensor = prepare_for_inference(image)
    results = predict(tensor)

    pred_labels = {r["class"] for r in results if r["positive"]}

    for cls in CLASSES:
        actual = cls in true_labels
        predicted = cls in pred_labels
        if actual and predicted:
            tp[cls] += 1
        elif not actual and predicted:
            fp[cls] += 1
        elif actual and not predicted:
            fn[cls] += 1
        else:
            tn[cls] += 1

    if (i + 1) % 20 == 0:
        print(f"  İşlendi: {i + 1}/{N}")

print()
print("=" * 70)
print(f"{'Sınıf':25s} {'Precision':>10s} {'Recall':>10s} {'F1':>10s} {'TP':>5s} {'FP':>5s} {'FN':>5s}")
print("=" * 70)

total_tp = total_fp = total_fn = 0
for cls in CLASSES:
    precision = tp[cls] / (tp[cls] + fp[cls]) if (tp[cls] + fp[cls]) > 0 else 0
    recall = tp[cls] / (tp[cls] + fn[cls]) if (tp[cls] + fn[cls]) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    total_tp += tp[cls]
    total_fp += fp[cls]
    total_fn += fn[cls]
    if tp[cls] + fp[cls] + fn[cls] > 0:
        print(f"  {cls:25s} {precision:10.3f} {recall:10.3f} {f1:10.3f} {tp[cls]:5d} {fp[cls]:5d} {fn[cls]:5d}")

print("=" * 70)
micro_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
micro_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
micro_f1 = 2 * micro_p * micro_r / (micro_p + micro_r) if (micro_p + micro_r) > 0 else 0
print(f"  {'MICRO AVG':25s} {micro_p:10.3f} {micro_r:10.3f} {micro_f1:10.3f}")
print()

# Normal (No Finding) doğruluk
no_finding_correct = 0
no_finding_total = 0
finding_detected = 0
finding_total = 0

for img_name in test_subset:
    row = df[df["Image Index"] == img_name]
    if row.empty:
        continue
    labels_str = row.iloc[0]["Finding Labels"]
    is_normal = labels_str == "No Finding"

    path = os.path.join(img_dir, img_name)
    if not os.path.exists(path):
        continue
    image, _ = load_image(path)
    tensor = prepare_for_inference(image)
    results = predict(tensor)
    has_finding = any(r["positive"] for r in results)

    if is_normal:
        no_finding_total += 1
        if not has_finding:
            no_finding_correct += 1
    else:
        finding_total += 1
        if has_finding:
            finding_detected += 1

print(f"Normal (No Finding) doğruluk: {no_finding_correct}/{no_finding_total}")
print(f"Patoloji tespit oranı: {finding_detected}/{finding_total}")
