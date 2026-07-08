"""Test radiology AI pipeline"""
import os
import sys
import numpy as np
from PIL import Image

# Test görüntüsü oluştur
test_image = Image.new('RGB', (256, 256), color=(100, 100, 100))
test_path = "test_chest.jpg"
test_image.save(test_path)
print(f"[OK] Test görüntüsü oluşturuldu: {test_path}")

# Şimdi radiology AI ile analiz et
sys.path.insert(0, r"Kod (1)\saglikcebim (1)\backend (1)")

try:
    from app.services.radiology_ai import radiology_ai
    
    findings, heatmap_filename = radiology_ai.analyze(test_path, "uploads/radiology")
    print(f"[OK] Analiz başarılı!")
    print(f"Bulunan {len(findings)} bulgu:")
    for f in findings:
        print(f"  - {f['tr_name']}: {f['confidence']:.2%} ({f['severity']})")
    print(f"Heatmap: {heatmap_filename}")
    
except Exception as e:
    print(f"[HATA] Analiz başarısız: {e}")
    import traceback
    traceback.print_exc()
