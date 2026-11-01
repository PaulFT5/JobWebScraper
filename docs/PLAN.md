# Plan — docs cleanup + 2-week minimal slice (2026-10-29)

## Context
JobWebScraper is the user's **bachelor thesis**. The learning focus is the backend matching work (grounding, embeddings, similarity, metrics). Routing is low priority. A job-market analyzer is a later bonus.

The user needs concrete guidance: what data, where it lives, how to use it, how the parts fit. The tracking docs have drifted from the code and from each other.

**New deadline (user, 2026-10-29):**
- **By ~2026-11-12**, a minimal working project:
  - at least **exact + fuzzy grounding**;
  - **one compare method (Chamfer)**;
  - the **end-to-end flow**: upload CV → click job → real score + missing skills in the UI.
- **By March 2027**, mostly done.
- Implementation is postponed, never dropped, unless time runs out.

Constraints: Claude edits docs/frontend only (hook). Backend is written by the user. Rule 5 applies: dated, nothing overwritten, change-log rows. Memory stays project-only, in `CLAUDE.md`.

## Decisions taken 2026-10-29 (to record)
| # | Decision | Replaces |
|---|---|---|
| P1 | Grounding stays at `backend/matching/grounding.py`. It is shared by job and CV skills; `esco/` = ESCO data layer only (loader, index, graph). | `esco/grounding.py` in the roadmap tree |
| P2 | **Chamfer first**, then Tversky → Soft Cosine → Hungarian. | Hardest-first order (Tversky first) |
| P3 | Slice uses an **in-memory dict** cache; `grounding.sqlite` follows in November. | Cache DB before embeddings (build step 6) |
| P4 | **Keep FastAPI** for the slice; T2 reconsidered after March, if at all. | "Reconsider week of 2026-10-26" |
| P5 | Thin end-to-end slice by ~2026-11-12, then deepen. | Strict dependency-driven build order to the end |
| P6 | Help depth: concrete guidance for each step (data, file/table, function/library call, inputs/outputs, how it connects) plus a tiny snippet of the key call. No full code. Full solution only when asked directly. | Rule 3 "snippet only when stuck" |

## Slice (user builds backend; Claude does FE on request)
*Assumption:* without step C, the matrix is 1.0 for the same ESCO concept or the same normalized string, else 0. Chamfer then = share of job requirements matched. Step C (embeddings + cosine) is a **stretch goal** inside the 2 weeks.

**Week 1 (10-29 → 11-04):**
1. Finish step B in `grounding.py`:
   - rapidfuzz `process.extract` over index keys of length ≥ `fuzzy_min_length`;
   - accept if score ≥ `fuzzy_threshold` **and** gap to 2nd ≥ `gap_acceptance_min`;
   - numbers must match;
   - return `MatchResult(method="fuzzy")`.
2. `ground(skill)` chains: exact → fuzzy → unresolved, with an in-memory dict cache.
3. CV parser minimum: CV1 (path/stream input), CV4 (fixed JSON shape, `cv_tier_map` names), CV5 (parse + validate), CV6 (return dict).

**Week 2 (11-05 → 11-11):**
4. Matrix: CV skills × job requirements (rule as in the assumption above).
5. `metrics/chamfer.py`: for each job requirement, take the best CV score; the result is the mean. Keep the per-requirement best match.
6. Minimal report: % score, best CV skill per requirement, missing requirements.
7. FastAPI: `POST` CV upload (session) + score for a job id (user).
8. FE (Claude, on request): replace the mock 72 (L5/I5), show missing skills, real upload (I4/CV11: PDF only).

**Stretch:** `embeddings.py` (bge-small, `model_folder` + `revision` from config) + step C full search, floor 0.80; cosine in the matrix.

**November → March, in order:**
- `grounding.sqlite` cache;
- step C if not done; acronyms + overrides; ambiguity rule (candidates + gap);
- ESCO graph + subsumption boost; seniority;
- Tversky → Soft Cosine → Hungarian;
- eval set (20 pairs) + batch grounding stats;
- full report; remaining CV items;
- analyzer (bonus); thesis writing (from `BE_IMPLEMENTATION.md`, start early).

