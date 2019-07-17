from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_204_NO_CONTENT

from app.models import Statistics, AuthorizableAttribute

router = APIRouter()


@router.get(
    "/",
    tags=["Statistics"],
    summary="Get an aggregated view of optional info values, for issued credentials",
)
def index():
    return Statistics.aggregate()


@router.get(
    "/{authorizable_attribute_id}",
    summary="Get an aggregated view of optional info values, for an Authorizable Attribute",
    tags=["Statistics"],
)
def get_authorizable_attribute_stats(authorizable_attribute_id):
    aa = AuthorizableAttribute.by_aa_id(authorizable_attribute_id)
    if not aa:
        raise HTTPException(
            status_code=HTTP_204_NO_CONTENT, detail="Authorizable Attribute Not Found"
        )

    return Statistics.by_aa(aa)
