"""B1, B2, B12 and data integrity on a copy of the real DB."""
import json, shutil, sqlite3, time
from common import WORK, real_db_copy, summary, check, RESULTS
from backend.database.repositories import jobExtractionRepository as repo

SRC = real_db_copy("copy.sqlite")
NOIDX, IDX = WORK / "b1_noidx.sqlite", WORK / "b1_idx.sqlite"
shutil.copy(SRC, NOIDX); shutil.copy(SRC, IDX)
c = sqlite3.connect(IDX); c.execute("CREATE INDEX idx_jobs_slug ON Jobs(slug)"); c.commit(); c.close()

def plan(conn, sql, args):
    return "; ".join(r[3] for r in conn.execute("EXPLAIN QUERY PLAN " + sql, args))

def timeit(fn, reps=5):
    best = 1e9
    for _ in range(reps):
        t = time.perf_counter(); fn(); best = min(best, time.perf_counter() - t)
    return best * 1000

# ---------- B1
out = {}
for name, path in (("noidx", NOIDX), ("idx", IDX)):
    conn = sqlite3.connect(path); cur = conn.cursor()
    avail = [s for (s,) in cur.execute("SELECT slug FROM Jobs WHERE available=1")]
    sample = avail[:200]
    p_exist = plan(conn, "SELECT EXISTS(SELECT 1 FROM Jobs WHERE slug = ?)", ("x",))
    p_upd = plan(conn, "UPDATE Jobs SET available = 1 WHERE slug = ?", ("x",))
    t_exist = timeit(lambda: [repo.check_existing_slug(cur, s) for s in avail])
    def mark():
        repo.reset_all_availability(cur, conn); repo.mark_available(cur, avail); conn.rollback()
    t_mark = timeit(mark, 3)
    def desc():
        for s in sample: repo.add_description_experience(cur, "Junior", "x", s)
        conn.rollback()
    t_desc = timeit(desc, 3)
    out[name] = dict(n=len(avail), p_exist=p_exist, p_upd=p_upd, exist=t_exist, mark=t_mark, desc200=t_desc)
    conn.close()
print(json.dumps(out, indent=1))
check("B1", "plan without index", "SCAN" in out["noidx"]["p_exist"], out["noidx"]["p_exist"] + " | " + out["noidx"]["p_upd"])
check("B1", "plan with index", "idx_jobs_slug" in out["idx"]["p_exist"], out["idx"]["p_exist"] + " | " + out["idx"]["p_upd"])
check("B1", "timings (best of N)", True,
      f"exists x{out['idx']['n']}: {out['noidx']['exist']:.0f}->{out['idx']['exist']:.1f} ms; "
      f"reset+mark {out['idx']['n']}: {out['noidx']['mark']:.0f}->{out['idx']['mark']:.0f} ms; "
      f"desc update x200: {out['noidx']['desc200']:.0f}->{out['idx']['desc200']:.1f} ms")
sz = (NOIDX.stat().st_size, IDX.stat().st_size)
check("B1", "index size cost", True, f"file {sz[0]/1e6:.2f} MB -> {sz[1]/1e6:.2f} MB")

# ---------- B2: check-then-insert vs INSERT OR IGNORE + rowcount
def listing(conn):
    ex = [s for (s,) in conn.execute("SELECT slug FROM Jobs WHERE available=1")]
    return ex + [f"zz-new-{i}" for i in range(300)] + ex[:50]  # incl. dup inside the run
INS = ("INSERT OR IGNORE INTO Jobs (source, slug, title, available) VALUES ('bestjobs', ?, 't', 1)")
res = {}
for name, path in (("noidx", NOIDX), ("idx", IDX)):
    conn = sqlite3.connect(path); cur = conn.cursor(); L = listing(conn)
    def old():
        new = []
        for s in L:
            if repo.check_existing_slug(cur, s): continue
            new.append(s); cur.execute(INS, (s,))
        conn.rollback(); return new
    def prop():
        new = []
        for s in L:
            cur.execute(INS, (s,))
            if cur.rowcount == 1: new.append(s)
        conn.rollback(); return new
    n_old, n_new = old(), prop()
    res[name] = (n_old == n_new, len(n_old), timeit(old, 3), timeit(prop, 3), len(L))
    conn.close()
check("B2", "same new/existing split", res["noidx"][0] and res["idx"][0], f"{res['idx'][1]} new of {res['idx'][4]} items in both variants")
check("B2", "time saved", True, f"no index: {res['noidx'][2]:.0f}->{res['noidx'][3]:.0f} ms; with slug index: {res['idx'][2]:.1f}->{res['idx'][3]:.1f} ms")

# ---------- B12
conn = sqlite3.connect(SRC)
nxt = conn.execute("SELECT slug FROM Jobs WHERE description IS NOT NULL AND required_skills IS NULL LIMIT 90").fetchall()
un = conn.execute("SELECT COUNT(*) FROM Jobs WHERE slug IN (SELECT slug FROM Jobs WHERE description IS NOT NULL "
                  "AND required_skills IS NULL LIMIT 90) AND COALESCE(available,0)=0").fetchone()[0]
