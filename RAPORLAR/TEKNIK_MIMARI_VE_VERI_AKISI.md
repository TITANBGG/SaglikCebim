# 🏥 SağlıkCebim - TeknikMimari ve Veri Akışı

## 1. SISTEM MİMARİSİ DIYAGRAMI

```
╔════════════════════════════════════════════════════════════════════════════╗
║                           FRONTEND LAYER (React PWA)                        ║
║  ┌─────────────────┬──────────────────┬─────────────────┬────────────────┐ ║
║  │   Login/Reg     │   Dashboard      │   Lab Results   │   Radiology    │ ║
║  │   (Auth)        │   (Overview)     │   (Charts)      │   (X-Ray AI)   │ ║
║  └─────────────────┴──────────────────┴─────────────────┴────────────────┘ ║
║  ┌──────────────────────────────────────────────────────────────────────┐  ║
║  │    Anamnesis/History       │    Chatbot                │  Profile     │  ║
║  │    (Symptoms CRUD)         │    (AI Assistant)         │  (Settings)  │  ║
║  └──────────────────────────────────────────────────────────────────────┘  ║
║                                                                              ║
║     Service Worker (Offline support)     │     AuthContext (State Mgmt)     ║
║     Tailwind CSS (Responsive UI)         │     Recharts (Data Viz)          ║
╚═══════════════════════════╤════════════════════════════════════════════════╝
                            │ HTTP/HTTPS
                            │ (Axios client)
                            ▼
╔════════════════════════════════════════════════════════════════════════════╗
║                        NGINX REVERSE PROXY                                  ║
║  ┌──────────────────────────────────────────────────────────────────────┐  ║
║  │  Port 80 (HTTP) / Port 443 (HTTPS)                                  │  ║
║  │  - Serve SPA (React build)                                          │  ║
║  │  - Proxy /api/* → Backend (port 8000/8001)                          │  ║
║  │  - CORS headers, compression                                        │  ║
║  └──────────────────────────────────────────────────────────────────────┘  ║
╚═══════════════════════════╤════════════════════════════════════════════════╝
                            │ REST API calls
                            ▼
╔════════════════════════════════════════════════════════════════════════════╗
║                    BACKEND LAYER (FastAPI + Services)                       ║
║                                                                              ║
║  ┌────────────────────────────────────────────────────────────────────┐   ║
║  │                      API ROUTES (26 Endpoint)                      │   ║
║  │  ┌──────────┬──────────────┬─────────────┬──────────┬────────────┐ │   ║
║  │  │ /auth    │ /reports     │ /radiology  │ /articles│ /anamnesis│ │   ║
║  │  │ (3 ep)   │ (11 ep)      │ (2 ep)      │ (2 ep)   │ (6 ep)    │ │   ║
║  │  │ Register │ Upload PDF   │ Upload X-Ray│ Search   │ Profile   │ │   ║
║  │  │ Login    │ List Reports │ Analyze DNN │ Trending │ Conditions│ │   ║
║  │  │ Profile  │ Analyze Tests│ Get Results │ Details  │ Meds      │ │   ║
║  │  │          │ Get Trends   │             │          │ Allergies │ │   ║
║  │  │          │ Monitoring   │             │          │ History   │ │   ║
║  │  └──────────┴──────────────┴─────────────┴──────────┴────────────┘ │   ║
║  │                                                                      │   ║
║  │  + /notifications (7 ep) + /chatbot (2 ep) + /health (1 ep)         │   ║
║  └────────────────────────────────────────────────────────────────────┘   ║
║                                                                              ║
║  ┌────────────────────────────────────────────────────────────────────┐   ║
║  │                      SERVICE LAYER                                 │   ║
║  │  ┌──────────────────┬─────────────────┬──────────────────────────┐ │   ║
║  │  │  Auth Service    │  PDF Parser     │  Multi-Agent AI System   │ │   ║
║  │  │  - JWT tokens    │  Service        │  ┌────────────────────┐  │ │   ║
║  │  │  - PBKDF2 hashing│  - pdfplumber   │  │ Intent Agent       │  │ │   ║
║  │  │  - User CRUD     │  - 503 tests    │  │ Personal Agent     │  │ │   ║
║  │  │                  │  - Regex parse  │  │ Knowledge Agent    │  │ │   ║
║  │  │                  │  - Value/unit   │  │ Answer Agent       │  │ │   ║
║  │  │                  │  - Normalization│  │                    │  │ │   ║
║  │  │                  │  - DB save      │  │ + Ollama (Llama3)  │  │ │   ║
║  │  │                  │                 │  └────────────────────┘  │ │   ║
║  │  └──────────────────┴─────────────────┴──────────────────────────┘ │   ║
║  │                                                                      │   ║
║  │  ┌──────────────────┬──────────────────┬──────────────────────────┐ │   ║
║  │  │  Radiology AI    │  PubMed Svc      │  Notification Service    │ │   ║
║  │  │  - DenseNet-121  │  - Hybrid search │  - VAPID Web Push        │ │   ║
║  │  │  - Preprocessing │  - BM25 + Dense  │  - APScheduler tasks     │ │   ║
║  │  │  - Inference     │  - Re-ranking    │  - Email optional        │ │   ║
║  │  │  - 14 findings   │  - Evidence      │  - Subscription mgmt     │ │   ║
║  │  │  - AUROC 0.8079  │  - Academic refs │  - Notification types    │ │   ║
║  │  └──────────────────┴──────────────────┴──────────────────────────┘ │   ║
║  │                                                                      │   ║
║  │  ┌──────────────────┬──────────────────┬──────────────────────────┐ │   ║
║  │  │  Report Gen      │  Scheduler       │  Error Handling          │ │   ║
║  │  │  - reportlab PDF │  - APScheduler   │  - Middleware            │ │   ║
║  │  │  - A4 format     │  - Background    │  - Exception logger      │ │   ║
║  │  │  - Charts        │    tasks         │  - Audit logging         │ │   ║
║  │  │  - Patient summary│  - Notif queues  │  - Consistency check     │ │   ║
║  │  └──────────────────┴──────────────────┴──────────────────────────┘ │   ║
║  └────────────────────────────────────────────────────────────────────┘   ║
║                                                                              ║
║  ┌────────────────────────────────────────────────────────────────────┐   ║
║  │                    DATA ACCESS LAYER (ORM)                         │   ║
║  │  SQLAlchemy 2.0  ─  Pydantic Schemas  ─  Alembic Migrations      │   ║
║  └────────────────────────────────────────────────────────────────────┘   ║
╚═══════════════════════════╤════════════════════════════════════════════════╝
                            │ SQL queries
                            ▼
╔════════════════════════════════════════════════════════════════════════════╗
║                    DATABASE LAYER (PostgreSQL 15)                           ║
║  ┌─────────────────────────────────────────────────────────────────────┐  ║
║  │                                                                     │  ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │  ║
║  │  │ USERS        │  │ REPORTS      │  │ TEST_RESULTS             │ │  ║
║  │  │ ├─ id (PK)   │  │ ├─ id (PK)   │  │ ├─ id (PK)              │ │  ║
║  │  │ ├─ email     │  │ ├─ user_id   │  │ ├─ report_id (FK)       │ │  ║
║  │  │ ├─ password  │  │ ├─ filename  │  │ ├─ test_name            │ │  ║
║  │  │ └─ full_name │  │ ├─ file_path │  │ ├─ value                │ │  ║
║  │  │              │  │ ├─ status    │  │ ├─ unit                 │ │  ║
║  │  │              │  │ └─ timestamps│  │ ├─ ref_min/max          │ │  ║
║  │  │              │  │              │  │ └─ status (H/L/N)       │ │  ║
║  │  └──────────────┘  └──────────────┘  └──────────────────────────┘ │  ║
║  │                                                                     │  ║
║  │  ┌─────────────────────────┐  ┌──────────────────────────────────┐ │  ║
║  │  │ PATIENT_PROFILE         │  │ ANAMNESIS_STATE                  │ │  ║
║  │  │ ├─ age, gender          │  │ ├─ chief_complaint               │ │  ║
║  │  │ ├─ height, weight, bmi  │  │ ├─ symptoms (JSONB)              │ │  ║
║  │  │ ├─ blood_type           │  │ ├─ onset_date                    │ │  ║
║  │  │ └─ chronic_conditions   │  │ └─ duration                      │ │  ║
║  │  └─────────────────────────┘  └──────────────────────────────────┘ │  ║
║  │                                                                     │  ║
║  │  ┌──────────────────────────┐  ┌──────────────────────────────────┐ │  ║
║  │  │ RADIOLOGY_IMAGES         │  │ NOTIFICATIONS                    │ │  ║
║  │  │ ├─ image_path            │  │ ├─ user_id (FK)                  │ │  ║
║  │  │ ├─ analysis_status       │  │ ├─ title, body                   │ │  ║
║  │  │ ├─ findings (14 types)   │  │ ├─ type (reminder/alert)         │ │  ║
║  │  │ └─ confidence_scores     │  │ ├─ is_read                       │ │  ║
║  │  │                          │  │ └─ created_at                    │ │  ║
║  │  └──────────────────────────┘  └──────────────────────────────────┘ │  ║
║  │                                                                     │  ║
║  │  + PATIENT_CONDITION, PATIENT_MEDICATION, PATIENT_ALLERGY,          │  ║
║  │    PATIENT_FAMILY_HISTORY, CHAT_SESSION, PUSH_SUBSCRIPTIONS         │  ║
║  │                                                                     │  ║
║  │  📊 14 Tablo | 4 Migration | Auto-generated Indexes               │  ║
║  │  🔒 ACID Transactions | Foreign Key Constraints                   │  ║
║  └─────────────────────────────────────────────────────────────────────┘  ║
╚════════════════════════════════════════════════════════════════════════════╝
```

