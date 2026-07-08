"""Quick test for e-Nabız PDF parsing."""
from app.services.pdf_parser import parse_pdf

results = parse_pdf(
    "uploads/910a841c-ef7b-475c-b7d9-4fa21259b648_ugur17.07.2025 (1).pdf"
)
print(f"Total parsed: {len(results)}")
print()
for r in results:
    status_icon = {"normal": "OK", "high": "HIGH", "low": "LOW"}.get(r["status"], "?")
    print(
        f"  [{status_icon:4s}] {r['original_name']:45s} {r['value']:>8} {r['unit']:>10}"
        f"  ref: {r['ref_min']}-{r['ref_max']}  -> {r['test_name']}"
    )
