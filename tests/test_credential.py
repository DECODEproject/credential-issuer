import json
import random
import string

from starlette.status import HTTP_412_PRECONDITION_FAILED

from app.zencontract import ZenContract, CONTRACTS
from tests.conftest import auth


def test_credential(client):
    aaid = "".join(random.choice(string.ascii_letters) for i in range(10))
    info = [
        dict(value_set=["some val 1", "five", "love"], name="name_1", type="int"),
        dict(value_set=["3"], name="name_2", type="str"),
    ]
    insert = client.post(
        "/authorizable_attribute/",
        json={
            "authorizable_attribute_id": aaid,
            "authorizable_attribute_info": info,
            "authorizable_attribute_info_optional": [],
            "reissuable": False,
        },
        headers={"Authorization": "Bearer %s" % auth()},
    )

    assert insert.status_code == 201
    keys = ZenContract(CONTRACTS.CITIZEN_KEYGEN).execute()
    contract = ZenContract(CONTRACTS.CITIZEN_REQ_BLIND_SIG)
    contract.keys(keys)
    blind_sign_request = contract.execute()
    values = [dict(name="name_1", value="love"), dict(name="name_2", value="3")]

    r = client.post(
        "/credential/",
        json={
            "authorizable_attribute_id": aaid,
            "values": values,
            "optional_values": [],
            "blind_sign_request": json.loads(blind_sign_request),
        },
    )

    assert r.status_code == 200
    assert r.json() is not None


def test_fake_value_attr_credential(client):
    aaid = "".join(random.choice(string.ascii_letters) for i in range(10))
    info = [
        dict(value_set=["some val 1", "five", "love"], name="name_1", type="int"),
        dict(value_set=["3"], name="name_2", type="str"),
    ]
    insert = client.post(
        "/authorizable_attribute/",
        json={
            "authorizable_attribute_id": aaid,
            "authorizable_attribute_info": info,
            "authorizable_attribute_info_optional": [],
            "reissuable": False,
        },
        headers={"Authorization": "Bearer %s" % auth()},
    )

    assert insert.status_code == 201
    keys = ZenContract(CONTRACTS.CITIZEN_KEYGEN).execute()
    contract = ZenContract(CONTRACTS.CITIZEN_REQ_BLIND_SIG)
    contract.keys(keys)
    blind_sign_request = contract.execute()
    values = [dict(name="some_fake_name", value="love"), dict(name="name_2", value="3")]

    r = client.post(
        "/credential/",
        json={
            "authorizable_attribute_id": aaid,
            "values": values,
            "optional_values": [],
            "blind_sign_request": json.loads(blind_sign_request),
        },
    )

    assert r.status_code == 412
    assert r.json()["detail"] == "Missing mandatory value 'name_1'"

    values = [
        dict(name="some_fake_name", value="some_fake_value"),
        dict(name="name_2", value="3"),
    ]

    r = client.post(
        "/credential/",
        json={
            "authorizable_attribute_id": aaid,
            "values": values,
            "optional_values": [],
            "blind_sign_request": json.loads(blind_sign_request),
        },
    )

    assert r.status_code == 412
    assert r.json()["detail"] == "Missing mandatory value 'name_1'"


def test_credential_missing_value(client):
    aaid = "".join(random.choice(string.ascii_letters) for i in range(10))
    info = [
        dict(value_set=["some val 1", "five", "love"], name="name_1", type="int"),
        dict(value_set=["3"], name="name_2", type="str"),
    ]
    insert = client.post(
        "/authorizable_attribute/",
        json={
            "authorizable_attribute_id": aaid,
            "authorizable_attribute_info": info,
            "authorizable_attribute_info_optional": [],
            "reissuable": False,
        },
        headers={"Authorization": "Bearer %s" % auth()},
    )

    assert insert.status_code == 201
    keys = ZenContract(CONTRACTS.CITIZEN_KEYGEN).execute()
    contract = ZenContract(CONTRACTS.CITIZEN_REQ_BLIND_SIG)
    contract.keys(keys)
    blind_sign_request = contract.execute()
    values = [dict(name="name_1", value="love")]

    r = client.post(
        "/credential/",
        json={
            "authorizable_attribute_id": aaid,
            "values": values,
            "optional_values": [],
            "blind_sign_request": json.loads(blind_sign_request),
        },
    )

    assert r.status_code == 412
    assert r.json()["detail"] == "Missing mandatory value 'name_2'"


def test_no_double_issuing_credential(client):
    aaid = "".join(random.choice(string.ascii_letters) for i in range(10))
    info = [
        dict(value_set=["some val 1", "five", "love"], name="name_1", type="int"),
        dict(value_set=["3"], name="name_2", type="str"),
    ]
    insert = client.post(
        "/authorizable_attribute/",
        json={
            "authorizable_attribute_id": aaid,
            "authorizable_attribute_info": info,
            "authorizable_attribute_info_optional": [],
            "reissuable": False,
        },
        headers={"Authorization": "Bearer %s" % auth()},
    )

    assert insert.status_code == 201
    keys = ZenContract(CONTRACTS.CITIZEN_KEYGEN).execute()
    contract = ZenContract(CONTRACTS.CITIZEN_REQ_BLIND_SIG)
    contract.keys(keys)
    blind_sign_request = contract.execute()
    values = [dict(name="name_1", value="love"), dict(name="name_2", value="3")]

    r = client.post(
        "/credential/",
        json={
            "authorizable_attribute_id": aaid,
            "values": values,
            "optional_values": [],
            "blind_sign_request": json.loads(blind_sign_request),
        },
    )

    assert r.status_code == 200
    assert r.json() is not None

    r = client.post(
        "/credential/",
        json={
            "authorizable_attribute_id": aaid,
            "values": values,
            "optional_values": [],
            "blind_sign_request": json.loads(blind_sign_request),
        },
    )

    assert r.status_code == 412
    assert r.json()["detail"] == "Credential already issued"


