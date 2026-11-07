from fastapi.testclient import TestClient
import app as deployment


def test_same_origin_spa_and_api_routing(tmp_path,monkeypatch):
    (tmp_path/'index.html').write_text('<html><title>PrivyCommerce AI</title></html>')
    monkeypatch.setattr(deployment,'PUBLIC',tmp_path)
    with TestClient(deployment.app) as client:
        assert client.get('/api/health').json()=={'status':'ok'}
        for path in ['/','/assistant','/products/p1','/compare']:
            response=client.get(path)
            assert response.status_code==200
            assert 'PrivyCommerce AI' in response.text
            assert response.headers['content-type'].startswith('text/html')
        assert client.get('/api/nonexistent').status_code==404
