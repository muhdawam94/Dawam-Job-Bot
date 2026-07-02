#!/usr/bin/env python3
import re

output_file = r'C:\Users\ASUS\AppData\Local\Temp\claude\C--Users-ASUS-Desktop\64fce311-059c-4c21-b64d-7d60b2c5ec39\tasks\bf1qc1kar.output'

successful = []
failed = []

with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

current_job = None
current_company = None
current_url = None
current_platform = None

for i, line in enumerate(lines):
    # Parse AutoApply header
    if '[AutoApply]' in line and ' @ ' in line:
        parts = line.split('[AutoApply]')[1].strip().split(' @ ')
        current_job = parts[0].strip()
        current_company = parts[1].strip() if len(parts) > 1 else 'Unknown'

    # Parse platform
    if '[AutoApply] Platform:' in line:
        current_platform = line.split('Platform:')[1].strip()

    # Parse URL
    if current_platform and ('https://' in line or 'http://' in line):
        url_match = re.search(r'(https?://[^\s]+)', line)
        if url_match:
            current_url = url_match.group(1)

    # Parse result
    if '[OK] Submitted!' in line or '[OK] Auto-applied successfully!' in line:
        if current_job and current_company:
            successful.append({
                'title': current_job,
                'company': current_company,
                'url': current_url,
                'platform': current_platform
            })
            current_job = None

    if '[WARNING] Auto-apply failed' in line or 'X Message:' in line:
        if current_job and current_company:
            failed.append({
                'title': current_job,
                'company': current_company,
                'url': current_url,
                'platform': current_platform
            })
            current_job = None

# Print results
print(f'\n{"="*80}')
print(f'   APPLICATIONS FROM OUTPUT LOG')
print(f'{"="*80}\n')

print(f'[OK] SUCCESSFUL APPLICATIONS: {len(successful)}\n')
for i, job in enumerate(successful, 1):
    print(f'{i}. {job["title"][:60]}')
    print(f'   Company: {job["company"]}')
    print(f'   Platform: {job["platform"]}')
    print(f'   URL: {job["url"]}')
    print()

print(f'\n[FAILED] FAILED APPLICATIONS: {len(failed)}\n')
for i, job in enumerate(failed[:10], 1):
    print(f'{i}. {job["title"][:60]}')
    print(f'   Company: {job["company"]}')
    print(f'   Platform: {job["platform"]}')
    print()

print(f'{"="*80}')
print(f'TOTAL PROCESSED: {len(successful) + len(failed)}')
print(f'SUCCESS RATE: {len(successful)}/{len(successful) + len(failed)} = {len(successful)*100//(len(successful)+len(failed)) if (len(successful)+len(failed)) > 0 else 0}%')
print(f'{"="*80}\n')
