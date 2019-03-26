from typing import List, Dict

from pydantic import BaseModel, Schema


class TokenOutput(BaseModel):
    access_token: str
    token_type: str


class AuthorizableAttributeInfo(BaseModel):
    name: str
    type: str
    value_set: List[str]


class AuthorizableAttributeInfoOptional(AuthorizableAttributeInfo):
    k: int


class AuthorizableAttributeSchema(BaseModel):
    authorizable_attribute_id: str
    authorizable_attribute_info: List[AuthorizableAttributeInfo]
    authorizable_attribute_info_optional: List[AuthorizableAttributeInfoOptional]
    reissuable: bool


class AuthorizableAttributeOutput(BaseModel):
    authorizable_attribute_id: str
    authorizable_attribute_info: List[Dict]
    verification_key: Dict
    reissuable: bool


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
    scheme: str = Schema(..., alias="schema")


class BlindSignatureInput(BaseModel):
    request: RequestInput


class ValidateAuthorizableAttributeInfoInput(BaseModel):
    authorizable_attribute_id: str
    values: List[AuthorizableAttributeInfoValue]
    blind_sign_request: BlindSignatureInput


class UidOutput(BaseModel):
    verification_key: Dict
    credential_issuer_id: str
    authorizable_attribute_id: str
