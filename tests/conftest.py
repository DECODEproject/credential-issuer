import pytest
from starlette.testclient import TestClient

from app.database import engine, Base
from app.main import api


@pytest.fixture(scope="session", autouse=True)
def client(request):
    def fn():
        Base.metadata.drop_all(bind=engine)

    request.addfinalizer(fn)
    return TestClient(api)


def auth():
    client = TestClient(api)
    r = client.post(
        "/token", data=dict(username="demo", password="demo", grant_type="password")
    )
    return r.json()["access_token"]
