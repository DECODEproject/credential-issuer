import json
from pathlib import Path

from fastapi import FastAPI

from app.config.config import BaseConfig
from app.zencontract import ZenContract, CONTRACTS

config = BaseConfig()
log = config.logger

api = FastAPI(
    title="DDDC Credential Issuer",
    description="Credential Issuer for DDDC project",
    version="0.1.0",
)


def _generate_secret_key():
    return ZenContract(CONTRACTS.GENERATE_KEYPAIR).execute()


def _load_keypair():
    keypair = Path(config.get("keypair"))
    if not keypair.is_file():
        log.info("CREATING KEYPAIR IN %s" % keypair.as_posix())
        keypair.touch()
        keypair.write_text(_generate_secret_key())

    if config.get("debug"):  # pragma: no cover
        log.debug("+" * 50)
        log.debug("KEYPAIR IS: \n%s" % keypair.read_text())
        log.debug("+" * 50)

    return keypair.read_text()


@api.get("/verification_key")
def verification_key():
    secret = _load_keypair()
    contract = ZenContract(CONTRACTS.PUBLIC_VERIFY)
    contract.keys(secret)
    return json.loads(contract.execute())


@api.get("/")
def root():
    return {"message": "Hello World", "config": config.get("keypair")}
