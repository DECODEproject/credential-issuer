import json
from datetime import timedelta, datetime
from pathlib import Path

import jwt
from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from app.config.config import BaseConfig
from app.schema import TokenOutput
from app.zencontract import ZenContract, CONTRACTS

router = APIRouter()
config = BaseConfig()
log = config.logger


def load_keypair():
    keypair = Path(config.get("keypair"))
    if not keypair.is_file():
        log.info("CREATING KEYPAIR IN %s" % keypair.as_posix())
        keypair.touch()
        keypair.write_text(
            ZenContract(
                CONTRACTS.GENERATE_KEYPAIR, {"issuer_identifier": config.get("uid")}
            ).execute()
        )

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
    secret = keypair[config.get("uid")]["sign"]["x"]
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=config.get("ALGORITHM"))
    return encoded_jwt


@router.post(
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
