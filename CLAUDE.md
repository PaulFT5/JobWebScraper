# JobWebScraper — Claude working rules

## Project at a glance
- **Purpose:** scrape job ads from bestjobs.eu, extract hard skills from descriptions with an LLM, serve them to a SvelteKit UI that will match them against a user's CV.
- **Backend (Python, owned by the user):** `backend/`, `main.py`, `dev.py`, `requirements.txt`, `.github/workflows/`, `data/`.
  - `scraper/bestjobs/` — weekly scraper (listing JSON API + detail HTML pages), run by `scrape.yml`.
  - `services/skill_extraction_service.py` — daily Groq LLM skill extraction, run by `extract.yml`.
  - `api/` — FastAPI app (`/api/filters`, `/api/jobs`), routers → services/repositories → SQLite (`data/jobs/JobsDatabase.sqlite`, table `Jobs`).
  - `cv_parser/`, `services/matcher_service.py` — CV parsing / matching (WIP, not wired to the API).
- **Frontend (SvelteKit + TS):** `frontend/` — the only area Claude may edit.
- Run both: `python dev.py` (uvicorn :8000 + vite :5173).

## Rules (mandatory)
1. **Frontend only, and only on request.** Claude modifies files under `frontend/` *only when the user explicitly asks*. Enforced by the PreToolUse hook `.claude/hooks/guard_fe_only.py` (blocks Edit/Write/NotebookEdit outside `frontend/`, `tests/` and the tracking docs below). Do not bypass it via shell commands (sed, redirects, scripts) either, unless the user explicitly approves a specific change.
   - **`tests/`** (since 2026-10-22) is writable for test code only, mainly by the `db-tester` agent (`.claude/agents/db-tester.md`). Tests never modify the real DB or backend files: DB copies and results go to a temp dir. A check passes when the code behaves as intended, so open issues show as FAIL. Run with `.venv\Scripts\python.exe tests/<file>.py`.
   - Project agents: `code-finder` (targeted read-only code search) and `db-tester`, both in `.claude/agents/`.
2. **Backend: assist, never modify.** Claude helps design and review the backend but never edits backend files. Explain what to change and why; the user writes it.
3. **Explain first, snippets when stuck** (since 2026-10-23; before: no code unless asked). When the user asks for help with an implementation, reason about functionality, logic, data flow, redundancy, latency, edge cases and trade-offs. Give a short, helpful snippet — never the full solution — when the user is stuck: they ask for one, or the same question comes up a 3rd time. The snippet shows the key idea only; the user writes the rest. Since 2026-10-24: when the user directly asks for the solution, give the full solution.
4. **Keep the tracking files current** (Claude may edit only these outside `frontend/`):
   - `docs/ASSIST_LOG.md` — tracked issues and needed changes only (review findings, needed-change lists). **Do not log individual prompts, questions or answers.** When something happens to a tracked item, only append its new status with the date (e.g. `open → done 2026-10-28`). A new section is added only for a new review or needed-change list, and only when the user asks for one.
   - `docs/BE_IMPLEMENTATION.md` — living description of the backend implementation for the user's paper: architecture, components, data model, pipelines, design decisions and their rationale, known limitations, change history. Update it whenever the user changes or decides something about the backend.
   - `docs/MATCHING_ROADMAP.md` (since 2026-10-22) — matching-engine roadmap checklist. Mark items `open → done <date>` as the user completes them; record design changes there and in `BE_IMPLEMENTATION.md`.
5. **Everything is dated, nothing is overwritten.** In both docs, every change carries its date (YYYY-MM-DD). When a technology, component or decision is replaced, set an *Until* date on the old item, add the new one with a *Since* date, add a row to the change log, and move replaced descriptions to *Superseded versions*. Status changes keep their history (`open → done 2026-10-28`). Known pending change: Web API stack (FastAPI + Uvicorn + Pydantic, T2) is expected to be reconsidered the week of 2026-10-26.
6. **Discuss every issue first** (since 2026-10-22). Any inconsistency, conflict, blocked action or other issue Claude encounters is raised with the user and discussed before acting on it — no silent workarounds or assumptions.
   - *(Since 2026-10-26)* When the user describes a flow, decision or change, Claude first restates its understanding, marks its assumptions as assumptions, and lists every conflict with the code, data, docs or an earlier decision as a question. Nothing is implemented or recorded until the user has answered.
7. Follow the global output rules (no code in replies, `updated <file>: <change>` reporting, short replies), except the snippets allowed by rule 3.
