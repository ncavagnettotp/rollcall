import json
import os
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
import pytest

from backup_rollcall import create_backup, restore_backup, verify_backup
from test_document_integration import archive, pdf_with_text, upload


pytestmark = pytest.mark.skipif(not os.getenv('TEST_DOCUMENT_DATABASE_URL'),
                                reason='dedicated TEST_DOCUMENT_DATABASE_URL required')


def test_backup_restores_correction_and_original(archive, tmp_path, monkeypatch):
    client, _ = archive
    source_files = tmp_path / 'live-pdfs'
    monkeypatch.setenv('DOCUMENT_ARCHIVE_DIR', str(source_files))
    url = os.environ['TEST_DOCUMENT_DATABASE_URL']
    from app import document_store
    with document_store.connect() as source:
        schema = source.execute('SELECT current_schema() AS name').fetchone()['name']
    content = pdf_with_text('Invoice\nWork Order # 1234\n')
    document = upload(client, content)
    endpoint = '/api/documents/' + document['id']
    saved = client.patch(endpoint, json={
        'version': document['version'], 'fields': {'notes': 'Restore probe'}, 'status': 'reviewed',
    })
    assert saved.status_code == 200
    saved = saved.json()
    (source_files / ('0' * 64 + '.pdf')).write_bytes(b'unreferenced')
    tools = Path(os.environ.get('TEST_POSTGRES_BIN', 'C:/Program Files/PostgreSQL/18/bin'))
    folder = create_backup(make_conninfo(url, options=f'-c search_path={schema}'), source_files,
                           tmp_path / 'backups', tools)
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    assert len(manifest['pdfs']) == 1
    verify_backup(folder)
    pdf = folder / 'pdfs' / (manifest['pdfs'][0] + '.pdf')
    pdf.write_bytes(b'broken')
    with pytest.raises(ValueError, match='checksum'):
        verify_backup(folder)
    restore_name = 'rollcall_restore_' + uuid4().hex
    with pytest.raises(ValueError, match='checksum'):
        restore_backup(url, restore_name, folder, tmp_path / 'recovered', tools)
    pdf.write_bytes(content)
    try:
        restore_backup(url, restore_name, folder, tmp_path / 'recovered', tools)
        restored_url = make_conninfo(url, dbname=restore_name, options=f'-c search_path={schema}')
        from psycopg.rows import dict_row
        monkeypatch.setattr(document_store, 'connect', lambda: psycopg.connect(restored_url, row_factory=dict_row))
        monkeypatch.setenv('DOCUMENT_ARCHIVE_DIR', str(tmp_path / 'recovered'))
        reopened = client.get(endpoint).json()
        assert reopened['fields'] == saved['fields']
        assert reopened['review_history'] == saved['review_history']
        assert reopened['version'] == saved['version']
        assert client.get(document['pdf_url']).content == content
        with pytest.raises(psycopg.errors.DuplicateDatabase):
            restore_backup(url, restore_name, folder, tmp_path / 'second-archive', tools)
    finally:
        with psycopg.connect(url, autocommit=True) as connection:
            connection.execute(sql.SQL('DROP DATABASE IF EXISTS {}').format(sql.Identifier(restore_name)))
