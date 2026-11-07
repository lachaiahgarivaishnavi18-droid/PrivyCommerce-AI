from fastapi.testclient import TestClient
from backend.main import app

def test_sync_policies():
    with TestClient(app) as c:
        assert c.post('/api/auth/register',json={'email':'sync@example.com','password':'correct-horse-123'}).status_code==200
        assert c.get('/api/admin/summary').status_code==403
        c.put('/api/privacy',json={'personalization':True,'collection':True,'federation':True,'categories':['category']})
        mid=c.put('/api/memories/new',json={'node':'atelier','category':'category','value':'Home'}).json()['id']
        payload={'source':'atelier','target':'earthgoods','memory_id':mid,'expected_version':1}
        assert c.post('/api/federation/sync',json=payload).status_code==200
        assert c.post('/api/federation/sync',json=payload).status_code==409
        assert len(c.get('/api/memories').json())==2
        c.put('/api/privacy',json={'personalization':True,'collection':True,'federation':False,'categories':['category']})
        assert c.post('/api/federation/sync',json={**payload,'target':'techhaven'}).status_code==403
