from pathlib import Path
from urllib.parse import urlparse
from fastapi.testclient import TestClient
from backend.main import app
from backend.catalog import DATA


def test_catalog_photo_coverage_and_existing_product_contract():
    with TestClient(app) as client:
        products=client.get('/api/products').json()
        assert len(products)==308
        assert len({p['id'] for p in products})==308
        original=next(p for p in products if p['id']=='p1')
        assert original['name']=='Studio Wireless Headphones'
        assert original['price']==129
        assert original['category']=='Electronics'
        families={}
        for p in products:
            assert p['image_url']==p['images'][0]['url']
            assert len(p['images'])>=2
            for image in p['images']:
                assert urlparse(image['url']).scheme=='https'
                assert urlparse(image['url']).hostname in {'images.pexels.com','images.unsplash.com'}
            assert p['fallback_image'].startswith('/product-images/')
            local=Path(__file__).resolve().parents[2]/'frontend/public'/p['fallback_image'].lstrip('/')
            assert local.exists(),p['name']
            # Related synthetic variants may share one image; unrelated families may not.
            previous=families.setdefault(p['image_url'],p['family'])
            assert previous==p['family']
        assert len(families)==30
        assert len(DATA['media'])==308


def test_all_requested_departments_have_photos():
    with TestClient(app) as client:
        for category in ['Electronics','Fashion','Home & Kitchen','Beauty','Sports']:
            result=client.get('/api/products',params={'category':category}).json()
            assert len(result)>=30
            assert all(p['images'] for p in result)
