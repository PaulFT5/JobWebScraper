---
target: jobs card
total_score: 25
max_score: 36
na_heuristics: 9
p0_count: 0
p1_count: 2
target_identity: "file:C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\main-page\\fit-variants.html"
target_fingerprint: "sha256:8f939f67fccde7b3f37827824944f7152dc32f9759340a090663844d4c26bc05"
target_path: "C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\main-page\\fit-variants.html"
timestamp: 2026-11-24T14-24-14Z
slug: frontend-drafts-main-page-fit-variants-html
---
Method: dual-agent (A: design review · B: detector + headless renders + measurements + contrast). Live overlay skipped: headless CLI only. Target: the job card.

## Design Health Score
| # | Heuristic | Score | Key Issue |
|---|---|---|---|
| 1 | Visibility of System Status | 3 | Clear selected state, honest sample badge; hover nearly invisible |
| 2 | Match System / Real World | 3 | EUR, normal case help; raw "Middle", "electric/ Electromecanic" leak |
| 3 | User Control and Freedom | 3 | Group toggle and selection work |
| 4 | Consistency and Standards | 3 | Icons consistent; two left edges (tile vs text column) |
| 5 | Error Prevention | 3 | Details line clips silently |
| 6 | Recognition Rather Than Recall | 3 | Band thresholds only stated in group view |
| 7 | Flexibility and Efficiency | 2 | No sort by salary, no density option |
| 8 | Aesthetic and Minimalist Design | 3 | Quiet; "/100" on every card, reserved empty gap |
| 9 | Error Recovery | n/a | No error paths in mock |
| 10 | Help and Documentation | 2 | Nothing explains 50 / Partial in default grid |
| Total | | 25/36 (69%) | Acceptable |

## Design Specificity
Clean, restrained, no template tells; generic apart from the score block and the skills line (styled as plain metadata). Detector: 13 findings, all design-system-* vs stale DESIGN.md (n/a). Contrast: all pairs pass AA (tightest light fit on selected 4.97). Equal heights confirmed at 1440, 1280 grouped, 500.

## What's Working
- Score block: 20px green number leads on 40+, grey on weak; the fit cliff reads at a glance.
- Detail icons: 14px, 1.8 stroke, centred on 13px text, sr-only labels, missing facts omitted.
- Theme parity: both themes pass AA with margin.

## Priority Issues
1. [P1] Reserved title space reads as a hole (~20-30px under company on 1-line titles) and is wasted on phones (single column, ~5 cards per screen). Fix: put slack at the bottom (or between salary and skills) in multi-column; drop reservation in single column. Cmd: layout.
2. [P1] Bottom block has no leader: salary and skills line same size/weight/colour, 4px apart. Fix: salary 14px/600 (or into the score corner), skills line secondary (muted), 6-8px rhythm. Cmd: typeset.
3. [P2] Tie-breaker doesn't break ties: top four all "50 Partial · 2 of 4"; "2 of 7" vs "1 of 4" can read as contradicting the score. Fix: "2 to learn", top missing skill, or secondary sort shown in head row. Cmd: clarify.
4. [P2] Details line clips silently (18px, overflow hidden, no ellipsis). Fix: ellipsis on last fact or drop experience first; test at 360px. Cmd: harden.
5. [P3] Green + "Partial" disagree (nothing reaches Strong; green = least bad); 11px word ignored. Fix: word 12px or in score colour; state bands once in the head row. Cmd: clarify.

## Persona Red Flags
- Fast scanner: 5 lines x 3 cards zigzag; four identical top cards; salary not privileged.
- Casey: ~5 cards per screen; clipping hits first; "/100"+word take ~60px of 328px.
- Riley: clipped details; company ellipsis without tooltip; dangling "-" on wrap; "100/100" squeezes title; source spacing untidied.
- Jordan: is green 50 Partial good? "Middle" unclear.

## Minor Observations
- Selected light: tile #f2f2f2 nearly vanishes on #f6f6f6.
- Two left edges: bottom block aligned to tile, header text 42px in.
- Light border ~1.3:1, hover nearly invisible.
- Grey single-letter tiles cost 42px of title width.
- aria-pressed reads as toggle, not "current".

## Questions to Consider
- Would one dense row per job beat a 3-column grid for scanning?
- Why is salary fourth in reading order at the same weight as a line restating the score?
- Does every card need "/100" and a word, or one legend in the head row?
