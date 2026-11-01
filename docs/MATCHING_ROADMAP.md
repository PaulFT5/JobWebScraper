# Matching Engine — Roadmap

*Created: 2026-10-22 · design recorded in `docs/BE_IMPLEMENTATION.md` §5.4 (T10–T13)*

*(Since 2026-10-26)* Score a user's CV against **one clicked job** (available, with extracted skills) and explain the score. English-only ESCO grounding, relative seniority, similarity matrix, set-matching metrics. *(Until 2026-10-26: score a CV against every available job with extracted skills.)*

**Context (2026-10-29):** this engine is the core of the user's bachelor thesis; the learning focus is grounding, embeddings, similarity and metrics. Deadlines: minimal working slice by ~2026-11-12 (see *Minimal slice*), engine mostly done by March 2027. Parts are postponed, never dropped, unless time runs out. A job-market analyzer is a later bonus.

**Status convention:** `[ ]` open, `[x]` done. Status changes keep their history, e.g. `open → done 2026-11-03`. Nothing is deleted; replaced items get *Until* dates.

---

## Data facts behind the design (2026-10-22)
- `Jobs`: 5,203 rows, 3,332 available; 1,733 available **with** extracted skills, 1,572 still in the extraction backlog (90/day) → matching covers only jobs with skills.
- 12,799 distinct skill strings: 9,864 seen once, 1,091 differ only by case; ~9 skills per job.
- Failure marker `["__EXTRACTION_FAILED__"]` (13 rows) and 163 empty lists.
- 255 distinct skills contain a slash, mostly single concepts (CI/CD 72, SAP S/4HANA 26, A/B testing 21, TCP/IP 20, PL/SQL, Legea 98/2016).
- ≥280 Romanian skills → **English only**: they go to the unresolved path and mostly won't match.
- Job `experience_level` (available + skills): Middle 508, Entry 253, Senior 240, Executive 59, "Fără" 109, NULL 564 → 39% without a level.
  - *(2026-10-29)* Count scopes clarified: 109 = available jobs **with skills** (2026-10-22); the 174 in the 2026-10-26 change log = **all rows**. Re-count 2026-10-29: "Fără" 178 all rows / 111 available / 95 available + skills.
- CV output: tiers entry_level / junior / mid_level / senior + languages; unvalidated; unknown experience currently defaults to entry_level.
- Both workflows install `requirements.txt` → sentence-transformers there would pull ~2 GB of CUDA torch into every run.

## Target structure
*Last changed: 2026-10-29 (grounding.py location, match_result_object.py, per-machine folders, config table synced with config.json)* · before: 2026-10-26 (Fără job level, CV tier names, embedding model, step D postponed, acronym list, on-click flow)

### File organization
```
backend/
├── matching/                      ← engine, plain Python in/out, no web framework
│   ├── __init__.py
│   ├── config.json                ← all tunable values (table below)
│   ├── config.py                  ← load once + cache, validate, ignore metadata notes, config fingerprint
│   ├── normalization.py           ← one shared cleaning function (ESCO labels, job skills, CV skills)
│   ├── match_result_object.py     ← shared `MatchResult` (status match / ambiguous / not found, concept, candidates, label kind, key, score, method) (since 2026-10-27)
│   ├── grounding.py               ← overrides → cache → acronyms → A → B → C → unresolved; one pipeline for job AND CV skills; fuzzy (B) started here 2026-10-28 (location since 2026-10-29, see below)
│   ├── esco/                      ← ESCO data layer only: knows nothing about embeddings, cache or CVs
│   │   ├── __init__.py
│   │   ├── loader.py              ← reads ESCO CSVs (multi-line alt/hidden labels)
│   │   ├── index.py               ← normalized label → URI(s); exact lookup (A); ambiguity flags
│   │   └── graph.py               ← broader / narrower relations, depth, parent
│   │   *(until 2026-10-29: `esco/grounding.py` ← overrides → table → acronyms → A → B → C → unresolved; fuzzy (B) listed in `index.py`)*
│   ├── embeddings.py              ← local model wrapper + vector cache
│   ├── similarity.py              ← matrix, subsumption boost, caps, threshold, seniority
│   ├── metrics/
│   │   ├── __init__.py            ← metric name → strategy
│   │   ├── base.py                ← shared interface (matrix + metadata in, score + alignments out)
│   │   ├── tversky.py
│   │   ├── soft_cosine.py
│   │   ├── hungarian.py
│   │   └── chamfer.py
│   ├── report.py                  ← %, per-requirement attribution, gaps, extra skills, ranking
│   └── engine.py                  ← orchestrates the pipeline
├── services/
│   ├── skill_grounding_service.py ← on-click grounding of a job's / CV's skills + local batch script for stats (since 2026-10-26; until then: offline batch after daily extraction)
│   └── matcher_service.py         ← online entry point: CV + jobs → engine
└── database/repositories/
    └── skillGroundingRepository.py ← grounding cache access (`data/cache/grounding.sqlite`, since 2026-10-26; until then: SkillGrounding table in JobsDatabase)

data/
├── esco/                          ← committed
│   ├── skills_en.csv
│   ├── skill_Pillars.csv          ← ESCO broaderRelationsSkillPillar_en (renamed 2026-10-23)
│   ├── skill_Hierarchy.csv        ← ESCO skillsHierarchy_en (renamed 2026-10-23)
│   └── overrides                  ← manual corrections (always win)
├── models/                        ← downloaded embedding model, git-ignored
├── cache/                         ← vectors, git-ignored, rebuilt when missing
└── eval/                          ← hand-labelled CV–job pairs
```
*(2026-10-29)* `data/models/` and `data/cache/` are **per machine**: git never carries them, so a new machine starts without the model and with an empty cache (see `BE_IMPLEMENTATION.md` §7, *Setting up a new machine*). `data/eval/`, `data/esco/overrides` and the acronym file don't exist yet (planned).

