# Assist Log

Tracked backend issues and needed changes, grouped by review date. Only item statuses are updated (with dates). Individual questions and answers are not logged.

Status legend: `open` · `accepted` · `rejected` · `done` · `reverted` · `closed` · `unimportant`

**Dating rules:** each section is headed with its date (`## YYYY-MM-DD — topic`). Status changes are appended with their date and the previous status is kept, e.g. `open → accepted 2026-10-25 → done 2026-10-28`. Past text is not rewritten.

---

## 2026-10-22 — Project setup: working rules
- Claude edits only `frontend/`, and only on request (enforced by `.claude/hooks/guard_fe_only.py`).
- Backend: Claude reviews and reasons, never edits; no code unless explicitly asked.
- Tracking files: this log + `docs/BE_IMPLEMENTATION.md` (for the paper).
- 2026-10-22: log changed to status-only; individual questions are no longer recorded.

---

## 2026-10-22 — Backend quality review (issues, redundancy, latency)

Measured on the current DB (5,496 rows): unfiltered `/api/jobs` returns 1,676 rows ≈ **974 KB** JSON, query ≈ 26 ms, Pydantic validation ≈ 7 ms.

### A. Correctness bugs — FIXED 2026-10-22 (A1–A4, A7 done; A5 closed as works as is; A6 marked unimportant, not changed)
| # | Where | Issue | Recommendation | Status |
|---|---|---|---|---|
| A1 | `scraper/bestjobs/config.json` | "Management" mapped to domain **13**, but bestjobs' catalogue (`config/filters_config_bestjobs.json`) has 13 = *educatie_training_coaching*, 19 = *management*. The 293 "Management" rows are probably education jobs. | Verify on the site; fix the ID and re-label/re-scrape affected rows. | open → done 2026-10-22 (config: Management = 19). **Residual:** 293 existing rows still `domain='13'` labelled "Management" (actually education). They stay `available=1` until the next scrape (Mon 2026-10-26). Until then they show in unfiltered results but never under the Management filter. After that they become unavailable, but stay in the DB with the wrong label. Delete or re-label them if they matter for stats. → residual rows deleted 2026-10-22 (5,496 → 5,203 rows). |
| A2 | `runner.py` + `reset_all_availability` | Availability reset is committed immediately, before scraping. If the run crashes or a listing request fails, those jobs stay `available = 0` and disappear from the UI until next week. | Do reset + re-mark in one transaction, or mark the run's seen slugs and flip availability only after a successful run (e.g. compare a "last_seen" run date). | open → done 2026-10-22 (availability recomputed once at the end in a single commit; skipped if any listing failed; connection closed in finally). DB-tester verification pending. → verified by DB tests 2026-10-22 (normal run, failed listing, crash, empty listing, duplicate slug: all pass); follow-ups T1, T2 |
| A3 | `skill_extraction_service.populate_skills` | Division by zero when no job has a description (`total_eligible = 0`). | Guard the progress calculation. | open → bug reproduced by test 2026-10-22 (ZeroDivisionError, no e-mail, connection leaked) → done 2026-10-22 (progress guarded when nothing is eligible; T6 connection leak still open) |
| A4 | `skill_extraction_service` | "Invalid shape" and "other errors" are never marked → the same broken rows are retried every day forever and eat the 90-job budget. | Add a retry counter / attempts column, or sentinel after N failures. | open → bug reproduced by test 2026-10-22 (also JSON list/string replies retried forever) → done 2026-10-22 (user policy: drop failures. Every non-rate-limit failure gets the single failure marker and is committed; extra marker removed; mocked test: 5 failure types marked, nothing retried on run 2) |
| A5 | `jobsCardRoute` / repository | `domain` and `work_type` are stored as TEXT; the API takes ints and casts them to str. Works, but the type contract is inconsistent (filters endpoint returns ints). | Store IDs as INTEGER, or accept strings consistently. | open → closed 2026-10-22, works as is (API ints are converted for the TEXT columns; filters verified by test, IT + Full time = 325 rows) |
| A6 | `notifier_service` | Receiver address not checked (only sender + password); SMTP connection not closed on exceptions. | Validate all three; use a context-managed connection. | open → unimportant 2026-10-22 (user decision: low impact, process exits right after sending) |
| A7 | `scraper.py` `json_response` | `response.json()` and `data['items']` / `item['...']` unguarded — a schema change or an HTML error page with 200 crashes the whole run (caught only at runner level, which then stops all remaining URLs). | Handle per-URL failures so one bad listing doesn't abort the run. | open → in progress 2026-10-22 (per-item KeyError handled, run continues; still open: JSON decode + `items` check, slug added to new list before insert) → done 2026-10-22 (non-JSON body, missing/non-list `items`, non-dict JSON and bad items all handled: listing counted as failed or item skipped, run continues; 6 runner tests pass) |

