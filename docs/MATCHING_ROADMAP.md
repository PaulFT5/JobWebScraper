# Matching Engine — Roadmap

*Created: 2026-10-22 · design recorded in `docs/BE_IMPLEMENTATION.md` §5.4 (T10–T13)*

Score a user's CV against every available job with extracted skills and explain the score. English-only ESCO grounding, relative seniority, similarity matrix, set-matching metrics.

**Status convention:** `[ ]` open, `[x]` done. Status changes keep their history, e.g. `open → done 2026-11-03`. Nothing is deleted; replaced items get *Until* dates.

---

## Data facts behind the design (2026-10-22)
- `Jobs`: 5,203 rows, 3,332 available; 1,733 available **with** extracted skills, 1,572 still in the extraction backlog (90/day) → matching covers only jobs with skills.
- 12,799 distinct skill strings: 9,864 seen once, 1,091 differ only by case; ~9 skills per job.
- Failure marker `["__EXTRACTION_FAILED__"]` (13 rows) and 163 empty lists.
- 255 distinct skills contain a slash, mostly single concepts (CI/CD 72, SAP S/4HANA 26, A/B testing 21, TCP/IP 20, PL/SQL, Legea 98/2016).
- ≥280 Romanian skills → **English only**: they go to the unresolved path and mostly won't match.
- Job `experience_level` (available + skills): Middle 508, Entry 253, Senior 240, Executive 59, "Fără" 109, NULL 564 → 39% without a level.
- CV output: tiers entry_level / junior / mid_level / senior + languages; unvalidated; unknown experience currently defaults to entry_level.
- Both workflows install `requirements.txt` → sentence-transformers there would pull ~2 GB of CUDA torch into every run.

## Target structure
*Last changed: 2026-10-26 (Fără job level, CV tier names, embedding model, step D postponed, acronym list, on-click flow)*