---

## 2. VERİ AKIŞI DİYAGRAMLARI

### A. Kan Tahlili PDF Upload Flow

```
┌──────────────────────────────────────────────────────────────┐
│  1. Frontend: PDF Seçim ve Upload                           │
└──────────────────────┬───────────────────────────────────────┘
                       │ POST /reports/upload (multipart/form-data)
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  2. Backend: File Validation                                │
│  └─ Boyut kontrolü (≤50MB)                                 │
│  └─ MIME type kontrolü (application/pdf)                   │
│  └─ Virus scan (optional)                                  │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  3. PDF Parser Service                                       │
│  └─ pdfplumber ile text çıkar                             │
│  └─ 503 test regex patterns uygula                        │
│  └─ Laboratory format detect (9 format)                   │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  4. Data Extraction                                          │
│  ├─ Test Name (normalize: "WBC" → "White Blood Cell")    │
│  ├─ Value (float): 5.2                                    │
│  ├─ Unit (string): 10^3/μL                                │
│  ├─ Ref Min/Max: 4.5-11.0                                 │
│  └─ Status: NORMAL | HIGH | LOW                           │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  5. Database Save (SQLAlchemy)                               │
│  ├─ reports table:                                          │
│  │  ├─ filename: "report_2026-05-08_123456.pdf"           │
│  │  ├─ file_path: "/app/uploads/..."                      │
│  │  └─ status: "parsed"                                   │
│  │                                                          │
│  └─ test_results table (bulk insert 30-50 rows):           │
│     ├─ test_results[0]: {test_name: "WBC", value: 5.2}   │
│     ├─ test_results[1]: {test_name: "RBC", value: 4.8}   │
│     └─ ...                                                 │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  6. Frontend Notification                                    │
│  └─ 200 OK response + test list                           │
│  └─ Charts update (Recharts)                              │
│  └─ Trends visible                                        │
│  └─ Abnormal values highlighted (red)                     │
└──────────────────────────────────────────────────────────────┘
```

