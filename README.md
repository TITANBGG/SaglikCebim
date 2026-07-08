
https://youtu.be/Gd3x-HQGDXs


<div align="center">
  <img src="frontend/public/logo.svg" alt="SağlıkCebim Logo" width="110"/>

  <h1>SağlıkCebim</h1>
  <p><strong>Turkish-language Clinical Decision Support System and offline AI medical assistant.</strong></p>
  <p>Lab report parsing, chest X-ray analysis, and a multi-agent clinical chat pipeline, backed by evidence retrieval.</p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python 3.11"/>
    <img src="https://img.shields.io/badge/FastAPI-005571?logo=fastapi&logoColor=white" alt="FastAPI"/>
    <img src="https://img.shields.io/badge/React-18.3-20232A?logo=react&logoColor=61DAFB" alt="React 18.3"/>
    <img src="https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white" alt="TypeScript"/>
    <img src="https://img.shields.io/badge/PyTorch-2.1+-EE4C2C?logo=pytorch&logoColor=white" alt="PyTorch"/>
    <img src="https://img.shields.io/badge/PostgreSQL-15-316192?logo=postgresql&logoColor=white" alt="PostgreSQL 15"/>
    <img src="https://img.shields.io/badge/Docker-2CA5E0?logo=docker&logoColor=white" alt="Docker"/>
    <img src="https://img.shields.io/badge/Llama_3-via_Ollama-blueviolet" alt="Llama 3"/>
    <img src="https://img.shields.io/badge/License-MIT-yellow" alt="MIT License"/>
  </p>
</div>

---

> [!CAUTION]
> **Medical disclaimer.** This project is a prototype built for academic and demonstration purposes. It is not a medical device and must not be used to replace professional diagnosis, advice, or treatment. Always consult a qualified healthcare provider.

## Overview

SağlıkCebim is a Turkish clinical assistant that turns raw patient inputs into structured, safety-checked guidance. It reads lab report PDFs, analyzes chest X-rays, and answers clinical questions through a multi-agent pipeline, with every recommendation passed through a safety layer before it reaches the user.