### File organization
```
backend/
├── matching/                      ← engine, plain Python in/out, no web framework
│   ├── __init__.py
│   ├── config.json                ← all tunable values (table below)
│   ├── config.py                  ← load once + cache, validate, ignore metadata notes, config fingerprint
│   ├── normalization.py           ← one shared cleaning function (ESCO labels, job skills, CV skills)
│   ├── esco/
│   │   ├── __init__.py
│   │   ├── loader.py              ← reads ESCO CSVs (multi-line alt/hidden labels)
│   │   ├── index.py               ← normalized label → URI(s); exact (A) + fuzzy (B); ambiguity flags
│   │   ├── graph.py               ← broader / narrower relations, depth, parent
│   │   └── grounding.py           ← overrides → table → acronyms → A → B → C → unresolved (since 2026-10-26; until then: … → C → D → unresolved)
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

### Config contents (`backend/matching/config.json`)
| Group | Setting | Starting value | Purpose |
|---|---|---|---|
| esco | version | exact downloaded version (v1.2.0?) | Reproducibility; stored with every grounding row |
| | language | "en" | English-only decision |
| | data folder | `data/esco` | CSV location |
| model | name | `BAAI/bge-small-en-v1.5` (chosen 2026-10-26) | Embedding model, 384-dim |
| | revision | `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a` (latest on 2026-10-26) | Pinning |
| | cache folder | `data/cache` | Vectors |
| grounding | fuzzy threshold | 90 | Step B acceptance |
| | fuzzy min gap to 2nd best | ~5 | Avoid ambiguous fuzzy matches |
| | fuzzy min length | 4 | Short skills (C, R, Go) exact only |
| | embedding floor | 0.80 (fixed 2026-10-26; no gap rule for now) | Step C acceptance |
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

### Build order (dependency-driven)
1. `config.json` + `config.py` — open → done 2026-10-26 (esco, model, seniority groups; other groups added with their steps)
2. `normalization.py` — open → done 2026-10-26
3. `esco/loader.py` — open → done 2026-10-26
4. `esco/index.py` — exact, then fuzzy
5. `esco/graph.py`
6. Grounding cache DB `data/cache/grounding.sqlite` (git-ignored) + repository *(since 2026-10-26)* — until 2026-10-26: `SkillGrounding` table in `JobsDatabase.sqlite`
7. `embeddings.py`
8. `esco/grounding.py` — overrides → table → A → B → C; local batch script over all job skills for stats *(since 2026-10-26)*; **then** step D *(postponed 2026-10-26, may not be implemented)*
9. CV parser rework (independent; any time before 10)
10. Hand-labelled eval set
11. `similarity.py`
12. `metrics/base.py` + `tversky.py`
13. Minimal `engine.py` + `report.py` (first end-to-end result)
14. `soft_cosine.py` → `hungarian.py` → `chamfer.py`
15. Full `report.py` (gaps, extra skills, ranking)
16. `matcher_service.py` (on click: ground unseen job skills, score one CV vs one job) *(since 2026-10-26)* — until 2026-10-26: + grounding step in `extract.yml` with CPU torch (dropped: no matching work in GitHub Actions)
17. API endpoint + analyzer page (after the API decision)

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
- `backend/database/repositories/skillGroundingRepository.py` — table `SkillGrounding` in a separate git-ignored file `data/cache/grounding.sqlite` *(since 2026-10-26)*; rebuildable cache, never committed (avoids binary merge conflicts with the daily `JobsDatabase.sqlite` commits); also model revision and config fingerprint per row. Columns: raw skill, normalized form, ESCO URI, **relation** (same as / narrower than), method (exact / fuzzy / embedding / llm_parent / manual), score, ESCO version, date.
- `data/esco/` — pinned ESCO English CSVs, committed.
- `data/esco/overrides` — manual skill → concept / parent corrections (always win).
- Vectors — local cache, git-ignored, rebuilt when missing.
- Separate matching requirements file; CPU-only torch installed locally / on the app server only *(since 2026-10-26)* (until 2026-10-26: only in `extract.yml`).

---

## Phase 0 — Groundwork
- [x] Download ESCO v1.2.x English CSVs (`skills_en`, `broaderRelationsSkillPillar_en`, `skillsHierarchy_en`) into `data/esco/`; record the version. — open → done 2026-10-26 (v1.2.1 in config)
- [x] Pin the embedding model name + revision in config (all-MiniLM-L6-v2 or bge-small-en-v1.5). — open → done 2026-10-26
  - *(2026-10-26)* Model chosen: `BAAI/bge-small-en-v1.5`, revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`. Model in `data/models/`, vectors in `data/cache/`, both git-ignored. Config entry added 2026-10-26.
- [ ] Create the package skeleton and config (weights, thresholds, α/β, model, ESCO version).
- [ ] Separate matching requirements file; CPU torch step in `extract.yml`; `scrape.yml` unchanged.
  - *(2026-10-26)* `requirements-matching.txt` created (CPU torch index, torch 2.14.1+cpu, sentence-transformers 6.2.0, rapidfuzz 3.14.6, all pinned); `extract.yml` step **not needed** (2026-10-26: grounding happens on click, not in GitHub Actions).
- [ ] Filter the failure marker and empty lists in every skill reader.
- [ ] Optional: extraction prompt asks for English skill names.
- [ ] Hand-label ≈20 CV–job pairs in `data/eval/`.

## Phase 1 — Input preprocessing
- [ ] Normalization: casefold, trim/collapse spaces, punctuation cleanup, small curated acronym list (ESCO alt labels first). Same function for ESCO labels and for input skills.
  - *(2026-10-26)* Acronym list moved to grounding (Phase 2), applied after normalization; the normalization function itself is done (build step 2).
- [ ] Compound split ("/", "&", "and") only if the whole string fails grounding **and** every part grounds confidently; never around digits. (CI/CD stays whole, C/C++ splits.)
- [ ] CV parser returns a validated structure; tiers entry / junior / mid / senior / **unknown**; skill in several tiers → highest.
  - *(2026-10-26)* Config `cv_tier_map` is the source of truth for tier names. The prompt names the exact keys; an alias table maps variants (`entry_level`, `Entry-level`, `mid_level`, `middle`, …; case-insensitive) to canonical keys; anything unrecognized → `unknown` (no default to entry).
