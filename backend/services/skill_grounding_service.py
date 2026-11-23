import json
import time
from collections import Counter
from dataclasses import asdict

from backend.database.connection import database_connect
from backend.database.repositories.jobGroundingRepository import get_available_jobs_grounding, save_job_grounding
from backend.matching.config import get_config
from backend.matching.grounding import ground

COMMIT_EVERY = 100


def populate_grounding():
    start = time.perf_counter()
    fingerprint = get_config()["grounding_fingerprint"]
    cursor, conn = database_connect()

    stats = {"rows": 0, "skipped": 0, "skills": 0}
    statuses = Counter()
    methods = Counter()

    try:
        rows = get_available_jobs_grounding(cursor, fingerprint)

        for i, (slug, required_skills) in enumerate(rows, 1):
            try:
                skills = json.loads(required_skills)
            except json.JSONDecodeError:
                stats["skipped"] += 1
                continue

            results = [asdict(ground(skill)) for skill in skills]
            save_job_grounding(cursor, slug, json.dumps(results), fingerprint)

            stats["rows"] += 1
            stats["skills"] += len(results)
            statuses.update(r["status"] for r in results)
            methods.update(r["method"] for r in results)

            if i % COMMIT_EVERY == 0:
                conn.commit()

        conn.commit()
    finally:
        conn.close()

    seconds = time.perf_counter() - start
    print(f"Fingerprint: {fingerprint}")
    print(f"Rows grounded: {stats['rows']}  skipped: {stats['skipped']}  skills: {stats['skills']}")
    print(f"By status: {dict(statuses)}")
    print(f"By method: {dict(methods)}")
    print(f"Time: {seconds:.1f} s")
    return stats


if __name__ == "__main__":
    populate_grounding()