### B. Latency / performance
| # | Where | Issue | Impact | Recommendation | Status |
|---|---|---|---|---|---|
| B1 | DB schema | PK is `(source, slug)`; every lookup is `WHERE slug = ?` only → **full table scan** per call (confirmed with EXPLAIN QUERY PLAN). Used by existence check, mark-available, add-description, both skill updates. | O(rows) per job; grows with table size; runs thousands of times per scrape. | Add an index on `slug` (or filter by `source` AND `slug` so the PK is used). | open → proposal validated 2026-10-22 (reset+mark 3,332 slugs: 34.8 s → 0.16 s; 3,332 existence checks: 580 → 177 ms) |
| B2 | `check_existing_slug` + `add_new_jobs` | Redundant round-trip: a SELECT per item, then `INSERT OR IGNORE` which already ignores duplicates. | 2 queries per listed job. | Rely on `INSERT OR IGNORE` and use the affected-row count to know if it was new. | open → proposal validated 2026-10-22 (same new/existing split; 657 → 8 ms) |
| B3 | `runner.py` | Declared `async` and run with `asyncio.run`, but everything inside is blocking → fully sequential: 81 listing calls + every detail page with a 1 s sleep. | Run time grows linearly with new jobs. | Either drop the fake async, or make it really concurrent (async HTTP client with a small concurrency limit + polite delay). | open |
| B4 | `utils/response.get_response` | New `requests.get` per URL (new TCP+TLS handshake each time) and **always** parses the body with BeautifulSoup — including the JSON listing responses where the soup is unused. | Extra handshake per request; wasted CPU parsing large JSON as HTML. | Reuse one HTTP session; parse HTML only where needed. | open |
| B5 | `additional_info` | Commit after every row (fsync per job). | Minor vs network, but avoidable. | Commit per batch / per listing. | open |
| B6 | `populate_skills` | Fixed `time.sleep(20)` **before every call, including the first** → 90 jobs ≈ 30 min wall time regardless of actual limits. | Slow coverage growth. | Throttle based on the provider's rate-limit headers / backoff on 429 instead of a constant sleep. | open |
| B7 | `llm_service` | Creates a new Groq client on every call; no JSON-mode response format; reasoning model with default effort; prints whole response. | Extra setup per call; more malformed JSON; slower/longer responses. | One client per process; request JSON object output; lower reasoning effort for extraction; log instead of print. | open |
| B8 | `GET /api/jobs` | No pagination / limit; ~1 MB per unfiltered request; `required_skills` returned as a JSON *string* the client must re-parse. | Large payload on every filter change. | Paginate (limit/offset or cursor) and/or return only card fields; return skills as a list. | open → bug reproduced by test 2026-10-22 (1,642 rows, ~956 KB) |
| B9 | `filter_service` | Reads and parses `config.json` from disk on every `/api/filters` request. | Small but pointless I/O. | Load once (cache) — data only changes on deploy. | open |
| B10 | `/api/jobs` filter conditions | Four string comparisons on `required_skills` to exclude empty/failed rows; no index on `available`, `domain`, `city`. | Fine at 5k rows, scans at scale. | Use an explicit extraction-status column and index the filter columns if the table grows. | open |
| B12 | `get_available_for_extraction` (found 2026-10-22, while checking A1) | Skill extraction selects rows without filtering `available = 1`. The daily 90-call budget is spent on expired ads (e.g. the 293 mislabelled rows from A1) that the API never shows. | Wasted LLM calls; slower coverage of visible jobs. | Restrict extraction to available jobs, or prioritise them. | open → bug reproduced by test 2026-10-22 (25 of next 90 picks unavailable; 715 unavailable pending vs 1,572 available) |
| B11 | `requirements.txt` | Pins many unused heavy packages (streamlit, pandas, pyarrow, playwright, customtkinter, altair, pydeck, openai, google-genai, google-generativeai, `generativeai==0.0.1`…); `fastapi` unpinned; **uvicorn missing**. | Both workflows reinstall everything on every run → slower CI; API can't start from a clean install. | Trim to what's imported; pin fastapi; add uvicorn; consider pip caching in workflows. | open |

