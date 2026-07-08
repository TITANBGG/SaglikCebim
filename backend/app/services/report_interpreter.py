from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.services.normalizer import display_name_for, normalize_test_name


def _status(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"high", "h", "abnormal", "above", "elevated", "yuksek", "yüksek"}:
        return "high"
    if normalized in {"low", "l", "below", "decreased", "dusuk", "düşük"}:
        return "low"
    return "normal"


def _field(result: Any, name: str, default: Any = None) -> Any:
    if isinstance(result, dict):
        return result.get(name, default)
    return getattr(result, name, default)


def _number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_results(results: list[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for result in results:
        raw_name = str(_field(result, "test_name", "") or _field(result, "original_name", "") or "")
        test_name = normalize_test_name(raw_name)
        normalized.append(
            {
                "test_name": test_name,
                "display_name": display_name_for(test_name),
                "original_name": str(_field(result, "original_name", raw_name) or raw_name),
                "value": _number(_field(result, "value")),
                "unit": str(_field(result, "unit", "") or ""),
                "ref_min": _number(_field(result, "ref_min")),
                "ref_max": _number(_field(result, "ref_max")),
                "status": _status(_field(result, "status")),
            }
        )
    return normalized


def _has(index: dict[str, dict[str, Any]], name: str, status: str | None = None) -> bool:
    item = index.get(name)
    if not item:
        return False
    return status is None or item["status"] == status


def _value_text(result: dict[str, Any]) -> str:
    value = result["value"]
    unit = result["unit"]
    if value is None:
        return unit
    text = f"{value:g}"
    return f"{text} {unit}".strip()


def _individual_advice(result: dict[str, Any]) -> dict[str, Any] | None:
    status = result["status"]
    if status == "normal":
        return None

    name = result["test_name"]
    display = result["display_name"]
    advice_map: dict[str, dict[str, dict[str, list[str] | str]]] = {
        "glukoz": {
            "high": {
                "meaning": "Kan şekeri referans aralığının üzerinde.",
                "eat": ["Lifli sebzeler", "Tam tahıllar", "Protein içeren dengeli öğünler"],
                "avoid": ["Şekerli içecekler", "Tatlılar", "Beyaz unlu ürünler"],
                "next": ["Açlık/tokluk durumuna göre hekimle tekrar değerlendirin", "HbA1c kontrolü düşünülebilir"],
            },
            "low": {
                "meaning": "Kan şekeri referans aralığının altında.",
                "eat": ["Küçük ve sık öğünler", "Kompleks karbonhidratlar"],
                "avoid": ["Uzun açlık", "Alkol"],
                "next": ["Terleme, titreme veya baygınlık varsa gecikmeden sağlık desteği alın"],
            },
        },
        "hemoglobin": {
            "low": {
                "meaning": "Kansızlık ile uyumlu olabilecek düşük hemoglobin saptandı.",
                "eat": ["Demirden zengin besinler", "C vitamini içeren gıdalar", "Yeterli protein"],
                "avoid": ["Yemekle birlikte aşırı çay/kahve", "Kontrolsüz demir takviyesi"],
                "next": ["Ferritin, demir ve B12/folat ile birlikte değerlendirin"],
            },
            "high": {
                "meaning": "Hemoglobin referans aralığının üzerinde.",
                "eat": ["Yeterli sıvı alımı"],
                "avoid": ["Sigara", "Susuz kalma"],
                "next": ["Tekrar kan sayımı ve klinik değerlendirme önerilir"],
            },
        },
        "ferritin": {
            "low": {
                "meaning": "Demir depolarında azalma ile uyumlu olabilir.",
                "eat": ["Kırmızı et/kurubaklagil", "C vitamini kaynakları"],
                "avoid": ["Öğünle birlikte yoğun çay/kahve"],
                "next": ["Hemoglobin ve MCV ile birlikte değerlendirin"],
            }
        },
        "demir": {
            "low": {
                "meaning": "Demir düzeyi düşük görünüyor.",
                "eat": ["Demir içeriği yüksek besinler", "C vitamini"],
                "avoid": ["Kontrolsüz takviye"],
                "next": ["Ferritin ve tam kan sayımı ile birlikte değerlendirin"],
            }
        },
        "kolesterol": {
            "high": {
                "meaning": "Kolesterol yüksekliği kardiyometabolik risk açısından izlenmelidir.",
                "eat": ["Zeytinyağı", "Yulaf", "Sebze ve baklagiller"],
                "avoid": ["Trans yağlar", "Kızartmalar", "İşlenmiş etler"],
                "next": ["LDL, HDL ve trigliserid ile birlikte risk hesabı yapılabilir"],
            }
        },
        "ldl": {
            "high": {
                "meaning": "LDL yüksekliği damar sağlığı açısından önemlidir.",
                "eat": ["Akdeniz tipi beslenme", "Lifli gıdalar"],
                "avoid": ["Trans yağ", "Doymuş yağ fazlalığı"],
                "next": ["Kişisel risk durumuna göre hekim değerlendirmesi önerilir"],
            }
        },
        "trigliserid": {
            "high": {
                "meaning": "Trigliserid yüksekliği karbonhidrat/alkol yükü veya metabolik riskle ilişkili olabilir.",
                "eat": ["Balık", "Sebze ağırlıklı öğünler", "Şekersiz içecekler"],
                "avoid": ["Şekerli yiyecekler", "Alkol", "Rafine karbonhidrat"],
                "next": ["Açlık ölçümüyle tekrar kontrol ve lipid panel takibi önerilir"],
            }
        },
        "hdl": {
            "low": {
                "meaning": "HDL düşüklüğü koruyucu kolesterol düzeyinin düşük olabileceğini gösterir.",
                "eat": ["Zeytinyağı", "Kuruyemiş", "Balık"],
                "avoid": ["Hareketsizlik", "Sigara"],
                "next": ["Düzenli egzersiz ve lipid panel takibi önerilir"],
            }
        },
        "tsh": {
            "high": {
                "meaning": "TSH yüksekliği tiroidin yavaş çalışmasıyla ilişkili olabilir.",
                "eat": ["Dengeli protein", "Yeterli iyot içeren beslenme"],
                "avoid": ["Kontrolsüz iyot veya tiroid takviyesi"],
                "next": ["Serbest T4 ve endokrinoloji değerlendirmesi önerilir"],
            },
            "low": {
                "meaning": "TSH düşüklüğü tiroidin hızlı çalışmasıyla ilişkili olabilir.",
                "eat": ["Dengeli öğünler"],
                "avoid": ["Kontrolsüz takviye"],
                "next": ["Serbest T3/T4 ile birlikte hekim değerlendirmesi önerilir"],
            },
        },
        "crp": {
            "high": {
                "meaning": "CRP yüksekliği vücutta inflamasyon/enfeksiyon olasılığını düşündürür.",
                "eat": ["Yeterli sıvı", "Dengeli beslenme"],
                "avoid": ["Kendi kendine antibiyotik kullanımı"],
                "next": ["Ateş, ağrı veya enfeksiyon bulgusu varsa muayene önerilir"],
            }
        },
        "wbc": {
            "high": {
                "meaning": "Beyaz kan hücresi yüksekliği enfeksiyon veya inflamasyonla ilişkili olabilir.",
                "eat": ["Yeterli sıvı", "Dengeli öğünler"],
                "avoid": ["Gereksiz ilaç kullanımı"],
                "next": ["Şikayetlerle birlikte değerlendirilmelidir"],
            },
            "low": {
                "meaning": "WBC düşüklüğü bağışıklık sistemi açısından takip gerektirebilir.",
                "eat": ["Yeterli protein", "Dengeli beslenme"],
                "avoid": ["Kalabalık ortamlarda korunmasız temas"],
                "next": ["Tekrar hemogram ve hekim değerlendirmesi önerilir"],
            },
        },
        "alt": {
            "high": {
                "meaning": "ALT yüksekliği karaciğer hücre etkilenmesini gösterebilir.",
                "eat": ["Sebze ağırlıklı öğünler", "Yeterli sıvı"],
                "avoid": ["Alkol", "Kontrolsüz ağrı kesici/takviye"],
                "next": ["AST, GGT ve bilirubin ile birlikte değerlendirin"],
            }
        },
        "ast": {
            "high": {
                "meaning": "AST yüksekliği karaciğer veya kas kaynaklı etkilenmeyle ilişkili olabilir.",
                "eat": ["Dengeli beslenme"],
                "avoid": ["Alkol", "Ağır egzersiz sonrası hemen test tekrarı"],
                "next": ["ALT ve klinik bulgularla birlikte değerlendirin"],
            }
        },
        "kreatinin": {
            "high": {
                "meaning": "Kreatinin yüksekliği böbrek fonksiyonu açısından önemlidir.",
                "eat": ["Yeterli sıvı", "Tuz tüketimini azaltmaya yönelik beslenme"],
                "avoid": ["Kontrolsüz ağrı kesici", "Aşırı protein yükü"],
                "next": ["eGFR ve idrar tahlili ile birlikte değerlendirme önerilir"],
            }
        },
    }

    template = advice_map.get(name, {}).get(status)
    if not template:
        direction = "yüksek" if status == "high" else "düşük"
        template = {
            "meaning": f"{display} değeri referans aralığına göre {direction}.",
            "eat": ["Dengeli ve düzenli öğünler", "Yeterli sıvı alımı"],
            "avoid": ["Kontrolsüz takviye/ilaç kullanımı"],
            "next": ["Sonucu şikayetleriniz ve önceki testlerinizle birlikte hekiminizle değerlendirin"],
        }

    return {
        "test_name": name,
        "title": display,
        "status": status,
        "value": result["value"],
        "unit": result["unit"],
        "meaning": template["meaning"],
        "eat": list(template["eat"]),
        "avoid": list(template["avoid"]),
        "next_steps": list(template["next"]),
    }


def _combo_patterns(index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    patterns: list[dict[str, Any]] = []

    if _has(index, "glukoz", "high") and (
        _has(index, "trigliserid", "high") or _has(index, "ldl", "high") or _has(index, "kolesterol", "high") or _has(index, "hdl", "low")
    ):
        patterns.append(
            {
                "code": "metabolic_risk",
                "title": "Metabolik risk paterni",
                "severity": "moderate",
                "tests": [name for name in ["glukoz", "trigliserid", "ldl", "kolesterol", "hdl"] if name in index],
                "interpretation": "Kan şekeri ile lipid değerlerindeki bozulma birlikte metabolik risk açısından dikkat gerektirir.",
                "recommendations": [
                    "Şekerli içecekler ve rafine karbonhidratı azaltın.",
                    "Haftada en az 150 dakika tempolu yürüyüş hedefleyin.",
                    "HbA1c ve tam lipid paneli için hekim kontrolü planlayın.",
                ],
            }
        )

    if _has(index, "hemoglobin", "low") and (
        _has(index, "ferritin", "low") or _has(index, "demir", "low") or _has(index, "mcv", "low")
    ):
        patterns.append(
            {
                "code": "iron_deficiency_pattern",
                "title": "Demir eksikliği ile uyumlu patern",
                "severity": "moderate",
                "tests": [name for name in ["hemoglobin", "ferritin", "demir", "mcv", "rdw"] if name in index],
                "interpretation": "Hemoglobin düşüklüğüne demir depoları veya MCV düşüklüğü eşlik ediyor; demir eksikliği açısından anlamlı olabilir.",
                "recommendations": [
                    "Demirden zengin beslenmeyi C vitamini ile destekleyin.",
                    "Demir takviyesini kendi kendinize başlatmadan hekimle görüşün.",
                    "Gerekirse B12, folat ve kan kaybı nedenleri araştırılabilir.",
                ],
            }
        )

    if _has(index, "crp", "high") and _has(index, "wbc", "high"):
        patterns.append(
            {
                "code": "inflammation_pattern",
                "title": "Enflamasyon/enfeksiyon paterni",
                "severity": "attention",
                "tests": ["crp", "wbc"],
                "interpretation": "CRP ve WBC birlikte yüksek; enfeksiyon veya inflamasyon olasılığı klinik belirtilerle birlikte değerlendirilmelidir.",
                "recommendations": [
                    "Ateş, öksürük, idrar yakınması veya ağrı varsa muayene olun.",
                    "Kendi kendinize antibiyotik kullanmayın.",
                    "Hekim önerirse takip CRP/hemogram yapılabilir.",
                ],
            }
        )

    if _has(index, "alt", "high") and _has(index, "ast", "high"):
        patterns.append(
            {
                "code": "liver_enzyme_pattern",
                "title": "Karaciğer enzim yüksekliği paterni",
                "severity": "moderate",
                "tests": ["alt", "ast"],
                "interpretation": "ALT ve AST birlikte yüksek; karaciğer etkilenmesi veya bazı durumlarda kas kaynaklı nedenler açısından değerlendirme gerekir.",
                "recommendations": [
                    "Alkol ve kontrolsüz takviye/ilaç kullanımından kaçının.",
                    "GGT, bilirubin ve hepatit belirteçleri gerekebilir.",
                    "Sonuçları önceki testlerle karşılaştırın.",
                ],
            }
        )

    if _has(index, "tsh", "high") and (_has(index, "kolesterol", "high") or _has(index, "ldl", "high")):
        patterns.append(
            {
                "code": "thyroid_lipid_pattern",
                "title": "Tiroid-lipid ilişkisi",
                "severity": "moderate",
                "tests": [name for name in ["tsh", "kolesterol", "ldl"] if name in index],
                "interpretation": "TSH yüksekliği ile kolesterol/LDL yüksekliği birlikte görüldüğünde tiroid yavaşlığı lipidleri etkiliyor olabilir.",
                "recommendations": [
                    "Serbest T4 ile tiroid fonksiyonlarını tamamlayın.",
                    "Lipid tedavisi planlanmadan önce tiroid durumu gözden geçirilebilir.",
                    "Endokrinoloji veya aile hekimi takibi önerilir.",
                ],
            }
        )

    if _has(index, "kreatinin", "high"):
        patterns.append(
            {
                "code": "kidney_function_attention",
                "title": "Böbrek fonksiyonu dikkat gerektiriyor",
                "severity": "attention",
                "tests": ["kreatinin"],
                "interpretation": "Kreatinin yüksekliği böbrek fonksiyonları açısından takip gerektirir.",
                "recommendations": [
                    "eGFR ve idrar tahlili ile birlikte değerlendirin.",
                    "Yeterli sıvı alın ve kontrolsüz ağrı kesici kullanmayın.",
                    "Önceki kreatinin değerleriyle karşılaştırma önemlidir.",
                ],
            }
        )

    return patterns


def build_report_interpretation(results: list[Any]) -> dict[str, Any]:
    normalized = _normalize_results(results)
    abnormal = [result for result in normalized if result["status"] != "normal"]
    index = {result["test_name"]: result for result in normalized}
    combinations = _combo_patterns(index)
    individual = [advice for result in abnormal if (advice := _individual_advice(result)) is not None]

    high_count = sum(1 for result in abnormal if result["status"] == "high")
    low_count = sum(1 for result in abnormal if result["status"] == "low")
    attention_count = sum(1 for pattern in combinations if pattern["severity"] == "attention")

    if not normalized:
        summary = "Bu raporda yorumlanabilecek laboratuvar sonucu bulunamadı."
        patient_report = "PDF içeriğinden test sonucu çıkarılamadı. Daha net bir PDF yüklemeyi veya sonucu manuel kontrol etmeyi deneyin."
    elif not abnormal:
        summary = "Çıkarılan testlerin tamamı referans aralığında görünüyor."
        patient_report = "Genel tablo sakin görünüyor. Buna rağmen sonuçlar şikayetleriniz, yaşınız, ilaçlarınız ve önceki değerlerinizle birlikte değerlendirilmelidir."
    else:
        abnormal_names = ", ".join(item["display_name"] for item in abnormal[:5])
        summary = f"{len(normalized)} testten {len(abnormal)} tanesi referans dışı: {abnormal_names}."
        if combinations:
            patient_report = f"Raporda tekil sapmaların yanında {len(combinations)} önemli kombinasyon paterni görüldü. Öncelik bu paternlerin klinik durumunuzla birlikte değerlendirilmesidir."
        else:
            patient_report = "Referans dışı değerler var; belirgin bir kombinasyon paterni yakalanmadı. Tek tek değerlerin şikayetler ve önceki sonuçlarla karşılaştırılması önerilir."

    priority = "routine"
    if attention_count > 0 or high_count + low_count >= 4:
        priority = "attention"
    if _has(index, "glukoz", "low") or (_has(index, "crp", "high") and _has(index, "wbc", "high")):
        priority = "prompt_follow_up"

    next_steps: list[str] = []
    for pattern in combinations:
        for recommendation in pattern["recommendations"]:
            if recommendation not in next_steps:
                next_steps.append(recommendation)
    for advice in individual:
        for step in advice["next_steps"]:
            if step not in next_steps:
                next_steps.append(step)
    if not next_steps:
        next_steps = ["Sonuçları rutin kontrolünüzde hekiminizle paylaşın."]

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "total_tests": len(normalized),
        "normal_count": len(normalized) - len(abnormal),
        "abnormal_count": len(abnormal),
        "high_count": high_count,
        "low_count": low_count,
        "priority": priority,
        "summary": summary,
        "patient_report": patient_report,
        "abnormal_findings": [
            {
                "test_name": result["test_name"],
                "title": result["display_name"],
                "value": result["value"],
                "unit": result["unit"],
                "status": result["status"],
                "text": f"{result['display_name']}: {_value_text(result)} ({'yüksek' if result['status'] == 'high' else 'düşük'})",
            }
            for result in abnormal
        ],
        "combinations": combinations,
        "recommendations": individual,
        "next_steps": next_steps[:8],
        "disclaimer": "Bu yorum bilgilendirme amaçlıdır; tanı veya tedavi yerine geçmez. Acil şikayet varsa sağlık kuruluşuna başvurun.",
    }
