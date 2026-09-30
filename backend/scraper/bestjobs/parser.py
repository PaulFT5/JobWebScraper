import asyncio
import time
import aiohttp
from backend.database.connection import database_connect
from backend.database.repositories.job_repositories import reset_all_availability
from backend.scraper.bestjobs.scraper import get_experience_level, get_description, json_response, additional_info
from backend.services.notifier_service import sender
from backend.utils.generate_urls import generate_urls


async def parser():
    start = time.time()
    url_list = generate_urls()

    try:
        cursor, conn = database_connect()
    except Exception as e:
        print(f"WARNING: failed to connect to database: {e}")
        return

    totals = {"new_jobs": 0, "fetched_ok": 0, "http_failed": 0, "description_missing": 0}

    try:
        reset_all_availability(cursor, conn)

        for url, domain_name, domain_id, city, work_type_name, work_type_id in url_list:

            slug_list = json_response(url, domain_name, domain_id, city, work_type_name, work_type_id, cursor, conn)
            info_stats = additional_info(slug_list, cursor, conn)
            totals["new_jobs"] += len(slug_list)
            for key in ("fetched_ok", "http_failed", "description_missing"):
                totals[key] += info_stats[key]

    except Exception as e:
        print(f"Error during parser() execution: {e}")
    finally:
        conn.close()

    end = time.time()
    totals["duration_sec"] = int(round(end - start, 2))
    body = (
        f"New jobs found:        {totals['new_jobs']}\n"
        f"Detail pages fetched:  {totals['fetched_ok']}\n"
        f"Detail pages failed:   {totals['http_failed']}  (non-200 response)\n"
        f"Descriptions missing:  {totals['description_missing']}  (page fetched but description not found)\n"
        f"Run duration:          {totals['duration_sec']}s"
    )
    try:
        sender("Weekly Job Extraction Summary", body)
    except Exception as e:
        print(f"WARNING: failed to send summary email: {e}")
    print(body)

    print("Time taken: ", totals["duration_sec"])

if __name__ == "__main__":
    asyncio.run(parser())