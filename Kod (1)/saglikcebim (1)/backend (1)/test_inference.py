"""Radyoloji inference uçtan uca test."""
import sys
sys.path.insert(0, '.')

# 1. Preprocessing
from app.services.radiology.preprocessing import load_image, prepare_for_inference

img_path = 'data/chestxray14/images/00000001_000.png'
print('1. Goruntu yukleniyor...')
image, metadata = load_image(img_path)
print(f'   Boyut: {image.size}, Mode: {image.mode}')
print(f'   Metadata: {metadata}')

# 2. Tensor hazirlama
print('2. Tensor hazirlaniyor...')
tensor = prepare_for_inference(image)
print(f'   Tensor shape: {tensor.shape}')

# 3. Model tahmini
print('3. Model yukleniyor ve tahmin yapiliyor...')
from app.services.radiology.model import predict
results = predict(tensor, threshold=0.3)
print(f'   Toplam sinif: {len(results)}')
print()
print('=== TAHMIN SONUCLARI ===')
for r in results:
    marker = '***' if r['positive'] else '   '
    cls = r['class']
    conf = r['confidence']
    pos = r['positive']
    print(f'{marker} {cls:25s} | Guven: {conf:.4f} | Pozitif: {pos}')

# 4. Tam analiz pipeline
print()
print('4. Tam analiz pipeline calistiriliyor...')
from app.services.radiology.inference import analyze_image
result = analyze_image(img_path, threshold=0.3, generate_heatmaps=False)
print(f'   Bulgu sayisi: {len(result.get("findings", []))}')
print(f'   Ozet: {result.get("summary", "")}')
print()
if result.get('findings'):
    print('=== BULGULAR ===')
    for f in result['findings']:
        print(f'   - {f["tr_name"]} (guven: {f["confidence"]:.2%}, ciddiyet: {f.get("severity", "?")})')

print()
print('BASARILI! Sistem calisiyor.')
