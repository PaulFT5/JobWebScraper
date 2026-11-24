# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Primary: job seekers** browsing job ads from Romania. They upload their CV to see which ads fit their hard skills and which skills they are missing. *(confirmed 2026-11-05; 2026-11-24: ads are not limited to tech, so "tech" was removed — until 2026-11-24 this read "tech job ads from bestjobs.eu (Romania)")*
- **UI wording** *(since 2026-11-24)*: the data source (bestjobs.eu) is internal and is never named in the UI. Pages describe the jobs as job ads from Romania, without "tech".
- **Secondary: the bachelor-thesis committee.** The app is the user's CS bachelor thesis, so it must also demonstrate the matching engine (skill grounding, similarity, metrics) working end to end. *(confirmed 2026-11-05)*

## Product Purpose

Collect job ads, extract the hard skills each ad asks for, and match them against a user's CV. Success means a seeker can see, per job, how well they fit and why, and can see which skills the market asks for overall.

## Positioning

Two pillars, weighted equally *(confirmed 2026-11-05)*:

1. **Explainable skill match.** The score is not a black box: skills from the ad and the CV are grounded to the ESCO taxonomy, so the app can show which skills match, which are close, and which are missing.
2. **Market insight.** The analyzer shows which skills the job market asks for across all scraped ads.

## Operating Context

- Job data is scraped weekly from bestjobs.eu and skills are extracted daily by an LLM (GitHub Actions), stored in SQLite and served by a local FastAPI backend.
- The seeker filters the job list, uploads a CV, and compares match scores across jobs.
- The thesis demo runs locally (`dev.py`: API on :8000, UI on :5173).

## Capabilities and Constraints

- **Built:** job list with filters (sidebar), client-side search (title / company / skills), job details, CV match panel.
- **Placeholder / not yet real:** the match score is a fixed mock value until the matcher is wired to the API; the Analyzer page is designed (Extraction / Matching / Jobs sections) but not built.
- **Data facts:** ads are Romanian-market; some field values come in Romanian (e.g. experience "Fără" shown as "No experience"). UI language is English.
- **Score bands:** *(since 2026-11-24, user)* weak < 50, partial 50–70, strong > 70, shared by the match panel and the job cards. Drawn in the new Graphite/Night look *(decided 2026-11-24, option 1 of `drafts/main-page/fit-options.html`)*: one green for 50 and above (number and word), strong adds a filled green "✓ Strong" pill, weak and no match are grey; the word always travels with the number. *Until 2026-11-24:* red < 40, amber ≤ 70, emerald above.
- **Undecided:** salary period (until 2026-11-24 also the currency; shown as "€ / month", not verified); pagination; desktop app (deferred, see `FE_NOTES.md` D2).
- **Salary currency** *(since 2026-11-24, user)*: EUR. The period (month / year / gross / net) is still undecided, so the UI shows the currency only.
- Frontend decisions and open items are tracked in `frontend/FE_NOTES.md`.

## Evidence on Hand

- Real scraped job ads and extracted skills in `data/jobs/JobsDatabase.sqlite`.
- No real match scores, user testimonials or measured metric results yet. Future work must not invent scores, metric numbers or user quotes.

## Product Principles

1. **Show the why.** Every score should be traceable to the skills behind it.
2. **Real data only.** Mock values are marked as mock and replaced, never presented as results.
3. **Serve the seeker first, the demo second.** The committee should see the engine through a flow a real seeker would use.
4. **Market and match are one story.** What the market asks for and what this CV covers should read as connected views.