def test_reissuable_credential(client):
    aaid = "".join(random.choice(string.ascii_letters) for i in range(10))
    info = [
        dict(value_set=["some val 1", "five", "love"], name="name_1", type="int"),
        dict(value_set=["3"], name="name_2", type="str"),
    ]
    insert = client.post(
        "/authorizable_attribute/",
        json={
            "authorizable_attribute_id": aaid,
            "authorizable_attribute_info": info,
            "authorizable_attribute_info_optional": [],
            "reissuable": True,
        },
        headers={"Authorization": "Bearer %s" % auth()},
    )

    assert insert.status_code == 201
    keys = ZenContract(CONTRACTS.CITIZEN_KEYGEN).execute()
    contract = ZenContract(CONTRACTS.CITIZEN_REQ_BLIND_SIG)
    contract.keys(keys)
    blind_sign_request = contract.execute()
    values = [dict(name="name_1", value="love"), dict(name="name_2", value="3")]

    r = client.post(
        "/credential/",
        json={
            "authorizable_attribute_id": aaid,
            "values": values,
            "optional_values": [],
            "blind_sign_request": json.loads(blind_sign_request),
        },
    )

    assert r.status_code == 200
    first_result = r.json()
    assert first_result is not None

    r = client.post(
        "/credential/",
        json={
            "authorizable_attribute_id": aaid,
            "values": values,
            "optional_values": [],
            "blind_sign_request": json.loads(blind_sign_request),
        },
    )

    assert r.status_code == 200
    assert r.json() == first_result


def test_no_found_aa_for_credential(client):
    keys = ZenContract(CONTRACTS.CITIZEN_KEYGEN).execute()
    contract = ZenContract(CONTRACTS.CITIZEN_REQ_BLIND_SIG)
    contract.keys(keys)
    blind_sign_request = contract.execute()
    values = [dict(name="name_1", value="love"), dict(name="name_2", value="3")]

    r = client.post(
        "/credential/",
        json={
            "authorizable_attribute_id": "FAKE ID",
            "values": values,
            "optional_values": [],
            "blind_sign_request": json.loads(blind_sign_request),
        },
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Authorizable Attribute not found"


def test_non_validate_attribute_info(client):
    aaid = "".join(random.choice(string.ascii_lowercase) for i in range(10))
    client.post(
        "/authorizable_attribute/",
        json={
            "authorizable_attribute_id": aaid,
            "authorizable_attribute_info": [
                dict(
                    value_set=["some val 1", "five", "love"], name="name_1", type="int"
                )
            ],
            "authorizable_attribute_info_optional": [],
            "reissuable": False,
        },
        headers={"Authorization": "Bearer %s" % auth()},
    )

    blind_sign_request = {
        "request": {
            "zenroom": "0.8.1",
            "pi_s": {
                "rm": "d277c5eb12a50c6dd9800d00d34f426d9164a9dfa38f93d851405143d01d2193",
                "rk": "69b7c21b8c303fb80570feae9da7cd8bf0b929125053aa39a5e1c61ebc516c7c",
                "c": "e179ede630a325bbbacd3fd483af785bb2b703bab00b4e358fde2b3170781f50",
                "rr": "d3294ee00752c4186fb43a5f88f4f580ec274c0e622142d61af40d30eff296f6",
            },
            "c": {
                "a": "043544f625d514badc41ed744bcbdef4dddf90bed3e32bf27497cfdd6602feb8054be4f2b54ffcbdb134a56df317148ea806c657faeaeb54a74953493aab1542fd55110979592d4f09cab5a5ed608f91b9e65032922b81b9b9afeef7912f38742d",
                "b": "04491e37aa8e0e0c54a4c3b4a766797d1dfc62539de5cb5c86710354d66bb79775c00bf40a7db0fd8684c946105ef80d453ad38885ffd81ebd047faabfcdf62ff6ae815e0e68552bce5a12abedb3bc7b1f67a24694741cede58a0c98414f3bee3e",
            },
            "cm": "0413cd90e1ff111e3dc0ebf3dfe942ce338ee3e9e53ebd6101cece1b5e7a1f536e8cba1a18e1e286f00952560b4d5ef883162ee09ed700ef294b49513671f05caacb7ce39f56ce04ceb2e1b06961f8fb3f8a6c5f0e077908842d85d1c73beaeb33",
            "public": "041421f09217c0725a4a630637470a31e33df2a4b86aa9c92807ca5d0e777ac52e26ca80cda3b61a35b19b628dd7b9b0934f25ceb59b6f950f325e0774a1c972a63e806f23a6dacbdec0750d6cce340e3b752aee9abd42ae5114feaa8b48d6acdb",
            "curve": "bls383",
            "encoding": "hex",
            "schema": "lambda",
        }
    }

    r = client.post(
        "/credential/",
        json={
            "authorizable_attribute_id": aaid,
            "blind_sign_request": blind_sign_request,
            "values": [{"name": "name_1", "value": "miao"}],
            "optional_values": [],
        },
        headers={"Authorization": "Bearer %s" % auth()},
    )

    assert HTTP_412_PRECONDITION_FAILED is r.status_code
    assert r.json()["detail"] == "Values mismatch not in Authorizable Attribute"
