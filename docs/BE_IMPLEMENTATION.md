# Backend Implementation — JobWebScraper

Living, **dated** description of the backend for the project paper.

**How dates work in this document**
- Every component, technology and design decision has a **Since** date. Superseded ones keep their row with an **Until** date and a pointer to what replaced them. Nothing is deleted, so the evolution can be reconstructed for any date.
- Each section shows **Last changed**. When a section's content is replaced, the old text moves to *§10 Superseded versions*, under the date it stopped being valid.
- Every change is recorded in *§9 Change log* (newest at the bottom) with its date, what changed, what it replaced and why.
- Dates marked † come from the file's first git commit. That is the earliest *verifiable* date: the code may be older, and files moved during the 2026-09-30 reorganisation show the move date. "uncommitted" means the code existed only in the working tree on that date.

---

## 1. Purpose and scope
*Last changed: 2026-10-29 (thesis context, timeline)*

The system collects job advertisements from **bestjobs.eu** (Romania) and enriches each ad with a list of **hard skills** extracted by a Large Language Model. It exposes the data through a REST API consumed by a SvelteKit web client. The planned end goal is matching job requirements against skills extracted from a user's CV.

**Thesis context (since 2026-10-29).** The project is the author's bachelor thesis in Computer Science. The learning focus is the backend matching work: ESCO grounding, embeddings, similarity and set-matching metrics. Routing and web plumbing are low priority. A job-market analyzer is planned as a bonus once the minimal app works.

**Timeline (set 2026-10-29, revise as needed):**
| Milestone | Target | Content |
|---|---|---|
| Minimal slice | ~2026-11-12 | Exact + fuzzy grounding, Chamfer, end-to-end flow (CV upload → click job → score + missing skills); embeddings as stretch (`MATCHING_ROADMAP.md` → *Minimal slice*) |
| Engine mostly done | March 2027 | Cache DB, embeddings, graph + subsumption, seniority, all four metrics, eval set, full report |
| Bonus | after March *(until 2026-10-30)* | Job-market analyzer |
| Analyzer page | after the minimal slice, November 2026 *(since 2026-10-30)* | Extraction / Matching / Jobs views; design in `MATCHING_ROADMAP.md` → *Analyzer page* |
| Writing | from early, intensive after March | Based on this document |

## 2. Technology stack
*Last changed: 2026-10-29 (T2 kept, T10/T12 in progress, T11 replaced by T11b)*

| ID | Layer | Technology | Since | Until | Status | Rationale / notes |
|---|---|---|---|---|---|---|
| T1 | Language | Python 3.11 (CI) | 2026-09-06† | — | current | Version pinned in both workflows |
| T2 | Web API | FastAPI + Uvicorn, Pydantic schemas | 2026-10-22 (uncommitted) | — | current — ~~expected to change week of 2026-10-26~~ → **kept 2026-10-29** for the minimal slice; reconsidered after March 2027, if at all | Initial choice; it already works and routing is low priority for the thesis |
| T3 | Storage | SQLite single file `data/jobs/JobsDatabase.sqlite` | ≤2026-09-06† | — | current | Zero-ops; versioned in git so the CI runs can persist it |
| T4 | Scraping | `requests` + BeautifulSoup, bestjobs JSON proxy API | ≤2026-07-14† | — | current | JSON API for listings, HTML for detail pages |
| T5 | LLM | Groq API, model `openai/gpt-oss-120b` | ≤2026-03-19† | — | current | Model in use at time of writing; earlier model history not tracked |
| T6 | CV parsing | pdfplumber | 2026-03-19† | — | current (prototype) | |
| T7 | Scheduling | GitHub Actions cron | 2026-09-06† | — | current | Free, no server needed |
| T8 | Notifications | SMTP (Gmail) summary e-mails | 2026-09-06† | — | current | |
| T9 | Frontend | SvelteKit + TypeScript | 2026-10-22 (uncommitted) | — | current | Out of this document's scope |
| T10 | Skill taxonomy | ESCO ~~v1.2.x~~ **v1.2.1** (confirmed 2026-10-26), English labels only | 2026-10-22 (decided) | — | planned → in progress 2026-10-26 (loader, index, exact lookup) | Standard EU taxonomy with aliases and a concept hierarchy; Romanian left out to limit complexity |
| T11 | Embeddings | Local English sentence-transformers model (all-MiniLM-L6-v2 or bge-small-en-v1.5), CPU torch | 2026-10-22 (decided) | 2026-10-26 → T11b | superseded | Free, reproducible, no API key; CPU-only to keep CI installs small |
| T11b | Embeddings | sentence-transformers 6.2.0 + `BAAI/bge-small-en-v1.5` (revision `5c38ec7c…`), CPU torch 2.14.1, from `requirements-matching.txt` | 2026-10-26 (decided; row added 2026-10-29) | — | planned (stretch goal of the minimal slice) | Better short-text similarity than MiniLM at the same 384 dims; installed locally / on the app server only, never in GitHub Actions (grounding happens on click) |
| T12 | Fuzzy matching | rapidfuzz 3.14.6 | 2026-10-22 (decided) | — | planned → in progress 2026-10-28 (`backend/matching/grounding.py`) | Typo/variant matching against ESCO labels |
| T13 | Assignment | scipy (Hungarian, rectangular) | 2026-10-22 (decided) | — | planned | 1-to-1 skill matching metric |

