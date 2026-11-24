"""PostgreSQL document metadata and content-addressed local PDF archive."""
import hashlib
import os
from pathlib import Path
import tempfile
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


SCHEMA = '''CREATE TABLE IF NOT EXISTS storage_documents (
    id UUID PRIMARY KEY,
    sha256 TEXT NOT NULL UNIQUE,
    filename TEXT NOT NULL,
    pages INTEGER NOT NULL CHECK (pages BETWEEN 1 AND 50),
    extracted JSONB NOT NULL,
    fields JSONB NOT NULL,
    raw_text TEXT NOT NULL,
    warnings JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'needs_review' CHECK (status IN ('needs_review','reviewed')),
    version INTEGER NOT NULL DEFAULT 1,
    review_history JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
)'''


class StoreUnavailable(Exception):
    pass


class DocumentNotFound(Exception):
    pass


class RevisionConflict(Exception):
    pass


def connect():
    url = os.environ.get('DATABASE_URL', '')
    if not url.startswith(('postgresql://', 'postgres://')):
        raise StoreUnavailable()
    return psycopg.connect(url, connect_timeout=3, options='-c statement_timeout=5000', row_factory=dict_row)


def archive_root() -> Path:
    return Path(os.environ.get('DOCUMENT_ARCHIVE_DIR', Path(__file__).resolve().parents[1] / 'data' / 'documents'))


def present(row: dict, duplicate=False, related=False) -> dict:
    warnings = list(row['warnings'])
    if related:
        warnings.append('Another source document shares this work order. Both originals are retained; reconcile before later storage actions.')
    return {'id': str(row['id']), 'filename': row['filename'], 'pages': row['pages'],
            'extracted': row['extracted'], 'fields': row['fields'], 'warnings': warnings,
            'status': row['status'], 'version': row['version'], 'duplicate': duplicate,
            'pdf_url': f'/api/documents/{row["id"]}/pdf',
            'created_at': row['created_at'].isoformat(), 'review_history': row['review_history']}


def has_related(connection, row) -> bool:
    number = row['extracted'].get('work_order_number', '')
    if not number:
        return False
    return connection.execute("SELECT EXISTS (SELECT 1 FROM storage_documents WHERE id<>%s AND extracted->>'work_order_number'=%s) AS related",
                              (row['id'], number)).fetchone()['related']


def persist(content: bytes, filename: str, extracted: dict, warnings: list, pages: int, text: str) -> dict:
    digest = hashlib.sha256(content).hexdigest()
    root = archive_root()
    temporary = None
    try:
        with connect() as connection:
            # All uploaders for this content share a transaction lock, including across workers.
            lock = int.from_bytes(bytes.fromhex(digest[:16]), 'big', signed=True)
            connection.execute('SELECT pg_advisory_xact_lock(%s)', (lock,))
            row = connection.execute('SELECT * FROM storage_documents WHERE sha256=%s', (digest,)).fetchone()
            root.mkdir(parents=True, exist_ok=True)
            destination = root / (digest + '.pdf')
            # Restores a missing archive on exact re-upload without changing metadata.
            if not destination.exists():
                with tempfile.NamedTemporaryFile(dir=root, prefix='.upload-', delete=False) as output:
                    temporary = Path(output.name)
                    output.write(content)
                    output.flush()
                    os.fsync(output.fileno())
                os.replace(temporary, destination)
                temporary = None
            if row:
                return present(row, duplicate=True, related=has_related(connection, row))
            row = connection.execute('''INSERT INTO storage_documents
                (id,sha256,filename,pages,extracted,fields,raw_text,warnings)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *''',
                (uuid4(), digest, filename, pages, Jsonb(extracted), Jsonb(extracted), text, Jsonb(warnings))).fetchone()
            result = present(row, related=has_related(connection, row))
        return result
    except (psycopg.Error, OSError):
        # Keep any atomically installed PDF on uncertain commit; removing it could
        # leave a committed row (or another uploader) pointing at a missing file.
        # An orphaned hash file is safe to reuse on retry; temporary files are removed.
        raise StoreUnavailable() from None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def list_documents() -> list[dict]:
    try:
        with connect() as connection:
            rows = connection.execute('SELECT * FROM storage_documents ORDER BY created_at DESC, id DESC LIMIT 100').fetchall()
            return [present(row, related=has_related(connection, row)) for row in rows]
    except psycopg.Error:
        raise StoreUnavailable() from None


def get_document(document_id, original=False):
    try:
        with connect() as connection:
            row = connection.execute('SELECT * FROM storage_documents WHERE id=%s', (document_id,)).fetchone()
            if row is None:
                raise DocumentNotFound()
            if original:
                path = archive_root() / (row['sha256'] + '.pdf')
                if not path.is_file():
                    raise StoreUnavailable()
                return path, row['filename']
            return present(row, related=has_related(connection, row))
    except psycopg.Error:
        raise StoreUnavailable() from None


def save_review(document_id, version: int, fields: dict) -> dict:
    try:
        with connect() as connection:
            previous = connection.execute('SELECT * FROM storage_documents WHERE id=%s FOR UPDATE', (document_id,)).fetchone()
            if previous is None:
                raise DocumentNotFound()
            if previous['version'] != version:
                raise RevisionConflict()
            corrected = {**previous['fields'], **fields}
            row = connection.execute('''UPDATE storage_documents SET fields=%s,
                status='reviewed', version=version+1,
                review_history=review_history || jsonb_build_array(jsonb_build_object(
                    'version', version, 'fields', fields, 'status', status,
                    'superseded_at', CURRENT_TIMESTAMP)) WHERE id=%s RETURNING *''',
                (Jsonb(corrected), document_id)).fetchone()
            return present(row, related=has_related(connection, row))
    except psycopg.Error:
        raise StoreUnavailable() from None
