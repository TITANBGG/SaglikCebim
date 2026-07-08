# SaglikCebim QUICKSTART

Son guncelleme: 2026-06-01

---

## Hizli baslat (onerilen)

Proje kok klasorunde cift tikla:

```
START.bat
```

Bu script:
1. Port 8000 ve 5173'u temizler
2. Ollama durumunu kontrol eder
3. **Backend**'i ayri bir CMD penceresinde baslatir (PORT 8000)
4. Backend hazir olana kadar bekler
5. **Frontend**'i ayri bir CMD penceresinde baslatir (PORT 5173)
6. Tarayiciyi otomatik acar: http://127.0.0.1:5173

Durdurmak icin:

```
STOP.bat
```

---

## Portlar

| Servis    | URL                          |
|-----------|------------------------------|
| Frontend  | http://127.0.0.1:5173        |
| Backend   | http://127.0.0.1:8000        |
| API Docs  | http://127.0.0.1:8000/docs   |
| Ollama    | http://127.0.0.1:11434       |

---

## On kosullar

- **Python venv** hazir olmali: `backend (1)/venv/`
- **Node.js** kurulu olmali (`npm.cmd` calismali)
- **Ollama** acik ve `llama3` modeli yuklu olmali
  ```
  ollama list   # llama3:latest gorünmeli
  ```

---

## Manuel baslatis (gerekirse)

**Terminal 1 — Backend:**
```
cd "backend (1)"
venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 — Frontend:**
```
cd frontend
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

---

## Saglik kontrolu

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health
# Beklenen: {"status":"ok"}

Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5173
# Beklenen: 200 OK
```

---

## Test senaryolari

### 1. Dashboard — Modalite tamamlanma karti
Giris yaptiktan sonra Dashboard'da yuvarlak progress bar gormeli;
eksik moduller (anamnez / kan tahlili / radyoloji) listelenmeli.

### 2. NeyimVar — Klinik mesaj
> "3 gundur basim agriyor, ensem tutuldu"

Beklenen cikti:
- Risk rozeti (orta/yuksek)
- Olasi tanilar — kalibre % guven bari ile
- Onerilen bolumler (Kardiyoloji, Noroloji)
- Tetkikler (kan basinci, EKG)
- Tedavi fazlari
- Yasam tarzi onerileri
- Yapilmamasi gerekenler (NSAiD yasagi)

### 3. NeyimVar — Acil mesaj
> "Ani gogus agrim var, sol koluma vuruyor"

Beklenen: Kirmizi banner + "112'yi arayin"

### 4. NeyimVar — Sohbet
> "selam"

Beklenen: Klinik roadmap degil, dogal karsilama

### 5. Patient Summary API (yeni)
```
GET /patient/summary/basic
Authorization: Bearer <token>
```
Beklenen:
```json
{
  "completion_score": 0,
  "has_profile": false,
  "has_lab": false,
  "has_radiology": false,
  "missing_modalities": ["anamnez", "kan_tahlili", "radyoloji"]
}
```

---

## Sik sorunlar

| Sorun | Cozum |
|-------|-------|
| Login olunmuyor | Docker backend calisiyor olabilir: `docker stop saglikcebim_backend` |
| `npm` bulunamadi | `npm` yerine `npm.cmd` kullan |
| Port cakismasi | `STOP.bat` calistir, sonra `START.bat` |
| Chat/AI calismiyor | Ollama acik olmali ve `llama3` yuklu olmali |
| ClinicalKey veri gelmiyor | `.env` icinde `CLINICALKEY_COOKIE` gercek cookie ile doldurulmali |