- [ ] Job requirements: flatten, normalize, dedupe (by URI after grounding).
- [ ] Map job level: Fără/Entry→0, Middle→2, Senior/Executive→3, NULL→none. *(Since 2026-10-26; until 2026-10-26: "Fără"/NULL→none.)*

## Phase 2 — ESCO grounding (English)
Lookup order for every skill: **overrides → `SkillGrounding` table → acronym list → steps A–C.** *(Since 2026-10-26; until then: overrides → table → steps A–D.)*

- [ ] **Index:** preferred, alt and hidden labels → URI; each label also indexed without its qualifier ("Python (computer programming)" → "python"); labels pointing to several concepts marked ambiguous.
- [ ] **Concept graph:** broader/narrower relations, depth, parent.
- [ ] **A. Exact** — normalized string equals an indexed label. Ambiguous label → don't guess, pass to C.
- [ ] **B. Fuzzy** (rapidfuzz) — whole-string scoring (no partial: "Java" ≠ "JavaScript"); threshold ≈90, tuned on samples; clear gap to second-best or treat as ambiguous; no fuzzy for short strings (C, R, Go); numbers must match exactly (ISO 9001 vs 14001).
- [ ] **Acronym list** *(added 2026-10-26)* — small file in `data/esco/`: acronym → ESCO preferred label (e.g. erp → *manage standard enterprise resource planning system*, seo → *search engine optimisation*, vpn → *implement a virtual private network*). Applied before step A, only when the whole normalized input equals an entry; method `acronym`. Every target must resolve to exactly one concept in the index at load (fails loudly otherwise; catches renamed labels in a new ESCO version). Only frequent acronyms that A–C miss or get wrong, picked from the first batch run's stats; ambiguous ones (PC, REST) left out. Acronyms with no ESCO concept (XML, SCADA, FMEA, CI/CD) stay unresolved and still match on equal strings.
- [ ] **C. Embedding** — nearest ESCO concept above a confidence floor ("spreadsheet software" ↔ *use spreadsheets software*). *(2026-10-26)* Floor fixed at 0.80, no gap rule for now. Test with bge-small on bare acronyms: AI 0.80 and ITIL 0.81 correct; SEO → "search engines" 0.83 and ERP → wrong concept 0.80 (handled by the acronym list); VPN 0.76 below the floor; XML → PHP 0.74, SCADA → scaffolding 0.70 (correctly rejected; a 0.70 floor would accept them). Hand-check after the first batch run decides whether a gap rule is needed.
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
- [ ] 1. Continuous Tversky — fuzzy overlap = matched mass; α penalizes missing requirements, β extra CV skills.
- [ ] 2. Soft Cosine — skill-to-skill similarity over the union set.
- [ ] 3. Hungarian — scipy rectangular assignment, normalized by number of requirements.
- [ ] 4. Directed Chamfer (job → CV) — default for the UI.
- [ ] Shared strategy interface: matrix + metadata in, score + alignments out.

## Phase 5 — Result synthesis
- [ ] Score 0–100%.
- [ ] Per requirement: best CV skill, score, ESCO URI (or unresolved), relation, seniority applied.
- [ ] Gaps: **missing** (pre-seniority below threshold) vs **under-qualified** (matched, tier too low).
- [ ] Extra CV skills (not required by the job).
- [ ] On click: one CV vs one selected job *(since 2026-10-26)*. *(Until 2026-10-26: batch of one CV vs all available jobs, ranked — now optional/future, same per-pair engine in a loop.)*

## Phase 6 — Integration (after the API stack decision, week of 2026-10-26)
- [ ] Endpoint(s) for CV upload and match results. *(2026-10-26)* CV upload → parsed + grounded CV for the session; score(CV, job id) on click. Job list shows only available jobs with extracted skills.
- [ ] Analyzer page consumes them.

---

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