### B. Chatbot Multi-Agent Flow

```
┌──────────────────────────────────────────────────────────────┐
│  1. User Input                                               │
│  "Başımda ağrısı var, midede bulantı hissediyorum"        │
└──────────────────────┬───────────────────────────────────────┘
                       │ POST /api/v1/chatbot/chat
                       │ {message: "...", user_id: "..."}
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  2. Intent Agent                                             │
│  "Bu mesaj klinik mi, bilgi mi, beslenme mi?"               │
│  └─ LLM classification (Ollama)                            │
│  └─ Output: "CLINICAL" (triage needed)                    │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  3. Personal Agent (Context Injection)                      │
│  "Bu hastanın profilini ve geçmiş raporlarını ekle"        │
│  ├─ patient_profile (age: 34, gender: F, bmi: 24.5)      │
│  ├─ latest_reports (last 3 lab results)                   │
│  ├─ anamnesis_state (chief_complaint, symptoms)           │
│  └─ radiology_findings (if any chest X-ray)               │
│                                                              │
│  Output Context:                                             │
│  {                                                           │
│    "chief_complaint": "Başağrısı, bulantı",               │
│    "wbc_trend": [5.2, 6.1, 7.3], ← elevated              │
│    "recent_xray": "infiltration in left lower lobe",       │
│    "medications": ["Aspirin 100mg daily"]                  │
│  }                                                           │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  4. Knowledge Agent (Medical KB Lookup)                      │
│  ├─ Semptom: "Headache + Nausea + Elevated WBC"           │
│  ├─ Possible diagnoses: Migraine, URI, Sinusitis, ...     │
│  ├─ Confidence scores: Migraine (0.72), URI (0.65), ...   │
│  │                                                          │
│  └─ PubMed Search Triggered:                               │
│     ├─ Query: "migraine management fever"                  │
│     ├─ Top 5 papers: (with re-ranking)                    │
│     └─ Evidence level: A, B, C classifications              │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  5. Answer Agent (Response Generation)                      │
│  ├─ Recommendation:                                         │
│  │  {                                                       │
│  │    "triage": "HIGH - 2 hours",                          │
│  │    "department": "ENT / Neurology",                     │
│  │    "ddx": [                                             │
│  │      {"condition": "Migraine", "confidence": 0.72},    │
│  │      {"condition": "URI", "confidence": 0.65}          │
│  │    ],                                                    │
│  │    "action": "Immediate care if fever > 39°C",         │
│  │    "evidence_links": ["PubMed:12345", ...],            │
│  │    "red_flags": ["Fever + neck stiffness → meningitis"]│
│  │  }                                                       │
│  │                                                          │
│  └─ Consistency Check:                                      │
│     ├─ Rule: high_risk BUT no emergency action? → ERROR    │
│     ├─ Rule: red_flags present BUT low confidence? → ERROR │
│     └─ All rules pass → Proceed                            │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  6. Frontend Rendering                                       │
│  ├─ Risk Level: 🔴 HIGH (red card)                         │
│  ├─ Department: ENT / Neurology                            │
│  ├─ Differential Diagnosis:                                 │
│  │  ├─ 🟠 Migraine (72% confidence) ← highlighted         │
│  │  ├─ 🟡 URI (65% confidence)                             │
│  │  └─ [Evidence Papers] link                              │
│  ├─ Action:                                                 │
│  │  ├─ Call emergency if fever > 39°C                      │
│  │  ├─ Visit ENT within 2 hours                            │
│  │  └─ Home remedies in meantime...                        │
│  └─ Chat bubble rendered + saved to DB                     │
└──────────────────────────────────────────────────────────────┘
```

