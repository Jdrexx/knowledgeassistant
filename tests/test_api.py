from fastapi.testclient import TestClient
from src.main import app
client = TestClient(app)
def test_health():
    r=client.get('/api/health')
    assert r.status_code == 200
    assert r.json()['ok'] is True

def test_ingest_and_ask():
    client.post('/api/ingest', json={'title':'Manual','text':'FastAPI supports Python APIs and automatic documentation for backend services.'})
    data=client.post('/api/ask', json={'question':'What supports Python APIs?'}).json()
    assert data['citations']
