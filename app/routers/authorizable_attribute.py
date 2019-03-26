import json
import random
import string

from fastapi import APIRouter, Body, Security, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_201_CREATED, HTTP_409_CONFLICT, HTTP_204_NO_CONTENT

from app.config.config import BaseConfig
from app.database import DBSession
from app.models import AuthorizableAttribute
from app.schema import (
    UidOutput,
    AuthorizableAttributeSchema,
    AuthorizableAttributeOutput,
)
from app.zencontract import ZenContract, CONTRACTS

router = APIRouter()
config = BaseConfig()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


@router.post(
    "/",
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
            "authorizable_attribute_info_optional": [
                {
                    "name": "age",
                    "type": "str",
                    "value_set": ["0-18", "18-25", "25-45", ">45"],
                    "k": 2,
                }
            ],
            "reissuable": False,
        },
    ),
    token: str = Security(oauth2_scheme),
):
    info = [_.json() for _ in item.authorizable_attribute_info]
    optional = [_.json() for _ in item.authorizable_attribute_info_optional]
    keypair = ZenContract(CONTRACTS.GENERATE_KEYPAIR).execute()
    contract = ZenContract(CONTRACTS.PUBLIC_VERIFY)
    contract.keys(keypair)
    verification_key = contract.execute()
    aa = AuthorizableAttribute(
        authorizable_attribute_id=item.authorizable_attribute_id,
        authorizable_attribute_info=json.dumps(info),
        authorizable_attribute_info_optional=json.dumps(optional),
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


@router.get(
    "/{authorizable_attribute_id}",
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