### C. Radyoloji X-Ray Analysis Flow

```
┌──────────────────────────────────────────────────────────────┐
│  1. Frontend: X-Ray Image Upload                            │
│  └─ PNG/JPG selected, < 10MB                              │
└──────────────────────┬───────────────────────────────────────┘
                       │ POST /radiology/upload
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  2. Image Preprocessing (PIL/OpenCV)                         │
│  ├─ Load image: Convert to grayscale (if needed)           │
│  ├─ Resize: 224×224 pixels (DenseNet input)               │
│  ├─ Normalize: [0, 1] range                                │
│  ├─ Apply intensity correction (HU windowing if DICOM)     │
│  └─ Augmentation (test-time): slight rotations, flips      │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  3. DenseNet-121 Inference                                   │
│  ├─ Pretrained ImageNet weights                             │
│  ├─ Fine-tuned on ChexPert dataset (14 findings)           │
│  ├─ Output: 14-class probability logits                     │
│  │  ├─ Atelectasis: 0.15                                   │
│  │  ├─ Cardiomegaly: 0.87 ← HIGH                           │
│  │  ├─ Consolidation: 0.42                                 │
│  │  ├─ Infiltrate: 0.78 ← HIGH                             │
│  │  ├─ Pleural Effusion: 0.03                              │
│  │  └─ ... (9 more)                                        │
│  │                                                          │
│  └─ Inference time: 2-3 seconds (GPU), 4-5 sec (CPU)      │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  4. Confidence Thresholding                                   │
│  ├─ Threshold: 0.5 (configurable)                          │
│  ├─ High confidence (>0.5):                                 │
│  │  ├─ Cardiomegaly: 0.87 ✓ (flag as present)             │
│  │  └─ Infiltrate: 0.78 ✓ (flag as present)               │
│  │                                                          │
│  └─ Low confidence (<0.5): Not reported                     │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  5. Database Save (radiology_images table)                   │
│  ├─ image_path: "/uploads/2026-05-08_xyz.jpg"              │
│  ├─ analysis_status: "completed"                            │
│  ├─ findings: {                                             │
│  │   "cardiomegaly": {"detected": true, "confidence": 0.87},│
│  │   "infiltrate": {"detected": true, "confidence": 0.78}, │
│  │   ... (14 findings)                                      │
│  │ }                                                         │
│  └─ model_version: "densenet121_chexpert_v2"               │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  6. Chatbot Context Injection                                │
│  └─ Personal Agent pulls radiology findings                │
│  └─ "Patient has cardiomegaly + infiltrate on X-ray"      │
│  └─ Combined with: symptoms + labs → stronger diagnosis    │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  7. Frontend Display                                         │
│  ├─ Uploaded image preview                                  │
│  ├─ AI Findings:                                            │
│  │  ├─ ✓ Cardiomegaly (87% confidence)                     │
│  │  ├─ ✓ Infiltrate (78% confidence)                       │
│  │  └─ Details: "Likely left lower lobe pneumonia"         │
│  │                                                          │
│  └─ Report button → PDF export with findings               │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. AJANLAR ARASI KOMÜNİKASYON

```
                    USER INPUT
                        │
                        ▼
        ┌───────────────────────────────┐
        │    1. INTENT AGENT             │
        │    ─────────────────          │
        │ "Klinik mi, bilgi mi?"         │
        │ Output: {intent: "CLINICAL"}   │
        └───────────────┬─────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │    2. PERSONAL AGENT           │
        │    ─────────────────────      │
        │ "Hasta bilgisini getir"        │
        │ Output: {context: {...}}       │
        │   + anamnesis                  │
        │   + lab results                │
        │   + radiology findings         │
        └───────────────┬─────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │    3. KNOWLEDGE AGENT          │
        │    ───────────────────       │
        │ "Tıbbi bilgisi ara"            │
        │ Output: {ddx: [...], evidence} │
        │   + Wikipedia-like KB          │
        │   + PubMed integration         │
        │   + Reference links            │
        └───────────────┬─────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────────┐
        │    4. ANSWER AGENT                        │
        │    ──────────────────                    │
        │ "Son cevabı hazırla"                      │
        │ + Consistency Check:                      │
        │   ├─ Risk vs Actions match? ✓             │
        │   ├─ Evidence present? ✓                  │
        │   └─ Red flags checked? ✓                 │
        │                                           │
        │ Output: {                                 │
        │   recommendation: {...},                  │
        │   confidence: 0.72,                       │
        │   evidence: [...]                         │
        │ }                                         │
        └───────────────┬─────────────────────────────┘
                        │
                        ▼
                  FRONTEND RENDER
