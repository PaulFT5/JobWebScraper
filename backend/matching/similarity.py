"""Similarity between grounded skills.

Both sides (job requirements and CV skills) are lists of MatchResult dicts,
the format stored in Jobs.grounded_skills and produced by asdict(ground(skill)).
"""


def cell(job_entry, cv_entry):
    """1.0 if the two skills are the same, else 0.0.

    Same = same ESCO concept, or (when a concept is missing on either side,
    e.g. unresolved or ambiguous) the same normalized key.
    """
    job_concept, cv_concept = job_entry.get("concept"), cv_entry.get("concept")
    if job_concept and job_concept == cv_concept:
        return 1.0

    job_key, cv_key = job_entry.get("simplified_key"), cv_entry.get("simplified_key")
    if job_key and job_key == cv_key:
        return 1.0

    return 0.0


def build_matrix(job_entries, cv_entries):
    """Rows = job requirements, columns = CV skills; values from cell()."""
    return [[cell(job, cv) for cv in cv_entries] for job in job_entries]
