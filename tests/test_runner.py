"""A2 runner end-to-end with all HTTP/SMTP/sleep mocked."""
import asyncio
from unittest import mock
from bs4 import BeautifulSoup
from common import WORK, real_db_copy, summary, fixture_db, q, check, RESULTS
import backend.scraper.bestjobs.runner as runner
import backend.scraper.bestjobs.scraper as scraper
import backend.database.connection as connection

DETAIL_HTML = ('<div class="ml-2"><a>Junior level</a></div>'
               '<div class="mt-8 pt-8 border-t border-input break-words prose job-description text-sm">'
               '<p>Desc for {slug}</p><ul><li>Python</li></ul></div>')


class Resp:
    def __init__(self, data): self._d = data; self.ok = True
    def json(self): return self._d


class Raw:
    """A listing response whose JSON body is given verbatim (or whose .json() raises)."""
    def __init__(self, payload=None, error=None): self._p = payload; self._e = error; self.ok = True
    def json(self):
        if self._e:
            raise self._e
        return self._p


def item(slug, **drop):
    d = {"slug": slug, "title": "T " + slug, "companyName": "C", "salary": None, "estimatedSalary": None}
    for k in drop: d.pop(k, None)
    return d


def run(listings, initial, detail_fail=()):
    """listings: list of item-lists or None (failed). Returns (db, calls, mails, conn_ref)."""
    db = fixture_db("fx_runner.sqlite", initial)
    urls = [(f"https://www.bestjobs.eu/api/proxy/v2/jobs?L={i}", "IT", 9, "timisoara", "Full time", 1)
            for i in range(len(listings))]
    calls, mails, conns = [], [], []

    def fake_get(url, timeout=10):
        calls.append(url)
        if "api/proxy" in url:
            items = listings[int(url.split("L=")[1])]
            if items is None:
                return None, None
            if isinstance(items, Raw):
                return items, "soup"
            return Resp({"items": items}), "soup"
        slug = url.rsplit("/", 1)[1]
        if slug in detail_fail:
            return None, None
        return Resp(None), BeautifulSoup(DETAIL_HTML.format(slug=slug), "html.parser")

    real_connect = connection.database_connect

    def spy_connect():
        cur, conn = real_connect(); conns.append(conn); return cur, conn

    with mock.patch.object(runner, "generate_urls", lambda: urls), \
         mock.patch.object(runner, "sender", lambda s, b: mails.append(b)), \
         mock.patch.object(runner, "database_connect", spy_connect), \
         mock.patch.object(scraper, "get_response", fake_get), \
         mock.patch.object(scraper.time, "sleep", lambda s: None):
        asyncio.run(runner.runner())
    return db, calls, mails, conns


def avail(db):
    return {s for (s,) in q(db, "SELECT slug FROM Jobs WHERE available=1")}


INIT = [("old_avail", 1, "d"), ("old_gone", 1, "d"), ("old_expired", 0, "d"), ("old_expired_gone", 0, "d")]

# a) normal run
db, calls, mails, _ = run([[item("old_avail"), item("new1")], [item("old_expired"), item("new2")]], INIT)
details = [c for c in calls if "api/proxy" not in c]
descs = dict(q(db, "SELECT slug, description FROM Jobs"))
check("A2", "a) availability == seen slugs", avail(db) == {"old_avail", "old_expired", "new1", "new2"}, sorted(avail(db)))
check("A2", "a) only new slugs detail-fetched", sorted(d.rsplit('/', 1)[1] for d in details) == ["new1", "new2"], f"{len(details)} detail calls")
check("A2", "a) new rows have descriptions", all(descs[s] and "Desc for" in descs[s] for s in ("new1", "new2")), "new1/new2 described")
check("A2", "a) e-mail totals", "New jobs found:        2" in mails[0] and "Detail pages fetched:  2" in mails[0]
      and "Availability updated:  yes" in mails[0] and "Listings failed:       0" in mails[0], "new=2 fetched=2 updated=yes")

# b) one listing fails
db, calls, mails, _ = run([[item("old_avail"), item("new1")], None], INIT)
check("A2", "b) failed listing -> availability unchanged", avail(db) == {"old_avail", "old_gone", "new1"},
      f"avail={sorted(avail(db))} (new1 inserted available=1 by INSERT)")
check("A2", "b) new job inserted + described", q(db, "SELECT description IS NOT NULL FROM Jobs WHERE slug='new1'") == [(1,)], "new1 present")
check("A2", "b) e-mail says not updated", "Availability updated:  no" in mails[0] and "Listings failed:       1" in mails[0], "updated=no, failed=1")

