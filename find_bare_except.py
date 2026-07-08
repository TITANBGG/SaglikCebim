import os
import re

root_dir = r"c:\Users\AliNebiER\Desktop\Projelerim\SaglikCebim (1)\Kod (1)\saglikcebim (1)\backend (1)"
bare_except_pattern = re.compile(r"except\s*:")
unused_import_pattern = re.compile(r"unused import", re.IGNORECASE)

findings = []
for dirpath, dirnames, filenames in os.walk(root_dir):
    if 'node_modules' in dirpath or '.venv' in dirpath or 'venv' in dirpath or '__pycache__' in dirpath:
        continue
    for file in filenames:
        if file.endswith('.py'):
            filepath = os.path.join(dirpath, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except Exception:
                continue
            for i, line in enumerate(lines):
                if bare_except_pattern.search(line):
                    findings.append(f"Bare except in {filepath}:{i+1}")

if findings:
    print("\n".join(findings))
else:
    print("No bare excepts found.")
