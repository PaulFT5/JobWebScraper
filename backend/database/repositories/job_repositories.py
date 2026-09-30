
def check_existing_slug(cursor, conn, slug_check):
    'Check the existence of a slug in the db'
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM Jobs WHERE slug = ?)", (slug_check,)
    )
    result = cursor.fetchone()
    return bool(result[0])

def reset_all_availability(cursor, conn):
    'reset the availability of ALL the jobs'
    cursor.execute(
        "Update Jobs set available = 0 where available = 1"
    )
    conn.commit()