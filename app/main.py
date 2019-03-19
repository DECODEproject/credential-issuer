import json
import random
import string
from datetime import timedelta, datetime
from pathlib import Path

import jwt
from fastapi import FastAPI, Security, Depends, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_412_PRECONDITION_FAILED,
    HTTP_409_CONFLICT,
    HTTP_404_NOT_FOUND,
)

from app.config.config import BaseConfig
from app.database import DBSession
from app.models import AuthorizableAttribute, ValidatedCredentials
from app.schema import (
    TokenOutput,
    AuthorizableAttributeOutput,
    UidOutput,
    AuthorizableAttributeSchema,
    ValidateAuthorizableAttributeInfoInput,
)
from app.zencontract import ZenContract, CONTRACTS

config = BaseConfig()
log = config.logger

api = FastAPI(
    title="DDDC Credential Issuer",
    description="Credential Issuer for DDDC project (Authorize => demo:demo)",
    version="0.1.0",
    redoc_url=None,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def generate_secret_key():
    return ZenContract(CONTRACTS.GENERATE_KEYPAIR).execute()


def load_keypair():
    keypair = Path(config.get("keypair"))
    if not keypair.is_file():
        log.info("CREATING KEYPAIR IN %s" % keypair.as_posix())
        keypair.touch()
        keypair.write_text(generate_secret_key())

    if config.getboolean("debug"):  # pragma: no cover
        log.debug("+" * 50)
        log.debug("KEYPAIR IS: \n%s" % keypair.read_text())
        log.debug("+" * 50)

    return keypair.read_text()


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=config.getint("ACCESS_TOKEN_EXPIRE_MINUTES")
        )
    to_encode.update({"exp": expire, "sub": config.get("TOKEN_SUBJECT")})
    keypair = json.loads(load_keypair())
    secret = keypair["issuer_identifier"]["sign"]["x"]
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=config.get("ALGORITHM"))
    return encoded_jwt


@api.post(
    "/token",
    response_model=TokenOutput,
    tags=["API auth"],
    summary="Obtain OAuth2/Bearer token for protected API calls",
)
def token(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    if username != config.get("AUTH_USERNAME") or password != config.get(
        "AUTH_PASSWORD"
    ):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(
        minutes=config.getint("ACCESS_TOKEN_EXPIRE_MINUTES")
    )
    access_token = create_access_token(
        data={"username": form_data.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "uid": config.get("uid"),
    }


@api.post(
    "/authorizable_attribute",
    response_model=UidOutput,
    status_code=HTTP_201_CREATED,
    summary="Create rules definition of an attribute that allows users to obtain a credential",
    response_description="The verification key of the attribute, and the Credential Issuer uniqueId",
    tags=["Credential issuing"],
)
def authorizable_attribute(
    item: AuthorizableAttributeSchema = Body(
        ...,
        example={
            "authorizable_attribute_id": "Authorizable Attribute %s"
            % "".join(random.choice(string.hexdigits) for i in range(10)),
            "authorizable_attribute_info": [
                {
                    "name": "email",
                    "type": "str",
                    "value_set": [
                        "andres@example.com",
                        "jordi@example.com",
                        "pablo@example.com",
                    ],
                },
                {
                    "name": "zip_code",
                    "type": "int",
                    "value_set": ["08001", "08002", "08003", "08004", "08005", "08006"],
                },
            ],
            "reissuable": False,
        },
    ),
    token: str = Security(oauth2_scheme),
):
    info = [_.json() for _ in item.authorizable_attribute_info]
    keypair = generate_secret_key()
    contract = ZenContract(CONTRACTS.PUBLIC_VERIFY)
    contract.keys(keypair)
    verification_key = contract.execute()
    aa = AuthorizableAttribute(
        authorizable_attribute_id=item.authorizable_attribute_id,
        authorizable_attribute_info=json.dumps(info),
        keypair=keypair,
        verification_key=verification_key,
        reissuable=item.reissuable,
    )

    try:
        DBSession.add(aa)
        DBSession.commit()
    except IntegrityError:
        DBSession.rollback()
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail="Duplicate Authorizable Attribute Id"
        )

    return {
        "verification_key": json.loads(verification_key),
        "credential_issuer_id": config.get("uid"),
        "authorizable_attribute_id": aa.authorizable_attribute_id,
    }


@api.get(
    "/authorizable_attribute/{authorizable_attribute_id}",
    summary="Retrieves the ruleset and the verification key of an Authorizable Attribute",
    response_model=AuthorizableAttributeOutput,
    tags=["Credential issuing"],
)
def get_authorizable_attribute(authorizable_attribute_id):
    aa = AuthorizableAttribute.by_aa_id(authorizable_attribute_id)
    if not aa:
        raise HTTPException(
            status_code=HTTP_204_NO_CONTENT, detail="Authorizable Attribute Not Found"
        )
    return aa.publish()


@api.post(
    "/credential",
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
        },
    )
):
    authorizable_attribute_id = item.authorizable_attribute_id
    aa = AuthorizableAttribute.by_aa_id(authorizable_attribute_id)
    if not aa:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Authorizable Attribute not found"
        )

    sent_values = sorted(
        [json.loads(_.json()) for _ in item.values], key=lambda k: k["name"]
    )
    sent_names = [_["name"] for _ in sent_values]

    if not aa.reissuable:
        if ValidatedCredentials.exists(aa.authorizable_attribute_id, sent_values):
            raise HTTPException(
                status_code=HTTP_412_PRECONDITION_FAILED,
                detail="Credential already issued",
            )

    for name in aa.value_names:
        if name not in sent_names:
            raise HTTPException(
                status_code=HTTP_412_PRECONDITION_FAILED,
                detail="Missing mandatory value '%s'" % name,
            )

    for v in sent_values:
        if not aa.value_is_valid(v["name"], v["value"]):
            raise HTTPException(
                status_code=HTTP_412_PRECONDITION_FAILED,
                detail="Values mismatch not in Authorizable Attribute",
            )

    contract = ZenContract(CONTRACTS.BLIND_SIGN)
    contract.keys(aa.keypair)
    contract.data(item.blind_sign_request.json())
    credential_result = contract.execute()
    if not aa.reissuable:
        vc = ValidatedCredentials(
            aaid=aa.authorizable_attribute_id, value=json.dumps(sent_values)
        )
        DBSession.add(vc)
        DBSession.commit()
    return json.loads(credential_result)


@api.get(
    "/uid", summary="The unique identifier of the credential issuer", tags=["Misc"]
)
def uid():
    return {"credential_issuer_id": config.get("uid")}