```

---

## 4. AUTH FLOW

```
REGISTRATION
┌────────────────────────────┐
│ 1. User submits form       │
│    (email, password, name) │
└──────────┬─────────────────┘
           │ POST /auth/register
           ▼
┌────────────────────────────────────┐
│ 2. Backend validation              │
│    - Email format                  │
│    - Password strength             │
│    - Email uniqueness              │
└──────────┬─────────────────────────┘
           │ ✓ Valid
           ▼
┌────────────────────────────────────┐
│ 3. Hash password (PBKDF2-SHA256)   │
│    iterations: 600000              │
└──────────┬─────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│ 4. Create User in DB               │
│    - users.id = UUID()             │
│    - users.email = email           │
│    - users.hashed_password = hash  │
└──────────┬─────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│ 5. Return JWT token                │
│    {access_token: "...",           │
│     token_type: "bearer",          │
│     expires_in: 1800}              │
└──────────┬─────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│ 6. Frontend: Save token            │
│    localStorage.setItem(           │
│      'auth_token',                 │
│      access_token                  │
│    )                               │
└────────────────────────────────────┘

LOGIN
┌────────────────────────────────────┐
│ 1. User submits (email, password)  │
└──────────┬─────────────────────────┘
           │ POST /auth/login
           ▼
┌────────────────────────────────────┐
│ 2. Find user by email              │
│    users.query.filter_by(email)    │
└──────────┬─────────────────────────┘
           │
           ├─ Found ──────┐
           │              ▼
           │   ┌────────────────────┐
           │   │ 3. Verify password │
           │   │ passlib.verify()   │
           │   └────────┬───────────┘
           │            │
           │            ├─ Match ──────┐
           │            │              ▼
           │            │   ┌──────────────────┐
           │            │   │ 4. Create JWT    │
           │            │   │ {sub: user_id,   │
           │            │   │  exp: now + 30m} │
           │            │   └────────┬─────────┘
           │            │            │
           │            │            ▼
           │            │   ┌──────────────────────┐
           │            │   │ 5. Return token     │
           │            │   └────────┬─────────────┘
           │            │            │
           │            └────────────┴───┐
           │                             ▼
           │            ┌──────────────────────────┐
           │            │ 6. Frontend stores token │
           │            └──────────────────────────┘
           │
           └─ Not Found → 401 Unauthorized

