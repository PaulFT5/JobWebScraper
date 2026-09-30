import json
import time
from groq import RateLimitError
from backend.database.connection import database_connect
from backend.database.repositories.job_repositories import count_jobs_eligible_extraction, count_fully_populated_jobs, \
    get_available_for_extraction, set_failed_sentinel_extraction, set_successful_skill_extraction
from backend.services.llm_service import llm_service
from backend.services.notifier_service import sender


def skills_extraction(description):
    prompt ="""
    You are a professional recruiter analyzing a job description.
    Extract hard skills mentioned in the text below — concrete, verifiable tools, software, systems, certifications, methodologies, or specialized domain knowledge
    (e.g. Python, SQL, SAP, Google Ads, GDPR compliance, phlebotomy, payroll processing, AutoCAD). Do not include soft skills (e.g. "communication," "teamwork," "leadership") and do not include spoken/written language requirements (e.g. "English", "fluent in German").

    Return every extracted skill in a single list called required_skills, regardless of whether the posting marks it as mandatory or optional.

    Return only a JSON object in exactly this shape, with no explanation, no markdown, no code fences:
{
  "required_skills": ["Python", "SQL"]
}

    If no skills are found, return an empty list for required_skills — never omit the key or use null."""
    data = llm_service(prompt, description)
    return data


FAILED_SENTINEL = '["__EXTRACTION_FAILED__"]'
REQUIRED_KEYS = {"required_skills"}  # add "nice_to_have_skills" here if you keep it


def populate_skills(limit=1):
    cursor, conn = database_connect()

    total_eligible = count_jobs_eligible_extraction(cursor)
    already_populated = count_fully_populated_jobs(cursor)
    rows = get_available_for_extraction(cursor, limit)

    global_progress = round((already_populated / total_eligible) * 100, 2)

    stats = {
        "pending": len(rows),
        "processed": 0,
        "malformed_json": 0,
        "invalid_shape": 0,
        "other_errors": 0,
        "rate_limited": False,
        "global_progress": global_progress,
    }

    try:
        for slug, description in rows:
            time.sleep(20)
            try:
                raw = skills_extraction(description)
                parsed = json.loads(raw)

                if not REQUIRED_KEYS.issubset(parsed.keys()):
                    print(f"Missing expected keys for {slug}, skipping. Got: {list(parsed.keys())}")
                    stats["invalid_shape"] += 1
                    continue

                if not isinstance(parsed["required_skills"], list):
                    print(f"required_skills is not a list for {slug}, skipping. Got: {type(parsed['required_skills'])}")
                    stats["invalid_shape"] += 1
                    continue

                skills_json = json.dumps(parsed["required_skills"])

            except RateLimitError as e:
                print(f"Rate limit hit after {stats['processed']} jobs, stopping. {e}")
                stats["rate_limited"] = True
                break
            except json.JSONDecodeError as e:
                print(f"Malformed JSON for {slug}, marking failed. {e}")

                set_failed_sentinel_extraction(cursor, FAILED_SENTINEL, slug)

                conn.commit()
                stats["malformed_json"] += 1
                continue
            except Exception as e:
                print(f"Extraction failed for {slug}, skipping. {e}")
                stats["other_errors"] += 1
                continue

            set_successful_skill_extraction(cursor, skills_json, slug)
            conn.commit()
            stats["processed"] += 1
    finally:
        conn.close()

    body = (
        f"Pending jobs found:    {stats['pending']}\n"
        f"Successfully processed: {stats['processed']}\n"
        f"Malformed JSON:        {stats['malformed_json']}  (marked failed, won't retry)\n"
        f"Invalid shape:         {stats['invalid_shape']}  (skipped, will retry next run)\n"
        f"Other errors:          {stats['other_errors']}  (skipped, will retry next run)\n"
        f"Rate limit hit:        {'yes' if stats['rate_limited'] else 'no'}\n"
        f"Percentage of covered jobs: {stats['global_progress']}%"
    )
    try:
        sender("Daily Skill Extraction Summary", body)
    except Exception as e:
        print(f"WARNING: failed to send summary email: {e}")

    return stats["processed"]

if __name__ == "__main__":
    populate_skills(limit=1)