### C. Redundancy / structure
| # | Where | Issue | Recommendation | Status |
|---|---|---|---|---|
| C1 | `generate_urls.load_config`, `scraper.load_config`, `filter_service` | Same `config.json` loaded in three places, with two different `lru_cache` imports (`cachetools.func` vs `functools`) and a convoluted path in the scraper. | One config module used by all. | open |
| C2 | `FAILED_SENTINEL` | Defined in the service, duplicated as a literal in `jobCardsRepository`. | Single shared constant. | open |
| C3 | `jobsCardRoute` | Router calls the repository directly while `filterRoute` goes through a service; `jobs_card_service.py` exists but is empty. | Pick one layering rule and apply it to both. | open |
| C4 | Empty / unused files | `services/jobs_card_service.py`, `services/matcher_service.py` empty; `config/filters_config_bestjobs.json` and `identifier.sqlite` unreferenced. | Remove or document as reference data. | open |
| C5 | Entry points | `data_folder_setup()` runs in both `main.py` and `api/main.py`; `main.py` launches `main:app`, `dev.py` launches `backend.api.main:app`. | Keep one entry point and one startup hook. | open |
| C6 | URLs | Detail base URL in config (`/loc-de-munca/`) vs hardcoded ad link (`/ro/loc-de-munca/`) in the scraper. | Single source for URLs. | open |
| C7 | Schemas | Unused imports (`Dict`, `Any`, `List`), unused `sqlite3`/`DB_PATH` import in repository; jobs router tagged "Filters". | Cleanup. | open |
| C8 | `database_connect` | Returns `(cursor, conn)` and every caller manages closing manually. | A context-managed connection makes cleanup automatic and consistent. | open |
| C9 | `cv_parser` | Hardcoded `Test.pdf`, files opened without context managers, many `extract_text` args equal to defaults. | Parametrize input path when wiring it to the API. | open |

### D. Operational
| # | Issue | Recommendation | Status |
|---|---|---|---|
| D1 | Binary SQLite committed by two workflows; if the Monday scrape runs past 04:00, both push → `pull --rebase` on a binary file conflicts and one run's data is lost. | Add a workflow `concurrency` group or chain extraction after scrape. | open |
| D2 | Repo grows by a full DB copy per commit (daily). | Long-term: external storage / release artifact; short-term acceptable. | open |
| D3 | `allow_credentials=True` in CORS though no cookies/auth are used. | Disable unless needed. | open |

**Suggested priority:** A1, A2, B1, B11 (uvicorn), A4, B8, B6, then the redundancy cleanup.

---

## 2026-10-22 — CV parser: needed changes
- **Request:** make `backend/cv_parser/parser.py` extract the user's CV data.
- **History:** Claude implemented it once under a one-time access grant; the user reverted it and wants to implement it themselves. The list below is what the parser needs. The approach was verified: a real run on `Test.pdf` (3.6k chars of text) returned a valid structure.

| # | Problem in current parser | Needed change | Status |
|---|---|---|---|
| CV1 | Input is hardcoded to `data/cv/raw/Test.pdf`. | Make the CV source a parameter. pdfplumber accepts a path **or** a binary stream, so an uploaded file can be passed straight in without saving it first. | open |
| CV2 | `extract_text` returns `None` for image-only pages; adding `None` to the text string crashes. Pages are also glued together with no separator. | Skip pages with no text and join the rest with a blank line. If the whole CV has no text (scanned PDF), raise a clear error instead of sending an empty prompt to the LLM. | open |
| CV3 | Most `extract_text` arguments are just the defaults. | Keep only the tolerances you actually tune. | open |
| CV4 | The prompt names the categories but never defines the JSON shape, so key names and nesting change from run to run. | Write the exact JSON shape into the prompt, the way the job skill-extraction prompt does. Suggested: an object with `hard_skills` holding `entry_level`, `junior`, `mid_level` and `senior` lists, plus a `languages` list. State that every key is always present (empty list, never null/omitted) and that soft skills are excluded. Reuse the same "hard skill" definition as job extraction so CV and job skills can be compared later. | open |
| CV5 | The LLM reply is written to disk as raw text, never parsed or checked. | Parse it as JSON. Strip markdown code fences first (models add them despite instructions). Check that it is an object and fill any missing level/languages key with an empty list. Keep only non-empty strings and drop case-insensitive duplicates. On invalid JSON, raise or return an error, not a broken file. | open |
| CV6 | `parse_cv` returns nothing, so an API endpoint can't use the result. | Return the structured dict. Make saving to disk optional. | open |
| CV7 | Fixed output file names (`CV_Raw_Extracted_Data.txt`, `CV_Processed_Extracted_Data.txt`), so each new CV overwrites the previous one. The processed file is `.txt` though it holds JSON. | Name the outputs after the CV (or a user/session id). Save the processed result as `.json`. | open |
| CV8 | Files are opened/closed manually with no context manager, so they leak on exceptions. | Use context-managed writes, and create the folders if missing. | open |
| CV9 | The typo variable `promt` and the one-line prompt are hard to maintain. | Make the prompt a module-level constant in the same style as the skill-extraction prompt. | open |

