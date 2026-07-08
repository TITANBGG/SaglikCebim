# 🏥 SaglikCebim Backend API Referansı

**API Versiyonu**: 0.1.0  
**Framework**: FastAPI  
**Port**: 8001  
**Base URL**: `http://127.0.0.1:8001`

---

## 📋 İçindekiler

1. [API Konfigürasyonu](#api-konfigürasyonu)
2. [Authentication](#authentication)
3. [Tüm Endpoint'ler](#tüm-endpoints)
4. [Veritabanı Models](#veritabanı-models)
5. [Request/Response Örnekleri](#requestresponse-örnekleri)
6. [Türkçe Terminoloji Standartları](#türkçe-terminoloji-standartları)
7. [Frontend Integration](#frontend-integration)

---

## API Konfigürasyonu

### Temel Bilgiler
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SaglikCebim API",
    description="Tibbi Tahlil Analiz Platformu",
    version="0.1.0"
)

# CORS Ayarları
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]
```

### Root Endpoints
```
GET /
  └─ Response: {"message": "SaglikCebim API is running"}

GET /health
  └─ Response: {"status": "ok"}
```

---

## Authentication

### Token Mekanizması
- **Token Tipi**: JWT (Bearer Token)
- **Storage**: localStorage.getItem("token")
- **Header Format**: `Authorization: Bearer <token>`
- **Interceptor**: Otomatik 401 hatasında login sayfasına yönlendirme

### Auth Router Prefix
```
/auth
```

---

## Tüm Endpoints

### 1️⃣ AUTH ENDPOINTS

#### 📍 `POST /auth/register`
Yeni kullanıcı kaydı ve JWT token döndürme

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "Ahmet Yılmaz"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error (400):**
```json
{
  "detail": "Email already registered"
}
```

---

#### 📍 `POST /auth/login`
Mevcut kullanıcı girişi

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error (401):**
```json
{
  "detail": "Invalid credentials"
}
```

---

#### 📍 `GET /auth/me`
Mevcut kullanıcı profili (Kimlik doğrulaması gerekli)

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "email": "user@example.com",
  "full_name": "Ahmet Yılmaz"
}
```

**Error (401):**
```json
{
  "detail": "Invalid token"
}
```

---

### 2️⃣ REPORTS ENDPOINTS

#### 📍 `GET /reports/`
Kullanıcının tüm raporlarını listele

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "filename": "e-nabiz-report-2026-04-28.pdf",
    "original_filename": "e-Nabiz Kan Tahlili.pdf",
    "file_path": "/uploads/reports/550e8400-e29b-41d4-a716-446655440000.pdf",
    "status": "analyzed",
    "created_at": "2026-04-28T10:30:00"
  }
]
```

---

#### 📍 `GET /reports/monitoring`
Dashboard için özet verileri (KPI'lar, trendler, son raporlar)

**Query Parameters:**
- `window_days`: Integer (Kaç günlük veri - varsayılan 30)
- `limit_rows`: Integer (Kaç rapor gösterilecek - varsayılan 8)

**Example:** `/reports/monitoring?window_days=30&limit_rows=8`

**Response (200):**
```json
{
  "kpis": {
    "reports": 12,
    "abnormal": 7,
    "normal": 38,
    "radiology": 4,
    "reports_change": 12,
    "abnormal_change": 3,
    "normal_change": 8,
    "radiology_change": 5
  },
  "focus_trends": [
    {
      "date": "Oca",
      "normal": 45,
      "abnormal": 15
    },
    {
      "date": "Şub",
      "normal": 52,
      "abnormal": 12
    }
  ],
  "recent_reports": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "e-Nabiz Kan Tahlili.pdf",
      "status": "Analiz Edildi",
      "created_at": "2026-04-28T10:30:00"
    }
  ]
}
```

---

#### 📍 `POST /reports/upload`
PDF rapor yükleme

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body:**
```
file: <PDF dosyası>
```

**Response (200):**
```json
{
  "message": "PDF yuklendi.",
  "report_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

#### 📍 `POST /reports/{report_id}/parse`
PDF analizi başlat (OCR/metin çıkarma)

**Path Parameter:**
- `report_id`: UUID

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "PDF analizi baslatildi."
}
```

---

#### 📍 `GET /reports/{report_id}/results`
Rapordan çıkarılan test sonuçları

**Path Parameter:**
- `report_id`: UUID

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440100",
    "report_id": "550e8400-e29b-41d4-a716-446655440000",
    "test_name": "Hemoglobin",
    "original_name": "HGB",
    "value": 14.5,
    "unit": "g/dL",
    "ref_min": 13.5,
    "ref_max": 17.5,
    "status": "Normal",
    "created_at": "2026-04-28T10:30:00"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440101",
    "report_id": "550e8400-e29b-41d4-a716-446655440000",
    "test_name": "Kolesterol",
    "original_name": "CHOL",
    "value": 245.0,
    "unit": "mg/dL",
    "ref_min": 0,
    "ref_max": 200,
    "status": "High",
    "created_at": "2026-04-28T10:30:00"
  }
]
```

---

#### 📍 `GET /reports/{report_id}/download-pdf`
PDF raporunu indir (binary dosya)

**Path Parameter:**
- `report_id`: UUID

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** PDF binary dosyası

---

#### 📍 `DELETE /reports/{report_id}`
Rapor sil

**Path Parameter:**
- `report_id`: UUID

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Rapor silindi."
}
```

---

#### 📍 `POST /reports/{report_id}/pubmed`
Anormal test sonuçları için PubMed makaleleri getir

**Path Parameter:**
- `report_id`: UUID

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "articles": [
    {
      "title": "High Cholesterol and Cardiovascular Risk",
      "abstract": "...",
      "url": "https://pubmed.ncbi.nlm.nih.gov/12345678",
      "authors": "Smith J, Doe A",
      "publication_date": "2024-01-15"
    }
  ]
}
```

