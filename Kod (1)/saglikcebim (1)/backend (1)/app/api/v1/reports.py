from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, Response, UploadFile, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.report import Report
from app.models.test_result import TestResult
from app.models.radiology_image import RadiologyImage
from app.services.pdf_parser import parse_pdf as parse_pdf_service
from app.services.report_interpreter import build_report_interpretation

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".dcm"}

RECOMMENDATION_LIBRARY = {
    "glukoz": {
        "title": "Kan şekeri",
        "high": {
            "eat": ["Lifli sebzeler", "Tam tahıllar", "Protein ağırlıklı öğünler"],
            "avoid": ["Şekerli içecekler", "Tatlılar", "Beyaz unlu ürünler"],
            "lifestyle": ["Kısa yürüyüşleri artırın", "Öğün düzenini sabitleyin"],
        },
        "low": {
            "eat": ["Küçük ve sık öğünler", "Kompleks karbonhidratlar"],
            "avoid": ["Uzun açlık", "Alkol"],
            "lifestyle": ["Hipoglisemi belirtilerini izleyin"],
        },
    },
    "hemoglobin": {
        "title": "Hemoglobin",
        "low": {
            "eat": ["Demirden zengin besinler", "C vitamini içeren gıdalar"],
            "avoid": ["Aşırı çay/kahve", "Yetersiz protein alımı"],
            "lifestyle": ["Yorgunluk varsa doktor görüşü alın"],
        },
        "high": {
            "eat": ["Yeterli sıvı alımı"],
            "avoid": ["Sigara", "Dehidratasyon"],
            "lifestyle": ["Kan sayımını tekrar değerlendirin"],
        },
    },
    "kolesterol": {
        "title": "Kolesterol",
        "high": {
            "eat": ["Yulaf", "Zeytinyağı", "Kuruyemiş"],
            "avoid": ["Trans yağlar", "Kızartma", "Kırmızı et fazlalığı"],
            "lifestyle": ["Haftada 150 dk egzersiz", "Kilo kontrolü"],
        },
    },
    "trigliserid": {
        "title": "Trigliserid",
        "high": {
            "eat": ["Balık", "Sebze ağırlıklı öğünler"],
            "avoid": ["Şekerli yiyecekler", "Alkol"],
            "lifestyle": ["Karbonhidrat yükünü azaltın"],
        },
    },
    "tsh": {
        "title": "TSH",
        "high": {
            "eat": ["Yeterli iyot ve protein"],
            "avoid": ["Aşırı iyot takviyesi"],
            "lifestyle": ["Endokrinoloji takibi önerilir"],
        },
        "low": {
            "eat": ["Doktor önerisine göre dengeli beslenme"],
            "avoid": ["Takviye kullanımını rastgele artırmayın"],
            "lifestyle": ["Tiroid hormonlarını kontrol ettirin"],
        },
    },
}

PUBMED_LIBRARY = {
    "glukoz": [
        {
            "pmid": "1000001",
            "title": "Lifestyle interventions for elevated blood glucose",
            "authors": "Health Cebim Editorial",
            "journal": "Clinical Nutrition Review",
            "pub_date": "2026",
            "url": "https://pubmed.ncbi.nlm.nih.gov/1000001/",
            "abstract": "Dietary fiber and exercise were associated with better glucose control.",
        }
    ],
    "kolesterol": [
        {
            "pmid": "1000002",
            "title": "Dietary patterns and LDL cholesterol reduction",
            "authors": "Health Cebim Editorial",
            "journal": "Cardiology Frontiers",
            "pub_date": "2025",
            "url": "https://pubmed.ncbi.nlm.nih.gov/1000002/",
            "abstract": "Mediterranean dietary patterns improved lipid profiles in adults.",
        }
    ],
    "hemoglobin": [
        {
            "pmid": "1000003",
            "title": "Iron deficiency anemia: current approaches",
            "authors": "Health Cebim Editorial",
            "journal": "Hematology Update",
            "pub_date": "2026",
            "url": "https://pubmed.ncbi.nlm.nih.gov/1000003/",
            "abstract": "Iron supplementation and diet change are common strategies for anemia care.",
        }
    ],
    "default": [
        {
            "pmid": "1000004",
            "title": "General health and laboratory monitoring",
            "authors": "Health Cebim Editorial",
            "journal": "Primary Care Insights",
            "pub_date": "2026",
            "url": "https://pubmed.ncbi.nlm.nih.gov/1000004/",
            "abstract": "Laboratory monitoring supports preventive healthcare decisions.",
        }
    ],
}


