"""A3/A4 skill extraction (mocked LLM/SMTP/sleep) + API read path on the DB copy."""
import json, shutil, sqlite3, time
from unittest import mock
import httpx
from groq import RateLimitError
from common import WORK, real_db_copy, summary, fixture_db, q, check, RESULTS
import backend.services.skill_extraction_service as svc
import backend.database.connection as connection


N=[0]
def run_extract(rows, replies, limit=90):
    N[0]+=1
    db = fixture_db(f"fx_extract{N[0]}.sqlite", rows)
    mails, it = [], iter(replies)
    def fake_llm(prompt, content):
        r = next(it)
        if isinstance(r, Exception): raise r
        return r
    with mock.patch.object(svc, "llm_service", fake_llm), \
         mock.patch.object(svc, "sender", lambda s, b: mails.append(b)), \
         mock.patch.object(svc.time, "sleep", lambda s: None):
        try:
            ret, err = svc.populate_skills(limit), None
        except Exception as e:
            ret, err = None, f"{type(e).__name__}: {e}"
    return db, ret, err, mails

# A3
db, ret, err, mails = run_extract([("a", 1, None), ("b", 0, None)], [])
check("A3", "no eligible rows: no crash, e-mail sent", err is None and bool(mails), f"{err}; e-mail sent={bool(mails)}")

# A4 invalid shape retried every run
rows = [("s1", 1, "d"), ("s2", 1, "d")]
for run_no in (1, 2):
    if run_no == 1:
        db, ret, err, mails = run_extract(rows, ['{"skills": ["x"]}', '{"required_skills": "Python"}'])
    else:
        # second run on the same DB: re-point and run again
        mails2 = []
        with mock.patch.object(svc, "llm_service", lambda p, c: '{"foo": 1}'), \
             mock.patch.object(svc, "sender", lambda s, b: mails2.append(b)), \
             mock.patch.object(svc.time, "sleep", lambda s: None):
            svc.populate_skills(90)
        mails = mails2
vals = q(db, "SELECT required_skills FROM Jobs")
check("A4", "invalid shape -> marked failed, not re-picked next run",
      all(v[0] == svc.FAILED_SENTINEL for v in vals) and "Pending jobs found:    0" in mails[0],
      f"after 2 runs required_skills={vals}; run 2 mail starts: {mails[0].splitlines()[0]}")
# also: a JSON array / string reply (not an object) -> .keys() AttributeError -> 'other errors'
db, ret, err, mails = run_extract([("s1", 1, "d"), ("s2", 1, "d")], ['["Python"]', '"Python"'])
vals = q(db, "SELECT required_skills FROM Jobs")
check("A4", "non-object JSON reply ([...] / string) -> marked failed", all(v[0] == svc.FAILED_SENTINEL for v in vals),
      f"other_errors={mails[0].split('Other errors:')[1].split()[0]}, rows={vals}")

# malformed JSON -> sentinel; fenced JSON too
db, ret, err, mails = run_extract([("s1", 1, "d"), ("s2", 1, "d"), ("s3", 1, "d")],
                                  ['not json', '```json\n{"required_skills": ["SQL"]}\n```', '{"required_skills": ["Python", "SQL"]}'])
v = dict(q(db, "SELECT slug, required_skills FROM Jobs"))
check("A4", "malformed JSON -> sentinel", v["s1"] == svc.FAILED_SENTINEL, f"s1={v['s1']}")
check("T4", "code-fenced valid JSON keeps its skills", v["s2"] != svc.FAILED_SENTINEL, f"s2={v['s2']}; s3={v['s3']}")

# rate limit stops the run
req = httpx.Request("POST", "https://x"); rsp = httpx.Response(429, request=req)
rl = RateLimitError("429", response=rsp, body=None)
calls = []
db = fixture_db("fx_extract_rl.sqlite", [(f"r{i}", 1, "d") for i in range(5)])
mails = []
def llm(p, c):
    calls.append(1)
    if len(calls) == 3: raise rl
    return '{"required_skills": ["X"]}'
with mock.patch.object(svc, "llm_service", llm), mock.patch.object(svc, "sender", lambda s, b: mails.append(b)), \
     mock.patch.object(svc.time, "sleep", lambda s: None):
    ret = svc.populate_skills(90)
done = q(db, "SELECT COUNT(*) FROM Jobs WHERE required_skills IS NOT NULL")[0][0]
check("A4", "rate limit stops run", len(calls) == 3 and done == 2 and "Rate limit hit:        yes" in mails[0], f"LLM calls={len(calls)}, saved={done}, ret={ret}")
# progress % reported is pre-run
check("T5", "e-mail coverage % reflects this run", False if "Percentage of covered jobs: 0.0%" in mails[0] else True,
      mails[0].splitlines()[-1] + f" although {done}/5 done after run")

# ---------- API read path on DB copy
api_db = real_db_copy("api_copy.sqlite")
connection.DB_PATH = api_db
from backend.database.repositories.jobCardsRepository import get_jobs_card_details
t = time.perf_counter(); allrows = get_jobs_card_details(); ms = (time.perf_counter() - t) * 1000
size = len(json.dumps(allrows).encode())
check("B8", "unfiltered rows / payload", True, f"{len(allrows)} rows, {size/1024:.0f} KB JSON, query {ms:.0f} ms")
bad = [r for r in allrows if r["required_skills"] in (None, "", "[]", svc.FAILED_SENTINEL)]
check("API", "sentinel/empty exclusions", not bad, f"{len(bad)} excluded-kind rows leaked")
exp = q(api_db, "SELECT COUNT(*) FROM Jobs WHERE available=1 AND required_skills NOT IN ('', '[]', ?) ", (svc.FAILED_SENTINEL,))[0][0]
check("API", "row count matches independent query", exp == len(allrows), f"expected {exp}")
f1 = get_jobs_card_details(domains=[9], work_types=[1])
f2 = get_jobs_card_details(domains=[9, 19], work_types=[1, 2], cities=["timisoara"])
f3 = get_jobs_card_details(domains=[13])
check("A5", "int->text domain/work_type filter", len(f1) > 0 and all(r["domain"] == "IT" and r["work_type"] == "Full time" for r in f1),
      f"IT+Full time={len(f1)}; IT/Mgmt+FT/PT+timisoara={len(f2)}; domain 13={len(f3)}")
nulls = {k: sum(1 for r in allrows if r[k] is None) for k in ("title", "company", "experience_level", "salary")}
check("API", "NULLs in card fields (info)", True, f"{nulls}")

try:
    from fastapi.testclient import TestClient
    from backend.api.main import app
    cl = TestClient(app)
    r = cl.get("/api/jobs"); r2 = cl.get("/api/jobs", params={"domains": [9], "work_types": [1]})
    r3 = cl.get("/api/filters"); r4 = cl.get("/api/jobs", params={"domains": ["abc"]})
    check("API", "/api/jobs via TestClient", r.status_code == 200 and len(r.json()) == len(allrows),
          f"200, {len(r.json())} rows, {len(r.content)/1024:.0f} KB; filtered={len(r2.json())}; bad int -> {r4.status_code}")
    check("API", "/api/filters", r3.status_code == 200, f"{r3.status_code}; domains={len(r3.json()['domains'])}, ids are {type(r3.json()['domains'][0]['id']).__name__}")
except Exception as e:
    check("API", "TestClient", False, f"{type(e).__name__}: {e}")
json.dump(RESULTS, open(WORK / "res_extract_api.json", "w"))

raise SystemExit(summary())