---

#### 📍 `GET /reports/{report_id}/recommendations`
Kişiselleştirilmiş sağlık önerileri

**Path Parameter:**
- `report_id`: UUID

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "recommendations": [
    {
      "category": "Beslenme",
      "recommendation": "Kolesterol oranını düşürmek için doymuş yağları azaltın.",
      "priority": "high"
    },
    {
      "category": "Egzersiz",
      "recommendation": "Haftada 150 dakika orta yoğunluklu egzersiz yapın.",
      "priority": "medium"
    }
  ]
}
```

---

#### 📍 `GET /reports/trends/{test_name}`
Spesifik test için zaman serisi trend verisi

**Path Parameter:**
- `test_name`: String (Test adı, örn. "Hemoglobin")

**Query Parameters:**
- `window_days`: Integer (Kaç günlük veri)

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "test_name": "Hemoglobin",
  "unit": "g/dL",
  "trends": [
    {
      "date": "2026-04-01",
      "value": 13.8,
      "status": "Normal"
    },
    {
      "date": "2026-04-15",
      "value": 14.2,
      "status": "Normal"
    },
    {
      "date": "2026-04-28",
      "value": 14.5,
      "status": "Normal"
    }
  ]
}
```

---

#### 📍 `GET /reports/available-tests`
Sistemde mevcut tüm test türleri

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "available_tests": [
    {
      "test_name": "Hemoglobin",
      "unit": "g/dL",
      "ref_min": 13.5,
      "ref_max": 17.5,
      "category": "Hematology"
    },
    {
      "test_name": "Kolesterol",
      "unit": "mg/dL",
      "ref_min": 0,
      "ref_max": 200,
      "category": "Biochemistry"
    }
  ]
}
```

---

### 3️⃣ RADIOLOGY ENDPOINTS

#### 📍 `POST /radiology/upload`
Göğüs röntgeni (chest X-ray) yükleme ve analiz

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body:**
```
file: <DICOM veya PNG dosyası>
```

**Response (200):**
```json
{
  "message": "Upload X-ray endpoint",
  "image_id": "550e8400-e29b-41d4-a716-446655440200",
  "findings": [
    {
      "pathology_name": "Normal",
      "confidence_score": "0.95",
      "heatmap_path": "/uploads/heatmaps/550e8400.png"
    }
  ]
}
```

---

### 4️⃣ ANAMNESIS ENDPOINTS

#### 📍 `POST /api/v1/anamnesis/chat`
Multi-agent AI sağlık danışmanı sohbeti (Türkçe)

**Endpoint Prefix:** `/api/v1/anamnesis` (diğer endpointlerden farklı)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "message": "Hemoglobin seviyem düşük, ne yapmalıyım?",
  "context": {
    "age": 35,
    "gender": "Female",
    "recent_symptoms": ["Yorgunluk", "Nefes darlığı"]
  }
}
```

