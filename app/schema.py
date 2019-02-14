from typing import List

from pydantic import BaseModel


class TokenOutput(BaseModel):
    access_token: str
    token_type: str


class AuthorizableAttributeSchema(BaseModel):
    authorizable_attribute_id: str
    authorizable_attribute_info: List[dict]


class AuthorizableAttributeOutput(BaseModel):
    authorizable_attribute_id: str
    authorizable_attribute_info: str
    aaid: int


class VerifyOutput(BaseModel):
    g2: str
    beta: str
    alpha: str


class VerificationOutput(BaseModel):
    verify: VerifyOutput


class VerificationKeyOutput(BaseModel):
    ci_unique_id: VerificationOutput


class ValidateAuthorizableAttributeInfoOutput(BaseModel):
    pass


class UidOutput(BaseModel):
    credential_issuer_id: str