tot = conn.execute("SELECT COALESCE(available,0), COUNT(*) FROM Jobs WHERE description IS NOT NULL AND required_skills IS NULL GROUP BY 1").fetchall()
check("B12", "next 90 picked that are unavailable", un == 0, f"{un}/{len(nxt)} next-batch rows unavailable; pending by available: {dict(tot)}")

# ---------- Data integrity
cfg = json.load(open(r"C:\Users\User\PycharmProjects\JobWebScraper\backend\scraper\bestjobs\config.json", encoding="utf-8"))
bad_json, shapes = 0, {}
for slug, rs in conn.execute("SELECT slug, required_skills FROM Jobs WHERE required_skills IS NOT NULL"):
    try:
        v = json.loads(rs); ok = isinstance(v, list) and all(isinstance(x, str) for x in v)
    except Exception:
        ok = False
    if not ok: bad_json += 1
    shapes[rs if rs in ('[]', '["__EXTRACTION_FAILED__"]', '') else 'list'] = shapes.get(rs if rs in ('[]', '["__EXTRACTION_FAILED__"]', '') else 'list', 0) + 1
check("INT", "required_skills valid JSON string arrays", bad_json == 0, f"invalid={bad_json}; distribution={shapes}")
nodesc = conn.execute("SELECT COUNT(*) FROM Jobs WHERE available=1 AND (description IS NULL OR description='')").fetchone()[0]
check("T7", "available rows without description", nodesc == 0, f"{nodesc}")
dups = conn.execute("SELECT COUNT(*) FROM (SELECT slug FROM Jobs GROUP BY slug HAVING COUNT(*)>1)").fetchone()[0]
srcs = conn.execute("SELECT source, COUNT(*) FROM Jobs GROUP BY source").fetchall()
check("INT", "duplicate slugs across sources", dups == 0, f"dups={dups}; sources={srcs}")
doms = {str(v) for v in cfg["filters"]["domains"].values()}; wts = {str(v) for v in cfg["filters"]["work_types"].values()}
cities = set(cfg["filters"]["cities"])
d_db = conn.execute("SELECT domain, domain_name, COUNT(*), SUM(available) FROM Jobs GROUP BY domain, domain_name").fetchall()
w_db = conn.execute("SELECT work_type, worktype_name, COUNT(*) FROM Jobs GROUP BY work_type, worktype_name").fetchall()
c_db = conn.execute("SELECT city, COUNT(*) FROM Jobs GROUP BY city").fetchall()
bad_d = [r for r in d_db if str(r[0]) not in doms]; bad_w = [r for r in w_db if str(r[0]) not in wts]
bad_c = [r for r in c_db if r[0] not in cities]
check("INT", "domains/work types/cities not in config", not (bad_d or bad_w or bad_c), f"domains={bad_d} work_types={bad_w} cities={bad_c}")
name_map = {str(v): k for k, v in cfg["filters"]["domains"].items()}
mism = [r for r in d_db if name_map.get(str(r[0])) != r[1]]
check("INT", "domain id <-> name consistent with config", not mism, f"{mism}")
d13 = conn.execute("SELECT COUNT(*) FROM Jobs WHERE domain='13' OR domain=13").fetchone()[0]
check("INT", "leftover domain 13 rows", d13 == 0, f"{d13}")
types = conn.execute("SELECT typeof(domain), typeof(work_type), typeof(available), COUNT(*) FROM Jobs GROUP BY 1,2,3").fetchall()
check("INT", "storage types of domain/work_type/available", True, f"{types}")
nullav = conn.execute("SELECT COUNT(*) FROM Jobs WHERE available IS NULL").fetchone()[0]
check("INT", "available NULL", nullav == 0, f"{nullav}")
# truncation risk (A2 g on real data): combos at the 200 cap
cap = conn.execute("SELECT city, domain, work_type, COUNT(*) n FROM Jobs WHERE available=1 GROUP BY 1,2,3 HAVING n>=190 ORDER BY n DESC").fetchall()
mx = conn.execute("SELECT MAX(n) FROM (SELECT COUNT(*) n FROM Jobs WHERE available=1 GROUP BY city, domain, work_type)").fetchone()[0]
check("T2", "g) real-data combos at/near 200 cap", not cap, f"max available per (city,domain,work_type)={mx}; combos>=190: {cap}")
sd = conn.execute("SELECT scraped_date, COUNT(*) FROM Jobs GROUP BY 1 ORDER BY 1 DESC LIMIT 3").fetchall()
check("INT", "scraped_date recent values (info)", True, f"{sd}; NULL={conn.execute('SELECT COUNT(*) FROM Jobs WHERE scraped_date IS NULL').fetchone()[0]}")
conn.close()
json.dump(RESULTS, open(WORK / "res_db.json", "w"))

raise SystemExit(summary())
