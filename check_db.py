#!/usr/bin/env python3
import sqlite3
import os

db_path = 'data/jobs.db'

print(f'\n{"="*70}')
print(f'   DATABASE DIAGNOSTIC')
print(f'{"="*70}\n')

# Check if file exists
print(f'Database file: {db_path}')
print(f'File exists: {os.path.exists(db_path)}')
if os.path.exists(db_path):
    print(f'File size: {os.path.getsize(db_path)} bytes')

print()

try:
    # Connect to database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Get all tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()

    if tables:
        print(f'Tables found: {len(tables)}')
        for table in tables:
            print(f'  - {table[0]}')

            # Get table schema
            c.execute(f"PRAGMA table_info({table[0]})")
            columns = c.fetchall()
            print(f'    Columns: {", ".join([col[1] for col in columns])}')

            # Get row count
            c.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = c.fetchone()[0]
            print(f'    Rows: {count}')
            print()
    else:
        print('NO TABLES FOUND IN DATABASE!')
        print('Database file exists but is empty or not initialized.')

    conn.close()

except Exception as e:
    print(f'Error: {e}')

print(f'{"="*70}\n')
