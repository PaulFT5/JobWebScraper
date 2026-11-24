---
target: start page draft
total_score: 20
max_score: 28
na_heuristics: 7,9,10
p0_count: 0
p1_count: 2
target_identity: "file:C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\start-page\\index.html"
target_fingerprint: "sha256:0b20e56a8973aee6a2ca3765f680f04a0c910becee253ac9837b3fc61ed58be4"
target_path: "C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\start-page\\index.html"
timestamp: 2026-11-24T10-56-15Z
slug: frontend-drafts-start-page-index-html
---
Method: dual-agent (A: design review · B: detector + headless renders). Live overlay skipped: no mutable browser automation (headless CLI only).

## Design Health Score
| # | Heuristic | Score | Key Issue |
|---|---|---|---|
| 1 | Visibility of System Status | 3 | Merge gives live feedback on the CTA; mid-scroll the faded CTA stays clickable |
| 2 | Match System / Real World | 3 | Overlap = fit reads; "How the fit is worked out" slightly British |
| 3 | User Control and Freedom | 3 | Browse path now in hero, compact header, close; pinned scroll still holds ~1 screen |
| 4 | Consistency and Standards | 3 | Colour roles hold; missing skill drawn as a blue ring vs filled blue ink |
| 5 | Error Prevention | 3 | Little input; CTA leads to an unbuilt flow (known) |
| 6 | Recognition Rather Than Recall | 2 | Blue = job never named; overlap logic must be inferred |
| 7 | Flexibility and Efficiency | n/a | Persuade surface |
| 8 | Aesthetic and Minimalist Design | 3 | Strong reduction; short empty-brown beat around vh65 |
| 9 | Error Recovery | n/a | No error states |
| 10 | Help and Documentation | n/a | "How it works" is the help |
| Total | | 20/28 (71%) | Good |

## Design Specificity
Art direction authored for the product (CV ink x job ink = fit, carried by logo, hero, scroll, step marks). Substance thin: nothing says tech jobs / Romania / bestjobs.eu, no real ad or skill, ESCO unnamed in default "Type, no text" mode.
Detector: 28 findings (exit 2). 5 quality: undersized "to learn" REAL (~9.8px at <=875px wide; detector's 5.6px figure wrong); low-contrast white-on-paper FP (nav sits on cobalt); #8f8770 on brown FP (large display text, 4.0:1 >= 3:1); cramped-padding on close FP (48-90px padding); tight-leading intentional display type. 23 design-system findings: n/a, DESIGN.md describes the old app.

## What's Working
- One metaphor at four scales, fixed colour roles (orange CV, blue job, brown fit, yellow action).
- Step 2 (JS -> JavaScript) explains grounding with the skills themselves.
- Reduced motion, keyboard focus merge, inert/pointer handling of both headers.

## Priority Issues
1. [P1] Engine invisible to the committee: default mode hides step text and the only ESCO mention; no "close" match state; market-insight pillar absent. Fix: one short caption per step (ESCO named), a "close" row, a pointer to the market view. Cmd: clarify.
2. [P1] No real data / doesn't say what jobs: no tech/Romania/bestjobs.eu, no count, invented example skills. Fix: quiet fact line (N tech ads from bestjobs.eu, updated weekly), example skills from a real ad labelled as example. Cmd: clarify (or onboard).
3. [P2] Remaining dead beat in the pinned scroll: gap between fit line out (s .72) and section becoming readable (~vh65). Fix: keep the line until the section covers it, or start the section rise earlier / shorten the stage. Cmd: animate.
4. [P2] Phone loses the metaphor: at rest the inks only touch (no brown); headline on paper below a cropped disc; hard paper->brown cut; narrow non-touch windows never auto-merge. Fix: start with visible overlap on phones, headline on/under it, softer edge into the brown. Cmd: adapt.
5. [P3] Focus ring and small text: yellow 3px focus ring ~1.3:1 on paper (brand, nav, CTA edge); "to learn" ~10px on phones (detector agrees). Fix: two-tone ring (ink + yellow halo); "to learn" >= 12px. Cmd: harden.

## Persona Red Flags
- Jordan: which jobs, from where? Blue unexplained; must sign up before any value.
- Riley: #login/#jobs dead (mock); 820x1180 floats mid-page; 2560x900 lopsided; 900x420 headline ~35px; "Your CV" orphan "fit."
- Casey: no overprint at rest on narrow non-touch; "to learn" ~10px; full-width CTA good.
- Committee: no ESCO in default mode, no real ad, no close match, no metric, no analyzer link.

## Minor Observations
- Headline ink on cobalt ~3.3:1 (passes as large text only).
- scroll-behavior:smooth not disabled under reduced motion.
- Faded mid-scroll CTA still clickable.
- Legend's "Log in or sign up to add it" repeats the CTA.
- PostgreSQL vanishes between step 1 and step 3 without a word.
- Light paper band under the brown on overscroll (html background paper).
- Dead CSS: .legend.job, footer rules.
- Short landscape (~420px tall): white nav can land on paper.

## Questions to Consider
- Why ask for an account before showing one real overlap? Could the brown hold one real job's shared skills?
- Is "Log in / Sign up" the right promise for a demo whose working path is browsing?
- Brown = fit. What colour is "close"?
