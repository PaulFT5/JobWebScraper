---
target: start-page
total_score: 18
max_score: 28
na_heuristics: 7,9,10
p0_count: 0
p1_count: 3
target_identity: "file:C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\start-page\\index.html"
target_fingerprint: "sha256:8360173f2b6efaacd03b656d3015b66a72d8f99d6bd62859759687b9a679dec5"
target_path: "C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\start-page\\index.html"
timestamp: 2026-11-23T18-07-55Z
slug: frontend-drafts-start-page-index-html
---
Method: dual-agent (A: design review · B: detector + headless renders). Live overlay skipped: no mutable browser automation.

## Design Health Score
| # | Heuristic | Score | Key Issue |
|---|---|---|---|
| 1 | Visibility of System Status | 2 | ~1 screen of scroll shows only a growing brown field |
| 2 | Match System / Real World | 3 | Overlap metaphor reads; "Log in" wrong for visitors with no account |
| 3 | User Control and Freedom | 2 | Header fades and goes inert after half-way; no nav returns |
| 4 | Consistency and Standards | 3 | Close promises "browse the jobs" but only offers Log in |
| 5 | Error Prevention | 3 | Little input; mid-fade headline is the weak moment |
| 6 | Recognition Rather Than Recall | 2 | Only orange labelled; blue = job and brown = fit must be guessed |
| 7 | Flexibility and Efficiency | n/a | Persuade surface, two actions |
| 8 | Aesthetic and Minimalist Design | 3 | Strong reduction; lead repeats the headline |
| 9 | Error Recovery | n/a | No forms yet |
| 10 | Help and Documentation | n/a | "How it works" is the help |
| Total | | 18/28 (64%) | Acceptable |

## Design Specificity
Concept authored for the product (CV ∩ job = fit as an overprint; brown becomes the page). Resting hero generic: nothing above the fold says tech jobs / skills / Romania.
Detector: 26 findings; 3 quality: undersized "to learn" (real, ~10px on phone), white-on-paper low contrast (false positive, ink layers invisible to static scan), #8f8770 on brown 4.0:1 (false positive, large text). 23 design-system findings vs the discarded old DESIGN.md: not applicable.

## What's Working
- One overprint metaphor across logo, hero, scroll, step marks, ground.
- "Type, no text" steps: JS -> JavaScript explains grounding at a glance.
- Fallbacks: reduced motion, keyboard focus merge, phone layout, no overflow at 1440 / 500.

## Priority Issues
1. [P1] Hero cropped on laptop/wide (16:10 sheet taller than 730/800px viewports); "Your CV" legend off-screen. Fix: cap sheet to viewport, geometry from smaller dimension, legends anchored to viewport. Cmd: adapt.
2. [P1] Headline illegible mid-fade (~1.6:1 on cobalt at t~0.5). Fix: threshold switch with short crossfade. Cmd: polish.
3. [P1] Browse path disappears after hero; close has no Browse link. Fix: Browse text link at close + compact returning header. Cmd: layout.
4. [P2] Scroll-pin dead zone (~90vh of colour only). Fix: shorter stage or a line in the brown. Cmd: animate.
5. [P2] Hero doesn't say what the product is; "Log in" implies an account; blue unlabelled. Fix: one-line sub, "Log in / Sign up", label the blue. Cmd: clarify.

## Persona Red Flags
- Jordan: "fit" unexplained until screen 2; Log in with no sign-up.
- Riley: half-way cursor greys the headline; PageDown skips the merge; faded header inert; light band on overscroll; blur un-merges.
- Casey: layout solid; auto-merge easy to miss; no Browse at the end.
- Committee: no engine evidence; ESCO unnamed in default variant; "no black-box score" claimed, not shown.

## Minor Observations
- Yellow button edge nearly invisible on paper side.
- Missing skill (Docker, "to learn") is the quietest element.
- html background still paper: light band under brown on overscroll.
- Header "Browse jobs" bold (leftover class) reads as primary.
- Footer removed by user request (not counted); page ends abruptly.

## Questions to Consider
- Should the brown flood be the reward after login, not the logged-out landing?
- Would one real job with 3 grounded skills in the overlap beat abstract circles?
- Why is the gap, CVMatch's most useful output, the quietest element?