def _coerce_report_id(report_id: str) -> int:
    try:
        return int(report_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid report ID") from exc


def _coerce_user_id(current_user_id: str) -> int:
    try:
        return int(current_user_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user ID") from exc


def _normalize_status(status_value: Any) -> str:
    value = str(status_value or "").strip().lower()
    if value in {"high", "h", "abnormal", "above", "elevated"}:
        return "high"
    if value in {"low", "l", "below", "decreased"}:
        return "low"
    return "normal"


def _allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def _read_file_text(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        try:
            return file_path.read_bytes().decode("utf-8", errors="ignore")
        except Exception:
            return ""


def parse_pdf(file_path: str | Path) -> list[dict[str, Any]]:
    return parse_pdf_service(file_path)


def build_pdf_report(*, report: Report, results: list[TestResult], recommendations: dict[str, Any] | None = None) -> bytes:
    """Build a lightweight PDF-like byte payload.

    The function is intentionally easy to monkeypatch in tests.
    """

    lines = [
        "%PDF-1.4",
        f"SaglikCebim Report: {report.original_filename}",
        f"Status: {report.status}",
        f"Total results: {len(results)}",
    ]
    for result in results:
        lines.append(f"- {result.test_name}: {result.value} {result.unit} [{_normalize_status(result.status)}]")

    if recommendations:
        lines.append("Recommendations:")
        for key, value in recommendations.items():
            lines.append(f"- {key}: {json.dumps(value, ensure_ascii=False)}")

    return "\n".join(lines).encode("utf-8")


def _serialize_result(result: Any) -> dict[str, Any]:
    return {
        "test_name": result.test_name,
        "original_name": result.original_name,
        "value": float(result.value),
        "unit": result.unit,
        "ref_min": float(result.ref_min) if result.ref_min is not None else None,
        "ref_max": float(result.ref_max) if result.ref_max is not None else None,
        "status": _normalize_status(result.status),
        "created_at": result.created_at.isoformat() if result.created_at else None,
    }


def _get_user_reports(db: Session, user_id: int) -> list[Any]:
    return db.query(Report).filter(Report.user_id == user_id).order_by(Report.created_at.desc()).all()


def _get_report_results(db: Session, report_id: int) -> list[Any]:
    return db.query(TestResult).filter(TestResult.report_id == report_id).order_by(TestResult.created_at.asc()).all()


def _build_recommendations(results: list[Any]) -> dict[str, Any]:
    recommendations: dict[str, Any] = {}
    for result in results:
        status_value = _normalize_status(result.status)
        if status_value == "normal":
            continue

        test_key = result.test_name.lower()
        template = RECOMMENDATION_LIBRARY.get(test_key)
        if template is None:
            template = {
                "title": result.original_name,
                "high": {
                    "eat": ["Dengeli öğünler", "Sebze ve lif ağırlıklı beslenme"],
                    "avoid": ["Aşırı şeker", "İşlenmiş gıda"],
                    "lifestyle": ["Doktor takibi", "Yeterli sıvı alımı"],
                },
                "low": {
                    "eat": ["Dengeli öğünler"],
                    "avoid": ["Uzun açlık"],
                    "lifestyle": ["Doktor değerlendirmesi"],
                },
            }

        advice = template.get(status_value) or template.get("high") or template.get("low") or {}
        recommendations[result.test_name] = {
            "title": template.get("title", result.original_name),
            "value": float(result.value),
            "unit": result.unit,
            "status": status_value,
            "eat": advice.get("eat", []),
            "avoid": advice.get("avoid", []),
            "lifestyle": advice.get("lifestyle", []),
            "message": f"{template.get('title', result.original_name)} için {status_value} bulgusu var.",
        }

    return recommendations


def _build_pubmed_articles(test_names: Sequence[str]) -> list[dict[str, Any]]:
    articles: list[dict[str, Any]] = []
    for test_name in test_names:
        key = test_name.lower()
        items = PUBMED_LIBRARY.get(key, PUBMED_LIBRARY["default"])
        for item in items:
            enriched = dict(item)
            enriched["query"] = test_name
            articles.append(enriched)
    if not articles:
        articles.extend(PUBMED_LIBRARY["default"])
    return articles[:10]


def _build_interpretation(results: list[Any]) -> dict[str, Any]:
    return build_report_interpretation(results)


@router.post("/upload")
@limiter.limit("10/minute")
async def upload_reports(
    request: Request,
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        fname = getattr(file, "filename", "<no-filename>")
    except Exception:
        fname = "<error-getting-filename>"
    try:
        import os
        os.makedirs(os.path.join(os.getcwd(), "backend_logs"), exist_ok=True)
        with open(os.path.join(os.getcwd(), "backend_logs", "upload_trace.log"), "a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now(timezone.utc).isoformat()} - upload_called - filename={fname}\n")
    except Exception:
        pass
    print(f"[TRACE] upload_reports called; filename={fname}")
    user_id = _coerce_user_id(current_user_id)
    print(f"[TRACE] coerced user_id={user_id}")

    if not file or not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")

    if not _allowed_file(file.filename):
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File type not allowed. Allowed: {allowed}")

    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size must be less than 10MB")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safe_name = Path(file.filename).name
    stored_name = f"{user_id}_{timestamp}_{safe_name}"
    file_path = UPLOAD_DIR / stored_name
    file_path.write_bytes(file_content)

    report: Any = Report(
        user_id=user_id,
        filename=stored_name,
        original_filename=safe_name,
        file_path=str(file_path),
        status="uploaded",
        created_at=datetime.now(timezone.utc),
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "id": str(report.id),
        "report_id": str(report.id),
        "filename": report.filename,
        "original_filename": report.original_filename,
        "status": report.status,
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "message": "File uploaded successfully",
    }


@router.get("/")
async def list_reports(current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = _coerce_user_id(current_user_id)
    reports = _get_user_reports(db, user_id)

    return [
        {
            "id": str(report.id),
            "report_id": str(report.id),
            "filename": report.original_filename,
            "file_name": report.original_filename,
            "original_filename": report.original_filename,
            "status": report.status,
            "date": report.created_at.strftime("%d %B %Y") if report.created_at else "",
            "created_at": report.created_at.isoformat() if report.created_at else None,
            "type": "pdf" if report.original_filename.lower().endswith(".pdf") else "image",
        }
        for report in reports
    ]


@router.get("/{report_id}/results")
async def get_report_results(report_id: str, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = _coerce_user_id(current_user_id)
    report_pk = _coerce_report_id(report_id)

    report: Any = db.query(Report).filter(Report.id == report_pk, Report.user_id == user_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    test_results = _get_report_results(db, report_pk)

    return {
        "report_id": str(report.id),
        "filename": report.original_filename,
        "status": report.status,
        "total_tests": len(test_results),
        "results": [_serialize_result(result) for result in test_results],
    }


@router.post("/{report_id}/parse")
@limiter.limit("5/minute")
async def parse_report(request: Request, report_id: str, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = _coerce_user_id(current_user_id)
    report_pk = _coerce_report_id(report_id)

    report: Any = db.query(Report).filter(Report.id == report_pk, Report.user_id == user_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    if not Path(report.file_path).exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report file not found")

    parsed_results = parse_pdf(report.file_path)
    db.query(TestResult).filter(TestResult.report_id == report_pk).delete()

    for parsed in parsed_results:
        db.add(
            TestResult(
                report_id=report_pk,
                test_name=str(parsed.get("test_name", "unknown")),
                original_name=str(parsed.get("original_name", parsed.get("test_name", "unknown"))),
                value=float(parsed.get("value", 0.0)),
                unit=str(parsed.get("unit", "")),
                ref_min=parsed.get("ref_min"),
                ref_max=parsed.get("ref_max"),
                status=str(parsed.get("status", "Normal")),
                created_at=datetime.now(timezone.utc),
            )
        )

    report.status = "analyzed" if parsed_results else "parsed"
    db.commit()
    interpretation = _build_interpretation(parsed_results)

    return {
        "id": str(report.id),
        "status": report.status,
        "total_tests": len(parsed_results),
        "results": parsed_results,
        "interpretation": interpretation,
        "message": "Parsing completed",
    }


@router.get("/{report_id}/interpretation")
async def get_interpretation(report_id: str, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = _coerce_user_id(current_user_id)
    report_pk = _coerce_report_id(report_id)

    report = db.query(Report).filter(Report.id == report_pk, Report.user_id == user_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    results = _get_report_results(db, report_pk)

    return {
        "report_id": str(report.id),
        "filename": report.original_filename,
        "status": report.status,
        "interpretation": _build_interpretation(results),
    }


@router.get("/{report_id}/download-pdf")
async def download_pdf(report_id: str, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = _coerce_user_id(current_user_id)
    report_pk = _coerce_report_id(report_id)

    report: Any = db.query(Report).filter(Report.id == report_pk, Report.user_id == user_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    results = _get_report_results(db, report_pk)
    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Report must be parsed before download")

    recommendations = _build_recommendations(results)
    pdf_bytes = build_pdf_report(report=report, results=results, recommendations=recommendations)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="report_{report.id}.pdf"'},
    )


@router.delete("/{report_id}")
async def delete_report(report_id: str, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = _coerce_user_id(current_user_id)
    report_pk = _coerce_report_id(report_id)

    report: Any = db.query(Report).filter(Report.id == report_pk, Report.user_id == user_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    try:
        Path(report.file_path).unlink(missing_ok=True)
    except Exception:
        pass

    db.query(TestResult).filter(TestResult.report_id == report_pk).delete()
    db.delete(report)
    db.commit()

    return {"message": "Report deleted successfully"}


@router.get("/monitoring")
async def get_dashboard_monitoring(
    current_user_id: str = Depends(get_current_user),
    window_days: int = Query(default=30, ge=7, le=365),
    focus_tests: str | None = Query(default=None),
    limit_rows: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    user_id = _coerce_user_id(current_user_id)
    focus_test_list = [item.strip().lower() for item in focus_tests.split(",")] if focus_tests else []
    now = datetime.now()
    cutoff = now - timedelta(days=window_days)

    reports = _get_user_reports(db, user_id)
    report_ids = [report.id for report in reports]
    recent_results: list[Any] = (
        db.query(TestResult)
        .filter(TestResult.report_id.in_(report_ids), TestResult.created_at >= cutoff)
        .order_by(TestResult.created_at.desc())
        .all()
        if report_ids
        else []
    )

    normal_count = sum(1 for result in recent_results if _normalize_status(result.status) == "normal")
    high_count = sum(1 for result in recent_results if _normalize_status(result.status) == "high")
    low_count = sum(1 for result in recent_results if _normalize_status(result.status) == "low")

    # Radyoloji verilerini de çekelim
    radiology_images = db.query(RadiologyImage).filter(RadiologyImage.user_id == user_id).all()
    radiology_count = len(radiology_images)

    # Raporlar ve Radyoloji görüntülerini birleştirip sıralayalım
    all_recent = []
    for r in reports:
        all_recent.append({
            "id": str(r.id),
            "file_name": r.original_filename,
            "status": r.status,
            "date": r.created_at.strftime("%d %B %Y") if r.created_at else "",
            "type": "pdf",
            "created_at": r.created_at
        })
    for img in radiology_images:
        all_recent.append({
            "id": str(img.id),
            "file_name": img.original_filename,
            "status": img.status,
            "date": img.created_at.strftime("%d %B %Y") if img.created_at else "",
            "type": "image",
            "created_at": img.created_at
        })
    
    all_recent.sort(key=lambda x: x["created_at"] or datetime.min, reverse=True)

    latest_results_table = [
        {
            "report_id": str(result.report_id),
            "test_name": result.test_name,
            "original_name": result.original_name,
            "value": float(result.value),
            "unit": result.unit,
            "status": _normalize_status(result.status),
            "created_at": result.created_at.isoformat() if result.created_at else None,
        }
        for result in recent_results[:limit_rows]
    ]

    gauges: list[dict[str, Any]] = []
    gauge_names = focus_test_list or sorted({result.test_name.lower() for result in recent_results})
    for test_name in gauge_names:
        matching = [result for result in recent_results if result.test_name.lower() == test_name]
        if not matching:
            continue
        latest = matching[-1]
        gauges.append(
            {
                "test_name": latest.test_name,
                "value": float(latest.value),
                "unit": latest.unit,
                "status": _normalize_status(latest.status),
                "ref_min": float(latest.ref_min) if latest.ref_min is not None else None,
                "ref_max": float(latest.ref_max) if latest.ref_max is not None else None,
            }
        )

    focus_trends: list[dict[str, Any]] = []
    for test_name in focus_test_list:
        matching = [result for result in recent_results if result.test_name.lower() == test_name]
        if not matching:
            continue
        focus_trends.append(
            {
                "test_name": test_name,
                "points": [
                    {
                        "date": result.created_at.strftime("%d/%m") if result.created_at else "",
                        "value": float(result.value),
                        "status": _normalize_status(result.status),
                    }
                    for result in matching
                ],
            }
        )

    return {
        "window_days": window_days,
        "focus_tests": focus_test_list,
        "kpis": {
            "total_reports": len(reports),
            "total_results": len(recent_results),
            "normal_results": normal_count,
            "abnormal_results": high_count + low_count,
        },
        "status_breakdown": {"normal": normal_count, "high": high_count, "low": low_count},
        "gauges": gauges,
        "focus_trends": focus_trends,
        "latest_results_table": latest_results_table,
        "recent_reports": all_recent[:10],
        "total_reports": len(reports),
        "normal_count": normal_count,
        "abnormal_count": high_count + low_count,
        "radiology_count": db.query(RadiologyImage).filter(RadiologyImage.user_id == user_id).count(), #
    }


@router.get("/trends/{test_name}")
async def get_trends(test_name: str, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = _coerce_user_id(current_user_id)
    reports = _get_user_reports(db, user_id)
    report_ids = [report.id for report in reports]

    if not report_ids:
        return {"test_name": test_name, "data_points": []}

    results: list[Any] = (
        db.query(TestResult)
        .filter(TestResult.report_id.in_(report_ids), TestResult.test_name.ilike(f"%{test_name}%"))
        .order_by(TestResult.created_at.asc())
        .all()
    )

    return {
        "test_name": test_name,
        "data_points": [
            {
                "date": result.created_at.strftime("%d/%m") if result.created_at else "",
                "value": float(result.value),
                "status": _normalize_status(result.status),
            }
            for result in results
        ],
    }


@router.get("/available-tests")
async def get_available_tests(current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = _coerce_user_id(current_user_id)
    reports = _get_user_reports(db, user_id)
    report_ids = [report.id for report in reports]

    if not report_ids:
        return {"tests": []}

    tests = (
        db.query(TestResult.test_name)
        .filter(TestResult.report_id.in_(report_ids))
        .distinct()
        .order_by(TestResult.test_name.asc())
        .all()
    )

    return {"tests": [item[0] for item in tests]}


@router.post("/{report_id}/pubmed")
async def get_pubmed_articles(report_id: str, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = _coerce_user_id(current_user_id)
    report_pk = _coerce_report_id(report_id)

    report = db.query(Report).filter(Report.id == report_pk, Report.user_id == user_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    results = _get_report_results(db, report_pk)
    focus_tests = [result.test_name for result in results if _normalize_status(result.status) != "normal"]
    articles = _build_pubmed_articles(focus_tests or [result.test_name for result in results[:1]])

    return {
        "report_id": str(report.id),
        "focus_tests": focus_tests,
        "count": len(articles),
        "articles": articles,
    }


@router.get("/{report_id}/recommendations")
async def get_recommendations(report_id: str, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = _coerce_user_id(current_user_id)
    report_pk = _coerce_report_id(report_id)

    report = db.query(Report).filter(Report.id == report_pk, Report.user_id == user_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    results = _get_report_results(db, report_pk)
    recommendations = _build_recommendations(results)
    interpretation = _build_interpretation(results)

    return {
        "report_id": str(report.id),
        "count": len(recommendations),
        "data": recommendations,
        "interpretation": interpretation,
        "summary": "Anormal sonuçlar için beslenme ve yaşam tarzı önerileri üretildi." if recommendations else "Öneri üretmek için önce analiz gerekir.",
    }
