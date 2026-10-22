import asyncio
import time
from backend.database.connection import database_connect
from backend.database.repositories.jobExtractionRepository import reset_all_availability, mark_available
from backend.scraper.bestjobs.scraper import json_response, additional_info
from backend.services.notifier_service import sender
from backend.utils.generate_urls import generate_urls

async def runner():
    start = time.time()
    url_list = generate_urls()

    try:
        cursor, conn = database_connect()
    except Exception as e:
        print(f"WARNING: failed to connect to database: {e}")
        return

    totals = {"new_jobs": 0, "fetched_ok": 0, "http_failed": 0, "description_missing": 0,
              "listings_failed": 0, "availability_updated": False}

    seen_slugs = set()

    try:
        for url, domain_name, domain_id, city, work_type_name, work_type_id in url_list:

            result = json_response(url, domain_name, domain_id, city, work_type_name, work_type_id, cursor, conn)
            if result is None:
                totals["listings_failed"] += 1
                continue

            new_slugs, slug_list = result
            seen_slugs.update(slug_list)

            info_stats = additional_info(new_slugs, cursor, conn)
            totals["new_jobs"] += len(new_slugs)
            for key in ("fetched_ok", "http_failed", "description_missing"):
                totals[key] += info_stats[key]

        # availability is only recomputed after a complete run, in a single commit
        if totals["listings_failed"] == 0:
            reset_all_availability(cursor, conn)
            mark_available(cursor, seen_slugs)
            conn.commit()
            totals["availability_updated"] = True
        else:
            print(f"{totals['listings_failed']} listing(s) failed, availability left unchanged")

    except Exception as e:
        print(f"Error during parser() execution: {e}")
        conn.rollback()
    finally:
        conn.close()

    end = time.time()
    totals["duration_sec"] = int(round(end - start, 2))
    body = (
        f"New jobs found:        {totals['new_jobs']}\n"
        f"Detail pages fetched:  {totals['fetched_ok']}\n"
        f"Detail pages failed:   {totals['http_failed']}  (non-200 response)\n"
        f"Descriptions missing:  {totals['description_missing']}  (page fetched but description not found)\n"
        f"Run duration:          {totals['duration_sec']}s\n"
        f"Listings failed:       {totals['listings_failed']}\n"
        f"Availability updated:  {'yes' if totals['availability_updated'] else 'no'}\n"
    )
    try:
        sender("Weekly Job Extraction Summary", body)
    except Exception as e:
        print(f"WARNING: failed to send summary email: {e}")
    print(body)

    print("Time taken: ", totals["duration_sec"])

if __name__ == "__main__":
    asyncio.run(runner())