The system is designed to be **offline and privacy-first**: the language model runs locally through [Ollama](https://ollama.com) (Llama 3), so patient text does not have to leave the host. It is **multimodal**, combining free-text symptoms, parsed lab values, and radiology images. The backend is a **FastAPI** service; the frontend is a **React 18** Progressive Web App.

This is a graduation project. The architecture is real and runnable, but see [Known limitations](#known-limitations) for what is production-ready versus what is still a prototype.

## Key features

- **Lab report analysis** parses Turkish medical PDFs with `pdfplumber` and a set of Turkish-tuned regex patterns, then interprets values against reference ranges. (`services/pdf_parser.py`, `services/report_interpreter.py`, `services/medical_knowledge.py`)
- **Radiology AI** classifies chest X-rays across the 14 NIH ChestX-ray14 findings and returns per-class probabilities with Grad-CAM heatmaps for explainability. (`services/radiology_ai.py`, `ml/`)
- **Multi-agent clinical chat** orchestrates symptom extraction, patient history, a local LLM, a pharmacology firewall, and a safety validator into a single clinical response. (`services/diagnosis_agent.py`, `services/clinical/`)
- **Evidence retrieval** queries external medical sources through pluggable providers (PubMed E-utilities, UpToDate, ClinicalKey) and ranks results with BM25. (`services/evidence/`)
- **Anamnesis (clinical history)** tracks demographics, chronic conditions, medications, and allergies, and uses them to contextualize interpretation. (`api/v1/anamnesis.py`)
- **Auth and safety** JWT authentication, `pbkdf2_sha256` password hashing, per-user data isolation on reports, request rate limiting, and Web Push notifications. (`core/security.py`, `api/v1/auth.py`, `main.py`)

## System architecture

```mermaid
flowchart TD
    subgraph Client
        UI["React 18 PWA<br/>Vite, TypeScript, Tailwind, Radix UI"]
    end

    subgraph API["FastAPI backend"]
        R["API routers<br/>/api/v1/*"]
        SVC["Service layer"]
    end

    subgraph Services
        DA["DiagnosisAgent<br/>+ ClinicalRoadmapEngine"]
        RAD["RadiologyAI<br/>EfficientNet-B4 + Grad-CAM"]
        EV["EvidenceEngine"]
        PDF["PDF parser<br/>+ report interpreter"]
    end

    subgraph Data
        DB[("Database<br/>SQLite dev / PostgreSQL target")]
        UP[("Uploads<br/>PDFs, X-rays")]
    end

    subgraph External
        OL["Ollama<br/>Llama 3 (local)"]
        PM["PubMed E-utilities"]
    end

    UI -->|HTTPS + JWT| R --> SVC
    SVC --> DA & RAD & EV & PDF
    DA --> OL
    EV --> PM
    SVC --> DB
    PDF --> UP
    RAD --> UP
```

### Clinical chat request flow

```mermaid
sequenceDiagram
    participant U as User
    participant API as /api/v1/chatbot
    participant DA as DiagnosisAgent
    participant DB as Anamnesis / DB
    participant LLM as OllamaDiagnosisAgent (Llama 3)
    participant PH as PharmacologyAgent
    participant SV as SafetyValidator

    U->>API: clinical question
    API->>DA: analyze(complaint)
    DA->>DB: fetch history, extract symptoms
    DA->>LLM: build context, generate roadmap
    LLM-->>DA: draft clinical response
    DA->>PH: drug interaction / safety check
    DA->>SV: forbidden-pattern + emergency-referral check
    SV-->>API: validated, safe response
    API-->>U: structured answer + disclaimer
```

## Multi-agent clinical pipeline

The chat pipeline is an orchestration of small, single-purpose components rather than one large prompt:

- **`DiagnosisAgent`** is the orchestrator. It extracts symptoms from the message, pulls the patient's anamnesis from the database, and coordinates the downstream steps.
- **`ClinicalRoadmapEngine`** builds the structured clinical roadmap and enriches it via `ClinicalKeyAgent`.
- **`OllamaDiagnosisAgent`** talks to the locally hosted Llama 3 model through the Ollama HTTP API, with retry handling and optional JSON-mode output.
- **`PharmacologyAgent`** acts as a firewall that checks for medication and interaction safety before a response is finalized.
- **`SafetyValidator`** is the final gate. It scans the output for forbidden patterns (dosages, drug names, "no doctor needed" phrasing) and enforces emergency referral when red flags or critical risk are present.

## Radiology AI

- **Model.** `EfficientNet-B4` (torchvision) with a 14-output classifier head, loaded from a checkpoint at `backend/models/`.
- **Labels.** The 14 NIH ChestX-ray14 findings: Atelectasis, Cardiomegaly, Effusion, Infiltration, Mass, Nodule, Pneumonia, Pneumothorax, Consolidation, Edema, Emphysema, Fibrosis, Pleural Thickening, and Hernia, with Turkish display names.
- **Thresholds.** Per-class decision thresholds are loaded from a JSON file rather than a single fixed 0.5 cutoff.
- **Explainability.** Grad-CAM heatmap overlays highlight the regions driving each prediction. (`ml/gradcam.py`)
- **Training and evaluation.** The `ml/` directory contains the full pipeline: dataset preparation, augmentation, training (`train.py`, `train_v2.py`), export, and evaluation scripts including ECE calibration (`evaluate_ece.py`).

## Evidence engines

Clinical advice can be anchored to external literature through provider abstractions in `services/evidence/`:

- **PubMed** via the NCBI E-utilities API.
- **UpToDate** and **ClinicalKey** via configurable providers (these require credentials or cookies supplied through environment variables).
- Retrieved passages are ranked with **BM25** (`rank-bm25`) before being surfaced.

## Tech stack

| Layer | Technology | Version | Purpose |
| --- | --- | --- | --- |
| Backend | FastAPI | 0.100+ | REST API and OpenAPI docs |
| Backend | SQLAlchemy | 2.0+ | ORM |
| Backend | Alembic | 1.13+ | Database migrations |
| Auth | python-jose, passlib | 3.5 / 1.7.4 | JWT and password hashing |
| Parsing | pdfplumber, regex | 0.11.9 | Turkish lab PDF extraction |
| LLM | langchain-ollama, Ollama | 1.1+ | Local Llama 3 inference |
| Vision | PyTorch, torchvision | 2.1+ | EfficientNet-B4 X-ray model |
| Retrieval | rank-bm25 | 0.2.2+ | Evidence ranking |
| Rate limit | slowapi | 0.1.9+ | Per-route request limits |
| Frontend | React | 18.3.1 | PWA UI |
| Frontend | Vite, TypeScript | latest | Build and typing |
| Frontend | Tailwind CSS, Radix UI, MUI | - | Styling and components |
| Frontend | recharts | 2.15 | Charts and trends |
| Infra | Docker, PostgreSQL, Nginx | 15 / alpine | Containerized deployment |

## Project structure

<details>
<summary><b>📂 Click to expand repository structure</b></summary>

```text
SaglikCebim/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Routers: auth, reports, radiology, chatbot, anamnesis, ...
│   │   ├── core/            # database, security, config, logging
│   │   ├── services/        # diagnosis_agent, pdf_parser, radiology_ai, report_interpreter
│   │   │   ├── clinical/    # roadmap engine, safety validator, pharmacology agent
│   │   │   └── evidence/    # pubmed / uptodate / clinicalkey providers, BM25 ranker
│   │   ├── models/          # SQLAlchemy models
│   │   └── main.py          # FastAPI app entrypoint
│   ├── ml/                  # X-ray training, evaluation, Grad-CAM
│   ├── tests/               # 28 test modules (pytest)
│   └── requirements.txt
├── frontend/
│   ├── src/app/pages/       # Dashboard, Radyoloji, PDFAnaliz, Anamnez, Trendler, ...
│   └── package.json
├── docker-compose.yml       # Dev stack
├── docker-compose.prod.yml  # Prod stack (Postgres + Nginx)
└── README.md
```

</details>

## Getting started

### Prerequisites

- **Python 3.11**
- **Node.js 22**
- **Docker** and Docker Compose (for the containerized path)
- **Ollama** with the Llama 3 model pulled locally:
  ```bash
  ollama pull llama3
  ```

### Environment variables

The backend reads configuration from environment variables (loaded from `backend/.env`). Create a `.env.example` and copy it to `.env`. **Never commit real secrets.**

<details>
<summary><b>⚙️ Click to view all Environment Variables</b></summary>

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `SECRET_KEY` | Yes | none (app fails if unset) | JWT signing key |
| `ALGORITHM` | No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | Token lifetime |
| `CORS_ALLOW_ORIGINS` | Yes (dev) | empty | Comma-separated allowed origins |
| `CORS_ALLOW_ORIGIN_REGEX` | No | none | Regex alternative for CORS |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama endpoint |
| `OLLAMA_MODEL` | No | `llama3:latest` | Local model tag |
| `OLLAMA_TIMEOUT` | No | `120` | LLM request timeout (s) |
| `PUBMED_EMAIL` | No | placeholder | Contact for NCBI E-utilities |
| `UPTODATE_API_KEY` | No | empty | UpToDate provider auth |
| `CLINICALKEY_COOKIE` | No | empty | ClinicalKey provider auth |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |
| `VAPID_PUBLIC_KEY` / `VAPID_PRIVATE_KEY` / `VAPID_EMAIL` | For push | none | Web Push notifications |
| `DATABASE_URL` | See note | `sqlite:///./dev.db` | Database connection (see [Known limitations](#known-limitations)) |

Example `.env`:

```env
SECRET_KEY=change-me-to-a-long-random-string
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ALLOW_ORIGINS=http://localhost:5173
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:latest
```

</details>

### Run locally (without Docker)

Backend:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

The API is then at `http://localhost:8000` and the app at the Vite dev URL.

### Run with Docker

Development stack:

```bash
docker compose up --build
```

Production stack (PostgreSQL + Nginx). Provide a `.env` with the production values first:

```bash
docker compose -f docker-compose.prod.yml up --build
```

## API reference

Interactive documentation is generated automatically:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

<details>
<summary><b>🌐 Click to view Key API Endpoints</b></summary>

| Group | Prefix | Responsibility |
| --- | --- | --- |
| Auth | `/api/v1/auth` | Register, login, current user |
| Reports | `/api/v1/reports` | Upload, list, parse, interpret lab PDFs |
| Radiology | `/api/v1/radiology` | X-ray upload and analysis |
| Chatbot | `/api/v1/chatbot` | Multi-agent clinical chat |
| Anamnesis | `/api/v1/anamnesis` | Clinical history management |
| Evidence | `/api/v1/evidence` | Literature retrieval |
| Roadmap | `/api/v1/roadmap` | Clinical roadmap sessions |
| Notifications | `/api/v1/notifications` | Web Push notifications |
<img width="538" height="1021" alt="Ekran görüntüsü 2026-05-19 001645" src="https://github.com/user-attachments/assets/8454457a-4670-4e15-8b83-11bcf741ff71" />
<img width="1912" height="1012" alt="Ekran görüntüsü 2026-05-19 000948" src="https://github.com/user-attachments/assets/b6d82bf7-a2a4-4e0e-84fa-42d86405585d" />
<img width="1912" height="1012" alt="Ekran görüntüsü 2026-05-19 000948 (2)" src="https://github.com/user-attachments/assets/a39daf91-9a38-4c0d-832b-4b480d7ce729" />
<img width="1915" height="1020" alt="Ekran görüntüsü 2026-05-19 000920 (2)" src="https://github.com/user-attachments/assets/be41ee14-0d34-48af-8f83-4512082883a6" />
<img width="1625" height="731" alt="Ekran görüntüsü 2026-05-19 000700" src="https://github.com/user-attachments/assets/dcba8190-a8dc-4223-9bf0-072089c3c74c" />
<img width="1675" height="808" alt="Ekran görüntüsü 2026-05-19 000613" src="https://github.com/user-attachments/assets/1880e15c-79ed-4f46-b83a-3bc2d9dbb077" />
<img width="1918" height="876" alt="Ekran görüntüsü 2026-05-19 000607" src="https://github.com/user-attachments/assets/4aeddb65-074d-4043-9edf-b3c84746848c" />
<img width="831" height="812" alt="Ekran görüntüsü 2026-05-19 000510" src="https://github.com/user-attachments/assets/3e751edd-d41e-4f8d-a450-0edef5390329" />
<img width="1918" height="877" alt="Ekran görüntüsü 2026-05-19 000313" src="https://github.com/user-attachments/assets/40083653-1903-4366-9ed4-5ba60ca7196b" />
<img width="1675" height="573" alt="Ekran görüntüsü 2026-05-19 000306" src="https://github.com/user-attachments/assets/096ccffc-72af-462a-bf5d-83d81bfe16d0" />
<img width="1693" height="821" alt="Ekran görüntüsü 2026-05-19 000259" src="https://github.com/user-attachments/assets/5a0ec3ea-71b7-4dad-ac4c-89a056b67b1a" />
<img width="1487" height="855" alt="Ekran görüntüsü 2026-05-18 235223" src="https://github.com/user-attachments/assets/feac3342-12b2-49e7-b1d9-8cb73aa6555d" />
<img width="937" height="707" alt="Ekran görüntüsü 2026-05-18 234455" src="https://github.com/user-attachments/assets/68205705-b963-4a37-82e8-66ebeb123d72" />
<img width="968" height="833" alt="Ekran görüntüsü 2026-05-18 234448" src="https://github.com/user-attachments/assets/6416cce2-aaa2-4207-87f9-f6eb0b407271" />
<img width="955" height="705" alt="Ekran görüntüsü 2026-05-18 234441" src="https://github.com/user-attachments/assets/a2f25fa8-3bf6-495a-a040-75e6f68a7596" />
<img width="1007" height="707" alt="Ekran görüntüsü 2026-05-18 234434" src="https://github.com/user-attachments/assets/8d9a08b0-3e15-44f6-a9b4-54aa21f409a8" />
<img width="1653" height="261" alt="Ekran görüntüsü 2026-05-18 234426" src="https://github.com/user-attachments/assets/3f8a05f7-ed42-492c-8762-409dae7fe7ba" />
<img width="1906" height="855" alt="Ekran görüntüsü 2026-05-18 234406 - Kopya" src="https://github.com/user-attachments/assets/2c4b5bd7-259d-4a3c-b650-f3bf6b9a02ee" />
<img width="1583" height="842" alt="Ekran görüntüsü 2026-05-04 001542" src="https://github.com/user-attachments/assets/3f44945b-9206-4086-b157-414fc5425b9b" />
<img width="1583" height="842" alt="Ekran görüntüsü 2026-05-04 001542 - Kopya" src="https://github.com/user-attachments/assets/4cbe951e-d950-491d-9433-3df074f72c8d" />
<img width="537" height="159" alt="Ekran görüntüsü 2026-05-03 221914 - Kopya" src="https://github.com/user-attachments/assets/44d88d3c-97a8-46b3-aa7b-437d2c56d8bb" />
<img width="1238" height="868" alt="Ekran görüntüsü 2026-05-02 214543 - Kopya" src="https://github.com/user-attachments/assets/3a1feca5-eb47-4ab4-8728-5b3c1a8e8da8" />
<img width="545" height="1007" alt="Ekran görüntüsü 2026-05-19 001751" src="https://github.com/user-attachments/assets/ce8ae0bc-7575-4307-af18-5771b0ab9241" />
<img width="552" height="1018" alt="Ekran görüntüsü 2026-05-19 001720" src="https://github.com/user-attachments/assets/a7fc33d3-1d38-471b-95c6-d60f77397a66" />
<img width="612" height="607" alt="0 1 - Kopya" src="https://github.com/user-attachments/assets/a94846c7-260b-497b-82d1-cf9491276cc7" />
<img width="611" height="591" alt="_PubMed Entegrasyon Akışı Diyagram drawio" src="https://github.com/user-attachments/assets/fb556aa2-ba73-4c95-b2b4-cb3030dd5a37" />
<img width="611" height="465" alt="_PDF Ayrıştırma Akışı drawio" src="https://github.com/user-attachments/assets/80c98897-1095-458a-b645-560c4741fd3c" />
<img width="581" height="631" alt="Radyoloji Analiz Pipeline Diyagram drawio (1)" src="https://github.com/user-attachments/assets/92e84a2b-1953-4005-a711-0d365c702890" />
<img width="361" height="521" alt="PDF Ayrıştırma Akışı Diyagram drawio" src="https://github.com/user-attachments/assets/0b14ffa1-b6e6-45f4-9200-76d4964558a3" />
<img width="641" height="601" alt="Çok Etkenli AI Akışı Diyagram drawio" src="https://github.com/user-attachments/assets/a83522cd-e42b-41f8-9150-f9b968cb1a47" />

</details>

## Testing

The backend ships with 28 pytest modules covering the PDF parser, agents, radiology inference, auth, report interpretation, safety validation, and end-to-end and golden-scenario flows.

```bash
cd backend
pytest
```

## Known limitations

This is a prototype, and the README aims to describe it honestly:

- **Database.** `core/database.py` currently hardcodes a SQLite connection and does not read `DATABASE_URL` from the environment yet, even though `docker-compose.prod.yml` provisions PostgreSQL 15. SQLite is the working default; wiring the app to read `DATABASE_URL` is required before the Postgres path is truly active.
- **Not for clinical use.** The models and safety layer are for demonstration. Outputs are not validated for real patient care.
- **External providers.** UpToDate and ClinicalKey integrations require credentials that are not bundled; without them, evidence retrieval falls back to PubMed.

## Security and privacy

- JWT-based authentication with `pbkdf2_sha256` password hashing.
- Per-user isolation on report queries (`Report.user_id` filtering) to prevent cross-account access.
- Per-route rate limiting via `slowapi`.
- Local LLM inference to keep patient text on the host.
- The project targets KVKK and GDPR alignment as a design goal.

## License

Released under the [MIT License](LICENSE).

## Acknowledgments

Built as a graduation project. Chest X-ray classification is trained on the NIH ChestX-ray14 dataset; literature retrieval uses the NCBI PubMed E-utilities.
