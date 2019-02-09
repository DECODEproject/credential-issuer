from fastapi import FastAPI

from app.config.config import BaseConfig

config = BaseConfig()
conf = config.values
log = config.logger

api = FastAPI(title="DDDC Credential Issuer",
              description="Credential Issuer for DDDC project",
              version="0.1.0")


@api.get("/")
def root():
    log.info(conf['main']['keypath'])
    return {"message": "Hello World", "config": conf['main']['keypath']}
