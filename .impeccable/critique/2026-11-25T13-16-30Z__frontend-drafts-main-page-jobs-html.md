---
target: profile sidebar
total_score: 21
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 3
target_identity: "file:C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\main-page\\jobs.html"
target_fingerprint: "sha256:ac4e50da8d6fee1510eda88272284d22b56c0e4a9157a9006d07bcb8408ef5b2"
target_path: "C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\main-page\\jobs.html"
timestamp: 2026-11-25T13-16-30Z
slug: frontend-drafts-main-page-jobs-html
---
Method: dual-agent (A: design review · B: detector + headless Chrome via DevTools protocol: real keys/clicks, measurements, contrast). Live overlay skipped: no interactive browser tool. Target: account / profile sidebar (aside#acct, #me, #prefs) in frontend/drafts/main-page/jobs.html.

## Design Health Score
| # | Heuristic | Score | Key Issue |
|---|---|---|---|
| 1 | Visibility of System Status | 2 | "Scores use a Sample CV" only visible 3 levels deep |
| 2 | Match System / Real World | 1 | "Account", "My account", "Sign out" next to "Not signed in", in an app with no accounts |
| 3 | User Control and Freedom | 3 | Esc one level at a time, back, outside press; sub-panels have no X |
| 4 | Consistency and Standards | 2 | Dark CTA uses the fit green; level-1 and level-2 headers differ; "Account" 3 times |
| 5 | Error Prevention | 3 | Sign out looks live, does nothing |
| 6 | Recognition Rather Than Recall | 2 | CV filed under "My account" |
| 7 | Flexibility and Efficiency | 1 | Every CV action costs 3 clicks; no direct path |
| 8 | Aesthetic and Minimalist Design | 3 | Clean, but level 1 is a tall panel with 2 rows and a stranded Sign out |
| 9 | Error Recovery | 1 | The only primary action ("Add your CV") ends at file-not-found |
| 10 | Help and Documentation | 3 | Good hints ("scores on the job list come from this CV") |
| Total | | 21/40 (53%) | Acceptable |

## Design Specificity
Competent, generic SaaS account drawer (avatar, chevron rows, Sign out at the bottom). The one thing specific to CVMatch, the CV card, sits two levels down. Detector: 21 findings, all design-system-* against an absent/stale DESIGN.md (false positives); only the scrim colour (line 271) touches the drawer directly. No console errors.

## What's Working
- Mechanics: panel under a still-visible bar, icon fills while open, Esc one level at a time, focus returns to the opener, outside press only closes (click swallowed), reduced motion honoured, theme choice persists.
- Copy states cause and effect: "12 skills · scores on the job list come from this CV"; "Upload a PDF, check the skills we read, and your scores update".
- Phones: full-width panels, 44px close/back/rows/theme options.

## Priority Issues
1. [P1] CV buried 3 levels under a misleading label (repeat of 2026-11-24 #1): icon → Account → My account → card; the middle level exists to hold 2 rows. Fix: one panel, CV card first, Theme inline below; title "Your CV & settings". Cmd: distill.
2. [P1] Account words without accounts (repeat of 2026-11-24 #2): "Not signed in" + an active-looking Sign out that does nothing. Fix: hide Sign out and "My account" until accounts exist; status line "Using a sample CV: upload yours to see real scores". Cmd: clarify.
3. [P1] Keyboard focus escapes App preferences: with Dark or Light checked, Tab leaves the panel to "How fit works" and the cards behind the scrim; two aria-modal dialogs exposed at once; page behind not inert and still scrolls. Also opening Preferences focuses Light instead of the checked option; My account skips Back. Fix: make the page (and lower panel) inert while open, lock scroll, focus the checked radio. Cmd: harden.
4. [P2] Sample state hidden and the only CTA dead: "Add your CV" → missing you.html (moved to deprecated, user decision); the user learns the scores are sample data last. Fix: "Sample CV" marker near the icon/list; until the CV page exists, a disabled "CV upload coming soon". Cmd: onboard.
5. [P2] Weak edges and colour roles: dark scrim changes the page 1.02:1 (drawer vs page 1.10:1); light drawer edge 2.88:1; Theme selected state 1.06–1.16:1 (only text colour shows it); dark CTA = fit green. Fix: dark scrim about .6, stronger selected segment, neutral CTA. Cmd: colorize / polish.

## Persona Red Flags
- Jordan: sees "Account", looks for sign-in, finds none; doesn't link "My account" with the CV; trusts sample scores without knowing.
- Sam: focus leak in Preferences; two modal dialogs at once; page not inert; Sign out announced but inert; sub-menu buttons lack aria-expanded.
- Casey: tall panel with 2 rows and Sign out ~600px lower; 3 taps to the CV; 10px dimmed sliver at 390; "Add your CV" 42px (<44).

## Minor Observations
- Sub-panels have no X; the stacked panel exactly covers the root (back arrow is the only cue).
- Filters sidebar stays open under the scrim.
- Header subtitle wraps leaving "session" alone on phones.
- "12 skills" can't be inspected.
- ?theme= hook doesn't update the Theme radio (screenshot hook only).

## Questions to Consider
- If the CV is the product, why is it behind a person icon instead of a CV chip in the bar?
- What would the panel lose if "Account" left the vocabulary until accounts exist?
- Should anyone see a fit score before knowing whose CV it was computed against?
