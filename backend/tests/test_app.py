import os
import tempfile
from pathlib import Path

os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp())/'test.db')
from fastapi.testclient import TestClient
from backend.main import app
from backend.federation import experiment

def account(client,email):
    r=client.post('/api/auth/register',json={'email':email,'password':'correct-horse-123'})
    assert r.status_code==200,r.text

def test_customer_journey_and_privacy():
    with TestClient(app) as c:
        account(c,'journey@example.com')
        assert c.put('/api/memories/new',json={'node':'atelier','category':'category','value':'Home'}).status_code==403
        assert c.put('/api/privacy',json={'personalization':True,'collection':True,'federation':True,'categories':['category']}).status_code==200
        mid=c.put('/api/memories/new',json={'node':'atelier','category':'category','value':'Home'}).json()['id']
        m=c.get('/api/memories').json()[0]
        assert c.put('/api/memories/'+mid,json={**m,'value':'Electronics'}).status_code==200
        assert c.put('/api/memories/'+mid,json={**m,'value':'Home'}).status_code==409
        reply=c.post('/api/chat',json={'message':'headphones under $150','node':'techhaven'}).json()
        assert len(reply['trace'])==3
        assert not reply['persistent_memory_saved']
        assert all(p['price']<=150 for p in reply['products'])
        assert c.get('/api/federation/analytics').json()['atelier']=={'category':1}
        assert c.put('/api/cart/p1',json={'quantity':2}).status_code==200
        order=c.post('/api/orders').json()
        assert order['total']==258
        assert c.get('/api/cart').json()==[]
        assert len(c.get('/api/orders').json())==1
        assert 'memory' in c.get('/api/export').json()
        assert c.put('/api/privacy',json={'personalization':False,'collection':False,'federation':False,'categories':[]}).status_code==200
        assert c.get('/api/federation/analytics').status_code==403
        assert c.delete('/api/memories/'+mid).status_code==200
        assert c.get('/api/memories').json()==[]
        c.post('/api/logout')
        assert c.get('/api/orders').status_code==401

def test_tenant_isolation_and_csrf():
    with TestClient(app) as a,TestClient(app) as b:
        account(a,'alice@example.com');account(b,'bob@example.com')
        a.put('/api/privacy',json={'personalization':True,'collection':True,'federation':False,'categories':['brand']})
        mid=a.put('/api/memories/new',json={'node':'atelier','category':'brand','value':'Private brand'}).json()['id']
        assert b.get('/api/memories').json()==[]
        b.delete('/api/memories/'+mid)
        assert len(a.get('/api/memories').json())==1
        assert b.put('/api/cart/p1',json={'quantity':1},headers={'origin':'https://evil.test'}).status_code==403
        assert b.put('/api/cart/p1',json={'quantity':-1}).status_code==422
        assert b.get('/api/export').json()['memory']==[]

def test_fedavg_comparison():
    result=experiment(rounds=12)
    assert result['clients']==3
    assert result['history'][-1]['federated']<result['history'][0]['federated']
    assert not result['formal_dp_guarantee']
    assert experiment(noise=.5)['history']!=experiment(noise=0)['history']
