from typing import List

from pydantic import BaseModel


class TokenOutput(BaseModel):
    access_token: str
    token_type: str


class AuthorizableAttributeInfo(BaseModel):
    name: str
    type: str
    valid_values: List[str]


class AuthorizableAttributeSchema(BaseModel):
    authorizable_attribute_id: str
    authorizable_attribute_info: List[
        AuthorizableAttributeInfo
    ]  # AuthorizableAttributeInfo


class AuthorizableAttributeOutput(BaseModel):
    authorizable_attribute_id: str
    authorizable_attribute_info: str
    aaid: int


class VerifyOutput(BaseModel):
    beta: str
    alpha: str


class VerificationOutput(BaseModel):
    verify: VerifyOutput


class VerificationKeyOutput(BaseModel):
    issuer_identifier: VerificationOutput


class AuthorizableAttributeInfoValue(BaseModel):
    name: str
    value: str


class C(BaseModel):
    b: str
    a: str


class π_s(BaseModel):
    c: str
    rk: str
    rr: str
    rm: str


class RequestInput(BaseModel):
    pi_s: π_s
    c: C
    cm: str
    encoding: str
    public: str
    curve: str
    zenroom: str


class BlindSignatureInput(BaseModel):
    request: RequestInput


class ValidateAuthorizableAttributeInfoInput(BaseModel):
    authorizable_attribute_id: str
    values: List[AuthorizableAttributeInfoValue]
    blind_sign_request: RequestInput


class UidOutput(BaseModel):
    credential_issuer_id: str