**Related, outside the parser:**
- **CV10:** No upload endpoint exists. The FE sidebar only stores the file name. An endpoint should accept the uploaded file and hand its stream to the parser (CV1).
- **CV11:** The FE file input accepts `.csv`, but the parser reads only PDF. Either restrict the input to PDF or add a CSV path.
- **CV12:** `llm_service` caps `max_tokens` at 2000. With a reasoning model, reasoning tokens count toward that cap, so long CVs can come back truncated, which shows up as invalid JSON in CV5.
- **CV13:** Matching needs CV skills and job `required_skills` normalized the same way (case and synonyms).

---

## 2026-10-22 — DB test run findings (user-requested testing)
Tests run on DB copies with HTTP/LLM/SMTP mocked. Real DB verified untouched.

| # | Where | Issue | Needed change | Status |
|---|---|---|---|---|
| T1 | runner (A2 follow-up) | If **every** listing returns 200 with no items (block page, API change), the run counts as successful and **all jobs become unavailable** (test: 4 → 0, e-mail "updated: yes"). | Guard the final step: skip it when no slugs were seen, or when the seen count drops sharply compared with the current available count. | open |
| T2 | scraper listing request (A2 follow-up) | Fixed limit of 200 with no paging. Jobs beyond 200 are never seen, so they are set unavailable every week (test: 250 live → 50 hidden). Real combinations are already at 197–199. | Page through the listing until a page returns fewer items than the limit. | open |
| T3 | runner e-mail after an exception | After a crash the e-mail looks like a normal run ("Listings failed: 0", "updated: no"). Later listings are skipped, and the failing listing's earlier valid items are rolled back. | Record the exception in the totals and report it in the e-mail; per-item tolerance in the listing parsing (see A7). | open |
| T4 | skill extraction | Valid JSON wrapped in a markdown code fence gets the failure sentinel, so good skills are lost permanently. | Strip code fences before parsing (and/or request JSON-mode output, B7). | open |
| T5 | skill extraction e-mail | Coverage % is computed before the run, so it never reflects the run's work. | Compute it after the loop. | open |
| T6 | skill extraction | The count queries and the progress division run before the `try/finally`, so on A3 the connection is never closed (DB file stays locked on Windows). | Move all DB work inside the guarded block. | open |
| T7 | descriptions | 50 available rows lack a description: 24 NULL are never retried (detail pages are fetched only for new slugs); 26 empty strings pass `IS NOT NULL` and can be sent to the LLM as empty input. 3,664 older rows have a NULL `scraped_date`. | Retry missing descriptions on later runs; treat empty strings as missing (store NULL or filter them out of extraction). | open |
| T8 | `Jobs` table (raised by user 2026-10-22) | Dates are not stored for key events: when skills were extracted (or marked failed), and when a job was last seen online or became unavailable. Only `scraped_date` (first discovery) exists, and it is NULL for 3,664 older rows. This makes it impossible to tell how old an extraction is, re-extract after prompt/model changes, or measure how long ads stay online (useful for the paper). | Add an extraction date (set together with the skills or the failure marker) and a last-seen date (set from the scrape's seen slugs; it can also drive availability, see A2 discussion). Backfill is not possible for past events, so leave old rows NULL and document the start date. | open |

Test scripts (session scratchpad; re-runnable): `dbtests/common.py`, `test_runner.py`, `test_db.py`, `test_extract_api.py`.