# c) A7: a listing item with a missing field must not abort the run
db, calls, mails, _ = run([[item("new1")], [item("new2"), item("bad", title=1)], [item("new3")]], INIT)
slugs = {s for (s,) in q(db, "SELECT slug FROM Jobs")}
check("A7", "c) bad item does not abort the run", {"new1", "new2", "new3"} <= slugs,
      f"new1/new2/new3 inserted={sorted(slugs & {'new1', 'new2', 'new3'})}")
check("A7", "c) availability updated normally", avail(db) >= {"new1", "new2", "new3"} and "updated:  yes" in mails[0],
      f"available={sorted(avail(db))}")
check("A7", "c) e-mail sent", len(mails) == 1, f"mails={len(mails)}")
bad_inserted = "bad" in slugs
bad_fetched = any(c.endswith("/bad") for c in calls)
check("NEW-1", "c) item missing an optional field: inserted, or at least not detail-fetched",
      bad_inserted or not bad_fetched,
      f"bad inserted={bad_inserted}; detail page fetched={bad_fetched}; counted as new="
      f"{mails[0].split('found:')[1].split()[0]} (expected 3 if skipped, 4 if inserted)")

# A7: malformed listing responses count as failed listings, never crash the run
import requests
bad_bodies = {
    "non-JSON body (HTML block page with 200)": Raw(error=requests.exceptions.JSONDecodeError("Expecting value", "<html>", 0)),
    "JSON without 'items'": Raw({"data": []}),
    "'items' is not a list": Raw({"items": {"slug": "x"}}),
    "top-level JSON is a list": Raw([{"slug": "x"}]),
}
for label, body in bad_bodies.items():
    db, calls, mails, _ = run([[item("new1")], body, [item("new3")]], INIT)
    slugs = {s for (s,) in q(db, "SELECT slug FROM Jobs")}
    failed = mails[0].split("Listings failed:")[1].split()[0] if mails else "?"
    check("A7", f"{label} -> failed listing, run continues",
          bool(mails) and failed == "1" and {"new1", "new3"} <= slugs and "updated:  no" in mails[0],
          f"listings failed={failed}; new1/new3 inserted={sorted(slugs & {'new1', 'new3'})}; e-mail sent={bool(mails)}")

db, calls, mails, _ = run([[item("new1"), None, "junk", item("new2")]], INIT)
slugs = {s for (s,) in q(db, "SELECT slug FROM Jobs")}
check("A7", "non-dict items (None / string) skipped, rest inserted", {"new1", "new2"} <= slugs and bool(mails),
      f"inserted={sorted(slugs & {'new1', 'new2'})}")

# d) empty listing vs failed
db, calls, mails, _ = run([[item("old_avail")], []], INIT)
check("A2", "d) empty listing does not block update", avail(db) == {"old_avail"} and "updated:  yes" in mails[0], sorted(avail(db)))
db, calls, mails, _ = run([[], [], []], INIT)
check("T1", "d2) ALL listings empty (e.g. 200 with items=[]) wipes availability", len(avail(db)) != 0,
      f"available after run={len(avail(db))} of {len(INIT)} rows; e-mail updated={'yes' if 'updated:  yes' in mails[0] else 'no'}")

# e) same slug in two listings
db, calls, mails, _ = run([[item("dup")], [item("dup")]], INIT)
n = q(db, "SELECT COUNT(*) FROM Jobs WHERE slug='dup'")[0][0]
details = [c for c in calls if c.endswith('/dup')]
check("A2", "e) duplicate slug inserted once, counted once", n == 1 and "New jobs found:        1" in mails[0] and len(details) == 1,
      f"rows={n}, detail fetches={len(details)}, new_jobs line={mails[0].splitlines()[0]}")

# f) connection left open?
db, calls, mails, conns = run([[item("x")]], INIT)
try:
    conns[0].execute("SELECT 1"); closed = False
except Exception as e:
    closed = True; err = str(e)
check("A2", "f) connection closed after runner", closed, "conn.close() in finally on disk -> " + (err if closed else "still open"))

# g) exactly 200 items while 250 exist
init = [(f"s{i}", 1, "d") for i in range(250)]
db, calls, mails, _ = run([[item(f"s{i}") for i in range(200)]], init)
check("T2", "g) 200-item truncation", len(avail(db)) == 250,
      f"250 live jobs, API returns 200 -> available after run={len(avail(db))}; {250-len(avail(db))} still-live jobs hidden")

import json; json.dump(RESULTS, open(WORK / "res_runner.json", "w"))

raise SystemExit(summary())
