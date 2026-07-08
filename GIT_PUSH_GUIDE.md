# GitHub Push Rehberi — Seçici ve Güvenli

Bu rehber, projeyi GitHub'a *başarıyla* ve *güvenli* şekilde yüklemek için adım adım yönerge sağlar. Her şeyi push etmeyin — sadece gerekli kaynakları.

## 1) Hazırlık: Temizlik ve Gizlileri Çıkarma
- Lokal hassas ayarları (`settings.local.json`, `.env`, `secrets/`) repoya eklemeyin.
- Büyük dosyaları (ör. `dev.db*`, `uploads/radiology/*`) `.gitignore` ile hariç bırakın veya ayrı bir depoya/arkiv servisine taşıyın.

## 2) `.gitignore` (örnek içerik)
Aşağıdaki içeriği `.gitignore` dosyanıza koyun:

```
# Python
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
env/
venv/

# Databases
*.sqlite3
*.db
dev.db*

# Node
node_modules/
dist/
build/

# Local IDE
.vscode/

# Secrets
.env
*.local.json
settings.local.json

# OS
.DS_Store
Thumbs.db

# Uploads / large
uploads/

# Runtime / temporary
(1).runtime/
.runtime/
```

## 3) Hangi Dosyaları Eklemeli (Önerilen Liste)
- `backend/` — tüm kaynak kodu, `requirements.txt`, `app/` ve `Dockerfile`(varsa)
- `frontend/` — `src/`, `package.json`, `pnpm-lock.yaml` veya `package-lock.json`, `vite.config.ts`
- `docker-compose.yml`, `docker-compose.prod.yml` (şablonlar)
- `scripts/`, `setup.ps1`, `start-local.cmd`, `README.md`, `GIT_PUSH_GUIDE.md`, `final.md`
- `RAPORLAR/BACKEND_API_REFERENCE.md` (API dokümanı)

NOT: Büyük modeller, veri setleri veya veritabanı dump'ları pushlanmamalıdır.

## 4) Seçici Commit Adımları
1. Yeni repo oluşturun (GitHub web arayüzü veya `gh` CLI):

```bash
# GitHub CLI ile
gh repo create SaglikCebim --public --source=. --remote=origin --push
```

2. Yerel git başlatma ve varsayılan dal:

```bash
git init
git checkout -b main
```

3. Değişiklikleri gözden geçirme ve seçici ekleme:

```bash
git status
# İnceleyin
git add -p
# veya tek tek ekleyin
git add backend/requirements.txt backend/ backend/app backend/Dockerfile
git add frontend/package.json frontend/src frontend/vite.config.ts
git add docker-compose.yml docker-compose.prod.yml README.md GIT_PUSH_GUIDE.md final.md
git add RAPORLAR/BACKEND_API_REFERENCE.md
```

4. Commit ve push:

```bash
git commit -m "Initial selective commit: backend, frontend, docs, compose"
git remote add origin https://github.com/<kullanici>/<repo>.git
git push -u origin main
```

## 5) Büyük Dosyalar / LFS
Eğer repoya model ağırlığı gibi büyük dosyalar eklemeniz gerekiyorsa Git LFS kullanın:

```bash
git lfs install
git lfs track "models/*.bin"
git add .gitattributes
```

## 6) Son Kontroller
- `git log --stat` ile commitlerinizi kontrol edin.
- `git show --name-only <commit>` ile dosya listelerini gözden geçirin.
- Hassas dosya eklediğinizi fark ederseniz hemen `git rm --cached <dosya>` sonrası yeni commit ve push yapın.

## 7) Örnek İş Akışı (Hızlı)
```bash
# 1. Hazırla
cp example.env .env  # veya .env.template oluşturun
# 2. Seçici ekle
git add backend/ frontend/package.json README.md GIT_PUSH_GUIDE.md final.md docker-compose.yml
# 3. Commit & push
git commit -m "Prepare initial public repo with core services and docs"
git remote add origin https://github.com/<kullanici>/SaglikCebim.git
git push -u origin main
```

## 8) İpuçları
- `git add -p` ile değişiklikleri parça parça ekleyin.
- Büyük veya hassas dosyalar için ayrı özel depolar veya bulut depolama kullanın.
- `secrets` veya `settings.local.json` gibi dosyaları asla repoya eklemeyin. Eğer kazara eklendiyse, GitHub'da gizliliği yeniden sağlamanın adımları vardır (ör. rotate keys).

