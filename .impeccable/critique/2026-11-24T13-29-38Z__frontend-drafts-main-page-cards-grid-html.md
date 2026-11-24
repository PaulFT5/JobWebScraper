---
target: light mode job cards
total_score: 19
max_score: 28
na_heuristics: 7,9,10
p0_count: 0
p1_count: 3
target_identity: "file:C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\main-page\\cards-grid.html"
target_fingerprint: "sha256:6110077ee64d1223f8743e7d6945bc205597624fc3ca395464239da1bd631bd5"
target_path: "C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\main-page\\cards-grid.html"
timestamp: 2026-11-24T13-29-38Z
slug: frontend-drafts-main-page-cards-grid-html
---
Method: dual-agent (A: design review · B: detector + headless renders + contrast calc). Live overlay skipped: headless CLI only. Target: light theme (Graphite).

## Design Health Score
| # | Heuristic | Score | Key Issue |
|---|---|---|---|
| 1 | Visibility of System Status | 3 | Count, sort and sample CV stated; first card preselected reads as a pick |
| 2 | Match System / Real World | 2 | Salary has no currency/period; raw ALL-CAPS titles/companies |
| 3 | User Control and Freedom | 2 | No sort control, no good-fits-only view, 14 items under "2,242" |
| 4 | Consistency and Standards | 3 | Uniform cards; data casing inconsistent |
| 5 | Error Prevention | 3 | Little to get wrong |
| 6 | Recognition Rather Than Recall | 3 | Band word helps; no "/100", 40 cutoff implicit |
| 7 | Flexibility and Efficiency | n/a | Static grid |
| 8 | Aesthetic and Minimalist Design | 3 | Clean; dead weight: Full time on 14/14, "Salary … as listed", empty initials tile |
| 9 | Error Recovery | n/a | No error/empty states in mock |
| 10 | Help and Documentation | n/a | None on this surface |
| Total | | 19/28 (68%) | Acceptable |

## Design Specificity
Palette discipline real (near-black/white, green only on fits >= 40) and fixes the "too much colour" complaint; card itself is the default job-board card, the fit score (the product's difference) gets a number and an 11px word. Detector: 12 findings, all design-system-* vs stale DESIGN.md (n/a). Contrast: all pairs pass AA; tightest fit/muted on selected fill ~4.8:1 at 11-11.5px.

## What's Working
- Score is the loudest element (20px/700, top-right), read right after the title.
- One colour meaning: green = good fit; weak drops to grey.
- Calm and dense: ~9-12 cards per 1440 screen; clear selected state.

## Priority Issues
1. [P1] Can't find the best job in 3 seconds: four identical "50 Partial" cards, band edge only a colour change mid-row, 0 shown as "Weak". Fix: band break in the grid (label row/gap), tie-breaker on card ("2 of 4 skills"), 0 = "No match". Cmd: clarify.
2. [P1] Keyboard/screen reader: div role=button with click only (Enter/Space dead), re-render destroys focus, aria-label on plain div ignored, Filters icon-only on phone has no accessible name. Fix: real button, update state in place, visually hidden score text, label on Filters. Cmd: harden.
3. [P1] Salary ambiguous and noisy: no unit, "as listed" on every card, ragged rows without salary. Fix: unit once known (PRODUCT.md: undecided), drop "Salary" label, muted "No salary listed". Cmd: clarify.
4. [P2] Title truncation hides the deciding part; ALL-CAPS data shouts. Fix: 2-line clamp, title-case all-caps companies. Cmd: typeset.
5. [P2] Meta line and tile carry little: Full time 14/14, level missing 9/14, grey initials tile. Fix: work type only when not full time, smaller/optional tile. Cmd: distill.

## Persona Red Flags
- Fast scanner: identical 50s at top, zigzag rank across 3 columns.
- Casey: ~106px sticky header on phone; Dark switch in primary row; Filters icon has no name.
- Riley: no tooltip on truncation; 0 = "Weak"; empty list state missing; focus lost on select.
- Jordan: "50" without /100; "sample CV" too quiet, may read scores as their own.

## Minor Observations
- Focus ring radius 6px vs card 10px.
- Card border ~1.2:1 on white, edges vanish on weak screens.
- 1px title-company gap vs 10px before meta.

## Questions to Consider
- Why five generic facts and none of the "why" (2 of 4 skills)?
- Does a zigzag 3-column grid suit a ranked list, or should bands be structure?
- Does "Dark" belong next to the one main action?
