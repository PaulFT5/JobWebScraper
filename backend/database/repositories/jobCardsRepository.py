import sqlite3

from backend.database.connection import database_connect, DB_PATH

def get_jobs_card_details(domains=None, work_types=None, cities=None):
    conditions = [
        "available = 1",
        "required_skills IS NOT NULL",
        "required_skills != ''",
        "required_skills != '[]'",
        "required_skills != '[\"__EXTRACTION_FAILED__\"]'",
    ]
    params = []

    if domains:
        conditions.append(f"domain IN ({','.join('?' * len(domains))})")
        for d in domains:
            params.append(str(d))

    if work_types:
        conditions.append(f"work_type IN ({','.join('?' * len(work_types))})")
        for w in work_types:
            params.append(str(w))

    if cities:
        conditions.append(f"city IN ({','.join('?' * len(cities))})")
        for c in cities:
            params.append(c)

    where_clause = " AND ".join(conditions)

    sql = """
        SELECT source, slug, title,
            company_name  AS company,
            salary,
            est_salary    AS estimated_salary,
            worktype_name AS work_type,
            experience_level,
            city,
            domain_name   AS domain,
            required_skills,
            ad_link
            FROM Jobs
        WHERE """ + where_clause

    cursor, conn = database_connect()
    try:
        cursor.row_factory = sqlite3.Row
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()