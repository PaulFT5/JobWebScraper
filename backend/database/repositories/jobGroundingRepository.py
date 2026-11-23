FAILED_SENTINEL = '["__EXTRACTION_FAILED__"]'

def get_available_jobs_grounding(cursor, current_fingerprint):
    cursor.execute(
        "SELECT slug, required_skills FROM Jobs "
        "WHERE required_skills IS NOT NULL "
        "AND required_skills NOT IN ('[]', ?) "
        "AND (grounded_skills IS NULL OR grounding_fingerprint != ?)",
        (FAILED_SENTINEL, current_fingerprint),
    )
    return cursor.fetchall()

def save_job_grounding (cursor, slug, grounded_skills, grounding_fingerprint):
    cursor.execute(
        "UPDATE Jobs SET grounded_skills = ?, grounding_fingerprint = ? "
        "WHERE slug = ?",
        (grounded_skills, grounding_fingerprint, slug)
    )