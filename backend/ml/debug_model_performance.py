"""
SağlıkCebim - Model Performance Debug
V1 vs V2 karşılaştırması, threshold analizi, preprocessing validation
"""

import json
import logging
from pathlib import Path

import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model sınıf isimleri
CLASSES = [
    "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration", "Mass",
    "Nodule", "Pneumonia", "Pneumothorax", "Consolidation", "Edema",
    "Emphysema", "Fibrosis", "Pleural_Thickening", "Hernia"
]

MODEL_PATH_V1 = Path(__file__).parent.parent / "models" / "chestxray_best.pt"
MODEL_PATH_V2 = Path(__file__).parent.parent / "models" / "chestxray_v2_best.pt"
THRESHOLDS_V1 = Path(__file__).parent.parent / "models" / "chestxray_best_thresholds.json"
THRESHOLDS_V2 = Path(__file__).parent.parent / "models" / "chestxray_v2_thresholds.json"


def load_thresholds(path):
    """Threshold dosyasını yükle."""
    with open(path, "r") as f:
        return json.load(f)


def compare_models():
    """V1 vs V2 model karşılaştırması."""
    logger.info("=" * 70)
    logger.info("MODEL COMPARISON: V1 vs V2")
    logger.info("=" * 70)
    
    # Threshold'ları yükle
    th_v1 = load_thresholds(THRESHOLDS_V1)
    th_v2 = load_thresholds(THRESHOLDS_V2)
    
    logger.info("\n📊 THRESHOLD COMPARISON:")
    logger.info(f"{'Class':<20} {'V1':<12} {'V2':<12} {'Ratio (V2/V1)':<15}")
    logger.info("-" * 60)
    
    ratios = {}
    for cls in CLASSES:
        v1_th = th_v1.get(cls, 0.5)
        v2_th = th_v2.get(cls, 0.5)
        ratio = v2_th / v1_th if v1_th > 0 else 1.0
        ratios[cls] = ratio
        
        logger.info(f"{cls:<20} {v1_th:<12.4f} {v2_th:<12.4f} {ratio:<15.2f}x")
    
    avg_ratio = np.mean(list(ratios.values()))
    logger.info(f"\n⚠️  AVERAGE RATIO: {avg_ratio:.2f}x")
    logger.info("   → V2 thresholds V1 modeline uygulanırsa TOO STRICT (false negatives artar)")
    
    # Model dosya boyutları
    logger.info("\n📁 MODEL FILES:")
    if MODEL_PATH_V1.exists():
        v1_size = MODEL_PATH_V1.stat().st_size / 1e6
        logger.info(f"   V1: {MODEL_PATH_V1.name} ({v1_size:.1f} MB)")
    else:
        logger.warning(f"   V1 NOT FOUND: {MODEL_PATH_V1}")
    
    if MODEL_PATH_V2.exists():
        v2_size = MODEL_PATH_V2.stat().st_size / 1e6
        logger.info(f"   V2: {MODEL_PATH_V2.name} ({v2_size:.1f} MB)")
    else:
        logger.warning(f"   V2 NOT FOUND: {MODEL_PATH_V2}")


def validate_preprocessing():
    """Preprocessing validation: training vs inference uyumsuzluğu."""
    logger.info("\n" + "=" * 70)
    logger.info("PREPROCESSING VALIDATION")
    logger.info("=" * 70)
    
    logger.info("\n✅ EXPECTED VALIDATION CHAIN:")
    logger.info("   • CLAHE contrast normalization")
    logger.info("   • Grayscale conversion")
    logger.info("   • Negative image detection")
    logger.info("   • Median blur (kernel 5)")
    logger.info("   • Resize to 224x224")
    logger.info("   • ToTensor()")
    logger.info("   • ImageNet Normalization")
    
    logger.info("\n📋 EXPECTED IMAGE STATS:")
    logger.info("   Normalization (ImageNet):")
    logger.info("   Mean: [0.485, 0.456, 0.406]")
    logger.info("   Std:  [0.229, 0.224, 0.225]")
    
    logger.info("\n✅ PREPROCESSING: No mismatches expected (inference == training)")


def recommend_strategy():
    """Recommendation strategy."""
    logger.info("\n" + "=" * 70)
    logger.info("🎯 RECOMMENDATION STRATEGY")
    logger.info("=" * 70)
    
    logger.info("""
    OPTION 1 (Recommended - SENSITIVE):
    ├─ Use V1 model + V1 thresholds
    ├─ Pros: Hassas (yüksek recall), eğitim setiyle doğru
    ├─ Cons: Daha fazla false positive
    └─ Use Case: Screening (hiçbirini kaçırma)
    
    OPTION 2 (CONSERVATIVE):
    ├─ Use V2 model + V2 thresholds
    ├─ Pros: Kesin (yüksek precision), daha az hata
    ├─ Cons: Bazı hastalıkları kaçırabilir
    └─ Use Case: Confirmation (sadece kesin olan söyle)
    
    OPTION 3 (BALANCED - TEST):
    ├─ Use V1 model + Averaged thresholds
    ├─ V1_th = 0.156, V2_th = 0.4094
    ├─ Avg_th = (0.156 + 0.4094) / 2 = 0.282
    ├─ Pros: Denge, ikisinin en iyisini al
    └─ Cons: Deneysel, validation gerekli
    
    CURRENT ISSUE:
    → V1 model + V2 thresholds = UNSUITABLE
    → V2 thresholds V1 modelinin çıktısında çok yüksek
    → 50-60% confidence → V2 threshold tarafından NEGATIVE ilan ediliyor
    → Oysa V1 threshold (0.156) ile POSITIVE olması gerekirdi
    """)


if __name__ == "__main__":
    try:
        compare_models()
        validate_preprocessing()
        recommend_strategy()
        logger.info("\n" + "=" * 70)
        logger.info("✅ DEBUG COMPLETE - İYİLEŞTİRME HAZIR")
        logger.info("=" * 70)
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
