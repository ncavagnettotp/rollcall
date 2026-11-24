import os
import pytest
from fastapi.testclient import TestClient
from app.main import app, check_database

client = TestClient(app)

def test_liveness():
    assert client.get('/api/health').json() == {'status': 'ok'}

def test_dashboard_placeholders():
    data = client.get('/api/dashboard').json()
    assert data['counts_are_placeholders'] is True
    assert len(data['categories']) == 4
    assert all(c['count'] is None for c in data['categories'])
    assert [c['label'] for c in data['categories']] == ['Stored', 'Due Soon', 'Overdue', 'Needs Attention']

def test_inventory_connection_failure_is_sanitized(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgresql://storage:secret-password@127.0.0.1:1/missing')
    response = client.get('/api/inventory', params={'q': '2356018'})
    assert response.status_code == 503
    assert 'secret-password' not in response.text

def test_missing_database_config_is_unavailable(monkeypatch):
    monkeypatch.delenv('DATABASE_URL', raising=False)
    assert client.get('/api/health/db').status_code == 503
    assert client.get('/api/health').status_code == 200

def test_real_connection_refused_is_sanitized(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgresql://storage:secret-password@127.0.0.1:1/missing')
    response = client.get('/api/health/db')
    assert response.status_code == 503
    assert 'secret-password' not in response.text

def test_database_failure_is_sanitized():
    def unavailable():
        from app.main import DatabaseUnavailable
        raise DatabaseUnavailable('secret-password')
    app.dependency_overrides[check_database] = unavailable
    try:
        response = client.get('/api/health/db')
        assert response.status_code == 503
        assert response.json() == {'status': 'unavailable', 'database': 'postgresql'}
        assert 'secret-password' not in response.text
    finally:
        app.dependency_overrides.clear()

def test_database_success():
    app.dependency_overrides[check_database] = lambda: True
    try:
        assert client.get('/api/health/db').json() == {'status': 'ok', 'database': 'postgresql'}
    finally:
        app.dependency_overrides.clear()

@pytest.mark.skipif(not os.getenv('TEST_DATABASE_URL'), reason='TEST_DATABASE_URL required for real PostgreSQL')
def test_real_postgres():
    from app.database import probe_database
    assert probe_database(os.environ['TEST_DATABASE_URL']) is True
