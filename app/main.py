import json
from datetime import timedelta, datetime
from pathlib import Path

import jwt
from fastapi import FastAPI, Security, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.exceptions import HTTPException
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_412_PRECONDITION_FAILED,
)

from app.config.config import BaseConfig
from app.database import DBSession
from app.models import AuthorizableAttribute
from app.schema import (
    TokenOutput,
    AuthorizableAttributeOutput,
    VerificationKeyOutput,
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

    if config.get("debug"):  # pragma: no cover
        log.debug("+" * 50)
        log.debug("KEYPAIR IS: \n%s" % keypair.read_text())
        log.debug("+" * 50)

    return keypair.read_text()


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "sub": config.get("TOKEN_SUBJECT")})
    keypair = json.loads(load_keypair())
    secret = keypair["issuer_identifier"]["sign"]["x"]
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=config.get("ALGORITHM"))
    return encoded_jwt


@api.post("/token", response_model=TokenOutput)
def token(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    if username != "demo" or password != "demo":
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
    response_description="The created item",
)
def authorizable_attribute(
    item: AuthorizableAttributeSchema, token: str = Security(oauth2_scheme)
):
    info = [_.json() for _ in item.authorizable_attribute_info]
    aa = AuthorizableAttribute(
        authorizable_attribute_id=item.authorizable_attribute_id,
        authorizable_attribute_info=json.dumps(info),
    )
    DBSession.add(aa)
    DBSession.commit()
    return {"credential_issuer_id": config.get("uid")}


@api.get(
    "/authorizable_attribute/{authorizable_attribute_id}",
    response_model=AuthorizableAttributeOutput,
)
def get_authorizable_attribute(authorizable_attribute_id):
    aa = AuthorizableAttribute.by_aa_id(authorizable_attribute_id)
    if not aa:
        raise HTTPException(
            status_code=HTTP_204_NO_CONTENT, detail="Authorizable Attribute Not Found"
        )
    return aa


@api.post("/validate_attribute_info")
def validate_attribute_info(item: ValidateAuthorizableAttributeInfoInput):
    authorizable_attribute_id = item.authorizable_attribute_id
    aa = AuthorizableAttribute.by_aa_id(authorizable_attribute_id)
    sent_values = [json.loads(_.json()) for _ in item.values]

    for v in sent_values:
        if not aa.value_is_valid(v["name"], v["value"]):
            raise HTTPException(
                status_code=HTTP_412_PRECONDITION_FAILED,
                detail="Values mismatch not in Authorizable Attribute",
            )

    contract = ZenContract(CONTRACTS.BLIND_SIGN)
    contract.keys(load_keypair())
    contract.data(json.dumps(item.blind_sign_request.json()))
    result = contract.execute()
    print(result)
    print(contract.errors())
    return result


@api.get("/verification_key", response_model=VerificationKeyOutput)
def verification_key():
    keypair = json.loads(load_keypair())
    verify = {
        "issuer_identifier": {
            "verify": {
                "alpha": keypair["issuer_identifier"]["verify"]["alpha"],
                "beta": keypair["issuer_identifier"]["verify"]["alpha"],
            }
        }
    }
    return verify


@api.get("/uid", response_model=UidOutput)
def uid():
    return {"credential_issuer_id": config.get("uid")}


@api.get("/test")
def test():
    return "OK"
