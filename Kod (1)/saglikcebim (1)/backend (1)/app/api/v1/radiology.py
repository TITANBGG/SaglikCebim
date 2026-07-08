from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.radiology_image import RadiologyFinding, RadiologyImage

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

_METRICS_PATH = Path(__file__).resolve().parents[3] / "models" / "model_metrics.json"


@router.get("/model-info")
def get_model_info():
    """Model mimarisi, sınıflar ve AUC metrikleri."""
    if not _METRICS_PATH.exists():
        raise HTTPException(status_code=404, detail="Model metrikleri bulunamadı.")
    with open(_METRICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

UPLOAD_DIR = Path("uploads") / "radiology"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".dcm", ".png", ".jpg", ".jpeg", ".bmp", ".gif"}


def _coerce_user_id(current_user_id: str) -> int:
    try:
        return int(current_user_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user ID") from exc


def _detect_body_part(filename: str) -> str:
    lower = filename.lower()
    if any(token in lower for token in ["chest", "thorax", "gogus", "akciğer", "akciyer", "lung"]):
        return "gogus"
    if any(token in lower for token in ["hand", "el"]):
        return "el"
    if any(token in lower for token in ["knee", "diz"]):
        return "diz"
    return "genel"


def _detect_modality(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".dcm":
        return "DICOM"
    return "X-RAY" if any(token in filename.lower() for token in ["xray", "x-ray", "xr", "ray"]) else "IMAGE"


try:
    from app.services.radiology_ai import radiology_ai
except ImportError:
    radiology_ai = None

@router.post("/upload")
@limiter.limit("30/minute")
async def upload_chest_xray(
    request: Request,
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a radiology image (X-Ray, DICOM, etc.) for AI analysis.
    The image is processed by DenseNet-121 and returns structured findings.
    """
    user_id = _coerce_user_id(current_user_id)

    if not file or not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")

    if Path(file.filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File type not allowed. Allowed: {allowed}")

    file_content = await file.read()
    if len(file_content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size must be less than 20MB")

    import time
    safe_name = Path(file.filename).name
    if len(safe_name) > 60:
        safe_name = safe_name[:50] + Path(safe_name).suffix

    timestamp = str(int(time.time()))
    stored_name = f"{user_id}_{timestamp}_{safe_name}"
    
    file_path = UPLOAD_DIR / stored_name
    file_path.write_bytes(file_content)
    
    # --------------------------
    # YENI: GERÇEK AI ANALİZİ
    # --------------------------
    try:
        findings_payload, heatmap_filename = radiology_ai.analyze(str(file_path), str(UPLOAD_DIR))
    except Exception as e:
        print("AI Analysis Error:", e)
        # Fallback in case of error
        findings_payload = []
        heatmap_filename = None

    image = RadiologyImage(
        user_id=user_id,
        filename=stored_name,
        original_filename=safe_name,
        file_path=str(file_path),
        modality=_detect_modality(safe_name),
        body_part=_detect_body_part(safe_name),
        status="analyzed",
        metadata_json=json.dumps({"uploaded_via": "api", "size": len(file_content)}, ensure_ascii=False),
        created_at=datetime.now(timezone.utc),
    )
    db.add(image)
    db.commit()
    db.refresh(image)

    findings_rows = []
    for finding in findings_payload:
        row = RadiologyFinding(
            image_id=image.id,
            finding_type=str(finding["finding_type"]),
            tr_name=str(finding["tr_name"]),
            description=str(finding["description"]),
            confidence=float(finding["confidence"]),
            severity=str(finding["severity"]),
            location=str(finding["location"]),
            suggested_actions=json.dumps(finding["suggested_actions"], ensure_ascii=False),
            heatmap_path=heatmap_filename if heatmap_filename else None,
            created_at=datetime.now(timezone.utc),
        )
        db.add(row)
        db.flush()
        findings_rows.append(
            {
                "id": row.id,
                "finding_type": row.finding_type,
                "tr_name": row.tr_name,
                "description": row.description,
                "confidence": row.confidence,
                "severity": row.severity,
                "location": row.location,
                "suggested_actions": finding["suggested_actions"],
            }
        )
    db.commit()

    # Upload klasörünü app.main de serve edeceğiz (/uploads/radiology/...)
    heatmap_url = f"/uploads/radiology/{heatmap_filename}" if heatmap_filename else None

    return {
        "image_id": str(image.id),
        "status": image.status,
        "modality": image.modality,
        "body_part": image.body_part,
        "original_filename": image.original_filename,
        "findings": findings_rows,
        "heatmap_url": heatmap_url,
        "message": "Radiology AI analysis completed",
    }


@router.get("/")
def list_radiology_images(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all radiology images uploaded by the current user."""
    user_id = _coerce_user_id(current_user_id)
    images = db.query(RadiologyImage).filter(RadiologyImage.user_id == user_id).order_by(RadiologyImage.created_at.desc()).all()
    
    return [
        {
            "id": img.id,
            "filename": img.filename,
            "original_filename": img.original_filename,
            "modality": img.modality,
            "body_part": img.body_part,
            "status": img.status,
            "created_at": img.created_at.isoformat(),
        }
        for img in images
    ]


@router.get("/{image_id}")
def get_radiology_details(
    image_id: int,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed analysis and findings for a specific radiology image."""
    user_id = _coerce_user_id(current_user_id)
    image = db.query(RadiologyImage).filter(RadiologyImage.id == image_id, RadiologyImage.user_id == user_id).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Görüntü bulunamadı")
        
    findings = db.query(RadiologyFinding).filter(RadiologyFinding.image_id == image_id).all()
    
    findings_data = []
    heatmap_url = None
    
    for f in findings:
        if f.heatmap_path:
            heatmap_url = f"/uploads/radiology/{f.heatmap_path}"
            
        findings_data.append({
            "id": f.id,
            "finding_type": f.finding_type,
            "tr_name": f.tr_name,
            "description": f.description,
            "confidence": f.confidence,
            "severity": f.severity,
            "location": f.location,
            "suggested_actions": json.loads(f.suggested_actions) if f.suggested_actions else [],
        })
        
    return {
        "image_id": str(image.id),
        "status": image.status,
        "modality": image.modality,
        "body_part": image.body_part,
        "original_filename": image.original_filename,
        "findings": findings_data,
        "heatmap_url": heatmap_url,
        "created_at": image.created_at.isoformat(),
    }
