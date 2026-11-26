---
target: filter sidebar
total_score: 25
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 2
target_identity: "file:C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\main-page\\jobs.html"
target_fingerprint: "sha256:7f001180e935517d1dd4334800709b42f9367f7738159199ffd1543b64869e46"
target_path: "C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\main-page\\jobs.html"
timestamp: 2026-11-25T12-17-52Z
slug: frontend-drafts-main-page-jobs-html
---
Method: dual-agent (A: design review · B: detector + headless renders + measurements + contrast). Live overlay skipped: no interactive browser tool. Target: Filters sidebar (aside#fpanel) in frontend/drafts/main-page/jobs.html.

## Design Health Score
| # | Heuristic | Score | Key Issue |
|---|---|---|---|
| 1 | Visibility of System Status | 2 | No result preview before Apply; on phones the reload happens behind the full-width panel |
| 2 | Match System / Real World | 3 | "Estimated salary" can never match the data; "View" is vague |
| 3 | User Control and Freedom | 2 | Reset also wipes sort + grouping and acts instantly; no in-panel close |
| 4 | Consistency and Standards | 2 | Everything staged except Reset; "View" heading styled differently from the other sections |
| 5 | Error Prevention | 2 | No option counts (facet counts exist in data.js) and a dead option, so zero-result traps |
| 6 | Recognition Rather Than Recall | 3 | Collapsed Sort shows its value; collapsed filter groups show only a number |
| 7 | Flexibility and Efficiency | 2 | Every tweak = Apply + reload + scroll to top |
| 8 | Aesthetic and Minimalist Design | 3 | Calm, but all 6 sections open (~26 controls); disabled Apply is a heavy grey slab |
| 9 | Error Recovery | 3 | Clear empty state with reset |
| 10 | Help and Documentation | 3 | Group by fit described inline |
| Total | | 25/40 (63%) | Acceptable |

## Design Specificity
Mostly generic e-commerce facet sidebar, carefully tokenised. Product-specific only in Group by fit. Fit (the product's core metric) can be sorted and grouped but not filtered. Detector: 21 findings, all design-system-* against an absent/stale DESIGN.md (false positives, as in the previous critique); 3 touch the sidebar (#2c3239 border, 5px checkbox radius, 17px heading).

## What's Working
- Real staged/applied model: Apply only live when changes differ; the count on Filters reflects applied state, and the accessible name says "N active, grouped by fit".
- Collapsed Sort shows its value; count pills have screen-reader text; 44px targets on phones; hidden panel is not tabbable.
- At 1920 the sidebar fills the left gutter exactly (gap 19.5px); dark theme edge and checked states well tuned. No console errors.

## Priority Issues
1. [P1] Overlap at 1100–1784px: covers 160px (1440) to 274px (1100) of the first card column, cutting titles mid-word, so results can't be read beside the filters. (User decision 2026-11-25: cover the cards.) Options: list shifts or drops to one column below ~1784px; or honest overlay with light scrim. Cmd: layout.
2. [P1] Focus is lost after Apply and after the empty-state Reset (the button disables or is removed while focused, so focus drops to the page body); on phones Apply changes nothing visible because the list reloads behind the panel. Fix: move focus to the results status or first card after reload; on phones close the panel on Apply or show the result count on the button. Cmd: harden.
3. [P2] Reset mixes up filters and view: it also clears Sort and Group by fit (a saved preference), stays enabled when only grouping is on while the badge shows 0, and acts instantly while everything else is staged. Fix: Reset/"Clear filters" clears filters only. Cmd: clarify.
4. [P2] Zero-result traps: "Estimated salary" never matches; no per-option counts; 0 results still shows 2 skeletons first. Fix: drop or hide "Estimated" until the data has it; show option counts (0 greyed out); live total on Apply. Cmd: harden.
5. [P2] Weak edges: checkbox/radio border 2.75:1 light, 2.45:1 dark (below 3:1); off-switch track 1.24:1; sidebar edge 1.24 / 1.46:1 against the page. Fix: darker checkbox border (about #8a8a8a light / #6b7380 dark), visible track border. Cmd: polish.

## Persona Red Flags
- Alex: every tweak costs Apply + reload + scroll; no keyboard shortcut; salary sort high→low only; Reset wipes grouping.
- Sam: focus lost after Apply/Reset; 4 extra Tab stops (search, Jobs, Analyzer, account) between Filters and the panel; no Esc (legend has one).
- Casey: panel hides the results and Apply doesn't close it; Apply/Reset out of thumb reach at the top; icon-only Filters button.

## Minor Observations
- Disabled Apply (light) looks heavier than enabled Reset.
- "Not specified" listed first in Experience.
- The search-in-group input is never rendered with current data (dead CSS; its focus cue is border only).
- ?filters=open hook leaves focus on body.
- Headless renders showed the slide-in stuck mid-way under virtual time; confirm once in a real browser.

## Questions to Consider
- If fit is the product, why filter by city but not by minimum fit?
- Does staging + Apply earn its cost on ~2,000 local ads, or could filters apply instantly?
- Is a sidebar that cuts the first column at 1440 really non-modal?
