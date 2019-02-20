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


class ValidateAuthorizableAttributeInfoInput(BaseModel):
    authorizable_attribute_id: str
    values: List[dict]


class UidOutput(BaseModel):
    credential_issuer_id: str


class C(BaseModel):
    a: str
    b: str


class π_s(BaseModel):
    rk: str
    c: str
    rr: str
    rm: str


class RequestInput(BaseModel):
    cm: str
    public: str
    pi_s: π_s
    c: C


class BlindSignatureInput(BaseModel):
    request: RequestInput
