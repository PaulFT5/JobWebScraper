
def check_existing_slug(cursor, slug):
    'Check the existence of a slug in the db'
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM Jobs WHERE slug = ?)", (slug,)
    )
    result = cursor.fetchone()
    return bool(result[0])

def reset_all_availability(cursor, conn):
    'reset the availability of ALL the jobs'
    cursor.execute(
        "Update Jobs set available = 0 where available = 1"
    )
    conn.commit()

def add_description_experience(cursor, experience_level, description, slug):
    'add experience level and description. This is done is the second scraping phase, where I already have the needed job slugs'
    cursor.execute(
        "UPDATE Jobs SET experience_level = ?, description = ? WHERE slug = ?",
        (experience_level, description, slug)
    )
    return cursor.rowcount > 0

def add_new_jobs(cursor, source, slug, title, company_name, salary, est_salary,
                 work_type_id, work_type_name, ad_link, city, domain_id, domain_name):
    cursor.execute(
        "INSERT OR IGNORE INTO Jobs (source, slug, title, company_name, salary, est_salary, "
        "work_type, worktype_name, ad_link, available, city, domain, domain_name) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)",
        (source, slug, title, company_name, salary, est_salary,
         work_type_id, work_type_name, ad_link, city, domain_id, domain_name),
    )

def mark_available(cursor, slug_list):
    cursor.executemany(
        "UPDATE Jobs SET available = 1 WHERE slug = ?",
        [(s,) for s in slug_list],
    )