**Response (200):**
```json
{
  "message": "Düşük hemoglobin genellikle anemi ile ilişkilidir...",
  "agents": [
    {
      "agent_name": "Nutritionist",
      "response": "Demir açısından zengin gıdalar tüketin..."
    },
    {
      "agent_name": "Doctor",
      "response": "Lütfen bir doktor ile görüşünüz..."
    }
  ]
}
```

---

### 5️⃣ ARTICLES ENDPOINTS

#### 📍 `GET /articles/daily`
PubMed'den günlük önerilen makaleler

**Query Parameters:**
- `limit`: Integer (Kaç makale - varsayılan 6)

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "articles": [
    {
      "title": "Cardiovascular Health and Cholesterol Management",
      "abstract": "This study examines...",
      "url": "https://pubmed.ncbi.nlm.nih.gov/12345678",
      "authors": ["Smith J", "Doe A"],
      "publication_date": "2024-01-15",
      "relevance_score": 0.92
    }
  ]
}
```

---

#### 📍 `POST /articles/search`
PubMed'de makale arama

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "query": "Kolesterol yönetimi",
  "max_results": 8,
  "include_focus": true
}
```

**Response (200):**
```json
{
  "query": "Kolesterol yönetimi",
  "total_results": 15234,
  "articles": [
    {
      "title": "Effective Cholesterol Management Strategies",
      "abstract": "...",
      "url": "https://pubmed.ncbi.nlm.nih.gov/...",
      "authors": ["..."],
      "publication_date": "2024-01-15"
    }
  ]
}
```

---

#### 📍 `POST /articles/chat`
Multi-agent AI makale analizi ve tartışma (Türkçe)

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "message": "Bu makaledeki bulguların klinikte uygulanabilirliği nedir?",
  "article_id": "550e8400-e29b-41d4-a716-446655440300"
}
```

**Response (200):**
```json
{
  "discussion": "Multi-agent AI tartışması...",
  "agents": [
    {
      "agent_name": "ResearchDoctor",
      "response": "Bu bulguların klinik uygulanabilirliği..."
    }
  ]
}
```

---

### 6️⃣ NOTIFICATIONS ENDPOINTS

#### 📍 `POST /notifications/subscribe`
Web Push Notifications'a abone ol

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "subscription": {
    "endpoint": "https://fcm.googleapis.com/fcm/send/...",
    "keys": {
      "p256dh": "...",
      "auth": "..."
    }
  }
}
```

**Response (200):**
```json
{
  "message": "Subscribe to push notifications",
  "subscription_id": "550e8400-e29b-41d4-a716-446655440400"
}
```

---

#### 📍 `DELETE /notifications/unsubscribe`
Push Notifications aboneliğinden çık

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Unsubscribe from push notifications"
}
```

---

#### 📍 `GET /notifications/vapid-key`
Web Push VAPID public key'i al

**Response (200):**
```json
{
  "vapid_public_key": "BCxxx..."
}
```

---

#### 📍 `GET /notifications/`
Kullanıcının tüm bildirimlerini listele

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit`: Integer (Kaç bildirim)
- `skip`: Integer (Pagination offset)

**Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440500",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Test Sonuçları Hazır",
    "body": "Kan tahlili sonuçlarınız analiz edildi.",
    "notification_type": "alert",
    "is_read": false,
    "created_at": "2026-04-28T15:30:00"
  }
]
```

---

#### 📍 `POST /notifications/{notification_id}/read`
Bildirimi okundu olarak işaretle

**Path Parameter:**
- `notification_id`: UUID

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Mark notification as read"
}
```

---

#### 📍 `POST /notifications/read-all`
Tüm bildirimleri okundu olarak işaretle

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Mark all notifications as read",
  "updated_count": 5
}
```

---

#### 📍 `POST /notifications/test-push`
Test push notification gönder (geliştirme için)

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Send test push notification",
  "notification_sent": true
}
```

---

## Veritabanı Models

### User Model
```python
class User(Base):
    __tablename__ = "users"
    
    id: Integer (Primary Key)
    email: String(255) - UNIQUE, INDEXED
    hashed_password: String(255)
    full_name: String(255) - Nullable
    created_at: DateTime - Default: now()
    updated_at: DateTime - Default & Updated: now()
```

**SQL:**
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

### Report Model
```python
class Report(Base):
    __tablename__ = "reports"
    
    id: UUID (Primary Key)
    user_id: UUID - INDEXED
    filename: String(255)
    original_filename: String(255)
    file_path: String(512)
    status: String(50) - Values: pending, parsed, analyzed, failed
    created_at: DateTime - Default: now()
```

---

### TestResult Model
```python
class TestResult(Base):
    __tablename__ = "test_results"
    
    id: UUID (Primary Key)
    report_id: UUID - INDEXED
    test_name: String(255) - Türkçe ad
    original_name: String(255) - Orijinal ad
    value: Numeric(10, 2)
    unit: String(50) - Ölçü birimi (g/dL, mg/dL, vb.)
    ref_min: Numeric(10, 2) - Referans minimum
    ref_max: Numeric(10, 2) - Referans maksimum
    status: String(50) - Values: High, Low, Normal, NotDetectable
    created_at: DateTime - Default: now()
```

---

### PatientProfile Model
```python
class PatientProfile(Base):
    __tablename__ = "patient_profiles"
    
    id: UUID (Primary Key)
    user_id: UUID - INDEXED, UNIQUE
    age: String(10)
    gender: String(10) - Values: Male, Female, Other
    height: String(10)
    weight: String(10)
    blood_type: String(10)
    created_at: DateTime - Default: now()
    updated_at: DateTime - Default & Updated: now()
```

---

### PatientAllergy Model
```python
class PatientAllergy(Base):
    __tablename__ = "patient_allergies"
    
    id: UUID (Primary Key)
    user_id: UUID - INDEXED
    allergen_name: String(255)
    reaction_type: String(255)
    created_at: DateTime - Default: now()
```

---

### PatientMedication Model
```python
class PatientMedication(Base):
    __tablename__ = "patient_medications"
    
    id: UUID (Primary Key)
    user_id: UUID - INDEXED
    medication_name: String(255)
    dosage: String(255)
    start_date: String(50) - ISO date format
    created_at: DateTime - Default: now()
```

---

### PatientFamilyHistory Model
```python
class PatientFamilyHistory(Base):
    __tablename__ = "patient_family_histories"
    
    id: UUID (Primary Key)
    user_id: UUID - INDEXED
    relation_type: String(255) - Anne, Baba, Kardeş, vb.
    condition_name: String(255)
    created_at: DateTime - Default: now()
```

---

### PatientCondition Model
```python
class PatientCondition(Base):
    __tablename__ = "patient_conditions"
    
    id: UUID (Primary Key)
    user_id: UUID - INDEXED
    condition_name: String(255)
    diagnosis_date: String(50)
    created_at: DateTime - Default: now()
```

---

### RadiologyImage Model
```python
class RadiologyImage(Base):
    __tablename__ = "radiology_images"
    
    id: UUID (Primary Key)
    user_id: UUID - INDEXED
    image_path: String(512)
    image_type: String(50) - DICOM, PNG, vb.
    created_at: DateTime - Default: now()
```

