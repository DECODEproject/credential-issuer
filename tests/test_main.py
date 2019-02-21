import json
import random
import string
from os import environ
from pathlib import Path

import pytest
from starlette.status import HTTP_204_NO_CONTENT, HTTP_412_PRECONDITION_FAILED
from starlette.testclient import TestClient

from app.config.config import BaseConfig
from app.database import engine
from app.main import api, generate_secret_key, load_keypair
from app.models import AuthorizableAttribute, init_models


def auth():
    client = TestClient(api)
    r = client.post(
        "/token", data=dict(username="demo", password="demo", grant_type="password")
    )
    return r.json()["access_token"]


def test_call():
    client = TestClient(api)
    r = client.get("/test")
    assert r.status_code == 200
    assert r.content.decode() == '"OK"'


def test_token():
    client = TestClient(api)
    r = client.post(
        "/token", data=dict(username="demo", password="demo", grant_type="password")
    )
    assert r.json()["access_token"]
    assert r.json()["token_type"] == "bearer"


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


def test_uid():
    client = TestClient(api)
    config = BaseConfig()
    r = client.get("/uid", headers={"Authorization": "Bearer %s" % auth()})
    assert r.json()["credential_issuer_id"]
    assert r.json()["credential_issuer_id"] == config.get("uid")


def test_authorizable_attribute():
    init_models(engine)
    client = TestClient(api)
    aaid = "".join(random.choice(string.ascii_lowercase) for i in range(10))
    r = client.post(
        "/authorizable_attribute",
        json={
            "authorizable_attribute_id": aaid,
            "authorizable_attribute_info": [{"super_long_key": "miao"}],
        },
        headers={"Authorization": "Bearer %s" % auth()},
    )
    attrib = AuthorizableAttribute.by_aa_id(aaid)
    assert attrib
    assert attrib.authorizable_attribute_id == aaid
    assert r.json()["credential_issuer_id"] == "Credential Issuer 01"
    assert "super_long_key" in attrib.authorizable_attribute_info


def test_get_authorizable_attribute():
    init_models(engine)
    client = TestClient(api)
    aaid = "".join(random.choice(string.ascii_lowercase) for i in range(10))
    client.post(
        "/authorizable_attribute",
        json={
            "authorizable_attribute_id": aaid,
            "authorizable_attribute_info": [{"super_long_key": "miao"}],
        },
        headers={"Authorization": "Bearer %s" % auth()},
    )
    r = client.get(
        "/authorizable_attribute/%s" % aaid,
        headers={"Authorization": "Bearer %s" % auth()},
    )
    assert r.json()["authorizable_attribute_id"] == aaid


def test_fake_get_authorizable_attribute():
    aaid = "".join(random.choice(string.ascii_lowercase) for i in range(10))
    client = TestClient(api)
    r = client.get(
        "/authorizable_attribute/%s" % aaid,
        headers={"Authorization": "Bearer %s" % auth()},
    )
    assert r.status_code == HTTP_204_NO_CONTENT


# validate_attribute_info
def test_validate_attribute_info():
    init_models(engine)
    client = TestClient(api)
    aaid = "".join(random.choice(string.ascii_letters) for i in range(10))
    client.post(
        "/authorizable_attribute",
        json={
            "authorizable_attribute_id": aaid,
            "authorizable_attribute_info": [{"one": "value"}, {"two": "value"}],
        },
        headers={"Authorization": "Bearer %s" % auth()},
    )

    r = client.post(
        "/validate_attribute_info",
        json={"authorizable_attribute_id": aaid, "values": [{"one": "value"}]},
    )

    assert r.json() is True


def test_non_validate_attribute_info():
    init_models(engine)
    client = TestClient(api)
    aaid = "".join(random.choice(string.ascii_lowercase) for i in range(10))
    client.post(
        "/authorizable_attribute",
        json={
            "authorizable_attribute_id": aaid,
            "authorizable_attribute_info": [{"one": "value"}, {"two": "value"}],
        },
        headers={"Authorization": "Bearer %s" % auth()},
    )

    r = client.post(
        "/validate_attribute_info",
        json={"authorizable_attribute_id": aaid, "values": [{"something": "mah"}]},
        headers={"Authorization": "Bearer %s" % auth()},
    )

    assert r.status_code == HTTP_412_PRECONDITION_FAILED
    assert r.json()["detail"] == "Values mismatch not in Authorizable Attribute"
