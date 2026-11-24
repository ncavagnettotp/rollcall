"""Explicit, repeatable Stage 2 schema migration; never runs at app startup."""
from pathlib import Path
from dotenv import load_dotenv
from app.document_store import connect, SCHEMA


def main():
    load_dotenv(Path(__file__).with_name('.env'))
    with connect() as connection:
        connection.execute(SCHEMA)
    print('PASS: Stage 2 storage_documents schema is ready.')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        raise SystemExit('Migration failed. Check PostgreSQL configuration/permissions; no connection details are printed.') from None