## 3. Architecture overview
*Last changed: 2026-10-29 (matching engine partially implemented)*

| Component | Location | Role | Since |
|---|---|---|---|
| Routers | `backend/api/routers/` | HTTP endpoints, query-parameter parsing | 2026-10-22 (uncommitted) |
| Schemas | `backend/api/schemas/` | Pydantic response models | 2026-10-22 (uncommitted) |
| Services | `backend/services/` | Business logic: filters, LLM calls, skill extraction, notifications, matching (WIP, empty) | 2026-03-19† (llm), 2026-09-06† (extraction, notifier), 2026-10-22 (filters) |
| Repositories | `backend/database/repositories/` | SQL access split by concern: `jobCardsRepository` (read side, API) and `jobExtractionRepository` (write side, scraper/extraction) | split on 2026-10-22 (uncommitted); previously a single `job_repositories.py` |
| Connection | `backend/database/connection.py` | Opens the SQLite DB | 2026-09-30† |
| Scraper | `backend/scraper/bestjobs/` | `runner` orchestrates, `scraper` fetches/parses; `config.json` holds URLs, limits, delays and the filter catalogue | 2026-07-14† (runner), moved 2026-09-30† |
| Utils | `backend/utils/` | URL generation (cartesian product of filters), HTTP helper, data-folder setup | 2026-10-01† (URL generation split out) |
| Matching engine (planned → partially implemented 2026-10-26) | `backend/matching/` | Framework-agnostic package: config, normalization, `esco/` (loader, index, graph), grounding, embeddings, similarity, `metrics/`, report, engine; plus `skill_grounding_service`, `matcher_service` and `skillGroundingRepository` (see §5.4). *(2026-10-29)* Implemented: `config.py` + `config.json`, `normalization.py`, `esco/loader.py`, `esco/index.py` (exact lookup), `match_result_object.py`; in progress: `grounding.py` (fuzzy). Grounding sits at package level since 2026-10-29 (until then planned as `esco/grounding.py`) | 2026-10-22 (decided) |

Two independent batch pipelines write the DB; the API only reads it.

## 4. Data model
*Last changed: 2026-10-22*

A single table, `Jobs`, with primary key `(source, slug)`.

| Column | Meaning | Since |
|---|---|---|
| source | origin site (`bestjobs`) | initial |
| slug | ad identifier on the source site | initial |
| title, company_name | ad metadata | initial |
| salary, est_salary | advertised / estimated salary | initial |
| work_type, worktype_name | bestjobs employment-type ID and display name | initial |
| domain, domain_name | bestjobs domain ID and display name | initial |
| city | city filter used when scraped | initial |
| description | plain-text description built from the detail page (`<p>` and `<li>` items) | initial |
| experience_level | parsed from the detail page | initial |
| required_skills | JSON array; `NULL` = not processed; `["__EXTRACTION_FAILED__"]` = permanent failure | ≤2026-09-06 |
| available | 1 if present in the latest scrape | initial |
| scraped_date | ISO date of first discovery | 2026-10-01† |
| logo | unused | initial |

"initial" = present before change tracking started (2026-10-22).