PROTECTED REQUEST
┌────────────────────────────────────┐
│ Frontend: Include token in headers │
│ GET /reports/list                  │
│ Authorization: Bearer <token>      │
└──────────┬─────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│ Backend: JWT Middleware            │
│ ├─ Extract token from header       │
│ ├─ Verify signature (HS256)        │
│ ├─ Check expiration                │
│ └─ Extract user_id from payload    │
└──────────┬─────────────────────────┘
           │
           ├─ Valid ──────┐
           │              ▼
           │   ┌──────────────────────┐
           │   │ Proceed with request │
           │   │ user_id available    │
           │   └──────────────────────┘
           │
           └─ Invalid → 401 Unauthorized
```

---

## 5. DATABASE RELATIONSHIP DIAGRAM

```
                    ┌─────────────────┐
                    │     USERS       │
                    │ (Primary Entity)│
                    │  ┌───────────┐  │
                    │  │ id (PK)   │  │
                    │  │ email     │  │
                    │  │ password  │  │
                    │  │ full_name │  │
                    │  └───────────┘  │
                    └────────┬────────┘
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
    ┌─────────┐      ┌──────────┐      ┌─────────────┐
    │ REPORTS │      │ ANAMNESIS│      │ PATIENT_    │
    │1:N with │      │ _STATE   │      │PROFILE      │
    │ USERS   │      │1:N       │      │1:1          │
    │         │      │          │      │             │
    │ - id    │      │ - id     │      │ - user_id   │
    │ - user_ │      │ - patient│      │ - age       │
    │  id(FK) │      │  _id(FK) │      │ - gender    │
    │ - file_ │      │ - symptoms     │ - height    │
    │  path   │      │ (JSONB)  │      │ - weight    │
    │ - status│      └──────────┘      │ - blood_    │
    └────┬────┘                        │  type      │
         │                             └─────────────┘
         ▼
    ┌──────────────┐
    │TEST_RESULTS  │
    │1:N with      │
    │REPORTS       │
    │              │
    │ - id         │
    │ - report_id  │
    │  (FK)        │
    │ - test_name  │
    │ - value      │
    │ - unit       │
    │ - ref_min    │
    │ - ref_max    │
    │ - status     │
    └──────────────┘

                    ┌──────────────────┐
                    │RADIOLOGY_IMAGES  │
                    │1:N with USERS    │
                    │                  │
                    │ - id             │
                    │ - patient_id(FK) │
                    │ - image_path     │
                    │ - findings(JSON) │
                    │ - confidence     │
                    └──────────────────┘

    ┌──────────────────┬────────────────────┬────────────────┐
    ▼                  ▼                    ▼                ▼