### Config contents (`backend/matching/config.json`)
| Group | Setting | Starting value | Purpose |
|---|---|---|---|
| esco | version | `1.2.1` (confirmed 2026-10-26; until then "v1.2.0?") | Reproducibility; stored with every grounding row |
| | language | "en" | English-only decision |
| | data folder | `data/esco` | CSV location |
| model | name | `BAAI/bge-small-en-v1.5` (chosen 2026-10-26) | Embedding model, 384-dim |
| | revision | `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a` (latest on 2026-10-26) | Pinning |
| | model folder (`model_folder`, added 2026-10-29 to this table) | `data/models` | Where the model weights are downloaded; must be passed to sentence-transformers as its cache folder, otherwise it downloads to `~/.cache/huggingface/hub`. Relative path → see open question in `BE_IMPLEMENTATION.md` §8 |
| | cache folder (`cache_folder`) | `data/cache` | Vectors |
| grounding *(group in `config.json` since 2026-10-28)* | fuzzy threshold (`fuzzy_threshold`) | 90 | Step B acceptance |
| | fuzzy min gap to 2nd best (`gap_acceptance_min`) | 5 | Avoid ambiguous fuzzy matches |
| | fuzzy min length (`fuzzy_min_length`) | 4 | Short skills (C, R, Go) exact only |
| | embedding floor (`embedding_floor`) | 0.80 (fixed 2026-10-26; no gap rule for now) | Step C acceptance |
| | parent candidates | 10 | Step D candidate list size *(postponed 2026-10-26, may not be implemented)* |
| | LLM parent enabled | true → false 2026-10-26 | Switch step D off *(postponed 2026-10-26, may not be implemented)* |
| similarity | boost specific → broad | e.g. 0.90 | Strong direction |
| | boost broad → specific | e.g. 0.50 | Weak direction |
| | noise threshold | 0.35 | Below → 0 |
| seniority | job level map | Fără 0, Entry 0, Middle 2, Senior 3, Executive 3 (Fără added 2026-10-26) | Keys = DB `experience_level` values; NULL → no penalty |
| | CV tier map | entry 0, junior 1, mid 2, senior 3 (since 2026-10-26; until 2026-10-26: entry_level / mid_level) | Canonical CV tier names; the parser maps its output onto them |
| | multipliers by tiers below | 0: 1.00, 1: 0.85, 2: 0.65, 3: 0.45 | Discount |
| | unknown CV tier / no job level | 1.00 | No penalty |
| metrics | default | "chamfer" | UI default |
| | Tversky α / β | e.g. 0.8 / 0.2 | Missing requirements weigh more than extra skills |
| report | gap threshold | 0.5 (tune) | Missing vs matched |

*(2026-10-29)* Groups `similarity`, `metrics` and `report` (and the step D rows) are not in `config.json` yet; they are added with their build steps. Names in backticks are the real keys.

### Build order (dependency-driven)
1. `config.json` + `config.py` — open → done 2026-10-26 (esco, model, seniority groups; other groups added with their steps)
2. `normalization.py` — open → done 2026-10-26
3. `esco/loader.py` — open → done 2026-10-26
4. `esco/index.py` — exact, then fuzzy — exact: open → done 2026-10-27 (`exact_match`, `tests/test_index.py`); fuzzy: open → in progress 2026-10-28 (in `grounding.py` since 2026-10-29, decision P1) → done 2026-10-29 (`fuzzy_match`)
5. `esco/graph.py`
6. Grounding cache DB `data/cache/grounding.sqlite` (git-ignored) + repository *(since 2026-10-26)* — until 2026-10-26: `SkillGrounding` table in `JobsDatabase.sqlite`
7. `embeddings.py`
8. `grounding.py` *(at `backend/matching/` since 2026-10-29; until then `esco/grounding.py`)* — overrides → table → A → B → C; local batch script over all job skills for stats *(since 2026-10-26)*; **then** step D *(postponed 2026-10-26, may not be implemented)*
9. CV parser rework (independent; any time before 10)
10. Hand-labelled eval set
11. `similarity.py`
12. `metrics/base.py` + `tversky.py`
13. Minimal `engine.py` + `report.py` (first end-to-end result)
14. `soft_cosine.py` → `hungarian.py` → `chamfer.py`
15. Full `report.py` (gaps, extra skills, ranking)
16. `matcher_service.py` (on click: ground unseen job skills, score one CV vs one job) *(since 2026-10-26)* — until 2026-10-26: + grounding step in `extract.yml` with CPU torch (dropped: no matching work in GitHub Actions)
17. API endpoint + analyzer page (after the API decision) — *(2026-10-30)* analyzer after the minimal slice (AN1), design in *Analyzer page* below

*(2026-10-29)* This order still holds for the full engine, but it is now reached **through the minimal slice first** (below): exact + fuzzy → matrix → Chamfer → minimal report → endpoints → FE, then the remaining steps. Changes to the order: Chamfer is the first metric (P2); the grounding cache (step 6) starts as an in-memory dict and becomes `grounding.sqlite` in November (P3).

## Minimal slice (since 2026-10-29)
**Goal by ~2026-11-12:** the end-to-end flow works with real data: upload a CV → click a job → see a real score and the missing skills in the UI. Minimum: exact + fuzzy grounding and one compare method (Chamfer). Accuracy is secondary; nothing below is dropped, only sequenced.

