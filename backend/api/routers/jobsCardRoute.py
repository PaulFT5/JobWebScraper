from fastapi import APIRouter, Query
from backend.api.schemas.jobsCardSchema import JobSchema
from backend.database.repositories.jobCardsRepository import get_jobs_card_details

router = APIRouter(prefix="/jobs", tags=["Filters"])

@router.get("", response_model=list[JobSchema])
def get_job_cards(
    domains: list[int] = Query(default=[]),
    work_types: list[int] = Query(default=[]),
    cities: list[str] = Query(default=[]),
):
    return get_jobs_card_details(domains, work_types, cities)