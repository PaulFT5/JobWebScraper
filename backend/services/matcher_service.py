"""Matcher: score one uploaded CV against every available job; detail for one job.

The grounded CV lives in memory only (session-only rule): it is never written to disk.
"""
import json
import uuid

from backend.cv_parser.parser import parse_cv_pdf
from backend.database.connection import database_connect
from backend.database.repositories.jobGroundingRepository import get_grounded_available_jobs
from backend.matching.cv_grounding import ground_cv
from backend.matching.metrics.chamfer import chamfer
from backend.matching.report import make_report
from backend.matching.similarity import build_matrix
from backend.services.llm_output_validator import MalformedJSONError

MAX_SESSIONS = 50
_sessions = {}  # session id -> {"names": [...], "tiers": [...], "entries": [...]}


def load_jobs():
    cursor, conn = database_connect()
    try:
        return get_grounded_available_jobs(cursor)
    finally:
        conn.close()


def parse_with_retry(pdf_bytes):
    """The LLM sometimes returns an empty reply (token limit); one retry is usually enough."""
    try:
        return parse_cv_pdf(pdf_bytes)
    except MalformedJSONError:
        return parse_cv_pdf(pdf_bytes)


def remember(session):
    while len(_sessions) >= MAX_SESSIONS:
        _sessions.pop(next(iter(_sessions)))  # drop the oldest
    session_id = uuid.uuid4().hex
    _sessions[session_id] = session
    return session_id


def match_cv(pdf_bytes):
    """PDF bytes -> {"session_id", "skills": [{name, tier, status}], "scores": {"source/slug": score}}."""
    cv = parse_with_retry(pdf_bytes)
    names, tiers, entries = ground_cv(cv)
    session_id = remember({"names": names, "tiers": tiers, "entries": entries})

    scores = {}
    for source, slug, _, grounded_skills in load_jobs():
        score, _ = chamfer(build_matrix(json.loads(grounded_skills), entries))
        if score is not None:
            scores[f"{source}/{slug}"] = score

    skills = [
        {"name": name, "tier": tier, "status": entry["status"]}
        for name, tier, entry in zip(names, tiers, entries)
    ]
    return {"session_id": session_id, "skills": skills, "scores": scores}


def match_detail(session_id, source, slug):
    """Report for one job, or None if the session or the job is unknown."""
    session = _sessions.get(session_id)
    if session is None:
        return None

    for job_source, job_slug, required_skills, grounded_skills in load_jobs():
        if job_source == source and job_slug == slug:
            score, best = chamfer(build_matrix(json.loads(grounded_skills), session["entries"]))
            return make_report(json.loads(required_skills), session["names"], score, best)
    return None
