---
target: two-column jobs page
total_score: 26
max_score: 36
na_heuristics: 9
p0_count: 0
p1_count: 2
target_identity: "file:C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\main-page\\two-columns.html"
target_fingerprint: "sha256:883d07afee8c972ebb62b5ed3f167583370ae0bf8a35bdfa8ee8faaca516c4b2"
target_path: "C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\main-page\\two-columns.html"
timestamp: 2026-11-24T19-54-27Z
slug: frontend-drafts-main-page-two-columns-html
---
Method: dual-agent (A: design review + declutter guide · B: detector + headless renders + measurements). Live overlay skipped: headless CLI only. Target: two-columns.html.

## Design Health Score
| # | Heuristic | Score | Key Issue |
|---|---|---|---|
| 1 | Visibility of System Status | 3 | Sample tag scrolls away |
| 2 | Match System / Real World | 3 | /100 beside a sample that tops out at 50; city diacritics |
| 3 | User Control and Freedom | 3 | Filters panel Esc/outside/focus fine |
| 4 | Consistency and Standards | 4 | Fixed fact order and position |
| 5 | Error Prevention | 2 | "skills you have" on sample scores |
| 6 | Recognition Rather Than Recall | 3 | Matched skills hidden behind a count |
| 7 | Flexibility and Efficiency | 2 | No visible sort, no salary/city scan |
| 8 | Aesthetic and Minimalist Design | 3 | Repeated facts, lopsided card |
| 9 | Error Recovery | n/a | |
| 10 | Help and Documentation | 3 | Legend inline but overloads count line |
| Total | | 26/36 (72%) | Good (same as 3-col) |

## Design Specificity
Quiet, deliberate tool; but the 2-col card is the 3-col card stretched: facts in a ~300px left stack, right half empty under the score (text uses ~35-40% of card width). Measured: card 526x147 at 1440 (8 full cards in first viewport) vs 3-col 401x166 (12). Detector: 13 findings, all design-system-* vs stale DESIGN.md (n/a).

## What's Working
- Titles on one line at 1280-1920.
- Right-aligned score column scans straight down.
- Night holds up.

## Priority Issues
1. [P1] Unused right half of each card (~220px under the score). Fix: right "decision rail" with score, word and salary; facts on one line with the company. Cmd: layout.
2. [P1] Dead space on phones/900px from equal row heights (unchanged). Fix: equal heights only within a row of 2. Cmd: adapt.
3. [P2] Repeated/constant facts: € + EUR, icon on no salary, Full time on 14/14. Fix: drop EUR suffix, no icon on no salary, work hours only when not full time. Cmd: distill.
4. [P2] Sample honesty: "skills you have" on sample; tag scrolls away. Fix: "skills matched" while sample active; sticky tag or "Sample CV:" prefix. Cmd: clarify.
5. [P3] Count line overloaded. Fix: legend to fit-word hover or Filters panel. Cmd: quieter.

## Declutter guide (summary)
Remove: initials tile (user's call: was kept), constant Full time, EUR suffix, icon on no salary, legend from count line. Merge: company · city · experience one line; score + word + salary as right rail. Keep: 2-line clamp, number+word, strong pill, grey skills line at bottom, same height within a row, selected style. Add: name 2-3 matched skills on the skills line.
Sizes: padding 20px (24 at >=1280), radius 12, gaps 16 (24 with group headers), title 17/600 lh 24, meta 14, score 24/700 with /100 at 12, word 13, salary 15/700 right-aligned, skills 13-14. Title->meta 4, header->skills >=16, score->salary 8. Card ~112-120px tall.
Sketch A (recommended): title + meta left, score/word/salary rail right, skills line at bottom. Sketch B: header + icon fact strip with salary right, divider, skills. Sketch C: matched/missing skill chips instead of the count (changes a decision).

## Persona Red Flags
- Fast scanner: score and salary in different places; zigzag among equal 50s.
- Casey: ~40px gaps; first card at y~210; tile costs 42px.
- Riley: /100 and "you have" on sample look like real poor results; strong pill never seen.
- Jordan: legend easy to miss; green Partial 50 vs /100.

## Minor Observations
- City diacritics vs title diacritics.
- Group header descriptions ~1000px from the label.
- Hover close to selected weight in light.
- 1120px column leaves ~400px margins at 1920; 1200-1240 would let Sketch A breathe.

## Questions to Consider
- With 2 named matches, is the N of M count still needed?
- Should the rail double as a sort control?
- Would a dense one-row-per-job list beat a card grid?