## Doc edits (all dated 2026-10-29)

### `docs/MATCHING_ROADMAP.md`
- **Status ticks:**
  - Phase 0 skeleton/config → done 2026-10-26.
  - Requirements file → done 2026-10-26 (extract.yml part dropped).
  - Phase 1 normalization → done 2026-10-26.
  - Phase 2 index + A. Exact → done 2026-10-27.
  - Build step 4: "exact done 2026-10-27; fuzzy in progress 2026-10-28".
- **Goal line:** "every available job" → *until 2026-10-26*; current goal: one CV vs one clicked job.
- **File tree:**
  - `grounding.py` moved to `matching/` (P1);
  - add `match_result_object.py`;
  - note that `data/models` and `data/cache` are per-machine.
- **Config table:**
  - ESCO version → 1.2.1;
  - add a `model_folder` row;
  - "fuzzy min gap" → key `gap_acceptance_min`;
  - `grounding` group added 2026-10-28.
- **Step C:** clarify that the general search has no gap rule, while ambiguous-candidate search needs floor + gap.
- **Fără counts:** label the scope. 109 = available + skills (2026-10-22); 174 = all rows (2026-10-26); 2026-10-29: 178 all / 111 available / 95 available + skills.
- **New section "Minimal slice (since 2026-10-29)"** with the plan above, and the build-order changes P2/P3/P5 (old order kept with *until*).
- **New section "How it fits together"** — walkthrough. For each stage: input data, source (file/table/column), module + function, output type, where it goes next. Planned stages are marked *planned*. Stages:
  1. `Jobs.required_skills` JSON string / CV parser dict;
  2. filter the failure marker and empty lists;
  3. `normalization.py`;
  4. index simplification + `exact_match` → `MatchResult`;
  5. fuzzy;
  6. embeddings (encode ESCO labels once → vectors in `data/cache/`);
  7. grounding cache;
  8. matrix;
  9. seniority;
  10. Chamfer;
  11. report;
  12. API → FE.

  Worked example with "Python (Programming)", "MS Excel" and "CI/CD".
- **Change-log rows** for P1–P5 and the cleanup.

### `docs/BE_IMPLEMENTATION.md`
- **§1:**
  - thesis context, learning focus, analyzer = future bonus;
  - timeline: slice by ~2026-11-12, mostly done March 2027.
- **§2:**
  - T2: P4 note.
  - T10: v1.2.1, in progress since 2026-10-26.
  - T11: close the old row (*until 2026-10-26*) and add a new row: bge-small-en-v1.5 at its pinned revision, local/app server only, no CI.
  - T12 rapidfuzz: in progress 2026-10-28.
  - Update the "Last changed" dates.
- **§3:** matching engine → partially implemented, list the modules.
- **§5.4:**
  - status "in progress";
  - goal line fixed (old text → §10);
  - slice + P2/P3 summarized.
- **§7:** new "Setting up a new machine" subsection:
  - venv: `py -m venv .venv`; in the Claude `!` shell, bash needs forward slashes;
  - two `pip install -r` steps;
  - pip never installs model weights; the first load downloads from Hugging Face to `data/models/` only if `model_folder` is passed (otherwise `~/.cache/huggingface/hub`); alternatives: `hf download` or copy the folder;
  - `data/models` and `data/cache` start empty on a new machine;
  - the hook needs `.venv`;
  - laptop Python 3.14 vs CI 3.11.
- **§8:** new open items:
  - the relative `model_folder` path depends on the working directory;
  - cross-reference B11 (uvicorn missing, fastapi unpinned).
- **§9 change-log rows; §10** superseded texts.

### `docs/ASSIST_LOG.md` (status/notes only)
- CV4: "key names superseded 2026-10-26 by `cv_tier_map` (entry/junior/mid/senior)".
- DB test section: "tests moved to `tests/` (+ `test_index.py`) — 2026-10-29".

