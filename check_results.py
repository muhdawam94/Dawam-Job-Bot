#!/usr/bin/env python3
import sqlite3

# Connect to database
conn = sqlite3.connect('data/jobs.db')
c = conn.cursor()

# Get successful applications
success = c.execute(
    'SELECT title, company, auto_apply_platform FROM jobs WHERE auto_apply_status="success" ORDER BY id DESC'
).fetchall()

# Get failed applications
failed = c.execute(
    'SELECT title, company, auto_apply_error FROM jobs WHERE auto_apply_status="failed" ORDER BY id DESC'
).fetchall()

# Print results
print(f'\n{"="*70}')
print(f'   AUTO-APPLY RESULTS')
print(f'{"="*70}\n')

print(f'=== {len(success)} SUCCESSFUL APPLICATIONS ===\n')
for i, (title, company, platform) in enumerate(success, 1):
    print(f'{i}. {title[:55]} @ {company} ({platform})')

print(f'\n\n=== {len(failed)} FAILED APPLICATIONS ===\n')
for i, (title, company, error) in enumerate(failed[:10], 1):
    error_short = error[:60] if error else 'Unknown error'
    print(f'{i}. {title[:55]} @ {company}')
    print(f'   Error: {error_short}')

print(f'\n{"="*70}')
print(f'SUCCESS RATE: {len(success)}/{len(success)+len(failed)} = {len(success)*100//(len(success)+len(failed)) if (len(success)+len(failed)) > 0 else 0}%')
print(f'{"="*70}\n')

conn.close()
