# JobWebScraper — Claude working rules

## Project at a glance
- **Purpose:** scrape job ads from bestjobs.eu, extract hard skills from descriptions with an LLM, serve them to a SvelteKit UI that will match them against a user's CV.
- **Backend (Python, owned by the user):** `backend/`, `main.py`, `dev.py`, `requirements.txt`, `.github/workflows/`, `data/`.
  - `scraper/bestjobs/` — weekly scraper (listing JSON API + detail HTML pages), run by `scrape.yml`.
  - `services/skill_extraction_service.py` — daily Groq LLM skill extraction, run by `extract.yml`.
  - `api/` — FastAPI app (`/api/filters`, `/api/jobs`), routers → services/repositories → SQLite (`data/jobs/JobsDatabase.sqlite`, table `Jobs`).
  - `cv_parser/`, `services/matcher_service.py` — CV parsing / matching (WIP, not wired to the API).
  - `matching/` (since 2026-10-26) — matching engine: config, normalization, `esco/` (loader, index), `grounding.py`, `match_result_object.py`; plan and status in `docs/MATCHING_ROADMAP.md`.
  - Dependencies: `requirements.txt` + `requirements-matching.txt` (CPU torch, sentence-transformers, rapidfuzz), both installed into `.venv`. Model weights and `data/cache/` are per machine (see `BE_IMPLEMENTATION.md` §7).
- **Frontend (SvelteKit + TS):** `frontend/` — the only area Claude may edit.
- Run both: `.venv\Scripts\python.exe dev.py` (uvicorn :8000 + vite :5173).

## Thesis context (since 2026-10-29)
- The project is the user's **bachelor thesis** (CS). The learning goal is the backend matching work: grounding, embeddings, similarity, metrics. Routing / web plumbing is low priority.
- Milestones: **minimal slice by ~2026-11-12** (exact + fuzzy, Chamfer, end-to-end flow), engine **mostly done by March 2027**, job-market analyzer as a bonus. Parts are postponed, never dropped, unless time runs out.
- The user is a student: explanations need concrete detail, not just design-level descriptions (see rule 3).
- **Memory is project-only:** facts worth keeping across sessions go into this file (or the tracking docs), never into the global Claude memory/config.

## Rules (mandatory)
1. **Frontend only, and only on request.** Claude modifies files under `frontend/` *only when the user explicitly asks*. Enforced by the PreToolUse hook `.claude/hooks/guard_fe_only.py` (blocks Edit/Write/NotebookEdit outside `frontend/`, `tests/` and the tracking docs below). Do not bypass it via shell commands (sed, redirects, scripts) either, unless the user explicitly approves a specific change.
   - **`tests/`** (since 2026-10-22) is writable for test code only, mainly by the `db-tester` agent (`.claude/agents/db-tester.md`). Tests never modify the real DB or backend files: DB copies and results go to a temp dir. A check passes when the code behaves as intended, so open issues show as FAIL. Run with `.venv\Scripts\python.exe tests/<file>.py`.
   - Project agents: `code-finder` (targeted read-only code search) and `db-tester`, both in `.claude/agents/`.
   - *(Since 2026-10-30)* More agents in `.claude/agents/`: `fe-specialist` (frontend work on request, edits only `frontend/`, type-checks + builds + FE_NOTES entry after every change), `grounding-evaluator` (read-only grounding stats on real job skills), `doc-keeper` (read-only check of the tracking docs against the code and rule 5), `metric-evaluator` (read-only metric comparison against `data/eval/`, usable once metrics and the eval set exist). Skills in `.claude/skills/`: `slice-check` (whole-project health check, changes nothing) and `thesis-writer` (thesis drafts from the dated docs, never invents results). The edit guard allows `.claude/agents/` and `.claude/skills/` since 2026-10-30 (user change). Agent files use project-relative paths only (the project runs on a PC and a laptop).
2. **Backend: assist, never modify.** Claude helps design and review the backend but never edits backend files. Explain what to change and why; the user writes it.
3. **Explain first, snippets when stuck** (since 2026-10-23; before: no code unless asked). When the user asks for help with an implementation, reason about functionality, logic, data flow, redundancy, latency, edge cases and trade-offs. Give a short, helpful snippet — never the full solution — when the user is stuck: they ask for one, or the same question comes up a 3rd time. The snippet shows the key idea only; the user writes the rest. Since 2026-10-24: when the user directly asks for the solution, give the full solution.
   - *(Since 2026-10-29)* For every implementation step, be concrete: **which data** (table/column/file and its exact shape), **where** it comes from and goes to, **which function or library call** to use, **inputs and outputs** (types, an example value), and **how it connects** to the previous and next step. Add a tiny snippet of the key call. Still no full code unless asked directly. The data walkthrough is in `docs/MATCHING_ROADMAP.md` → *How it fits together*.
4. **Keep the tracking files current** (Claude may edit only these outside `frontend/`):
   - `docs/ASSIST_LOG.md` — tracked issues and needed changes only (review findings, needed-change lists). **Do not log individual prompts, questions or answers.** When something happens to a tracked item, only append its new status with the date (e.g. `open → done 2026-10-28`). A new section is added only for a new review or needed-change list, and only when the user asks for one.
   - `docs/BE_IMPLEMENTATION.md` — living description of the backend implementation for the user's paper: architecture, components, data model, pipelines, design decisions and their rationale, known limitations, change history. Update it whenever the user changes or decides something about the backend.
   - `docs/PLAN.md` (since 2026-10-29) — the current work plan (docs cleanup + minimal slice).
   - `docs/MATCHING_ROADMAP.md` (since 2026-10-22) — matching-engine roadmap checklist. Mark items `open → done <date>` as the user completes them; record design changes there and in `BE_IMPLEMENTATION.md`.
5. **Everything is dated, nothing is overwritten.** In both docs, every change carries its date (YYYY-MM-DD). When a technology, component or decision is replaced, set an *Until* date on the old item, add the new one with a *Since* date, add a row to the change log, and move replaced descriptions to *Superseded versions*. Status changes keep their history (`open → done 2026-10-28`). Known pending change: Web API stack (FastAPI + Uvicorn + Pydantic, T2) is expected to be reconsidered the week of 2026-10-26. → *(2026-10-29)* kept for the minimal slice; reconsidered after March 2027, if at all.
6. **Discuss every issue first** (since 2026-10-22). Any inconsistency, conflict, blocked action or other issue Claude encounters is raised with the user and discussed before acting on it — no silent workarounds or assumptions.
   - *(Since 2026-10-26)* When the user describes a flow, decision or change, Claude first restates its understanding, marks its assumptions as assumptions, and lists every conflict with the code, data, docs or an earlier decision as a question. Nothing is implemented or recorded until the user has answered.
7. Follow the global output rules (no code in replies, `updated <file>: <change>` reporting, short replies), except the snippets allowed by rule 3.