---

### RadiologyFinding Model
```python
class RadiologyFinding(Base):
    __tablename__ = "radiology_findings"
    
    id: UUID (Primary Key)
    image_id: UUID - INDEXED
    pathology_name: String(255)
    confidence_score: String(10) - 0.0-1.0 range
    heatmap_path: String(512)
    created_at: DateTime - Default: now()
```

---

### Notification Model
```python
class Notification(Base):
    __tablename__ = "notifications"
    
    id: UUID (Primary Key)
    user_id: UUID - INDEXED
    title: String(255)
    body: String
    notification_type: String(50) - reminder, alert, weekly_summary, article
    is_read: Boolean - Default: False
    created_at: DateTime - Default: now()
```

---

### AnamnesisState Model
```python
class AnamnesisState(Base):
    __tablename__ = "anamnesis_state"
    
    id: Integer (Primary Key)
    user_id: Integer
    state_data: String - JSON formatında state
    created_at: DateTime - Default: now()
```

---

## Request/Response Örnekleri

### Tam Login Flow

**1. Register**
```bash
curl -X POST "http://127.0.0.1:8001/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ahmet@example.com",
    "password": "SecurePass123!",
    "full_name": "Ahmet Yılmaz"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDEiLCJleHAiOjE3MTQzNDU2MDB9.XXX",
  "token_type": "bearer"
}
```

**2. Login**
```bash
curl -X POST "http://127.0.0.1:8001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ahmet@example.com",
    "password": "SecurePass123!"
  }'
```

**3. Get Profile**
```bash
curl -X GET "http://127.0.0.1:8001/auth/me" \
  -H "Authorization: Bearer <token>"
```

---

### Rapor Yükleme ve Analiz

**1. PDF Yükle**
```bash
curl -X POST "http://127.0.0.1:8001/reports/upload" \
  -H "Authorization: Bearer <token>" \
  -F "file=@report.pdf"
```

**Response:**
```json
{
  "message": "PDF yuklendi.",
  "report_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**2. PDF'i Parse Et**
```bash
curl -X POST "http://127.0.0.1:8001/reports/550e8400-e29b-41d4-a716-446655440000/parse" \
  -H "Authorization: Bearer <token>"
```

**3. Test Sonuçlarını Al**
```bash
curl -X GET "http://127.0.0.1:8001/reports/550e8400-e29b-41d4-a716-446655440000/results" \
  -H "Authorization: Bearer <token>"
```

---

## Türkçe Terminoloji Standartları

### Test Sonuçları Status
| Değer | Anlamı | Kullanım |
|-------|--------|---------|
| `Normal` | Normal sonuç | `status: "Normal"` |
| `High` | Yüksek değer | `status: "High"` |
| `Low` | Düşük değer | `status: "Low"` |
| `NotDetectable` | Tespit edilemedi | `status: "NotDetectable"` |

### Report Status
| Değer | Anlamı |
|-------|--------|
| `pending` | Bekleniyor |
| `parsed` | Parse edildi |
| `analyzed` | Analiz edildi |
| `failed` | Başarısız |

### Notification Types
| Değer | Anlamı |
|-------|--------|
| `reminder` | Anımsatıcı |
| `alert` | Uyarı |
| `weekly_summary` | Haftalık özet |
| `article` | Makale |

### Gender Values
| Değer | Anlamı |
|-------|--------|
| `Male` | Erkek |
| `Female` | Kadın |
| `Other` | Diğer |

### Radiology Image Types
| Değer | Anlamı |
|-------|--------|
| `DICOM` | DICOM format |
| `PNG` | PNG format |
| `JPG` | JPG format |

### Family Relations
| Değer | Anlamı |
|-------|--------|
| `Mother` | Anne |
| `Father` | Baba |
| `Sibling` | Kardeş |
| `Grandparent` | Büyükanne/Büyükbaba |

---

## Frontend Integration

### API Client Setup

**File:** `frontend/src/services/api.js`

```javascript
import axios from "axios";

