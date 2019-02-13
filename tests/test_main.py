import json
from os import environ
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from app.config.config import BaseConfig
from app.main import api, generate_secret_key, load_keypair


def auth():
    client = TestClient(api)
    r = client.post(
        "/token", data=dict(username="demo", password="demo", grant_type="password")
    )
    return json.loads(r.content)["access_token"]


def test_home():
    client = TestClient(api)
    r = client.get("/")
    assert r.status_code == 200


def test_token():
    client = TestClient(api)
    r = client.post(
        "/token", data=dict(username="demo", password="demo", grant_type="password")
    )
    result = json.loads(r.content)
    assert result["access_token"], result
    assert result["token_type"] == "bearer"


def test_wrong_auth():
    client = TestClient(api)
    r = client.post(
        "/token", data=dict(username="fake", password="fake", grant_type="password")
    )
    assert r.status_code == 400


def test_verification_key():
    token = auth()
    client = TestClient(api)
    r = client.get("/verification_key", headers={"Authorization": "Bearer %s" % token})
    result = json.loads(r.content)
    assert r.status_code == 200
    assert result["ci_unique_id"]["verify"]
    assert result["ci_unique_id"]["verify"]["alpha"]
    assert result["ci_unique_id"]["verify"]["g2"]
    assert result["ci_unique_id"]["verify"]["beta"]


def test_generate_secret_key():
    key = json.loads(generate_secret_key())
    keys = ["encoding", "zenroom", "sign", "schema", "curve"]
    for _ in keys:
        assert key["ci_unique_id"][_]


@pytest.fixture(scope="function")
def remove_secret():
    environ[
        "DDDC_CREDENTIAL_ISSUER_CONFIGFILE"
    ] = "/home/travis/build/DECODEproject/dddc-credential-issuer/app/test.ini"
    bc = BaseConfig()
    secret = Path(bc.get("keypair"))
    if secret.is_file():
        secret.unlink()


def test_secret_key_creation(remove_secret):
    c = BaseConfig()
    assert not Path(c.get("keypair")).is_file()
    load_keypair()
    assert Path(c.get("keypair")).is_file()
