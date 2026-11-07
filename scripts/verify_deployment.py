"""Smoke-test an owned deployment with a disposable synthetic customer account."""
import argparse
import json
import secrets
import httpx


def verify(base):
    with httpx.Client(base_url=base.rstrip('/'),timeout=90,headers={'Origin':base.rstrip('/')}) as client:
        for path in ['/','/assistant','/products/p1','/compare']:
            response=client.get(path)
            assert response.status_code==200,(path,response.status_code)
            assert 'PrivyCommerce AI' in response.text,path
        assert client.get('/api/health').json()=={'status':'ok'}
        catalog=client.get('/api/products').json()
        assert len(catalog)==308
        image=client.get('/product-images/headphones.webp')
        assert image.status_code==200 and 'image/' in image.headers['content-type']
        credentials={'email':f'deployment-check-{secrets.token_hex(6)}@example.invalid','password':secrets.token_urlsafe(24)}
        response=client.post('/api/auth/register',json=credentials)
        assert response.status_code==200,('register',response.status_code,response.text)
        assert all(cookie.secure for cookie in response.cookies.jar)
        assert client.get('/api/me').status_code==200
        assert client.put('/api/cart/p1',json={'quantity':1}).status_code==200
        assert client.get('/api/cart').json()==[{'product_id':'p1','quantity':1}]
        reply=client.post('/api/chat',json={'message':'headphones under $150','node':'techhaven'})
        assert reply.status_code==200,reply.text
        assert reply.json()['products'][0]['image_url']
        assert client.post('/api/orders').status_code==200
        assert len(client.get('/api/orders').json())==1
        assert client.post('/api/logout').status_code==200
        assert client.get('/api/me').status_code==401
        assert client.post('/api/auth/login',json=credentials).status_code==200
        assert len(client.get('/api/orders').json())==1
        assert client.post('/api/logout').status_code==200
        print(json.dumps({'status':'passed','url':base,'products':len(catalog),'checks':['frontend deep links','API health','photo delivery','registration','secure sessions','cart','shopping agents with photos','demo checkout','persistent order after reauthentication','logout']},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('url')
    verify(parser.parse_args().url)
