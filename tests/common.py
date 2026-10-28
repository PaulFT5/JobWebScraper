"""Shared helpers for the DB tests.

Tests never touch the real DB or backend files: real-DB copies and fixture DBs live in a
temp work dir, and all network/LLM/SMTP/sleep calls are mocked inside the test process.
Convention: a check PASSES when the code behaves as intended, so an open issue shows as FAIL.
"""
import os, shutil, sqlite3, sys, tempfile
from pathlib import Path

sys.dont_write_bytecode = True  # no __pycache__ inside backend/

PROJECT = Path(__file__).resolve().parent.parent
REAL_DB = PROJECT / "data" / "jobs" / "JobsDatabase.sqlite"
WORK = Path(tempfile.gettempdir()) / "jobwebscraper_tests"
WORK.mkdir(exist_ok=True)

sys.path.insert(0, str(PROJECT))
os.chdir(PROJECT)

import backend.database.connection as connection  # noqa: E402

SCHEMA = '''CREATE TABLE "Jobs"(source text, slug text, title text, company_name text, salary TEXT,
 est_salary int, work_type text, description text, logo text, experience_level text, required_skills text,
 ad_link text, available boolean, city TEXT, domain TEXT, domain_name TEXT, worktype_name TEXT, scraped_date TEXT,
 primary key (source, slug))'''

RESULTS = []


def check(id_, name, ok, evidence):
    RESULTS.append((id_, name, "PASS" if ok else "FAIL", evidence))
    print(f"[{'PASS' if ok else 'FAIL'}] {id_} {name}: {evidence}")


def summary():
    failed = [r for r in RESULTS if r[2] == "FAIL"]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} passed")
    return 1 if failed else 0


def real_db_copy(name):
    """Fresh copy of the real DB in the work dir; the real file is only read."""
    dst = WORK / name
    shutil.copy(REAL_DB, dst)
    return dst


def fixture_db(name, rows):
    p = WORK / name
    if p.exists():
        p.unlink()
    c = sqlite3.connect(p)
    c.execute(SCHEMA)
    for slug, available, desc in rows:
        c.execute("INSERT INTO Jobs(source,slug,title,available,description,domain,work_type,city) "
                  "VALUES('bestjobs',?,?,?,?,'9','1','timisoara')", (slug, slug, available, desc))
    c.commit(); c.close()
    connection.DB_PATH = p
    return p


def q(path, sql, args=()):
    c = sqlite3.connect(path)
    try:
        return c.execute(sql, args).fetchall()
    finally:
        c.close()
