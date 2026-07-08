# WSL & Docker Desktop Optimizasyon Rehberi

## 🎯 Problem
Windows PC donması → Docker sınırsız kaynak tüketiyor

## ✅ Yapılan Optimizasyonlar

### 1. **Docker Compose Resource Limits** ✓
- **PostgreSQL**: 1.5 CPU, 512MB RAM limit
- **Backend**: 2 CPU, 1GB RAM limit  
- **Frontend**: 1 CPU, 256MB RAM limit

### 2. **Backend Optimizasyonu** ✓
- **uvloop** eklendi (Asyncio'dan 2-4x hızlı)
- **2 worker process** (default unlimited'den)
- **Connection timeout**: 5 sn (kaynak sızdırması önleme)
- **Lazy loading**: Sadece gerekli moduller

### 3. **Frontend Build Optimizasyonu** ✓
- **Node.js heap memory**: 512MB limit
- **Terser minification**: Console/debugger kodu kaldırma
- **Code splitting**: Vendor paketi ayrıştırma
- **Sourcemap deaktif**: Production build hızlandırma

### 4. **PostgreSQL WSL Ayarları** ✓
```
shared_buffers: 128MB (default 25%)
effective_cache_size: 256MB (default 25%)
work_mem: 8MB (default 4MB)
maintenance_work_mem: 32MB (default 64MB)
```

---

## 🔧 Windows Docker Desktop Konfigürasyonu

### WSL 2 Sınırlarını Ayarla
`C:\Users\<USERNAME>\.wslconfig` dosyası oluştur:

```ini
[wsl2]
memory=4GB
processors=4
swap=2GB
localhostForwarding=true

[interop]
enabled=true
appendWindowsPath=true
```

### Docker Desktop Ayarları
1. **Settings → Resources**
   - **Memory**: 2-3GB (sistem RAM'inin yarısından az)
   - **CPUs**: 4 (toplam CPU'nuzdan 2 az)
   - **Swap**: 1GB

2. **Settings → WSL Integration**
   - ✅ "WSL 2-based engine" aktif
   - ✅ "Ubuntu" (WSL distro) seç

---

## 📊 Beklenen Performans

| Öncesi | Sonrası |
|--------|---------|
| 1.94GB Docker context | ~200MB ✨ |
| 5-10 dakika startup | ~30 saniye ✨ |
| PC takılıyor | Smooth çalışma ✨ |
| Sınırsız resource | Kontrollü kullanım ✨ |

---

## 🚀 Kurulum & Test

```bash
# Eski container'ları temizle
docker system prune -a --volumes

# Yeni optimizasyonlarla başlat
npm run start  # Veya setup.ps1
```

---

## 📌 Sorun Çözümü

### Hala yavaş çalışıyorsa?
1. **WSL2 sürümünü güncelle**: `wsl --update`
2. **Docker Desktop restart et**: İşlem Yöneticisi → Docker ortamını kapat
3. **Disk alanı kontrol et**: En az 10GB boş alan gerekli
4. **Antivirus**: Docker klasörünü exclude et

### Container crash oluyorsa?
- Memory limit'i artır `docker-compose.prod.yml`'de
- Logs kontrol et: `docker-compose logs -f`

---

## 🔍 Monitoring

```bash
# Real-time resource kullanımı
docker stats

# Container detaylı log
docker-compose logs -f backend

# Disk kullanımı
docker system df
```

---

**Tarih**: 9 Mart 2026  
**Durum**: ✅ Tüm optimizasyonlar uygulandı