### `CLAUDE.md` (project memory)
- Project at a glance: add `backend/matching/` + `requirements-matching.txt`; thesis + learning focus; deadlines.
- Rule 3: add P6 (since 2026-10-29).
- Memory rule: project-only, in this file; no global memory.

## Verification
- Re-read each edited doc: every change has a date and a change-log row; nothing was deleted.
- Check every "done" claim against the code: `config.py`, `normalization.py`, `esco/loader.py`, `esco/index.py` (`exact_match`), `grounding.py`, `requirements-matching.txt`, `tests/test_index.py`.
- Search the docs for stale text outside history/superseded blocks: "MiniLM or", "v1.2.0?", "every available job", "esco/grounding.py".

---

# Plan — Analyzer page design (2026-10-30)

## Context
The user described the `/analyzer` page (currently a placeholder, FE_NOTES L4) with three sections:
1. **Extraction:** parsed skills, CV vs jobs, time per skill, method (exact / fuzzy / embedding), other performance metrics.
2. **Matching:** CV–job scoring, what matches what, insight into the algorithm.
3. **Jobs:** market overview, popular skills sortable by domain and week/year, most/least common per domain.

Goal of this step: **record the design only.** No code. Nothing is built before the minimal slice (~2026-11-12) is done.

## Decisions (user, 2026-10-30)
| # | Decision | Effect |
|---|---|---|
| AN1 | Build **after the slice** (November); design recorded now | The analyzer moves from "bonus after March" to "after the slice"; it waits for the batch grounding stats and `grounding.sqlite` |
| AN2 | Measure and store **all three** timings: grounding per skill, LLM extraction per job, CV parsing per upload | Grounding: new columns in the planned `SkillGrounding` table. LLM extraction: new `Jobs` columns written by the extraction service (user's backend change; links to ASSIST_LOG T8). CV: session only |
| AN3 | Skill rankings count **ESCO concepts**; unresolved skills are counted by normalized string | Needs the batch grounding of all job skills first |
| AN4 | CV data in the analyzer = **current session only** | Keeps the 2026-10-26 privacy decision; no stats across CVs |

## Sections (design to record)

### 1. Extraction
**Data needed:**
- `SkillGrounding` rows plus new columns: `duration_ms` (first lookup only; cache hits are not timed), `source` (job / cv).
- New `Jobs` columns: `extracted_at` (date), `extraction_ms`, optional `tokens`.
- CV parse time and grounding time, kept in the session.

**Views:**
- Coverage funnel: jobs → with description → extracted → failed.
- Share of skills found by each method; fuzzy score histogram.
- Latency per method (median, slowest 5%); LLM time per job; cache hit rate.
- Skills per job.
- Top unresolved skills: the to-do list for overrides and acronyms.
- The current CV's skills with method and time, shown next to the job aggregates.

**Caveat:** timings exist only from the date the columns are added. Older rows stay NULL; record that start date.

### 2. Matching (current session CV vs one chosen job)
- Similarity matrix heatmap.
- Lines from each requirement to its best CV skill, with score and method.
- Metric comparison (Chamfer in the slice; all four by March).
- Threshold / floor sliders, which recompute live.
- "Skills to learn": the most frequent missing concepts across one domain's jobs.

The match panel on the Jobs page keeps the compact view; the analyzer is the detailed view.

### 3. Jobs (market overview)
- Sortable table of top concepts, filterable by domain and by week/month of `scraped_date`.
- Most common and **distinctive** concepts per domain (common in this domain, rare elsewhere). Raw "least common" is mostly typos.
- Skills that often appear together.
- Experience level per domain; city × domain counts; salary vs skills where salary is given.
- Ad lifetime once a last-seen date exists (T8).

**Caveat:** `scraped_date` is the first-seen date and NULL for 3,664 older rows, so trends are reliable only from ~October 2026.

## Doc edits (dated 2026-10-30)
- **`docs/MATCHING_ROADMAP.md`:** new section "Analyzer page (design since 2026-10-30)" with AN1–AN4 and the three sections. Build order: step 17 stays "API endpoint + analyzer page", now *after the slice* (AN1). Add `duration_ms` and `source` to the planned `SkillGrounding` columns. Change-log row.
- **`docs/BE_IMPLEMENTATION.md`:**
  - §1 timeline: analyzer moves to after the slice; the superseded row gets *until*.
  - §5.4: timing columns in the grounding cache.
  - §8: new `Jobs` timing columns as a planned data-model change (T8 link).
  - §9 change-log rows.
- **`frontend/FE_NOTES.md`:** add to L4 the design reference to the roadmap and "build after the slice". Change-log row.
- **`docs/ASSIST_LOG.md`:** T8 note, append only — "2026-10-30: extraction timing/date requested for the analyzer (AN2)".

## Verification
- Every new item carries 2026-10-30; nothing deleted; replaced timeline row has an *until* date.
- The analyzer design is consistent with P3 (in-memory cache in the slice; the analyzer only after `grounding.sqlite` exists) and with the 2026-10-26 CV privacy decision.

---

# Plan — Jobs tab, view 1: "Most required skills" (2026-10-30)

## Context
The user finds the Jobs-tab tables hard to read and not relevant to the thesis. The tab is redesigned **one view at a time**. This section settles view 1 only; the other views (slope, specificity, bundles, treemap, must-have, experience level) are decided later, one by one, and stay untouched until then.

## Decisions (user, 2026-10-30)
| # | Decision |
|---|---|
| J1 | **Chart only**: no table, no Chart/Table toggle. Exact numbers live in the bar labels and the tooltip. |
| J2 | **Horizontal bars**, ranked high → low: full skill name on the left in one line, bar to the right. |
| J3 | **Top 10** skills. |
| J4 | Axis = **% of postings**; label at the bar end = `24% · 412 jobs`. |
| J5 | **100% = postings with extracted skills** that match the filters (no failure marker, non-empty list). Not extracted / failed ads are left out. |
| J6 | Counted **by ESCO concept, once per job** ("Excel" and "MS Excel" in one ad count once). Shown with the short name (qualifier removed). |
| J7 | Skills **not in ESCO** (Docker, CI/CD) are included, counted by their cleaned name, with a small **"not in ESCO"** marker. |
| J8 | Filters: **Domain, Experience level, City, Period**. |

## Frontend (mock, Claude)
- **New `frontend/src/lib/components/analyzer/TopSkillsBars.svelte`**, replacing `ShareColumnChart.svelte` (deleted):
  - grid rows `[name | bar | label]`;
  - one teal hue for every bar (a ranking, not identities);
  - "not in ESCO" as a small outlined tag after the name, plus a hatched lighter bar, so it is never shown by color alone;
  - tooltip: full ESCO label, share, jobs, and how many postings the 100% is.
- **`JobsView.svelte`:**
  - filter row with Domain, Experience (labels from `EXPERIENCE_LABELS` in `lib/jobs.ts`), City and Period. Domain and city options come from `/api/filters` (layout data), so `analyzer/+page.svelte` also passes `cities`;
  - remove the table, the toggle, the sort state and `rows`/`maxJobs`;
  - subtitle: "% of N postings with extracted skills · filters";
  - "click to highlight" is removed: it only existed for the slope chart, which is decided later. The slope keeps its default highlight of the top 6 until then.
- **`analyzerMock.ts`:** `topSkills(filters)` returns `{ postings, skills: [{ concept, label, jobs, share, inEsco }] }`, top 10 by share; mock includes 2 unresolved skills (Docker, CI/CD). `topConcepts`/`ConceptRow` are removed if nothing else uses them.
- **`FE_NOTES.md`:** dated change-log row.

## Backend data path (user implements later, after batch grounding; recorded in docs)
1. Filter `Jobs` by `domain`, `experience_level`, `city` and `scraped_date` (period), with `available = 1` and extracted skills only → the 100%.
2. Per job: `json.loads(required_skills)` → each string → grounding cache (`data/cache/grounding.sqlite`, filled by the batch script) → concept key (ESCO URI, or `unresolved:<cleaned key>`). Make it a set per job.
3. Count jobs per key; share = count ÷ jobs in the set; top 10.
4. Label: ESCO preferred label from `esco/loader.py` (qualifier removed), or the cleaned string for unresolved; `inEsco` flag.
5. Endpoint (FastAPI, P4), e.g. `GET /api/analyzer/top-skills?domain=&level=&city=&period=` → `{ postings, skills: [...] }`. ~1.7k jobs × ~9 skills: fine in Python per request. Optional later: a rebuildable `JobSkill(slug, concept_key)` table in the cache DB.
6. **No ESCO hierarchy / "ESCO domain" data is needed** for this view (only for a future treemap).

## Docs (dated 2026-10-30)
- `docs/MATCHING_ROADMAP.md` → *Analyzer page* §3: view 1 spec (J1–J8) and the data path; change-log row.
- `docs/BE_IMPLEMENTATION.md` §9: change-log row (Analyzer design, view 1).

## Verification
- `npx svelte-check` (0 errors, 0 warnings) and `npx vite build` in `frontend/`.
- The rendered `/analyzer` contains 10 bars, `% · N jobs` labels, the "not in ESCO" marker on the mock unresolved skills, the four filters, and no table/toggle.
- Changing a filter changes the bars and the postings count in the subtitle.

---

# Plan — Analyzer: real data on top, previews grayed below (2026-10-30)

## Context
Only some analyzer views can be filled with trustworthy data today. The user's spec (pasted 2026-10-30, numbers verified against the DB) puts verified counts on top and moves everything else into a grayed "preview" section below the fold.

## Decisions (user, 2026-10-30)
| # | Decision |
|---|---|
| R1 | **Extraction tab, real:** (1) coverage: 3 KPI cards + a 100% segmented bar (extracted / waiting / no description / empty / failed), an inspection drawer for empty and failed ads, and a warning banner for ads processed with an empty description (T7); (2) skills-per-job histogram: bins 1–3 … 21+, median line, max-outlier badge with an ad link. |
| R2 | **Jobs tab, real:** (3) experience level ordered by career stage, NULL shown as coverage in the subtitle, "No experience" and "Entry" kept separate; (4) jobs per domain and per city, cross-filtered by click; domains with 0 extracted (Management) pinned at the bottom as queued; footnote that a multi-city ad is stored once. |
| R3 | **Everything else is a preview:** 48px gap, dashed divider, header "Pending grounding & time-series backfill (preview only)", opacity 0.45 + grayscale 80%, full colour on hover. |
| R4 | **Matching tab:** kept, fully in the preview style. |
| R5 | **Data:** the Jobs views and the histogram compute from `/api/jobs` (= the 1,757 extracted available ads). Coverage, the drawer, the warning and the queued counts come from a **new endpoint the user writes first**: `GET /api/analyzer/coverage`. Until it exists, those parts say so; no fake numbers. |

## Endpoint spec (backend, the user implements)
See `docs/MATCHING_ROADMAP.md` → *Analyzer page* → coverage endpoint.

## Frontend (Claude)
- `lib/api/fetchCoverage.ts`: a 404 shows the "endpoint not available yet" state.
- New components in `components/analyzer/`: `PreviewSection`, `CoverageCard`, `SkillsHistogram`, `ExperienceLadder`, `DomainCityCards`.
- Analyzer page fetches `/api/jobs` once and passes the list down; JobsView / ExtractionView / MatchingView rearranged.

## Verification
- svelte-check and the build pass.
- The rendered page shows 1,757-based numbers (levels 95/220/527/247/61 + 607 unspecified; cities 782/546/429; bins 324/465/358/195/141/141/133).
- Coverage shows the "endpoint not available yet" state.
