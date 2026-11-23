from fastapi import APIRouter, HTTPException, Request
from groq import RateLimitError
from starlette.concurrency import run_in_threadpool

from backend.services.llm_output_validator import InvalidShapeError, MalformedJSONError
from backend.services.matcher_service import match_cv, match_detail

router = APIRouter(prefix="/match", tags=["Match"])

MAX_PDF_BYTES = 10 * 1024 * 1024


@router.post("")
async def upload_cv(request: Request):
    """Body = the raw PDF bytes (Content-Type: application/pdf)."""
    pdf_bytes = await request.body()
    if len(pdf_bytes) > MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="The PDF is larger than 10 MB.")
    if not pdf_bytes.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="The file is not a PDF.")

    try:
        return await run_in_threadpool(match_cv, pdf_bytes)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))
    except RateLimitError:
        raise HTTPException(status_code=429, detail="The CV parser is busy (rate limit). Try again later.")
    except (MalformedJSONError, InvalidShapeError):
        raise HTTPException(status_code=502, detail="The CV could not be read. Try again.")


@router.get("/{session_id}/{source}/{slug}")
def get_match_detail(session_id: str, source: str, slug: str):
    report = match_detail(session_id, source, slug)
    if report is None:
        raise HTTPException(status_code=404, detail="Unknown CV session or job. Upload the CV again.")
    return report
