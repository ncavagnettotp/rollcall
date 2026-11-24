"""Real PostgreSQL checks, opt in with a dedicated TEST_DOCUMENT_DATABASE_URL.

Each test creates/drops only a uniquely named schema and uses a temporary archive.
The isolated-database verifier sets this URL to its disposable test-only cluster.
"""
import io
import os
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.rows import dict_row
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from app.main import app
from app import document_store

pytestmark = pytest.mark.skipif(not os.getenv('TEST_DOCUMENT_DATABASE_URL'),
                                reason='dedicated TEST_DOCUMENT_DATABASE_URL required')


@pytest.fixture
def archive(monkeypatch, tmp_path):
    url = os.environ['TEST_DOCUMENT_DATABASE_URL']
    schema = 'document_test_' + uuid4().hex
    with psycopg.connect(url, autocommit=True) as connection:
        connection.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(schema)))
    def test_connection():
        return psycopg.connect(url, connect_timeout=3, row_factory=dict_row,
                               options=f'-c search_path={schema} -c statement_timeout=5000')
    monkeypatch.setattr(document_store, 'connect', test_connection)
    monkeypatch.setenv('DOCUMENT_ARCHIVE_DIR', str(tmp_path))
    with test_connection() as connection:
        connection.execute(document_store.SCHEMA)
        connection.execute(document_store.SCHEMA)  # Explicit schema utility is repeatable.
    try:
        yield TestClient(app), tmp_path
    finally:
        with psycopg.connect(url, autocommit=True) as connection:
            connection.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(schema)))


def pdf_with_text(text):
    writer = PdfWriter()
    page = writer.add_blank_page(width=600, height=800)
    font = DictionaryObject({NameObject('/Type'): NameObject('/Font'),
                             NameObject('/Subtype'): NameObject('/Type1'),
                             NameObject('/BaseFont'): NameObject('/Helvetica')})
    page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): writer._add_object(font)})})
    lines = ['BT /F1 12 Tf 40 760 Td 14 TL']
    for line in text.splitlines():
        lines.append('(' + line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)') + ') Tj T*')
    lines.append('ET')
    stream = DecodedStreamObject()
    stream.set_data('\n'.join(lines).encode('latin-1'))
    page[NameObject('/Contents')] = writer._add_object(stream)
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def upload(client, content, filename='invoice.pdf'):
    response = client.post('/api/documents', content=content,
                           headers={'Content-Type': 'application/pdf', 'X-Filename': filename})
    assert response.status_code == 200
    return response.json()


def test_original_archive_duplicate_review_history_and_stale_revision(archive):
    client, root = archive
    original = pdf_with_text('Invoice\nInvoice # 1001 Invoice Date 11/10/2026\nWork Order # 2001\n')
    first = upload(client, original, '..%2F..%2Finvoice.pdf')
    assert first['filename'] == 'invoice.pdf' and first['version'] == 1
    assert first['status'] == 'needs_review' and not first['duplicate']
    duplicate = upload(client, original, 'other-name.pdf')
    assert duplicate['id'] == first['id'] and duplicate['duplicate']
    assert len(list(root.glob('*.pdf'))) == 1
    assert client.get(first['pdf_url']).content == original
    first_fields = first['extracted'].copy()
    saved = client.patch('/api/documents/' + first['id'], json={
        'version': 1, 'fields': {'customer_name': 'Fictional correction', 'lug_nuts': 'yes'}, 'status': 'reviewed'})
    assert saved.status_code == 200
    result = saved.json()
    assert result['version'] == 2 and result['status'] == 'reviewed'
    assert result['extracted'] == first_fields
    assert result['fields']['customer_name'] == 'Fictional correction'
    assert result['review_history'][0]['fields'] == first['fields']
    stale = client.patch('/api/documents/' + first['id'], json={
        'version': 1, 'fields': {'notes': 'stale'}, 'status': 'reviewed'})
    assert stale.status_code == 409
    assert client.get('/api/documents/' + first['id']).json()['version'] == 2
    assert len(client.get('/api/documents').json()['documents']) == 1
    # New client demonstrates persisted metadata rather than browser/client state.
    assert TestClient(app).get('/api/documents/' + first['id']).json()['fields']['lug_nuts'] == 'yes'


def test_same_work_order_different_sources_retained_and_warned(archive):
    client, root = archive
    first = upload(client, pdf_with_text('Authorization\nWork Order # 2010\n'))
    second = upload(client, pdf_with_text('Invoice\nInvoice # 1020\nWork Order # 2010\n'))
    assert first['id'] != second['id']
    assert len(list(root.glob('*.pdf'))) == 2
    for document_id in (first['id'], second['id']):
        result = client.get('/api/documents/' + document_id).json()
        assert any('shares this work order' in warning for warning in result['warnings'])


def test_concurrent_exact_upload_has_one_archive_row_and_no_temporary_files(archive):
    client, root = archive
    content = pdf_with_text('Invoice\nInvoice # 3000\n')
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: upload(TestClient(app), content), range(2)))
    assert results[0]['id'] == results[1]['id']
    assert sorted(result['duplicate'] for result in results) == [False, True]
    assert len(client.get('/api/documents').json()['documents']) == 1
    assert len(list(root.glob('*.pdf'))) == 1
    assert not list(root.glob('.upload-*'))


def test_missing_document_and_archive_failure_are_safe(archive, monkeypatch):
    client, root = archive
    assert client.get('/api/documents/' + str(uuid4())).status_code == 404
    blocked = root / 'not-a-directory'
    blocked.write_text('occupied')
    monkeypatch.setenv('DOCUMENT_ARCHIVE_DIR', str(blocked))
    response = client.post('/api/documents', content=pdf_with_text('Invoice\n'),
                           headers={'Content-Type': 'application/pdf'})
    assert response.status_code == 503
    assert str(blocked) not in response.text
    assert client.get('/api/documents').json()['documents'] == []