const api = axios.create({
  baseURL: "/api"  // Proxy routes to backend
});

// Request interceptor - Add JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - Handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && window.location.pathname !== "/login") {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
```

### Frontend API Calls

**Authentication Context** (`src/context/AuthContext.jsx`):
```javascript
const login = async (email, password) => {
  const { data } = await api.post("/auth/login", { email, password });
  localStorage.setItem("token", data.access_token);
};

const register = async (email, password, full_name) => {
  await api.post("/auth/register", { email, password, full_name });
  return await login(email, password);
};
```

**Dashboard** (`src/pages/Dashboard.jsx`):
```javascript
api.get("/reports/monitoring?window_days=30&limit_rows=8")
  .then(({ data }) => {
    setMonitoring(data);
  });
```

**Upload** (`src/pages/Upload.jsx`):
```javascript
const formData = new FormData();
formData.append("file", file);
await api.post("/reports/upload", formData);

await api.post(`/reports/${id}/parse`);

await api.delete(`/reports/${id}`);
```

**Radiology** (`src/pages/Radiology.jsx`):
```javascript
const formData = new FormData();
formData.append("file", imageFile);
await api.post("/radiology/upload", formData);
```

**Articles** (`src/pages/Articles.jsx`):
```javascript
api.get("/articles/daily?limit=6");
api.post("/articles/search", { query, max_results: 8 });
```

---

## Router Configuration

**File:** `app/main.py`

```python
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(articles.router, prefix="/articles", tags=["articles"])
app.include_router(radiology.router, prefix="/radiology", tags=["radiology"])
app.include_router(anamnesis.router, prefix="/api/v1/anamnesis", tags=["anamnesis"])
```

---

## Dosya Yapısı

```
backend (1)/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py              ← Authentication endpoints
│   │   │   ├── reports.py           ← Report management
│   │   │   ├── radiology.py         ← Radiology endpoints
│   │   │   ├── anamnesis.py         ← Health chat AI
│   │   │   ├── articles.py          ← PubMed integration
│   │   │   ├── notifications.py     ← Push notifications
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── models/
│   │   ├── user.py
│   │   ├── report.py
│   │   ├── test_result.py
│   │   ├── anamnesis.py
│   │   ├── patient_allergies.py
│   │   ├── patient_conditions.py
│   │   ├── patient_family_history.py
│   │   ├── patient_medications.py
│   │   ├── patient_symptom_snapshot.py
│   │   ├── radiology_image.py
│   │   ├── radiology_finding.py
│   │   ├── radiology_context_link.py
│   │   ├── notification.py
│   │   ├── push_subscription.py
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py              ← Pydantic request/response models (empty)
│   ├── core/
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── dependencies.py
│   │   └── __init__.py
│   ├── services/
│   │   └── scheduler.py
│   ├── main.py                      ← FastAPI app setup & router registration
│   ├── __init__.py
│   └── __pycache__/
├── run.py                           ← Entry point (uvicorn)
├── requirements.txt
├── .env                             ← Environment variables
├── .env.example
└── alembic/                         ← Database migrations
```

---

## Notlar

- ⚠️ **Çoğu endpoint şu an "stub"** durumunda (template response döndürüyor)
- ⚠️ **UUID vs Integer Mixed** - User: Integer, Report/Test Results: UUID
- ✅ **Türkçe Terminoloji** - Tutarlı olarak uygulanıyor
- ✅ **Frontend Fallback Demo Veri** - Backend hazır değilse demo gösteriyor
- 🔐 **JWT Token Validation** - `/auth/me` endpoint'i korumalı
- 📱 **Web Push Ready** - Notification infrastructure var
- 🔬 **AI Integration** - Multi-agent chat endpoints (anamnesis, articles)

---

**Son Güncellenme:** 28 Nisan 2026  
**API Versiyonu:** 0.1.0
