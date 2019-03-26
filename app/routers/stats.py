from fastapi import APIRouter

from app.models import Statistics

router = APIRouter()


@router.get(
    "/",
    tags=["Statistics"],
    summary="Get an aggregated view of optional info values, for issued credentials",
)
def index():
    return Statistics.aggregate()
