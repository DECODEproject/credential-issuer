import json
from datetime import timedelta, datetime
from pathlib import Path

import jwt
from fastapi import FastAPI, Security, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.exceptions import HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.config.config import BaseConfig
from app.database import DB
from app.models import AuthorizableAttribute
from app.schema import (
    TokenOutput,
    AuthorizableAttributeOutput,
    VerificationKeyOutput,
    UidOutput,
    AuthorizableAttributeSchema,
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
    secret = keypair["ci_unique_id"]["sign"]["x"]
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
    aa = AuthorizableAttribute(
        authorizable_attribute_id=item.authorizable_attribute_id,
        authorizable_attribute_info=json.dumps(item.authorizable_attribute_info),
    )
    DB.add(aa)
    DB.commit()
    return {"credential_issuer_id": config.get("uid")}


@api.get(
    "/authorizable_attribute/{authorizable_attribute_id}",
    response_model=AuthorizableAttributeOutput,
)
def get_authorizable_attribute(
    authorizable_attribute_id, token: str = Security(oauth2_scheme)
):
    aa = AuthorizableAttribute.by_aa_id(authorizable_attribute_id)
    if not aa:
        raise HTTPException(
            status_code=HTTP_204_NO_CONTENT, detail="Authorizable Attribute Not Found"
        )
    return aa


@api.get("/verification_key", response_model=VerificationKeyOutput)
def verification_key(token: str = Security(oauth2_scheme)):
    secret = load_keypair()
    contract = ZenContract(CONTRACTS.PUBLIC_VERIFY)
    contract.keys(secret)
    return json.loads(contract.execute())


@api.get("/uid", response_model=UidOutput)
def uid(token: str = Security(oauth2_scheme)):
    return {"credential_issuer_id": config.get("uid")}


# @api.get(
#     "/validate_attribute_info"
# )  # , response_model=ValidateAuthorizableAttributeInfoOutput)
# def validate_attribute_info(authorizable_attributes_ids: str, authorized_values: str, token: str = Security(oauth2_scheme)):
#     # data = authorizable_attribute_info
#     # # do the magic, for the moment return TRUE no matter what, most likely it will be something like:
#     # if type(data) != dict:
#     #       raise TypeError('Data passed has invalid type')
#     # bool_vals = []
#     # for k in compulsory_items:
#     #     set_to_check = dict_of_authorized_values.get(k,set()) # dict_of_autorized_values is a dictionary of 'str':set() pairs
#     #     bool_val = data.get(k,None) in set_to_check
#     #     bool_vals.append(bool_val)
#     # return all(bool_vals)
#     return 1


@api.get("/test")
def test():
    return "OK"
