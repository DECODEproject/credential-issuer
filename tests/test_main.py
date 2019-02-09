from starlette.testclient import TestClient
from app.main import api


def test_home():
    client = TestClient(api)
    r = client.get('/')
    assert r.status_code == 200
