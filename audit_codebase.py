import os
import re
import json

root_dir = r"c:\Users\AliNebiER\Desktop\Projelerim\SaglikCebim (1)\Kod (1)\saglikcebim (1)"

secrets_pattern = re.compile(r"(SECRET_KEY|PASSWORD|API_KEY|TOKEN)\s*[:=]\s*['\"].*?['\"]", re.IGNORECASE)
localhost_pattern = re.compile(r"(localhost|127\.0\.0\.1|0\.0\.0\.0)")
debug_pattern = re.compile(r"DEBUG\s*=\s*True")
print_pattern = re.compile(r"print\(")
console_pattern = re.compile(r"console\.log\(")

findings = []

for dirpath, dirnames, filenames in os.walk(root_dir):
    if 'node_modules' in dirpath or '.venv' in dirpath or 'venv' in dirpath or '.git' in dirpath:
        continue
    for file in filenames:
        if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.env', '.env.example', '.env.prod')):
            filepath = os.path.join(dirpath, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except Exception:
                continue
                
            for i, line in enumerate(lines):
                line_num = i + 1
                if secrets_pattern.search(line):
                    findings.append({"file": filepath, "line": line_num, "issue": "Hardcoded secret", "content": line.strip()})
                if localhost_pattern.search(line):
                    findings.append({"file": filepath, "line": line_num, "issue": "Hardcoded localhost/IP", "content": line.strip()})
                if debug_pattern.search(line):
                    findings.append({"file": filepath, "line": line_num, "issue": "Debug flag", "content": line.strip()})
                if file.endswith('.py') and print_pattern.search(line):
                    findings.append({"file": filepath, "line": line_num, "issue": "Print statement", "content": line.strip()})
                if not file.endswith('.py') and console_pattern.search(line):
                    findings.append({"file": filepath, "line": line_num, "issue": "console.log", "content": line.strip()})

with open(os.path.join(root_dir, "audit_results.json"), "w", encoding='utf-8') as f:
    json.dump(findings, f, indent=4)
print("Audit complete.")
