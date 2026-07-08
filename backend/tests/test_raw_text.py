"""Show raw text from problematic PDFs."""
import os
from app.services.pdf_parser import extract_text_from_pdf, _preprocess_text

UPLOAD_DIR = "uploads"

# Get unique PDFs by original name
seen = {}
for f in sorted(os.listdir(UPLOAD_DIR)):
    if f.endswith(".pdf"):
        original = f.split("_", 1)[1] if "_" in f else f
        if original not in seen:
            seen[original] = f

# Show raw text for problematic PDFs
for pdf_name in ["2024 1 kasım TR.pdf", "2024 1 eylul EN.pdf", "2018 EN.pdf"]:
    if pdf_name in seen:
        filepath = os.path.join(UPLOAD_DIR, seen[pdf_name])
        print(f"\n{'='*80}")
        print(f"RAW TEXT: {pdf_name}")
        print(f"{'='*80}")
        raw = extract_text_from_pdf(filepath)
        for i, line in enumerate(raw.splitlines()):
            if line.strip():
                print(f"{i:3d}: {line}")
        
        print(f"\n--- PREPROCESSED ---")
        processed = _preprocess_text(raw)
        for i, line in enumerate(processed.splitlines()):
            if line.strip():
                print(f"{i:3d}: {line}")
