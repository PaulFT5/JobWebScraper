# Frontend notes

Living record of frontend decisions, open items and changes.
Conventions: every entry is dated (YYYY-MM-DD). Nothing is overwritten. Replaced items get an *Until* date and move to *Superseded versions*. Status changes keep their history (`open → done 2026-10-28`).

## 1. Overview (as of 2026-10-27)
- **Stack:** SvelteKit 2, Svelte 5 (runes), TypeScript, Tailwind CSS 4 (+ forms plugin), lucide icons, Vite.
- **Routes:** `/` shows the job list with filters, and `/analyzer` is a placeholder.
- **Layout:** dark sidebar (brand, CV upload, Apply/Reset, filter groups, nav) next to the main content area.
- **API:** `GET /api/filters` (loaded in the root layout) and `GET /api/jobs` (re-fetched when filters are applied). The base URL is hardcoded to `http://127.0.0.1:8000/api`.
- **Run:** `python dev.py` (vite on :5173).

## 2. Decisions
| ID | Decision | Since | Until | Rationale |
|----|----------|-------|-------|-----------|
| D1 | Web app running in the browser | 2026-10-27 | — | The data is central (Actions → SQLite → FastAPI), there's nothing to install, and it's easy to demo for the paper. |
| D2 | Desktop app: **deferred**. If built, Tauri wraps the existing SvelteKit app (static adapter, SPA) as a thin client calling a hosted FastAPI. | 2026-10-27 | — | Reuses the UI code with no rewrite. Bundling the Python backend was set aside because of installer size (ML models) and stale local data. |

## 3. Open items / known issues
Logged from the design review of 2026-10-27. Each item is filled in as the user decides on it.

### Layout & visuals (under discussion 2026-10-27)
- L1 Fixed 3-column job grid and fixed-width sidebar, with no responsive breakpoints. *open 2026-10-27*
- L2 Colors are hardcoded, with no theme tokens and no dark mode for the content area. *open 2026-10-27*
- L3 The nav items use different active styles (slate vs teal). *open 2026-10-27*
- L4 The score card is an unused placeholder, and the Analyzer page is a placeholder. *open 2026-10-27*. Score card: *open → done 2026-10-27*. It's now a compact CV match panel on the Jobs page, based on the Figma Make mock "CV Scraper App UI Design". Analyzer: still open.
- L5 *(2026-10-27)* The match panel's overall % is a fixed mock value (72) shown once a CV is picked, and 0 / "No CV" before that. Replace it with the real score once the matcher is wired to the API. *open 2026-10-27*

### Design decisions from the Figma mock (2026-10-27)
- Match panel: compact (no ⅓-height panel), keeps the app's font (no Fraunces), no "N jobs found" count.
- Score colors: the app's existing 3 bands (red < 40, amber ≤ 70, emerald above) are shared by the panel and the job cards. The mock's 4 bands were not adopted.

### Interaction (not yet discussed)
- I1 Nav uses buttons instead of links (no open in new tab). *open 2026-10-27*
- I2 Filters: Apply/Reset sit above the list, there's no per-group count, and filters aren't kept in the URL. *open 2026-10-27*
- I3 "View details" has no action. The ad link and experience level aren't shown. *open 2026-10-27*
- I4 CV upload keeps only the file name and accepts `.pdf,.csv`. *open 2026-10-27*
- I5 The score badge and bar can't receive a value yet. *open 2026-10-27*
- I6 Job search bar. *deferred 2026-10-27*. Agreed so far: runs in the browser on the loaded jobs, updates live while typing, searches the title by default, with a "Search in" option to switch to company or skills. Still open: whether "Search in" picks one field or several.

### Data & states (not yet discussed)
- S1 All jobs load at once, with no pagination. *open 2026-10-27*
- S2 Fast repeated Apply clicks can show stale results. *open 2026-10-27*
- S3 If the filters request fails, the whole layout fails. *open 2026-10-27*
- S4 Salary is always shown as "€ / month"; need to verify the currency and period. *open 2026-10-27*
- S5 The API base URL is hardcoded and should come from env config. *open 2026-10-27*

### Accessibility (not yet discussed)
- A1 Focus outlines are removed, so keyboard focus is invisible. *open 2026-10-27*

## 4. Change log
| Date | Change |
|------|--------|
| 2026-10-27 | File created. D1 (browser) and D2 (desktop deferred) recorded. Design review items logged. |
| 2026-10-27 | CV match panel added to the Jobs page (mock score). Score colors moved into one shared helper. |
| 2026-10-27 | Match ring enlarged (96 → 128px) and centered in the panel. |
| 2026-10-27 | Fixed the selected-card ring and focus outline being clipped on the edge rows of the job list. |
| 2026-10-27 | Job cards: info shown as a 2×2 grid (City, Domain / Job type, Experience); experience is hidden when empty. New "Experience" sidebar filter above "Salary info", applied in the browser like the salary filter (no backend change). Friendly labels: Middle → Mid-level, Fără → No experience, empty → Not specified; job details use the same labels. |

## 5. Superseded versions
_None yet._
