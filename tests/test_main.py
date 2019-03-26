import json
from os import environ
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from app.config.config import BaseConfig
from app.main import api
from app.routers.security import load_keypair
from app.zencontract import ZenContract, CONTRACTS


def auth():
    client = TestClient(api)
    r = client.post(
        "/token", data=dict(username="demo", password="demo", grant_type="password")
    )
    return r.json()["access_token"]


def test_token(client):
    r = client.post(
        "/token", data=dict(username="demo", password="demo", grant_type="password")
    )
    assert r.json()["access_token"]
    assert r.json()["token_type"] == "bearer"


def test_wrong_auth(client):
    r = client.post(
        "/token", data=dict(username="fake", password="fake", grant_type="password")
    )
    assert r.status_code == 400


def test_generate_secret_key():
    key = json.loads(ZenContract(CONTRACTS.GENERATE_KEYPAIR).execute())
    keys = ["encoding", "zenroom", "sign", "schema", "curve"]
    for _ in keys:
        assert key["issuer_identifier"][_]


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


def test_uid(client):
    config = BaseConfig()
    r = client.get("/uid")
    assert r.json()["credential_issuer_id"]
    assert r.json()["credential_issuer_id"] == config.get("uid")
