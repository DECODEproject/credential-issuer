from starlette.testclient import TestClient
from app.main import app


def test_home():
    client = TestClient(app)
    r = client.get('/')
    assert r.status_code == 200
