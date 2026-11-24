"""Explicit manual check; creates only a foundation probe table, not business records."""
import argparse
import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name('.env'))
parser = argparse.ArgumentParser()
parser.add_argument('action', choices=['write', 'read'])
args = parser.parse_args()
with psycopg.connect(os.environ['DATABASE_URL'], connect_timeout=3) as conn:
    with conn.cursor() as cursor:
        if args.action == 'write':
            cursor.execute('CREATE TABLE IF NOT EXISTS foundation_probe (id INTEGER PRIMARY KEY, value TEXT NOT NULL)')
            cursor.execute("INSERT INTO foundation_probe VALUES (1, 'step1-persistence') ON CONFLICT (id) DO UPDATE SET value = EXCLUDED.value")
        else:
            cursor.execute('SELECT value FROM foundation_probe WHERE id = 1')
            if cursor.fetchone() != ('step1-persistence',):
                raise SystemExit('FAIL: persistence marker missing')
print('PASS:', args.action)
