import json

from fastapi import Body, HTTPException, APIRouter
from starlette.status import HTTP_404_NOT_FOUND, HTTP_412_PRECONDITION_FAILED

from app.database import DBSession
from app.models import AuthorizableAttribute, ValidatedCredentials, Statistics
from app.schema import ValidateAuthorizableAttributeInfoInput
from app.zencontract import ZenContract, CONTRACTS

router = APIRouter()


def __get_aa(authorizable_attribute_id):
    aa = AuthorizableAttribute.by_aa_id(authorizable_attribute_id)
    if not aa:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Authorizable Attribute not found"
        )
    return aa


def __issue_credential(keypair, bsr):
    contract = ZenContract(CONTRACTS.BLIND_SIGN)
    contract.keys(keypair)
    contract.data(bsr)
    return contract.execute()


def __validate_reissuing(aa, received_values):
    if not aa.reissuable:
        if ValidatedCredentials.exists(aa.authorizable_attribute_id, received_values):
            raise HTTPException(
                status_code=HTTP_412_PRECONDITION_FAILED,
                detail="Credential already issued",
            )


def __check_mandatory_info_fields(aa, received_values):
    received_names = [_["name"] for _ in received_values]
    for name in aa.value_names:
        if name not in received_names:
            raise HTTPException(
                status_code=HTTP_412_PRECONDITION_FAILED,
                detail="Missing mandatory value '%s'" % name,
            )


def __check_optional_values(aa, received_optional_values):
    received_names = [json.loads(_.json()) for _ in received_optional_values]
    for name in received_names:
        if name["name"] not in aa.optionals:
            raise HTTPException(
                status_code=HTTP_412_PRECONDITION_FAILED,
                detail=f"Optional value '{name['name']}' is not valid",
            )


def __check_wrong_info_fields(aa, received_values):
    for v in received_values:
        if not aa.value_is_valid(v["name"], v["value"]):
            raise HTTPException(
                status_code=HTTP_412_PRECONDITION_FAILED,
                detail="Values mismatch not in Authorizable Attribute",
            )


@router.post(
    "/",
    tags=["Credential issuing"],
    summary="If the values make the user eligible, the blind sign request is signed and a credential is issued",
)
async def credential(
    item: ValidateAuthorizableAttributeInfoInput = Body(
        ...,
        example={
            "authorizable_attribute_id": "Authorizable Attribute Unique Identifier",
            "blind_sign_request": {
                "request": {
                    "pi_s": {
                        "c": "9fbe906553d2d15959094a42e3863f71f90634a15172d30cf5d5cda555836c1a",
                        "rk": "0cff3b2b8b9e28c63f4902303e4d6ba2c6aac096543098b87ff8fa817be22d61",
                        "rm": "2698c1e293341ca1d28782a34ef74814249b516431aab963fcb31c19a22f41a0",
                        "rr": "32c0c70c0f6a65b58ab8f23742e695743c4e3672f1ca4c92fd30545aab4e5b45",
                    },
                    "zenroom": "0.8.1",
                    "schema": "lambda",
                    "c": {
                        "a": "040b7c7b31f9c81daf812d87999a9f53e5a2e6c9b1a2a3df42db155066d1c22674acc579798d6d544427b23dd77b379b9e3d4556806f9b2bdd940aba61495f9d392011a639f8d75f1f0e68906f0e1a0d61eda3a2a621e4f173b35a6d00a36dd51d",
                        "b": "040acd0a9a4b39409c17ea2cbf73354c9f6bb410e126c25865003dcc356bcec31a81c8696e6dbe4011962f98d316f475a01d76d8b95ddd99dc97ef67119f82ccd6bd5711e5c63af48414a945604d620ac4dbf357cd2b250fc787e98ac754b66805",
                    },
                    "public": "0428f6fd3e9cb1b2a95acce09cc928097f8fe64802b30511d3b18e5fa0f1c50a902c0090b74942070f0fe5e2b84124590b0a45f37507a33ead6cd2f3650f606aea28dbe3506cd0011bddf7657de5d0211582803ea91e67103310d2f2b5c97509d3",
                    "cm": "043a0ddff5a122cd75a4bda44bd220b13d0d05d2b2e751d02a30b92ca148fd5e56fdf7530bf8c0f1071dab4ccb504b49f522f54047cd15fc4b3a5b34a42c702a8e6e4d396d3e60eb88f309530389c903f1d9f0354f44b1de4d4dccdb28705e677f",
                    "encoding": "hex",
                    "curve": "bls383",
                }
            },
            "values": [
                {"name": "zip_code", "value": "08001"},
                {"name": "email", "value": "pablo@example.com"},
            ],
            "optional_values": [{"name": "age", "value": "18-25"}],
        },
    )
):
    aa = __get_aa(item.authorizable_attribute_id)
    received_values = sorted(
        [json.loads(_.json()) for _ in item.values], key=lambda k: k["name"]
    )
    __validate_reissuing(aa, received_values)
    __check_mandatory_info_fields(aa, received_values)
    __check_wrong_info_fields(aa, received_values)
    issued_credential = __issue_credential(aa.keypair, item.blind_sign_request.json())
    if not aa.reissuable:
        vc = ValidatedCredentials(
            aaid=aa.authorizable_attribute_id, value=json.dumps(received_values)
        )
        DBSession.add(vc)

    __check_optional_values(aa, item.optional_values)
    for option in item.optional_values:
        option = json.loads(option.json())
        s = Statistics(
            aaid=aa.authorizable_attribute_id,
            name=option["name"],
            value=option["value"],
        )
        DBSession.add(s)

    DBSession.commit()
    return json.loads(issued_credential)