┌───────────────┐ ┌──────────────┐ ┌────────────────┐ ┌──────────┐
│NOTIFICATIONS  │ │CHAT_SESSION  │ │PUSH_           │ │PATIENT_  │
│1:N with USERS │ │1:N with USERS│ │SUBSCRIPTIONS   │ │MEDICATION│
│               │ │              │ │1:N with USERS  │ │1:N       │
│ - id          │ │ - id         │ │                │ │          │
│ - user_id(FK) │ │ - user_id(FK)│ │ - id           │ │ - id     │
│ - title       │ │ - messages   │ │ - user_id(FK)  │ │ - patient│
│ - body        │ │  (JSONB)     │ │ - endpoint     │ │  _id(FK) │
│ - type        │ │ - context    │ │ - auth         │ │ - med_   │
│ - is_read     │ │ - timestamps │ │ - p256dh       │ │  name    │
└───────────────┘ └──────────────┘ └────────────────┘ └──────────┘
```

---

## 6. API ENDPOINT TREE

```
┌─ /auth (JWT Authentication)
│  ├─ POST /register          (New user account creation)
│  ├─ POST /login             (User authentication)
│  └─ GET /me                 (Current user profile)
│
├─ /reports (PDF Lab Analysis)
│  ├─ POST /upload            (Upload PDF file)
│  ├─ GET /list               (List user's reports)
│  ├─ GET /{id}               (Get single report)
│  ├─ GET /analyze/{id}       (Parse & analyze PDF)
│  ├─ GET /trends/{test_name} (Historical trends)
│  ├─ GET /available-tests    (Known tests for user)
│  ├─ GET /monitoring         (KPI dashboard)
│  ├─ POST /export-pdf/{id}   (Generate PDF report)
│  ├─ DELETE /{id}            (Delete report)
│  └─ POST /{id}/share        (Share with doctor)
│
├─ /radiology (X-Ray Analysis)
│  ├─ POST /upload            (Upload X-ray image)
│  ├─ POST /analyze/{id}      (DenseNet inference)
│  ├─ GET /{id}/findings      (Get AI findings)
│  ├─ GET /{id}/comparison    (Compare multiple X-rays)
│  └─ DELETE /{id}            (Delete radiology image)
│
├─ /api/v1/anamnesis (Patient History)
│  ├─ GET /profile            (Get patient profile)
│  ├─ POST /profile           (Create profile)
│  ├─ PUT /profile/{id}       (Update profile)
│  ├─ GET /conditions         (List patient conditions)
│  ├─ POST /conditions        (Add condition)
│  ├─ DELETE /conditions/{id} (Remove condition)
│  ├─ GET /medications        (List medications)
│  ├─ POST /medications       (Add medication)
│  ├─ DELETE /medications/{id}(Remove medication)
│  └─ GET /family-history     (Family medical history)
│
├─ /api/v1/chatbot (AI Assistant)
│  ├─ POST /chat              (Send message, get response)
│  ├─ GET /history            (Get chat history)
│  └─ POST /context           (Get patient context snapshot)
│
├─ /articles (Medical References)
│  ├─ GET /search             (PubMed search)
│  ├─ GET /trending           (Trending articles)
│  └─ GET /{id}               (Article details)
│
├─ /notifications (Push Alerts)
│  ├─ POST /subscribe         (Browser push subscription)
│  ├─ GET /list               (Notification history)
│  ├─ POST /mark-read/{id}    (Mark as read)
│  ├─ DELETE /{id}            (Delete notification)
│  ├─ GET /preferences        (Notification settings)
│  └─ PUT /preferences        (Update preferences)
│
└─ /health (System Status)
   └─ GET /health             (Uptime check)
```

---

## 7. DEPLOYMENT ARCHITECTURE

```
┌──────────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT                      │
└──────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      DOCKER CONTAINERS                       │
│                                                              │
│  ┌────────────┐  ┌───────────┐  ┌────────────┐              │
│  │  Frontend  │  │  Backend  │  │ PostgreSQL │              │
│  │  Container │  │ Container │  │ Container  │              │
│  │            │  │           │  │            │              │
│  │  React PWA │  │  FastAPI  │  │  Port 5433 │              │
│  │  Port 3000 │  │ Port 8000 │  │  (5432)    │              │
│  │  (80)      │  │  (8000)   │  │            │              │
│  └────────────┘  └───────────┘  └────────────┘              │
│                                                              │
│  docker-compose up -d                                       │
│  ├─ Automatic health checks                                 │
│  ├─ Auto-restart on failure                                 │
│  ├─ Volume mounts for persistence                           │
│  └─ Network isolation (bridge)                              │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                       LOAD BALANCER                           │
│                    (Nginx, optional)                          │
│                                                              │
│  ├─ SSL/TLS termination                                     │
│  ├─ Gzip compression                                        │
│  ├─ Rate limiting                                           │
│  ├─ Static file caching                                     │
│  └─ Round-robin to backend replicas (if scaled)             │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                  MONITORING & LOGGING                         │
│                                                              │
│  ├─ Prometheus (metrics collection)                         │
│  ├─ Grafana (visualization)                                 │
│  ├─ ELK Stack (logs: Elasticsearch, Logstash, Kibana)      │
│  ├─ APScheduler jobs logging                                │
│  └─ Application error tracking (Sentry optional)            │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    CI/CD PIPELINE (GitHub)                    │
│                                                              │
│  1. Code Push → GitHub                                      │
│  2. Run Tests (pytest, npm test)                            │
│  3. Build Docker Images                                     │
│  4. Push to Registry (Docker Hub / GitHub Packages)          │
│  5. Deploy to Staging                                       │
│  6. Smoke Tests                                             │
│  7. Deploy to Production (manual approval)                  │
│  8. Health Checks & Rollback (if needed)                    │
└──────────────────────────────────────────────────────────────┘
```

---

**Bu diyagramlar teknik ekip ve stakeholder'lar için referans olarak kullanılabilir.**

Son güncelleme: 08.05.2026
