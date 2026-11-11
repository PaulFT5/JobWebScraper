import json
import time
from groq import RateLimitError
from backend.database.connection import database_connect
from backend.database.repositories.jobExtractionRepository import count_jobs_eligible_extraction, count_fully_populated_jobs, \
    get_available_for_extraction, set_failed_sentinel_extraction, set_successful_skill_extraction
from backend.services.llm_service import llm_service
from backend.services.llm_output_validator import validate_job_skills, MalformedJSONError, InvalidShapeError
from backend.services.notifier_service import sender


def skills_extraction(description):
    prompt ="""
    You are a professional recruiter analyzing a job description.
    Extract hard skills mentioned in the text below — concrete, verifiable tools, software, systems, certifications, methodologies, or specialized domain knowledge
    (e.g. Python, SQL, SAP, Google Ads, GDPR compliance, phlebotomy, payroll processing, AutoCAD). Do not include soft skills (e.g. "communication," "teamwork," "leadership") and do not include spoken/written language requirements (e.g. "English", "fluent in German").

    Write every skill in English, even when the job description is in Romanian or another language. Translate generic skills into their usual English term (e.g. "contabilitate primară" -> "bookkeeping", "diagnosticare" -> "medical diagnosis"). Keep product, software, standard and certification names exactly as written (e.g. SAP, AutoCAD, ISO 9001, PCI DSS); do not translate or expand them.

    Each list item must be exactly one skill, written as a short noun phrase. If the text lists several skills together (in brackets, with commas, or joined by "and" or "/"), return each one as its own item. Keep a name as written when it is a single tool, standard or concept (e.g. CI/CD, TCP/IP, SAP S/4HANA). Do not include duties, tasks or degrees.

    Return every extracted skill in a single list called required_skills, regardless of whether the posting marks it as mandatory or optional.

    Return only a JSON object in exactly this shape, with no explanation, no markdown, no code fences:
{
  "required_skills": ["Python", "SQL"]
}

    If no skills are found, return an empty list for required_skills — never omit the key or use null."""
    data = llm_service(prompt, description)
    return data


FAILED_SENTINEL = '["__EXTRACTION_FAILED__"]'


def populate_skills(limit=90):
    cursor, conn = database_connect()

    total_eligible = count_jobs_eligible_extraction(cursor)
    already_populated = count_fully_populated_jobs(cursor)
    rows = get_available_for_extraction(cursor, limit)

    if total_eligible != 0:
        global_progress = round((already_populated / total_eligible) * 100, 2)
    else:
        global_progress = 0

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
                skills = validate_job_skills(raw)
                skills_json = json.dumps(skills)

            except InvalidShapeError as e:
                print(f"Invalid shape for {slug}, marking failed. {e}")
                set_failed_sentinel_extraction(cursor, FAILED_SENTINEL, slug)
                conn.commit()
                stats["invalid_shape"] += 1
                continue

            except RateLimitError as e:
                print(f"Rate limit hit after {stats['processed']} jobs, stopping. {e}")
                stats["rate_limited"] = True
                break
            except MalformedJSONError as e:
                print(f"Malformed JSON for {slug}, marking failed. {e}")

                set_failed_sentinel_extraction(cursor, FAILED_SENTINEL, slug)

                conn.commit()
                stats["malformed_json"] += 1
                continue
            except Exception as e:
                print(f"Extraction failed for {slug}, marking failed. {e}")
                stats["other_errors"] += 1
                set_failed_sentinel_extraction(cursor, FAILED_SENTINEL, slug)
                conn.commit()
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
        f"Invalid shape:         {stats['invalid_shape']}  (marked failed, won't retry)\n"
        f"Other errors:          {stats['other_errors']}  (marked failed, won't retry)\n"
        f"Rate limit hit:        {'yes' if stats['rate_limited'] else 'no'}\n"
        f"Percentage of covered jobs: {stats['global_progress']}%"
    )
    try:
        sender("Daily Skill Extraction Summary", body)
    except Exception as e:
        print(f"WARNING: failed to send summary email: {e}")

    return stats["processed"]

if __name__ == "__main__":
    populate_skills(limit=90)