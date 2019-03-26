from fastapi import FastAPI
from app.config.config import BaseConfig
from app.routers import authorizable_attribute, stats, security, credential

config = BaseConfig()

api = FastAPI(
    title="DDDC Credential Issuer",
    description="Credential Issuer for DDDC project (Authorize => demo:demo)",
    version="0.1.0",
    redoc_url=None,
)

api.include_router(security.router)
api.include_router(authorizable_attribute.router, prefix="/authorizable_attribute")
api.include_router(credential.router, prefix="/credential")
api.include_router(stats.router, prefix="/stats")


@api.get(
    "/uid", summary="The unique identifier of the credential issuer", tags=["Misc"]
)
def uid():
    return {"credential_issuer_id": config.get("uid")}
