from Scraper.bestjobs_v3 import database_connect
from Utils.LLM import LLM_activation
import json
from groq import RateLimitError

from Utils.email_log_sender import sender


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
    data = LLM_activation(prompt, description)
    return data


FAILED_SENTINEL = '["__EXTRACTION_FAILED__"]'
REQUIRED_KEYS = {"required_skills"}  # add "nice_to_have_skills" here if you keep it


def populate_skills(limit=90):
    cursor, conn = database_connect()

    cursor.execute("SELECT COUNT(*) FROM Jobs WHERE description IS NOT NULL")
    total_eligible = cursor.fetchone()[0]

    # 2. Already processed globally before this run
    cursor.execute(
        "SELECT COUNT(*) FROM Jobs "
        "WHERE description IS NOT NULL AND required_skills IS NOT NULL"
    )
    already_populated = cursor.fetchone()[0]

    cursor.execute(
        "SELECT slug, description FROM Jobs "
        "WHERE description IS NOT NULL AND required_skills IS NULL "
        "LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()

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
                cursor.execute(
                    "UPDATE Jobs SET required_skills = ? WHERE slug = ?",
                    (FAILED_SENTINEL, slug)
                )
                conn.commit()
                stats["malformed_json"] += 1
                continue
            except Exception as e:
                print(f"Extraction failed for {slug}, skipping. {e}")
                stats["other_errors"] += 1
                continue

            cursor.execute(
                "UPDATE Jobs SET required_skills = ? WHERE slug = ?",
                (skills_json, slug)
            )
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

    #print(body)
    return stats["processed"]

if __name__ == "__main__":
    populate_skills(limit=90)