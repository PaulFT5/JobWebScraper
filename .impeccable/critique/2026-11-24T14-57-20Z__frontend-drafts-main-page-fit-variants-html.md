---
target: jobs card after polish
total_score: 26
max_score: 36
na_heuristics: 9
p0_count: 0
p1_count: 0
target_identity: "file:C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\main-page\\fit-variants.html"
target_fingerprint: "sha256:c06f0a036b5636131bffa82d2d3f0b5c332228fc24b81db050b7b4fb94662dcb"
target_path: "C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\main-page\\fit-variants.html"
timestamp: 2026-11-24T14-57-20Z
slug: frontend-drafts-main-page-fit-variants-html
---
Method: dual-agent (A: design review · B: detector + headless renders + measurements + contrast). Live overlay skipped: headless CLI only. Target: the job card after polish.

## Design Health Score
| # | Heuristic | Score | Key Issue |
|---|---|---|---|
| 1 | Visibility of System Status | 3 | Current state close to hover |
| 2 | Match System / Real World | 3 | Salary period unknown, ranges not comparable |
| 3 | User Control and Freedom | 3 | Group toggle, Esc, selection in place |
| 4 | Consistency and Standards | 3 | € icon + "EUR" twice; icon on "No salary listed" |
| 5 | Error Prevention | 3 | Clamp and ellipsis behave |
| 6 | Recognition Rather Than Recall | 4 | Word travels with number; legend in count line |
| 7 | Flexibility and Efficiency | 2 | One fixed sort, no keyboard move between cards |
| 8 | Aesthetic and Minimalist Design | 3 | Repeats: currency twice, "Full time" on ~90% |
| 9 | Error Recovery | n/a | |
| 10 | Help and Documentation | 2 | No on-card hint how the score is built |
| Total | | 26/36 (72%) | Good |

## Design Specificity
Mostly product-specific (score block, salary-first EUR, skills line, normalised titles); frame is generic job-board grammar. Detector: 13 findings, all design-system-* vs stale DESIGN.md (n/a). Text contrast passes in both themes; hover borders miss 3:1 (light 2.75, dark 2.45), advisory.

## What's Working
- Score block: number + word in one green, AA in both themes; Strong pill reads as an upgrade.
- Reading order: title, fit, bold salary, skills pinned to the bottom edge; rows align.
- Ad text handled with care: normal case, dash kept with next word, 2-line clamp.

## Priority Issues
1. [P2] Single column (phone) cards carry ~30px dead space from equal rows; ~4.5 cards per screen. Fix: auto row heights below 720px. Cmd: adapt.
2. [P2] Space between salary and skills reads as leftover. Fix: skills line as a footer with a hairline rule and fixed padding. Cmd: layout.
3. [P2] Honesty: "skills you have" on sample scores; sample tag scrolls away (PRODUCT.md principle 2). Fix: "2 of 4 skills in the sample CV" while sample active, or sticky sample tag. Cmd: clarify.
4. [P3] Repeated facts: € icon + EUR, icon on "No salary listed", "Full time" on nearly every card. Fix: drop one currency marker, no icon on no-salary, work type only for exceptions. Cmd: distill.
5. [P3] Weak band all same grey; count line overloaded (count + sort + legend). Fix: legend in a "?" popover or own quieter line; optional lighter very-low scores. Cmd: clarify.

## Persona Red Flags
- Fast scanner: four identical 50s decided by salary without period; weak band unrankable; Full time noise.
- Casey: dead space per card; ~100px of legend + tag before first card.
- Riley: empty 18px details row when no facts; Strong pill widens fit column; 100/100 widens it more.
- Jordan: sample tag scrolls away; 50/100 unexplained; salary period unknown.

## Minor Observations
- Dark: "Add your CV" shares the fit green.
- Current state close to hover; dark current border loud.
- Nested native tooltips (card + details line).
- City names without diacritics vs titles with them (data).
- Hover border below 3:1 in both themes.

## Questions to Consider
- Score is matched/total skills; does "/100" imply precision it lacks?
- Is salary ready to be second-loudest while its period is unknown?
- Would one or two missing-skill names beat the count?