**Snapshots** (append one row per measurement; don't overwrite):

| Date | Rows | Available | Avg description length |
|---|---|---|---|
| 2026-10-22 | 5,496 | 3,561 | ≈ 3.1k chars |
| 2026-10-22 (after cleanup) | 5,203 | 3,332 | — |

## 5. Pipelines

### 5.1 Weekly scrape (`scrape.yml`, Mondays 03:00 UTC)
*Last changed: 2026-10-22 (availability logic, A2) · workflow since 2026-09-06†*

1. Build every combination of city × domain × work type from `config.json` (3 × 9 × 3 = 81 listing URLs).
2. For each listing URL, call the bestjobs JSON API (limit 200, since 2026-09-25†). A failed request or an unusable response (not JSON, no `items` list) is counted as a failed listing and skipped; malformed items are skipped individually. Otherwise unseen slugs are inserted (committed per listing) and all returned slugs are added to an in-memory set of jobs seen in this run.
3. For each **new** slug, fetch the detail HTML page, parse the experience level and description, and store them. Wait 1 s between requests.
4. After the loop, if no listing failed: reset availability, mark the seen set available, and commit **once**. If any listing failed, availability is left unchanged. A crash rolls back only uncommitted work, so availability is never left half-updated.
5. E-mail a summary: new jobs, pages fetched/failed, descriptions missing, listings failed, whether availability was updated, duration.
6. The workflow commits the updated SQLite file to the repository.

Design choice: the scrape is incremental. Detail pages are fetched only for new slugs, and availability is recomputed every run, so expired ads are hidden rather than deleted. Since 2026-10-22, availability is recomputed atomically at the end of a complete run instead of being reset at the start (see §10).

### 5.2 Daily skill extraction (`extract.yml`, 04:00 UTC)
*Last changed: 2026-10-22 (failure handling, A4) · workflow since 2026-09-06†*

1. Select up to 90 jobs that have a description and no `required_skills`.
2. For each, send a recruiter-style prompt plus the description to the LLM, expecting `{"required_skills": [...]}` (hard skills only, no soft skills or spoken languages).
3. Validate the JSON shape:
   - malformed JSON, wrong shape or any other error → failure sentinel, committed immediately (not retried)
   - rate limit → stop the run (remaining rows are picked next day)
4. Pause 20 s between calls to respect the provider rate limits.
5. E-mail a summary that includes the global coverage percentage.

Design choice: a per-run cap and fixed throttling keep the job inside free-tier limits, spreading progress over several days. Since 2026-10-22, failed extractions are dropped instead of retried: failures are rare and retries consumed the daily budget.

### 5.3 CV parsing (`backend/cv_parser/parser.py`, prototype, not exposed by the API)
*Last changed: 2026-10-22 · file since 2026-03-19†*

Extracts text from a fixed PDF (`data/cv/raw/Test.pdf`) with pdfplumber and saves the raw text. It then sends the text to the LLM to obtain hard skills categorised by experience level (entry_level 0-2y, junior 2-3y, mid_level 3-5y, senior 5+y) and languages, and stores the reply as a text file. Planned rework: see `docs/ASSIST_LOG.md` → *2026-10-22 CV parser: needed changes*.

### 5.4 Matching engine (in progress since 2026-10-26)
*Last changed: 2026-10-29 (goal line, minimal slice, Chamfer first, in-memory cache first) · design decided 2026-10-22*

Goal *(since 2026-10-26)*: score a CV against one clicked job (available, with extracted skills) and explain the score. *(Old goal in §10.)*

**Build status (2026-10-29):** config, normalization, ESCO loader and exact lookup done; fuzzy in progress; the rest planned. Full checklist and the step-by-step data walkthrough (*How it fits together*): `docs/MATCHING_ROADMAP.md`.

**Minimal slice (since 2026-10-29).** The engine is first built as a thin end-to-end slice (target ~2026-11-12): exact + fuzzy grounding → matrix (same concept or same string = 1.0, else 0; cosine once embeddings exist) → directed Chamfer → minimal report → FastAPI endpoints → UI. Then it is deepened in the planned order. *(Since 2026-10-30)* For the analyzer page the grounding cache also stores the time of each skill's first lookup (`duration_ms`) and whether it came from a job or a CV (`source`). Two changes to that order: **Chamfer is implemented first** (until 2026-10-29: Tversky first, hardest first), because it is the simplest, the UI default, and its per-requirement output is the report; the **grounding cache starts as an in-memory dict** and becomes `grounding.sqlite` in November (until 2026-10-29: cache DB before embeddings), to keep the slice small. Nothing is dropped.

**Data facts behind the design (2026-10-22):** 12,799 distinct job-skill strings (9,864 seen once, 1,091 case-only duplicates); 255 contain a slash, mostly single concepts (CI/CD, SAP S/4HANA, TCP/IP); ≥280 Romanian skills; 39% of matchable jobs have no experience level (NULL or "Fără").

1. **Preprocessing.** Clean, casefold, small curated acronym list. Compounds ("/", "&", "and") are split only if the whole string fails grounding and every part grounds confidently; never around digits. The CV parser returns a validated structure with tiers entry/junior/mid/senior/unknown; a skill in several tiers keeps the highest. *(Since 2026-10-26)* Tier names come from `cv_tier_map` in the matching config; the parser maps the LLM's variants (`entry_level`, `mid_level`, `middle`, …) to them through an alias table, and anything unrecognized becomes unknown. Job requirements are deduplicated after grounding.
2. **ESCO grounding (English only)** *(since 2026-10-26)*. Small exact-match acronym list (acronym → ESCO preferred label, for frequent acronyms the later steps miss or get wrong) → exact match on preferred/alt/hidden labels *(index keys since 2026-10-27: every label is simplified — hyphens → spaces, trailing qualifier removed, normalized again — and stored only in that form; every job/CV skill goes through the same simplification before lookup. Index ambiguity rule since 2026-10-27: when a key points to several concepts, candidates are deduplicated by concept and ranked preferred > alt > hidden; the best rank wins, a tie stays ambiguous and goes to the embedding step, which since 2026-10-27 compares it only against those candidates and needs the 0.80 floor plus a clear gap to the runner-up)* → fuzzy (rapidfuzz) → embedding with a fixed 0.80 floor → otherwise *unresolved* (raw string and embedding kept). The LLM parent-link step D is postponed and may not be implemented. Abstraction tier is derived in memory from skill type, hierarchy depth and reuse level, never written to source data. *(Since 2026-10-26)* Job skills are grounded on click: the first time a job is opened, its not-yet-seen skills are grounded and stored; CV skills are grounded at upload. Results live in a `SkillGrounding` table in a separate git-ignored SQLite file `data/cache/grounding.sqlite` (raw skill, normalized form, ESCO URI, method, score, ESCO version, model revision, config fingerprint, date) — a rebuildable cache shared across sessions, kept out of `JobsDatabase.sqlite` so app writes never conflict with the daily workflow commits. A local batch script grounds all job skills for the paper statistics.
3. **Similarity matrix (CV skills × job requirements).** Same URI → 1.0; both unresolved with equal normalized strings → 1.0; otherwise cosine similarity. Then: directional ESCO subsumption boost (specific CV skill covering a broad requirement is strong, the reverse is weak) → cap 1.0 → noise threshold (≈0.35) → relative seniority multiplier → cap 1.0. Pre-seniority scores are kept for gap analysis.
4. **Relative seniority** *(since 2026-10-26)*. Job level Fără/Entry→0, Middle→2, Senior/Executive→3; NULL (no level) → no discount. Candidate tier ≥ job → 1.00, one below → 0.85, two → 0.65, three → 0.45; unknown CV tier → no (or a mild, configurable) discount.
5. **Metrics,** implemented one at a time, each checked on a hand-labelled set of ≈20 CV–job pairs. *(Since 2026-10-29)* Order: directed Chamfer (job → CV, default for the UI) → continuous Tversky → Soft Cosine → Hungarian. *(Until 2026-10-29: hardest first — Tversky → Soft Cosine → Hungarian → Chamfer.)*
6. **Result** *(since 2026-10-26)*. Computed when the user clicks one job: score 0–100% for that CV–job pair; per requirement the best CV skill, score, ESCO URI and seniority applied; gaps split into *missing* and *under-qualified*; extra CV skills listed. No ranking across jobs. The parsed CV lives only in the user's session; languages are parsed but not scored; the job list shows only available jobs with extracted skills.

**Operational decisions:** ESCO CSVs committed in `data/esco/` (portal download is not scriptable); vectors are a local, git-ignored cache rebuilt when missing (tens of MB would bloat history given daily DB commits); matching dependencies in a separate requirements file with CPU-only torch, installed locally / on the app server only — no matching work in GitHub Actions *(since 2026-10-26)*. API integration waits for the T2 decision. *(2026-10-29: T2 kept — integration starts in the minimal slice.)*

## 6. REST API
*Last changed: 2026-10-22 · implemented with T2 (FastAPI)*

| Endpoint | Description | Since |
|---|---|---|
| `GET /api/filters` | Filter catalogue from `config.json`: cities, work types `{id,name}`, domains `{id,name}` | 2026-10-22 (uncommitted) |
| `GET /api/jobs?domains=&work_types=&cities=` | Available jobs with successfully extracted skills, optionally filtered. Parameters are repeatable: values within a group are OR-ed, groups are AND-ed. | 2026-10-22 (uncommitted) |

CORS allows the Vite dev server (`localhost:5173`). Query parameters are bound to SQL with placeholders; values are never interpolated into the SQL string.

## 7. Operational aspects
*Last changed: 2026-10-29 (setting up a new machine)*

- Everything is scheduled on GitHub Actions (since 2026-09-06†). The database file is versioned in git, so each run produces a commit.
- Secrets (Groq key, SMTP credentials) come from environment variables / GitHub secrets, and from `.env` locally.
- Local development: `dev.py` (2026-10-22, uncommitted) starts backend and frontend together and tears down both process trees on exit.
- Testing (since 2026-10-22): plain-Python test scripts in `tests/`, grouped by area: scraper runner, DB schema/performance/integrity, and extraction/API. They run against a copy of the database or small fixture databases in a temp folder, with HTTP, LLM, SMTP and sleep mocked, so the real data and external services are never touched. A check passes when the code behaves as intended, so open issues show up as failures.

### Setting up a new machine (since 2026-10-29)
Written after moving from the PC to a laptop.
1. **Python + venv.** Install Python, then create the venv in the project root with `py -m venv .venv`. It must be called `.venv`: the Claude Code edit guard (`.claude/settings.json`) and the test commands run `.venv\Scripts\python.exe`, and without it every Claude edit is blocked. The laptop uses Python 3.14, while GitHub Actions uses 3.11 (T1); version differences are the first suspect if local and CI behaviour differ.
2. **Install, in this order:** `.venv\Scripts\pip install -r requirements.txt`, then `.venv\Scripts\pip install -r requirements-matching.txt` (CPU torch, large download). In a bash shell (e.g. Claude Code's `!` prefix) use forward slashes: `.venv/Scripts/pip …`. Check: `.venv\Scripts\python.exe -c "import torch, sentence_transformers, fastapi"` prints nothing.
3. **Embedding model.** pip installs libraries only, never model weights. The model (`BAAI/bge-small-en-v1.5`, ~130 MB) is downloaded from Hugging Face the first time code loads it. It lands in `data/models/` **only if** `embeddings.py` passes `model_folder` from the config as the cache folder (and the pinned `revision`); otherwise it goes to `~/.cache/huggingface/hub` outside the project. Alternatives: pre-download with `hf download` (from `huggingface_hub`, already installed) or copy `data/models/` from the other machine.
4. **What git does not carry.** `data/models/` and `data/cache/` are git-ignored, so a new machine starts with no model and an empty grounding cache; the cache rebuilds as jobs are clicked. `.env` (Groq key, SMTP) must also be copied by hand.

## 8. Known limitations / open issues
*Last changed: 2026-10-29*

| Date found | Summary | Details | Resolved on |
|---|---|---|---|
| 2026-10-22 | Backend quality review: missing index on `slug`, non-transactional availability reset, sequential scraping despite `async`, fixed 20 s LLM throttle, unpaginated `/api/jobs` (~1 MB), duplicated config loading, "Management" domain-ID mismatch, oversized `requirements.txt` | `docs/ASSIST_LOG.md` → *2026-10-22 Backend quality review* | — |
| 2026-10-22 | CV parser not usable for real uploads | `docs/ASSIST_LOG.md` → *2026-10-22 CV parser: needed changes* | — |
| 2026-10-29 | Model and cache folders are relative paths | `model_folder` (`data/models`) and `cache_folder` (`data/cache`) in `backend/matching/config.json` resolve against the working directory. Started from the repo root (`python dev.py`) they are correct; started from elsewhere (e.g. uvicorn from `backend/`) a second model copy is downloaded into the wrong folder. The ESCO folder is already resolved from the project root in `config.py`; the same could apply here. Open: user decision. | — |
| 2026-10-30 | No extraction timing or date in `Jobs` | Planned for the analyzer (AN2): `extracted_at`, `extraction_ms`, optional `tokens`, set by the skill-extraction service together with the skills or the failure marker. Extends ASSIST_LOG T8. Past rows cannot be backfilled; record the start date. Open: user implementation. | — |
| 2026-10-30 | Extraction has no "must-have vs nice-to-have" flag | The analyzer's requirement view needs the LLM to return, per skill, whether the posting requires it or only prefers it. Changing the prompt and output format means re-extracting every job (90/day ≈ 6–7 weeks). Planned for after March 2027; the view is a labelled mock until then. → 2026-10-30: view removed from the UI (user); limitation unchanged. | — |
| 2026-10-30 | Coverage endpoint missing; extracted ads undated | The analyzer's coverage card needs `GET /api/analyzer/coverage` (spec in MATCHING_ROADMAP → Analyzer page). Separately, no extracted ad has a `scraped_date` (extraction works through older, undated ads first), so period filters and trend views stay empty until dated ads are extracted (~1,850 waiting at 90/day). Related: ASSIST_LOG B12 (prioritise available jobs), T7, T8. Open: user implementation / decision on extraction order. | — |
| 2026-10-30 | An ad listed in several cities is counted under one city | `Jobs` has primary key `(source, slug)`, so an ad that appears in several city listings is stored once, with the city of the listing where it was first found. Per-city counts (analyzer) are therefore "city of first discovery", not "all cities the ad is offered in". Known limitation, no change planned. | — |
| 2026-10-29 | `requirements.txt`: uvicorn missing, fastapi unpinned | Already tracked as ASSIST_LOG B11; a clean install cannot start the API (`dev.py` runs uvicorn). | — |

## 9. Change log
Newest at the bottom. *Replaces* names what stopped being valid; the old description is kept in §10.

| Date | Area | Change | Replaces | Reason |
|---|---|---|---|---|
| 2026-03-19† | LLM / CV | `llm_service` and the CV parser prototype added | — | Project start (earliest tracked files) |
| 2026-07-14† | Scraper | Runner added | — | |
| 2026-09-06† | Ops | GitHub Actions weekly scrape + daily skill extraction, e-mail notifier | Manual runs | Automation |
| 2026-09-25† | Scraper | Listing URL limit set to 200 | Previous limit | |
| 2026-09-30† | Structure | Directory reorganisation; connection and response error handling | Flat layout | Maintainability |
| 2026-10-01† | Scraper / Data | URL generation split into its own module, config cached, `scraped_date` column added | | Avoid re-reading config; track discovery date |
| 2026-10-22 | API | FastAPI app with `/api/filters` and `/api/jobs` (T2) | — | Serve data to the SvelteKit frontend |
| 2026-10-22 | Repositories | `job_repositories.py` split into read (`jobCardsRepository`) and write (`jobExtractionRepository`) modules | Single repository module | Separate API reads from pipeline writes |
| 2026-10-22 | Docs | Dated documentation started | — | Track implementation changes for the paper |
| 2026-10-22 | Scraper config | "Management" domain ID corrected from 13 to 19 (ASSIST_LOG A1) | Management = 13, which bestjobs uses for education/training | Wrong category was being scraped under the Management label. 293 legacy rows keep `domain='13'`. |
| 2026-10-22 | Data | Deleted the 293 legacy rows with domain 13 (education jobs mislabelled as Management, see A1) | Rows labelled Management with domain 13 | Out of scope after the config fix; option 2 chosen over re-labelling (ASSIST_LOG 2026-10-22). The 78 extractions on those rows were discarded. |
| 2026-10-22 | Scraper | Availability recomputed once at the end of a complete run (single commit, skipped if any listing failed); listing request failures distinguished from empty listings; only new slugs detail-fetched; e-mail reports failed listings and availability update (ASSIST_LOG A2) | Upfront committed reset + per-listing mark-available (§10) | A crash or a failed listing used to hide live jobs for a week |
| 2026-10-22 | Skill extraction | Coverage percentage guarded against zero eligible jobs (ASSIST_LOG A3) | Unguarded division | A run with no eligible jobs crashed before sending the e-mail |
| 2026-10-22 | Skill extraction | Every non-rate-limit failure (wrong shape, malformed JSON, other errors) gets the single failure sentinel and is committed; separate other-error marker removed (ASSIST_LOG A4) | Wrong shape / other errors left NULL and retried (§10) | Endless retries spent the daily budget; failures are rare enough to drop |
| 2026-10-22 | Scraper | Listing parsing made fault-tolerant: a non-JSON body, a missing or non-list `items`, or non-dict JSON makes the listing count as failed; a malformed item is skipped (ASSIST_LOG A7) | Unguarded parsing | A single bad response or item aborted the whole weekly run |
| 2026-10-22 | Testing | `tests/` folder with mocked, DB-copy-based tests for the runner, DB layer and extraction/API | Ad-hoc manual checks | Repeatable verification of fixes and measurement of proposed changes |
| 2026-10-22 | Matching (design) | Matching-engine architecture and roadmap decided (§5.4, T10–T13): English-only ESCO grounding, offline job-skill grounding, local embedding model, relative seniority, metrics Tversky → Soft Cosine → Hungarian → Chamfer | Empty `matcher_service` placeholder | Start of the CV ↔ job matching work |
| 2026-10-23 | Matching / Data | ESCO CSVs renamed: `skill_Pillars.csv` (ESCO `broaderRelationsSkillPillar_en`), `skill_Hierarchy.csv` (ESCO `skillsHierarchy_en`); `skills_en.csv` kept. ESCO loader reads the three files through one shared CSV reader, cached once per process | Original ESCO file names | User's naming choice; a new ESCO download must be renamed the same way |
| 2026-10-26 | Matching (design) | Canonical CV tier names entry / junior / mid / senior (+ unknown) in `cv_tier_map`; parser output normalized to them via aliases | Config used entry_level / mid_level (as in the prompt), parser output unvalidated | Real parser output uses the short names; names must be enforced in one place, not trusted from the LLM |
| 2026-10-26 | Matching (design) | Job level "Fără" (no experience required) mapped to Entry (0) | "Fără" grouped with NULL as no level | "Fără" is a real requirement level, not missing data; scores unchanged since no candidate is below 0 |
| 2026-10-26 | Matching (design) | Embedding model `BAAI/bge-small-en-v1.5`, pinned to revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`; stored in git-ignored `data/models/`; installed with CPU-only torch from a separate matching requirements file | Undecided between all-MiniLM-L6-v2 and bge-small-en-v1.5 | Better short-text similarity at the same 384 dimensions; small enough for CPU in GitHub Actions |
| 2026-10-26 | Matching | First engine modules implemented: `config.py` (loads `config.json` once, strips metadata notes, validates esco/seniority groups, resolves the ESCO folder from the project root, short SHA-256 fingerprint, read-only result); ESCO loader takes its folder from the config (optional override for tests), keeps reuse level, description and modified date, splits alt and hidden labels, keeps the newest row for the 21 concepts listed twice; normalizer applies NFKC first, replaces inner bullets (•, ·), unifies apostrophes, collapses spaces, strips punctuation and bullets (incl. `*`, `-`) only at the ends, drops trailing dots but keeps a leading one (.NET), then casefolds; `requirements-matching.txt` separate from `requirements.txt` | Empty `config.py`; loader with hardcoded path | Build steps 1 and 3 of the matching roadmap |
| 2026-10-26 | Matching (design) | Grounding limited to steps A–C; LLM parent link (step D) postponed; embedding floor fixed at 0.80; exact-match acronym list before step A | Steps A–D with a tunable ≈0.80 floor | User decision to keep grounding local and simple. A test of bare acronyms showed step C misses or mismatches some (SEO, ERP, VPN), and a lower floor accepts nonsense (XML → PHP at 0.74); a short list fixes the frequent cases deterministically |
| 2026-10-26 | Matching (design) | On-click flow: one CV vs one clicked job (no ranking); job skills grounded on first click, CV skills at upload; grounding cache in separate git-ignored `data/cache/grounding.sqlite`; CV session-only; languages not scored; job list limited to jobs with extracted skills; no grounding or torch in `extract.yml` | Offline grounding after daily extraction, `SkillGrounding` in `JobsDatabase.sqlite`, CV ranked against all jobs | Matches the intended UX; keeps GitHub Actions light; avoids binary merge conflicts with the daily DB commits; CV is personal data |
| 2026-10-27 | Matching (design) | Exact-index ambiguity rule: dedupe by concept, rank preferred > alt > hidden > derived variant, best rank wins, ties ambiguous → step C | "Preferred label may win" (undecided) | Preferred labels name a concept's main meaning; hidden labels are mostly misspellings; variants produced by our own processing must never beat an original ESCO label |
| 2026-10-27 | Matching (design) | Ambiguous exact matches: embedding step restricted to the label-matched candidates, floor 0.80 + minimum top-two gap, own grounding method | Undecided (candidates vs full search) | Keeps the result consistent with the exact match and avoids drifting to an unrelated concept; few comparisons; without context the gap rule prevents coin-toss picks |
| 2026-10-27 | Matching | ESCO exact index (build step 4, partial): every preferred/alt/hidden label normalized and inserted with its kind; per key only the best-ranked kind is kept with the set of concepts having it (one concept → match, several → ambiguous candidates); built once per process | Empty index module | Single-pass implementation of the ambiguity rule; derived variants and lookup still to do |
| 2026-10-27 | Matching (design + code) | Index keys simplified (Way 2): hyphens → spaces, trailing qualifier removed, re-normalized; only the simplified key is stored; the lookup applies the same simplification to inputs | Original key kept + lower-ranked "derived" variants (§10) | Simpler and symmetric (inputs with hyphens/qualifiers also match); data check: 0 qualifier collisions, 1 hyphen collision (pay-per-click) that becomes ambiguous and goes to step C |
| 2026-10-27 | Matching | Exact lookup (step A) in the index module: empty input → not found; input simplified like the index keys; result is a shared result object with status match / ambiguous (sorted candidates) / not found, plus label kind and simplified key; falls back to the cached index when no table is passed (tests can pass their own) | — | Build step 4, exact part; fuzzy (step B) still to do |
| 2026-10-28 | Matching | Fuzzy step B started in `backend/matching/grounding.py` (rapidfuzz `process.extract` over index keys ≥ min length); `grounding` group added to `config.json` (fuzzy threshold 90, gap 5, min length 4, embedding floor 0.80) | — | Build step 4, fuzzy part (in progress; recorded 2026-10-29) |
| 2026-10-29 | Matching | Fuzzy step B done: `fuzzy_match` in `backend/matching/grounding.py`. Input simplified like the index keys; inputs shorter than 4 characters skipped; rapidfuzz `fuzz.ratio` over index keys ≥ 4 characters (key list cached), up to 5 candidates ≥ 85; accepted only if best ≥ 90, the numbers in input and key are equal, and the best leads the first candidate of a **different concept** by ≥ 5 points; returns a `MatchResult` (match with concept / ambiguous with sorted candidates / not found) with label kind, score and method "fuzzy" | — | Build step 4, fuzzy part. Digit rule measured on 14,632 distinct job skills: 529 contain digits, 9 reach a fuzzy hit ≥ 90, 5 of those with different numbers (2 wrong matches blocked: 2D → 3D modeling, Java 21 → java 2; 3 acceptable ones also rejected: Google Analytics 4 ×2, 2D technical drawing). Strict rule kept; a looser "key numbers ⊆ input numbers" rule would get all 5 right |
| 2026-10-29 | Project | Thesis context and timeline recorded (§1): minimal slice by ~2026-11-12, engine mostly done March 2027, analyzer as bonus | — | User's bachelor thesis milestones |
| 2026-10-29 | Matching (design) | Grounding module at package level (`backend/matching/grounding.py`), one pipeline for job and CV skills; `esco/` limited to the ESCO data layer | `esco/grounding.py` | Grounding also uses embeddings, cache, overrides and acronyms, not only ESCO |
| 2026-10-29 | Matching (design) | Minimal slice first (exact + fuzzy → matrix → Chamfer → minimal report → endpoints → UI; embeddings stretch); Chamfer implemented first; grounding cache starts in memory | Strict build order; Tversky first; cache DB before embeddings | 2-week milestone; Chamfer is simplest and its output is the report; fewer moving parts. Nothing dropped |
| 2026-10-29 | API (T2) | FastAPI kept for the slice; reconsidered after March, if at all | "Expected to change week of 2026-10-26" | Works already; routing is low priority for the learning goal |
| 2026-10-29 | Docs | Stack table synced (ESCO 1.2.1, T11 → T11b, rapidfuzz in progress); architecture lists implemented modules; §5.4 goal fixed; *Setting up a new machine* added (§7); relative model path and B11 listed in §8 | Outdated rows/lines (§10) | Docs had drifted from the code and from the 2026-10-26 decisions |
| 2026-10-30 | Analyzer (design) | Analyzer page designed: after the minimal slice; Extraction / Matching / Jobs sections; timings for grounding per skill (`duration_ms`, `source` in the grounding cache), LLM extraction per job (new `Jobs` columns, planned) and CV parsing per upload (session only); skill rankings by ESCO concept; CV data session-only | Analyzer as a bonus after March, undesigned | User's design; the extraction and matching views double as evaluation figures for the thesis |
| 2026-10-30 | Analyzer (design) | Jobs-tab relevancy views decided: rank change as a two-point slope (first 2 vs last 2 dated weeks), specificity (share × concentration in one domain), skill bundles (co-occurrence), category treemap (groups still open), must-have vs nice-to-have (needs a requirement flag from extraction, after March) | Weekly bump chart; "distinctive" and "often asked together" lists | Raw frequency overrates generic skills (office, budgets); these views show specialisation, bundles and requirement strength, and are candidate thesis figures |
| 2026-10-30 | Analyzer (design) | Jobs tab redesigned one view at a time. View 1 "Most required skills": horizontal bars, top 10, % of postings with extracted skills (label also gives job count), counted by ESCO concept once per job, non-ESCO skills included and marked, filters domain / experience level / city / period; no table. Data path: filter `Jobs` → ground each job's skills via the cache → set per job → count ÷ filtered postings | Column chart with a table toggle, share over all analyzed postings | Tables were hard to read; % stays comparable across domains of different size, weeks of different scrape volume, and listings capped at 200 ads; excluding non-extracted ads keeps shares from shrinking while extraction catches up |
| 2026-10-30 | Analyzer (design) | Analyzer split into verified counts (from `/api/jobs`: experience level, ads per domain/city, skills per job) and grayed previews. New planned endpoint `GET /api/analyzer/coverage` (extraction-state counts, queued per domain, lists of empty / failed / empty-description ads); spec in MATCHING_ROADMAP → Analyzer page. Data findings: none of the 1,757 extracted ads has a `scraped_date` yet (time views impossible until dated ads are extracted); Management has 0 extracted ads (269 queued, scraped after the domain-ID fix); 690 available ads have no description, 22 more were processed with an empty one (T7) | Mock-only analyzer | Only trustworthy numbers are shown as real; the endpoint is the user's backend work |

## 10. Superseded versions
Old descriptions of sections or components, kept verbatim under the date they stopped being valid.

### §5.4 Matching engine, header and goal line — valid until 2026-10-26 (moved here 2026-10-29)
> ### 5.4 Matching engine (planned, not implemented)
> Goal: score a CV against every available job with extracted skills and explain the score.

Reason for the change: the on-click flow (one CV vs one clicked job) was confirmed on 2026-10-26, but this line was not updated until 2026-10-29; implementation started 2026-10-26.

### §5.4 Matching engine, item 5 (metric order) — valid until 2026-10-29
> 5. **Metrics,** implemented one at a time, hardest first, each checked on a hand-labelled set of ≈20 CV–job pairs: continuous Tversky → Soft Cosine → Hungarian → directed Chamfer (job → CV, default for the UI).

Reason for the change: minimal slice by ~2026-11-12 needs one working metric; Chamfer is the simplest and its output is the report.

### §5.4 Matching engine, item 2 (index ambiguity rule) — valid 2026-10-27 until 2026-10-27
> *(index ambiguity rule since 2026-10-27: when a normalized label points to several concepts, candidates are deduplicated by concept and ranked preferred > alt > hidden > derived variant; the best rank wins, a tie stays ambiguous and goes to the embedding step, …)* Derived variants (hyphen-as-space, trailing qualifier stripped) were planned as extra index entries next to the original key, ranked below every real ESCO label.

### §5.4 Matching engine, item 2 (last sentence), item 6 and operational decisions (torch) — valid until 2026-10-26
- Item 2: Job skills are grounded offline in a batch after the daily extraction and stored in a new `SkillGrounding` table (raw skill, normalized form, ESCO URI, method, score, ESCO version, date); CV skills are grounded at request time.
- 6. **Result.** Score 0–100%; per requirement the best CV skill, score, ESCO URI and seniority applied; gaps split into *missing* and *under-qualified*; extra CV skills listed; jobs ranked for one CV.
- Operational decisions: matching dependencies in a separate requirements file with CPU-only torch installed only in `extract.yml`.
Reason for the change: the app flow was confirmed as one CV vs one clicked job; grounding moved from the daily workflow to on-click with a separate cache file.

### §5.4 Matching engine, item 2 (first sentence) — valid until 2026-10-26
2. **ESCO grounding (English only).** Exact match on preferred/alt/hidden labels → fuzzy (rapidfuzz) → embedding with a confidence floor → otherwise *unresolved* (raw string and embedding kept).
Reason for the change: step D postponed; acronym list added and floor fixed at 0.80 after the acronym embedding test.

### §5.4 Matching engine, item 1 (CV tiers sentence) — valid until 2026-10-26
The CV parser returns a validated structure with tiers entry/junior/mid/senior/unknown; a skill in several tiers keeps the highest.
Reason for the change: the tier names the LLM returned (entry / mid) differed from the prompt and the config (entry_level / mid_level), and nothing validated them.

### §5.4 Matching engine, item 4 — valid until 2026-10-26
4. **Relative seniority.** Job level Entry→0, Middle→2, Senior/Executive→3; no level → no discount. Candidate tier ≥ job → 1.00, one below → 0.85, two → 0.65, three → 0.45; unknown CV tier → no (or a mild, configurable) discount.
Reason for the change: "Fără" (no experience required) was grouped with missing levels although it is a real level.

### §5.1 Weekly scrape — valid until 2026-10-22
1. Build every combination of city × domain × work type from `config.json` (3 × 9 × 3 = 81 listing URLs).
2. Mark all jobs unavailable.
3. For each listing URL, call the bestjobs JSON API (limit 200, since 2026-09-25†), insert unseen slugs and mark all returned slugs available.
4. For each **new** slug, fetch the detail HTML page, parse the experience level and description, and store them. Wait 1 s between requests.
5. E-mail a summary: new jobs, pages fetched/failed, descriptions missing, duration.
6. The workflow commits the updated SQLite file to the repository.
Problem that led to the change: the reset was committed before scraping, so a crash or a failed listing left jobs hidden until the next weekly run (ASSIST_LOG A2).

### §5.2 Daily skill extraction, step 3 — valid until 2026-10-22
3. Validate the JSON shape:
   - malformed JSON → failure sentinel (not retried)
   - wrong shape / other errors → left `NULL` (retried next run)
   - rate limit → stop the run
Problem that led to the change: rows with a wrong-shape reply were retried every day forever, spending the 90-call budget (ASSIST_LOG A4).