| # | Decision (2026-10-29) | Replaces |
|---|---|---|
| P1 | Grounding lives at `backend/matching/grounding.py`: one pipeline used for job **and** CV skills; `esco/` stays the ESCO data layer (loader, index, graph). | `esco/grounding.py` in the file tree |
| P2 | **Chamfer first**, then Tversky → Soft Cosine → Hungarian. Chamfer is the simplest, the UI default, and its per-requirement output is exactly what the report needs. | Hardest first (Tversky first, Chamfer last) |
| P3 | Grounding cache starts as an **in-memory dict** (lost on restart); `grounding.sqlite` follows in November. | Cache DB built before embeddings (build step 6) |
| P4 | **Keep FastAPI** for the slice; T2 reconsidered after March, if at all (routing is low priority for the learning goal). | "Reconsider week of 2026-10-26" |
| P5 | Thin end-to-end slice by ~2026-11-12, then deepen in the build order. | Strict dependency-driven order to the end |

*Assumption:* without step C, a matrix cell is 1.0 when both skills have the same ESCO concept or the same normalized string, otherwise 0. Chamfer then equals the share of job requirements the CV covers. Step C (embeddings + cosine) is a **stretch goal** inside the 2 weeks.

**Week 1 (2026-10-29 → 11-04)** — open
- [x] *(open → done 2026-10-29)* Step B in `grounding.py`: rapidfuzz `process.extract` over index keys with length ≥ `fuzzy_min_length`, scorer `fuzz.ratio` (whole string); accept only if best ≥ `fuzzy_threshold` **and** best − second ≥ `gap_acceptance_min`; digits in input and key must be equal (ISO 9001 ≠ 14001); return `MatchResult(method="fuzzy", score=…)`.
- [ ] `ground(skill)`: normalize → exact → fuzzy → unresolved, results kept in an in-memory dict (P3).
- [ ] CV parser minimum (ASSIST_LOG CV1, CV4, CV5, CV6): file path/stream as input, fixed JSON shape with the `cv_tier_map` names, parsed and validated reply, returns a dict.

**Week 2 (2026-11-05 → 11-11)** — open
- [ ] Matrix: rows = job requirements, columns = CV skills, cell rule as in the assumption above.
- [ ] `metrics/chamfer.py`: per requirement, the best value in its row (and which CV skill gave it); score = mean of those bests × 100.
- [ ] Minimal report: % score, best CV skill per requirement, missing requirements (best = 0).
- [ ] FastAPI (user): CV upload → parsed + grounded CV for the session; score for a job id.
- [ ] Frontend (Claude, on request): real score instead of the mock 72 (FE_NOTES L5/I5), missing skills, PDF-only upload (I4/CV11).

**Stretch** — open
- [ ] `embeddings.py` (bge-small, `model_folder` + `revision` from config) + step C full search with floor 0.80; matrix cell = cosine for unmatched pairs.

**After the slice (November → March, in this order):** `grounding.sqlite` cache → step C (if not done) → acronym list + overrides → ambiguity rule in step C (candidates + gap) → `esco/graph.py` + subsumption boost → seniority → Tversky → Soft Cosine → Hungarian → eval set (20 pairs) + batch grounding stats → full report → remaining CV items → analyzer (bonus). Thesis writing from `BE_IMPLEMENTATION.md`, started early.

## How it fits together (walkthrough, since 2026-10-29)
One skill's path from the data to the screen. For each stage: **what goes in**, **where it comes from**, **which module/function**, **what comes out**, **where it goes next**. *Done* = exists in code; *planned* = not written yet.

| # | Stage | In | From | Module / call | Out | Next | State |
|---|---|---|---|---|---|---|---|
| 1 | Read job skills | JSON **string** like `'["Python (Programming)", "MS Excel", "CI/CD"]'` | `Jobs.required_skills` in `data/jobs/JobsDatabase.sqlite` | repository query + `json.loads` | `list[str]` | 2 | read side exists (API); matching reader planned |
| 1b | Read CV skills | uploaded PDF | user upload (session only) | `cv_parser` → Groq | `{"hard_skills": {"entry": [...], "junior": [...], "mid": [...], "senior": [...]}, "languages": [...]}` | 2 | rework planned (CV1–CV9) |
| 2 | Filter | `list[str]` | stage 1 | skip `["__EXTRACTION_FAILED__"]` and `[]` | clean `list[str]` | 3 | planned |
| 3 | Normalize | `"Python (Programming)"` | stage 2 | `normalization.py` | `"python (programming)"` | 4 | done 2026-10-26 |
| 4 | Simplify + exact (A) | normalized string | stage 3 + index built once from `data/esco/*.csv` (`esco/loader.py` → `esco/index.py`) | `exact_match(skill)` (simplifies: hyphens → spaces, trailing qualifier removed) | `MatchResult` — `"python"` → *match*, concept = ESCO URI for Python | done → 7; not found → 5; ambiguous → 6 (candidates) | done 2026-10-27 |
| 5 | Fuzzy (B) | `"ms excel"` (no exact key) | stage 4 | `grounding.py`, rapidfuzz over index keys | `MatchResult(method="fuzzy")` or not found | found → 7; else → 6 | in progress |
| 6 | Embedding (C) | string still not found | stage 5 | `embeddings.py`: ESCO labels encoded **once** → vectors saved in `data/cache/`; input encoded → cosine vs all labels (or only the candidates when ambiguous) | best concept if ≥ 0.80, else *unresolved* (raw string kept) | 7 | planned (stretch) |
| 7 | Cache | skill → `MatchResult` | stages 4–6 | dict (slice) → `grounding.sqlite` (November) | same result reused for every later job/CV | 8 | planned |
| 8 | Matrix | job requirements × CV skills, both grounded | stage 7 | `similarity.py` | 2-D table of values 0–1 (same concept or same unresolved string → 1.0) | 9 / 10 | planned |
| 9 | Seniority | job `experience_level`, CV tier of each skill | `Jobs.experience_level`, CV dict, `seniority` config | `similarity.py` | matrix × multiplier (e.g. CV junior vs Senior job → 0.65) | 10 | planned (after slice) |
| 10 | Metric | matrix | stage 8/9 | `metrics/chamfer.py` | score 0–100 + best CV skill per requirement | 11 | planned (slice) |
| 11 | Report | metric output | stage 10 | `report.py` | % score, matched, missing (and later under-qualified, extra skills) | 12 | planned (slice: minimal) |
| 12 | Serve + show | report | stage 11 | `matcher_service.py` → FastAPI endpoint → SvelteKit match panel | JSON → UI | — | planned (slice) |

