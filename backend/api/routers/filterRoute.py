from fastapi import APIRouter
from backend.api.schemas.filterSchema import FilterResponse
from backend.services.filter_service import get_bestjobs_filters

router = APIRouter(prefix="/filters", tags=["Filters"])

@router.get("", response_model=FilterResponse)
def get_filters():
    data = get_bestjobs_filters()
    return data