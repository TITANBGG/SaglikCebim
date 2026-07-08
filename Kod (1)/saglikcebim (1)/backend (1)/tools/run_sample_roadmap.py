import json
import sys
from pathlib import Path

# ensure package importable (use backend folder as package root)
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.clinical.roadmap_generator import RoadmapGenerator, fallback_roadmap


def main():
    gen = RoadmapGenerator()
    context = {
        "current_message": "Göğüs ağrısı ve nefes darlığı var, 2 gündür sürüyor",
        "symptoms": ["göğüs ağrısı", "nefes darlığı"],
        "duration": "2 gün",
        "age": "55",
        "gender": "erkek",
        "chronic_conditions": "hipertansiyon",
        "abnormal_labs": "troponin yüksek değil",
        "radiology_findings": "PA akciğer grafisi normal",
    }

    roadmap = gen.generate(context)
    # Use pydantic model export
    try:
        out = roadmap.model_dump()
    except Exception:
        out = fallback_roadmap().model_dump()

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
