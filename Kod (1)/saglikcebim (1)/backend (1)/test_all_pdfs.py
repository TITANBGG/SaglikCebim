"""Test all uploaded PDFs and show parsing results."""
import os
from app.services.pdf_parser import parse_pdf, extract_text_from_pdf, _preprocess_text

UPLOAD_DIR = "uploads"

# Get unique PDFs by original name (strip UUID prefix)
seen = {}
for f in sorted(os.listdir(UPLOAD_DIR)):
    if f.endswith(".pdf"):
        original = f.split("_", 1)[1] if "_" in f else f
        if original not in seen:
            seen[original] = f

print(f"Found {len(seen)} unique PDFs\n")

for original, filename in sorted(seen.items()):
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Get raw text
    raw_text = extract_text_from_pdf(filepath)
    raw_lines = [l for l in raw_text.splitlines() if l.strip()]
    
    # Get processed text
    processed = _preprocess_text(raw_text)
    proc_lines = [l for l in processed.splitlines() if l.strip()]
    
    # Parse
    results = parse_pdf(filepath)
    
    print(f"{'='*80}")
    print(f"PDF: {original}")
    print(f"Raw lines: {len(raw_lines)} | Processed lines: {len(proc_lines)} | Parsed tests: {len(results)}")
    print(f"Tests found:")
    for r in results:
        status = r['status'].upper()
        print(f"  [{status:4s}] {r['original_name']:40s} = {r['value']:>8} {r['unit']:>10} ({r['ref_min']}-{r['ref_max']})")
    print()
