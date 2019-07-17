import random
import string

from starlette.status import HTTP_204_NO_CONTENT

from app.models import AuthorizableAttribute
from tests.conftest import auth


def test_authorizable_attribute(client):
    aaid = "".join(random.choice(string.ascii_lowercase) for i in range(10))
    aa_info = [{"name": "super_long_key", "type": "str", "value_set": ["miao"]}]
    aa_info_optional = [
        {
            "name": "super_long_optional_key",
            "type": "str",
            "value_set": ["love"],
            "k": "2",
        }
    ]
    resp = client.post(
        "/authorizable_attribute",
        headers={"Authorization": f"Bearer {auth()}"},
        allow_redirects=False,
    )
    r = client.post(
        resp.headers["location"],
        json={
            "authorizable_attribute_id": aaid,
            "authorizable_attribute_info": aa_info,
            "authorizable_attribute_info_optional": aa_info_optional,
            "reissuable": False,
        },
        headers={"Authorization": "Bearer %s" % auth()},
    )
    assert r.status_code == 201
    attrib = AuthorizableAttribute.by_aa_id(aaid)
    assert attrib is not None
    assert attrib.authorizable_attribute_id == aaid
    assert r.json()["credential_issuer_id"] == "issuer_identifier"
    assert "super_long_key" in attrib.authorizable_attribute_info


def test_aa_duplicate(client):
    aaid = "".join(random.choice(string.ascii_lowercase) for i in range(10))
    aa_info = [{"name": "super_long", "type": "str", "value_set": ["miao"]}]
    aa_optionals = [
        {"name": "super_long_key_opt", "type": "str", "value_set": ["miao"], "k": "1"}
    ]
    resp = client.post(
        "/authorizable_attribute",
        headers={"Authorization": f"Bearer {auth()}"},
        allow_redirects=False,
    )
    r = client.post(
        resp.headers["location"],
        json={
            "authorizable_attribute_id": aaid,
            "authorizable_attribute_info": aa_info,
            "authorizable_attribute_info_optional": aa_optionals,
            "reissuable": False,
        },
        headers={"Authorization": "Bearer %s" % auth()},
    )
    assert r.status_code == 201

    resp = client.post(
        "/authorizable_attribute",
        headers={"Authorization": f"Bearer {auth()}"},
        allow_redirects=False,
    )
    r = client.post(
        resp.headers["location"],
        json={
            "authorizable_attribute_id": aaid,
            "authorizable_attribute_info": aa_info,
            "authorizable_attribute_info_optional": aa_optionals,
            "reissuable": False,
        },
        headers={"Authorization": "Bearer %s" % auth()},
    )

    assert r.status_code == 409
    assert r.json()["detail"] == "Duplicate Authorizable Attribute Id"


def test_get_authorizable_attribute(client):
    aaid = "".join(random.choice(string.ascii_lowercase) for i in range(10))
    resp = client.post(
        "/authorizable_attribute",
        headers={"Authorization": f"Bearer {auth()}"},
        allow_redirects=False,
    )
    r = client.post(
        resp.headers["location"],
        json={
            "authorizable_attribute_id": aaid,
            "authorizable_attribute_info_optional": [],
            "authorizable_attribute_info": [
                {"name": "super_long_key", "type": "str", "value_set": ["miao"]}
            ],
            "reissuable": False,
        },
        headers={"Authorization": "Bearer %s" % auth()},
    )
    r = client.get(
        "/authorizable_attribute/%s" % aaid,
        headers={"Authorization": "Bearer %s" % auth()},
    )
    assert r.json() is not None
    assert r.json()["authorizable_attribute_id"] == aaid


def test_fake_get_authorizable_attribute(client):
    aaid = "".join(random.choice(string.ascii_lowercase) for i in range(10))
    r = client.get(
        "/authorizable_attribute/%s" % aaid,
        headers={"Authorization": "Bearer %s" % auth()},
    )
    assert r.status_code == HTTP_204_NO_CONTENT
