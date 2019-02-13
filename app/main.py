import json
from datetime import timedelta, datetime
from pathlib import Path

import jwt
from fastapi import FastAPI, Security, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.exceptions import HTTPException

from app.config.config import BaseConfig
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


@api.post("/token")
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
    return {"access_token": access_token, "token_type": "bearer"}


@api.get("/verification_key")
def verification_key(token: str = Security(oauth2_scheme)):
    log.debug(token)
    secret = load_keypair()
    contract = ZenContract(CONTRACTS.PUBLIC_VERIFY)
    contract.keys(secret)
    return json.loads(contract.execute())


@api.get("/")
def root():
    return {"message": "Hello World", "config": config.get("keypair")}
