---
target: new job cards
total_score: 25
max_score: 36
na_heuristics: 9
p0_count: 0
p1_count: 3
target_identity: "file:C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\main-page\\jobs.html"
target_fingerprint: "sha256:2614e33fa3204e43912354b46419d97598de2e41e050100fc149a9ffe3ab85c2"
target_path: "C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\main-page\\jobs.html"
timestamp: 2026-11-24T20-28-18Z
slug: frontend-drafts-main-page-jobs-html
---
Method: dual-agent (A: design review · B: detector + headless renders + measurements + contrast). Live overlay skipped: headless CLI only. Target: jobs.html cards.

## Design Health Score
| # | Heuristic | Score | Key Issue |
|---|---|---|---|
| 1 | Visibility of System Status | 3 | Current state subtle in light |
| 2 | Match System / Real World | 3 | "No experience" ambiguous; no diacritics; salary period unknown |
| 3 | User Control and Freedom | 3 | Group toggle remembered |
| 4 | Consistency and Standards | 3 | Icon strip at different heights within a row |
| 5 | Error Prevention | 3 | Example card labelled but its real twin sits lower |
| 6 | Recognition Rather Than Recall | 3 | Bands only in a hover tooltip |
| 7 | Flexibility and Efficiency | 2 | No sort control, no missing-skills view |
| 8 | Aesthetic and Minimalist Design | 3 | Skills line repeats score; € + EUR |
| 9 | Error Recovery | n/a | |
| 10 | Help and Documentation | 2 | Legend mouse-only |
| Total | | 25/36 (69%) | Acceptable |

## Design Specificity
Product-specific fit block and fit/pay right edge; skills line is the score restated (score = matched/total). Detector: 10 findings, all design-system-* vs stale DESIGN.md (n/a). Text contrast passes both themes; example tag dashed border 2.75:1 (non-text, advisory).

## Priority Issues
1. [P1] Skills line repeats the score (user removed skill names). Fix options: missing skills by name, or drop the line / keep count as sr text. Cmd: distill.
2. [P1] Shared row height floats the icon strip: example card +24px, neighbour gets 57px gap vs 33px; strips at different heights in a row. Fix: anchor strip + skills line together at the bottom. Cmd: layout.
3. [P1] Facts truncated at 720-1000px two-column ("Timisoa…", "Full ti…"); city cut. Fix: two columns from ~960px, or salary on its own line when narrow; never truncate city. Cmd: adapt.
4. [P2] Example card disturbs its row and duplicates a real ad. Fix: disclosure in the skills-line slot, or a separate "what strong looks like" specimen. Cmd: clarify.
5. [P2] Legend hover-only (not keyboard/touch); 40 and 8 look alike. Fix: legend once in the list header. Cmd: clarify.

## Persona Red Flags
- Fast scanner: bold black salary competes with the score; skills line gives no reason to open.
- Casey: fine at 500; 375 unverified (headless min width), likely collision.
- Riley: no tests for missing city, long company + tag, large salary ranges.
- Jordan: 75 Strong then the same job at 25; bands only on hover.

## Minor Observations
- Current state same colour as focus outline.
- Weak dark hover.
- "/100" washed out next to grey weak numbers.
- € + EUR ~40px, feeds truncation.
- Odd "Good fits 5" leaves an empty cell.
- 11.5/12.5/13.5px off-ramp sizes; 9px vs 12px radii.

## Questions to Consider
- Number and count both, or "2 of 4 · missing X"?
- Example card in the list, or an onboarding specimen?
- Design the right column as a deliberate fit/pay stack?