**Worked example** (job requires `Python (Programming)`, `MS Excel`, `CI/CD`; CV lists `python`, `Excel`):
- `Python (Programming)` → normalize → simplify to `python` → **exact** hit → ESCO *Python* concept. CV `python` reaches the same concept → cell = 1.0.
- `MS Excel` → no exact key → **fuzzy** may reach an Excel/spreadsheet label if it scores ≥ 90 with a clear gap; if not, step C (embedding) is the fallback; if that fails too, it stays *unresolved* and matches only the equal string.
- `CI/CD` → not in ESCO → *unresolved*; it matches only a CV skill that normalizes to `ci/cd`. The CV has none → cell = 0.
- Chamfer over the three rows: (1.0 + Excel's value + 0) / 3 → between 33% and 67%; report lists `CI/CD` as missing.

### ESCO normalization rules (from the downloaded files, 2026-10-22)
- 13,960 concepts, 101,745 labels (preferred + alt + hidden); alt/hidden labels are newline-separated inside one quoted cell → proper CSV reader.
- Keep per concept: URI, original preferred label (display), all labels, skill type, reuse level, description. 5 rows have no skill type.
- Normalize: Unicode NFKC → unify apostrophes/quotes → casefold → collapse spaces/trim → strip punctuation **only at the ends** (keep C++, C#, .NET, CI/CD, R&D) → no stemming, no stopword removal.
- *(Until 2026-10-27)* Extra index entries: hyphen-as-space variant (3,776 labels with "-"); trailing qualifier stripped ("Java (computer programming)" → "java"; not leading, e.g. "(a9t9) FreeOCR").
- *(Since 2026-10-27)* **Index key simplification (Way 2)** instead of extra entries: every label is simplified before indexing — hyphens → spaces, trailing qualifier removed (not leading/middle brackets), then normalized again — and only the simplified key is stored, with the label's own kind. The lookup **must** apply the same simplification to every job and CV skill (symmetric; also covers inputs with hyphens/qualifiers). Data check 2026-10-27: qualifier removal 37 labels, 0 cross-concept collisions; hyphen replacement ~3,770 labels, 1 collision (pay-per-click), which becomes an ambiguous key handled by step C.
- 692 normalized labels map to several concepts → ambiguous; preferred-label match may win over alt-label match.
  - *(2026-10-27, decided)* Resolved once at index build: per key, dedupe candidates by concept (keep each concept's best label kind), rank **preferred > alt > hidden > derived variant** (hyphen-as-space, qualifier stripped; *derived rank unused since 2026-10-27, Way 2*), keep only concepts at the best rank present; one left → match, several → ambiguous (no guess, passes to step C). Report raw collisions and those still ambiguous after ranking. Open: whether ambiguous keys carry their candidates into step C. → *(2026-10-27, decided: option A)* ambiguous keys keep their candidates; step C compares the input only against them, accepts the best if ≥ 0.80 floor **and** a clear gap to the second (gap value to tune), else unresolved; stored with its own method (exact → embedding among candidates).
- Index built in memory at startup, not stored.
- Open: damaged characters (`�`, e.g. "Earth�s", "canap�s") — re-download or map to apostrophe; ESCO version to confirm.
- Not in ESCO (exact): Kubernetes, Docker, Microsoft Excel, AutoCAD, CI/CD → handled by steps C/D and overrides.

### Other components
- `backend/services/skill_grounding_service.py` — grounds a job's skills on first click and a CV's skills at upload; local batch script for paper stats *(since 2026-10-26)*. *(Until 2026-10-26: batch grounding of new job skills after daily extraction.)*
- `backend/services/matcher_service.py` — thin wrapper: CV + jobs → engine.
- `backend/database/repositories/skillGroundingRepository.py` — table `SkillGrounding` in a separate git-ignored file `data/cache/grounding.sqlite` *(since 2026-10-26)*; rebuildable cache, never committed (avoids binary merge conflicts with the daily `JobsDatabase.sqlite` commits); also model revision and config fingerprint per row. Columns: raw skill, normalized form, ESCO URI, **relation** (same as / narrower than), method (exact / fuzzy / embedding / llm_parent / manual), score, ESCO version, date. *(Added 2026-10-30, AN2)* `duration_ms` (time of the first lookup), `source` (job / cv).
- `data/esco/` — pinned ESCO English CSVs, committed.
- `data/esco/overrides` — manual skill → concept / parent corrections (always win).
- Vectors — local cache, git-ignored, rebuilt when missing.
- Separate matching requirements file; CPU-only torch installed locally / on the app server only *(since 2026-10-26)* (until 2026-10-26: only in `extract.yml`).

---

## Phase 0 — Groundwork
- [x] Download ESCO v1.2.x English CSVs (`skills_en`, `broaderRelationsSkillPillar_en`, `skillsHierarchy_en`) into `data/esco/`; record the version. — open → done 2026-10-26 (v1.2.1 in config)
- [x] Pin the embedding model name + revision in config (all-MiniLM-L6-v2 or bge-small-en-v1.5). — open → done 2026-10-26
  - *(2026-10-26)* Model chosen: `BAAI/bge-small-en-v1.5`, revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`. Model in `data/models/`, vectors in `data/cache/`, both git-ignored. Config entry added 2026-10-26.
- [x] Create the package skeleton and config (weights, thresholds, α/β, model, ESCO version). — open → done 2026-10-26 (skeleton + esco/model/seniority groups; grounding group 2026-10-28; the other groups come with their steps — noted 2026-10-29)
- [x] Separate matching requirements file; CPU torch step in `extract.yml`; `scrape.yml` unchanged. — open → done 2026-10-26 (file created; `extract.yml` part dropped, see below — ticked 2026-10-29)
  - *(2026-10-26)* `requirements-matching.txt` created (CPU torch index, torch 2.14.1+cpu, sentence-transformers 6.2.0, rapidfuzz 3.14.6, all pinned); `extract.yml` step **not needed** (2026-10-26: grounding happens on click, not in GitHub Actions).
- [ ] Filter the failure marker and empty lists in every skill reader.
- [ ] Optional: extraction prompt asks for English skill names.
- [ ] Hand-label ≈20 CV–job pairs in `data/eval/`.

## Phase 1 — Input preprocessing
- [x] Normalization: casefold, trim/collapse spaces, punctuation cleanup, small curated acronym list (ESCO alt labels first). Same function for ESCO labels and for input skills. — open → done 2026-10-26 (ticked 2026-10-29; acronym part moved to Phase 2)
  - *(2026-10-26)* Acronym list moved to grounding (Phase 2), applied after normalization; the normalization function itself is done (build step 2).
- [ ] Compound split ("/", "&", "and") only if the whole string fails grounding **and** every part grounds confidently; never around digits. (CI/CD stays whole, C/C++ splits.)
- [ ] CV parser returns a validated structure; tiers entry / junior / mid / senior / **unknown**; skill in several tiers → highest.
  - *(2026-10-26)* Config `cv_tier_map` is the source of truth for tier names. The prompt names the exact keys; an alias table maps variants (`entry_level`, `Entry-level`, `mid_level`, `middle`, …; case-insensitive) to canonical keys; anything unrecognized → `unknown` (no default to entry).
- [ ] Job requirements: flatten, normalize, dedupe (by URI after grounding).
- [ ] Map job level: Fără/Entry→0, Middle→2, Senior/Executive→3, NULL→none. *(Since 2026-10-26; until 2026-10-26: "Fără"/NULL→none.)*

## Phase 2 — ESCO grounding (English)
Lookup order for every skill: **overrides → `SkillGrounding` table → acronym list → steps A–C.** *(Since 2026-10-26; until then: overrides → table → steps A–D.)*

- [x] **Index:** preferred, alt and hidden labels → URI; each label also indexed without its qualifier ("Python (computer programming)" → "python"); labels pointing to several concepts marked ambiguous. — open → done 2026-10-27 (as Way 2: only the simplified key is stored; see *ESCO normalization rules*)
- [ ] **Concept graph:** broader/narrower relations, depth, parent.
- [x] **A. Exact** — normalized string equals an indexed label. Ambiguous label → don't guess, pass to C. — open → done 2026-10-27 (`exact_match` in `esco/index.py`, returns `MatchResult`)
- [x] **B. Fuzzy** (rapidfuzz) — open → in progress 2026-10-28 (`grounding.py`) → done 2026-10-29 (`fuzzy_match`; strict digit rule: numbers must be equal) — whole-string scoring (no partial: "Java" ≠ "JavaScript"); threshold ≈90, tuned on samples; clear gap to second-best or treat as ambiguous; no fuzzy for short strings (C, R, Go); numbers must match exactly (ISO 9001 vs 14001).
- [ ] **Acronym list** *(added 2026-10-26)* — small file in `data/esco/`: acronym → ESCO preferred label (e.g. erp → *manage standard enterprise resource planning system*, seo → *search engine optimisation*, vpn → *implement a virtual private network*). Applied before step A, only when the whole normalized input equals an entry; method `acronym`. Every target must resolve to exactly one concept in the index at load (fails loudly otherwise; catches renamed labels in a new ESCO version). Only frequent acronyms that A–C miss or get wrong, picked from the first batch run's stats; ambiguous ones (PC, REST) left out. Acronyms with no ESCO concept (XML, SCADA, FMEA, CI/CD) stay unresolved and still match on equal strings.
- [ ] **C. Embedding** — nearest ESCO concept above a confidence floor ("spreadsheet software" ↔ *use spreadsheets software*). *(2026-10-26)* Floor fixed at 0.80, no gap rule for now. Test with bge-small on bare acronyms: AI 0.80 and ITIL 0.81 correct; SEO → "search engines" 0.83 and ERP → wrong concept 0.80 (handled by the acronym list); VPN 0.76 below the floor; XML → PHP 0.74, SCADA → scaffolding 0.70 (correctly rejected; a 0.70 floor would accept them). Hand-check after the first batch run decides whether a gap rule is needed. *(2026-10-29, clarification)* Two cases: the **general search** (input not found by A/B, compared against all ESCO labels) uses only the 0.80 floor; the **ambiguous-candidate search** (A found a key with several concepts, decided 2026-10-27) needs the floor **and** a gap between the top two (value to tune).
- [ ] *(postponed 2026-10-26, may not be implemented)* **D. Parent link (LLM)** — for skills with no matching concept (e.g. "Claude Code"): embedding search proposes ~10 ESCO candidates, the Groq LLM picks the best **broader** concept or "none"; stored as relation *narrower than*. "None" → unresolved (raw string + embedding).
- [ ] *(postponed 2026-10-26, may not be implemented)* Optional: for unresolved skills embed a short LLM-written description instead of the bare name.
- [ ] Abstraction tier derived in memory (skill type, depth, reuse level); never written to source data.
- [ ] `SkillGrounding` table + repository — in the separate cache file `data/cache/grounding.sqlite` *(since 2026-10-26)*.
- [ ] On-click grounding: a job's unseen skills are grounded the first time it is opened; results cached for all later clicks and users *(since 2026-10-26)*. One-off local batch over all job skills for the paper stats. *(Until 2026-10-26: batch of all 12.8k job skills once + daily incremental step after extraction.)*
- [ ] Report grounding stats per method and the unresolved rate; curate the most frequent unresolved skills in overrides.

### CV flow (at upload time, no local LLM)
1. Parse the CV (existing Groq call) → skills + tiers.
2. Look up overrides and the `SkillGrounding` table (most common skills are already grounded from jobs).
3. Remaining skills: steps A–C locally (embedding model runs on CPU).
4. Still unresolved: **one batched Groq call** for step D (all skills + candidates in one request). *(postponed 2026-10-26, may not be implemented)* — skills stay unresolved.
5. Save new results to the grounding cache for reuse. The CV itself stays in the user's session only, never written to a DB *(since 2026-10-26)*; languages are parsed but not scored.
6. Groq unavailable / rate-limited → those skills stay unresolved (embedding only); result marked partial. *(Not applicable while step D is postponed.)*

## Phase 3 — Similarity matrix (CV skills × job requirements)
- [ ] Same URI → 1.0; both unresolved with equal normalized strings → 1.0; otherwise cosine.
- [ ] Directional subsumption via the graph and parent links: specific CV skill → broad requirement **strong** (CV "Claude Code" vs job "AI"); broad CV skill → specific requirement **weak**. Unresolved skills skip it.
- [ ] Cap at 1.0 right after the boost.
- [ ] Noise threshold (≈0.35, tuned on the eval set).
- [ ] Relative seniority multiplier: candidate ≥ job 1.00, one below 0.85, two 0.65, three 0.45; no job level or unknown CV tier → 1.00 (or mild, configurable).
- [ ] Final cap at 1.0.
- [ ] Keep pre-seniority scores for gap classification.

## Phase 4 — Metrics (one at a time, hardest → easiest; each checked on the eval set before the next)
*(Since 2026-10-29, P2)* Order: **Chamfer → Tversky → Soft Cosine → Hungarian**. *(Until 2026-10-29: the numbered order below, hardest first.)*
- [ ] 1. Continuous Tversky — fuzzy overlap = matched mass; α penalizes missing requirements, β extra CV skills.
- [ ] 2. Soft Cosine — skill-to-skill similarity over the union set.
- [ ] 3. Hungarian — scipy rectangular assignment, normalized by number of requirements.
- [ ] 4. Directed Chamfer (job → CV) — default for the UI. *(Built first since 2026-10-29, minimal slice.)*
- [ ] Shared strategy interface: matrix + metadata in, score + alignments out.

## Phase 5 — Result synthesis
- [ ] Score 0–100%.
- [ ] Per requirement: best CV skill, score, ESCO URI (or unresolved), relation, seniority applied.
- [ ] Gaps: **missing** (pre-seniority below threshold) vs **under-qualified** (matched, tier too low).
- [ ] Extra CV skills (not required by the job).
- [ ] On click: one CV vs one selected job *(since 2026-10-26)*. *(Until 2026-10-26: batch of one CV vs all available jobs, ranked — now optional/future, same per-pair engine in a loop.)*

## Phase 6 — Integration (after the API stack decision, week of 2026-10-26) — *(2026-10-29, P4: FastAPI kept; integration starts in the minimal slice)*
- [ ] Endpoint(s) for CV upload and match results. *(2026-10-26)* CV upload → parsed + grounded CV for the session; score(CV, job id) on click. Job list shows only available jobs with extracted skills.
- [ ] Analyzer page consumes them.

---

## Analyzer page (design since 2026-10-30)
Detailed view at `/analyzer` (FE_NOTES L4), mainly for the author and the thesis evaluation. **Design only; built after the minimal slice.**

| # | Decision (2026-10-30) | Effect |
|---|---|---|
| AN1 | Built **after the slice** (November), when `grounding.sqlite` and the batch grounding stats exist | Until 2026-10-30: bonus after March 2027 |
| AN2 | Three timings measured and stored: **grounding per skill**, **LLM extraction per job**, **CV parsing per upload** | New `SkillGrounding` columns; new `Jobs` columns written by the extraction service (backend change by the user, related to ASSIST_LOG T8); CV timings kept in the session only |
| AN3 | Skill rankings count **ESCO concepts**; unresolved skills are counted by normalized string | Needs all job skills grounded first (batch script) |
| AN4 | CV data = **current session only** | Keeps the 2026-10-26 privacy decision; no statistics across CVs |

### 1. Extraction
- **Data:**
  - `SkillGrounding` + `duration_ms` (first lookup only; cache hits are not timed) + `source` (job / cv);
  - new `Jobs` columns `extracted_at`, `extraction_ms`, optional `tokens`;
  - CV parse and grounding time from the session.
- **Views:**
  - coverage funnel (jobs → with description → extracted → failed);
  - share of skills per method (exact / fuzzy / embedding / unresolved); fuzzy score histogram;
  - latency per method (median, slowest 5%); LLM time per job; cache hit rate;
  - skills per job;
  - **top unresolved skills** (the to-do list for overrides and acronyms);
  - the current CV's skills with method and time next to the job aggregates.
- **Caveat:** timings exist only from the date the columns are added; older rows stay NULL. Record that start date.

### 2. Matching (session CV vs one chosen job)
*(2026-10-30)* Shown only once the user has **selected a job from the available positions**. It uses the same selection as the Jobs page; with no job selected, the section prompts the user to pick one.
- Similarity matrix heatmap.
- Requirement → best CV skill lines with score and method.
- Metric comparison (Chamfer in the slice; all four by March).
- Threshold / floor sliders with live recompute.
- **Skills to learn:** the most frequent missing concepts across one domain's jobs.
- The Jobs page keeps the compact match panel; this is the detailed view.

### 3. Jobs (market overview)
- Sortable table of top concepts, filterable by domain and week/month of `scraped_date`.
- Most common and **distinctive** concepts per domain (common here, rare elsewhere); raw "least common" is mostly typos.
- Skills that often appear together.
- Experience level per domain; city × domain counts; salary vs skills (where salary is given).
- Ad lifetime once a last-seen date exists (T8).
- **Caveat:** `scraped_date` = first-seen date, NULL for 3,664 older rows → trends reliable only from ~October 2026.
- *(2026-10-30)* **View 1, "Most required skills": settled** (user decisions; the Jobs tab is redesigned one view at a time):

  | # | Decision |
  |---|---|
  | J1 | Chart only, no table |
  | J2 | Horizontal bars, ranked high → low |
  | J3 | Top 10 |
  | J4 | Axis = % of postings; label `24% · 412 jobs` |
  | J5 | 100% = postings with extracted skills matching the filters (available, no failure marker, non-empty list) |
  | J6 | Counted by ESCO concept, once per job; short display name |
  | J7 | Skills not in ESCO included, counted by cleaned name, marked "not in ESCO" |
  | J8 | Filters: domain, experience level, city, period |

  **Data path** (user, after the batch grounding):
  1. Filter `Jobs` (all needed columns exist).
  2. `json.loads(required_skills)`, then map each string through the grounding cache to a concept key (URI, or `unresolved:<cleaned key>`); one set per job.
  3. Count jobs per key; share = count ÷ jobs in the set; take the top 10.
  4. Label = ESCO preferred label (qualifier removed) or the cleaned string.
  5. Endpoint e.g. `GET /api/analyzer/top-skills?domain=&level=&city=&period=` → `{ postings, skills: [{ concept, jobs, share, inEsco }] }`.

  No ESCO hierarchy data is needed. ~1.7k jobs × ~9 skills is fine in Python per request; a rebuildable `JobSkill(slug, concept_key)` table in the cache DB is optional.
- *(2026-10-30)* **Real data on top, previews below** (user decisions R1–R5, `docs/PLAN.md`). Verified views:
  - **Extraction tab:** coverage (KPI cards + segmented bar + inspection drawer + empty-description warning); skills-per-job histogram.
  - **Jobs tab:** experience level (career order, NULL as coverage); ads per domain and per city, cross-filtered.

  They compute from `/api/jobs` (= 1,757 extracted available ads on 2026-10-30), except coverage, which needs the endpoint below. Everything else, and the whole Matching tab, sits in a grayed preview section until it has trustworthy data.

  **Coverage endpoint (user implements; the frontend shows "waiting for the backend endpoint" while it returns 404):**
  - **Route:** `GET /api/analyzer/coverage`. New router `backend/api/routers/analyzerRoute.py` (prefix `/analyzer`, included with `/api` in `api/main.py` like the other two), a Pydantic response schema in `api/schemas/`, and one repository function, e.g. `get_coverage()` in a new `analyzerRepository.py`. The same `database_connect()` / `try … finally conn.close()` pattern as `jobCardsRepository.get_jobs_card_details`.
  - **Shared conditions:**
    - every count starts from `available = 1`;
    - `HAS_DESC` = `description IS NOT NULL AND TRIM(description) <> ''`;
    - `OK` = `required_skills IS NOT NULL AND required_skills NOT IN ('', '[]', '["__EXTRACTION_FAILED__"]')`, the same as `/api/jobs`.
  - **Fields:**

    | Field | Condition (besides `available = 1`) | Value 2026-10-30 |
    |---|---|---|
    | `available` | — | 3,707 |
    | `with_description` | `HAS_DESC` | 2,995 |
    | `extracted` | `OK` | 1,757 |
    | `waiting` | `HAS_DESC AND required_skills IS NULL` | 1,167 |
    | `no_description` | `NOT HAS_DESC AND required_skills IS NULL` | 690 |
    | `empty` | `required_skills = '[]'` | 83 |
    | `failed` | `required_skills = '["__EXTRACTION_FAILED__"]'` | 10 |
    | `no_description_processed` | `NOT HAS_DESC AND required_skills IS NOT NULL` (T7) | 22 |
    | `queued_by_domain` | `required_skills IS NULL GROUP BY domain_name` → `[{domain, queued}]` | Management 269, … |
    | `problem_ads.empty` / `.failed` / `.no_description_processed` | same conditions as the counts → `[{slug, title, company, domain, ad_link}]` | — |

    `extracted + waiting + no_description + empty + failed = available`; a quick test for `db-tester`.
  - **Key idea:** one `COUNT(*)` per condition. SQLite can do them all in a single query with `SUM(CASE WHEN … THEN 1 ELSE 0 END)`. The three lists are three small `SELECT`s with the same `WHERE`. Use the same column aliases as `/api/jobs` (`company_name AS company`, `domain_name AS domain`).
- *(2026-10-30, mock built; see FE_NOTES)* Jobs tab views and their data needs (views 2+ still to be redesigned one by one; now in the preview section):
  - share-of-postings column chart: weekly analyzed postings + per-concept job counts;
  - rank-change slope chart: first 2 vs last 2 dated weeks (first `scraped_date` = 2026-10-05), from the same counts;
  - specificity scatter: per-concept counts **per domain**;
  - skill bundles: per-job grounded concept sets (pair counts);
  - category treemap: needs category groups. ESCO's hierarchy is coarse for IT (SQL, Python and Java share one 163-skill group), so the groups are hand-made or derived via `esco/graph.py`. Open: user decision.
  - **must-have vs nice-to-have** needs the extraction step to return a requirement flag per skill. That is a backend change to the prompt and output format, plus re-extraction of all jobs (90/day ≈ 6–7 weeks); listed for after March, not in the slice. → *(2026-10-30)* **removed from the UI** (user). Idea kept. 61% of the extracted ads use "nice to have" wording (EN or RO), so real data is possible in two ways: (A) the extraction returns a must/nice flag per skill, which needs re-extraction; or (B) a rule-based pass that finds each skill near "nice"/"must" cues in the stored description (no LLM, rough, must report the unclassified share).

## Verification (per phase; tests by `db-tester` in `tests/`, DB copy, no network)
- [ ] Normalization/splitting: CI/CD whole, C/C++ split, Legea 98/2016 whole.
- [ ] Exact/fuzzy guards: Java ≠ JavaScript, C/R/Go exact only, ISO numbers exact.
- [ ] Grounding precision on a sample of job skills; unresolved rate; parent-link sample check.
- [ ] Matrix invariants: operation order, caps, threshold, seniority table, no level → no discount.
- [ ] Metric sanity: identical sets 100%, disjoint 0%, extra skills don't lower Chamfer.
- [ ] Eval set: agreement of each metric with hand labels (for the paper).

## Change log
| Date | Change |
|---|---|
| 2026-10-22 | Roadmap created: English-only ESCO, offline job grounding, local embedding model, relative seniority, metric order Tversky → Soft Cosine → Hungarian → Chamfer, parent-link step D, CV upload flow, exact/fuzzy rules. |
| 2026-10-22 | Target structure expanded: file tree, config table, build order, ESCO normalization rules. |
| 2026-10-23 | ESCO CSVs renamed in `data/esco/`: `broaderRelationsSkillPillar_en.csv` → `skill_Pillars.csv`, `skillsHierarchy_en.csv` → `skill_Hierarchy.csv`; `skills_en.csv` unchanged. A new ESCO download must be renamed the same way. |
| 2026-10-26 | Job level "Fără" (no experience required, 174 jobs) mapped to Entry (0) instead of grouped with NULL as "no level". Same scores (nobody is below 0), but it's an explicit level; only NULL uses the unknown path. |
| 2026-10-26 | CV tier names fixed as entry / junior / mid / senior (+ unknown), matching what the parser actually returns (the prompt asked for entry_level / mid_level). Config is the source of truth; the parser maps variants through an alias table at the step 9 rework. |
| 2026-10-26 | Embedding model chosen: `BAAI/bge-small-en-v1.5` (revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`) over all-MiniLM-L6-v2 — better on short-text matching, same 384 dimensions, ~130 MB, CPU-friendly. |
| 2026-10-26 | Step D (LLM parent link) postponed, may not be implemented: grounding is built with steps A–C only (user decision). Step C floor fixed at 0.80 without a gap rule; a small exact-match acronym list (acronym → ESCO preferred label) runs before step A for frequent acronyms that A–C miss or get wrong (ERP, SEO, VPN). Based on an embedding test of bare acronyms against all ESCO preferred labels. |
| 2026-10-26 | App flow confirmed (on-click flow): CV uploaded and parsed once (session only, languages not scored); job list shows available jobs with extracted skills; clicking a job grounds its unseen skills on the spot and scores that one CV–job pair (no ranking). Grounding results cached in a separate git-ignored `data/cache/grounding.sqlite`, not in `JobsDatabase.sqlite`; no grounding step or torch in `extract.yml`; paper stats via a local batch script. |
| 2026-10-27 | Index ambiguity rule decided: dedupe by concept, label-kind order preferred > alt > hidden > derived variant, best rank wins, ties stay ambiguous → step C. |
| 2026-10-27 | Ambiguous exact matches: step C searches only among their candidates (floor 0.80 + minimum gap between top two), separate method in the grounding cache; full search not used for them. |
| 2026-10-27 | Derived index variants replaced by Way 2: labels are simplified (hyphens → spaces, trailing qualifier removed, normalized again) and stored only in that form; the same simplification is applied to every input at lookup. Derived rank no longer used. Reason: simpler, symmetric, solves input-side variants; only 1 extra ambiguous key in the data. |
| 2026-10-29 | Minimal slice added (deadline ~2026-11-12: exact + fuzzy, Chamfer, end-to-end flow; step C stretch) with decisions P1–P5: grounding in `matching/grounding.py` (shared by job and CV skills), Chamfer first, in-memory cache first, FastAPI kept, slice before the full build order. Reason: user's thesis milestone; nothing dropped, only sequenced. |
| 2026-10-29 | Docs synced with the code: done ticks (skeleton/config, requirements file, normalization, index, step A), fuzzy in progress, `match_result_object.py` in the tree, config table with real keys + `model_folder` + ESCO 1.2.1, per-machine `data/models` / `data/cache`, step C floor vs gap clarified, "Fără" count scopes, goal line (one clicked job). "How it fits together" walkthrough added. |
| 2026-10-30 | Analyzer page designed (AN1–AN4): built after the slice; three sections Extraction / Matching / Jobs; timings for grounding per skill, LLM extraction per job and CV parsing per upload; rankings by ESCO concept; CV data session-only. `SkillGrounding` gets `duration_ms` and `source`. |
