from fastapi.testclient import TestClient

from serve_desktop_proof import build_app


def test_same_origin_keeps_api_and_static_routes_separate(tmp_path):
    (tmp_path / 'index.html').write_text('Rollcall proof', encoding='utf-8')
    assets = tmp_path / 'assets'
    assets.mkdir()
    (assets / 'proof.js').write_text('/* proof */', encoding='utf-8')
    client = TestClient(build_app(tmp_path))

    assert client.get('/').text == 'Rollcall proof'
    assert client.get('/assets/proof.js').text == '/* proof */'
    assert client.get('/api/health').json() == {'status': 'ok'}
    assert client.get('/api/missing').json() == {'detail': 'Not Found'}
    assert client.get('/assets/missing.js').status_code == 404
    assert client.get('/storage_documents').status_code == 404
