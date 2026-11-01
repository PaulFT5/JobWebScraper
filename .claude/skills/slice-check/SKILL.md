---
name: slice-check
description: One-shot health check of the JobWebScraper project on the current machine. Use when the user asks "does everything work", after switching machines, after installing dependencies, or before a demo or milestone. Checks the venv and dependencies, starts the API and frontend, calls the API endpoints, runs every test in tests/, and reports one table. Changes nothing in the project.
---

# Slice check

Run the steps in order. Keep going after a failure when the later step doesn't depend on it, so the report shows everything at once. **Never edit project files or install anything.** If a fix is needed, say what the user should run.

The project root is the working directory. In the Bash tool use forward slashes (`.venv/Scripts/python.exe`).

## 1. Environment
- `.venv/Scripts/python.exe --version`. If missing, stop. Tell the user to run `py -m venv .venv` and both `pip install -r` steps (BE_IMPLEMENTATION §7).
- Import check: `.venv/Scripts/python.exe -c "import fastapi, uvicorn, rapidfuzz, torch, sentence_transformers, groq, pdfplumber"`. Report each missing module. `uvicorn` is a known gap (ASSIST_LOG B11).
- `node -v`, and whether `frontend/node_modules` exists (if not: `cd frontend` then `npm install`).
- Embedding model present in `data/models/`? Missing is fine until `embeddings.py` exists; just report it.
- `.env` present? Don't print its contents.

## 2. Matching engine smoke test
Run with `PYTHONPATH=.` and `PYTHONDONTWRITEBYTECODE=1`:
- `exact_match("Python (Programming)")` → expect status `match`.
- `fuzzy_match("MS Exel")` → expect `match` with a score ≥ 90.
- `fuzzy_match("Go")` → expect `not found`.
- `ground(...)` with the same inputs, if `ground` exists in `backend/matching/grounding.py`.
Report the first-call time (index build) separately.

## 3. Servers
- Start the API in the background: `.venv/Scripts/python.exe -m uvicorn backend.api.main:app --port 8000`.
- Start the frontend in the background: `cd frontend && npm run dev -- --port 5173`.
- Wait until each port answers, using a Monitor with an until-loop on curl. No fixed sleeps; give up after ~60 s.
- `curl -s localhost:8000/api/filters`: expect JSON with `cities`, `work_types`, `domains`.
- `curl -s "localhost:8000/api/jobs"`: report the row count and response size.
- `curl -s localhost:5173/` and `/analyzer`: expect HTTP 200.
- **Stop both servers afterwards**, including their child processes.

## 4. Tests
- Run each `tests/*.py` (except `common.py`) as `.venv/Scripts/python.exe tests/<file>.py`.
- Collect pass/fail counts per file. Failing checks are often **known open issues** by design (see CLAUDE.md); name their ASSIST_LOG IDs rather than calling them regressions.

## 5. Frontend checks
In `frontend/`: `npx svelte-check --tsconfig ./tsconfig.json` and `npx vite build`.

## Report
One table: **area | check | result (OK / FAIL / SKIPPED) | detail**. Below it:
- what the user needs to run to fix each FAIL;
- known-open-issue failures listed separately from real regressions;
- confirmation that no project file was changed. Compare `git status --short` before and after the run.
