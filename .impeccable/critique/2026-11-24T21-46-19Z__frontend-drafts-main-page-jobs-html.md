---
target: top bar
total_score: 23
max_score: 36
na_heuristics: 9
p0_count: 0
p1_count: 2
target_identity: "file:C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\main-page\\jobs.html"
target_fingerprint: "sha256:2fc7d7a2346e415a8f0a4a413faae106790c58d686fded6dde7c4bd770e3a5d5"
target_path: "C:\\Users\\User\\PycharmProjects\\JobWebScraper\\frontend\\drafts\\main-page\\jobs.html"
timestamp: 2026-11-24T21-46-19Z
slug: frontend-drafts-main-page-jobs-html
closed: true
---
Method: dual-agent (A: design review · B: detector + headless renders + measurements + contrast). Live overlay skipped: headless CLI only. Target: top bar + account panels (Analyzer button included; it was added during the run).

## Design Health Score
| # | Heuristic | Score | Key Issue |
|---|---|---|---|
| 1 | Visibility of System Status | 3 | Filled icon and group dot work; dot colour-only, sample-CV state not in the bar |
| 2 | Match System / Real World | 2 | "My account" and "Sign out" with no accounts |
| 3 | User Control and Freedom | 3 | Esc, back, toggle, scrim all work; Sign out dead |
| 4 | Consistency and Standards | 2 | Left group on the content grid, right group on the viewport; Analyzer weighted like Filters |
| 5 | Error Prevention | 3 | Dead Sign out |
| 6 | Recognition Rather Than Recall | 2 | Add your CV 3 levels deep; theme under "account" |
| 7 | Flexibility and Efficiency | 2 | No "/" search shortcut, no direct CV route |
| 8 | Aesthetic and Minimalist Design | 3 | Calm; 2-item drawer is chrome for little content |
| 9 | Error Recovery | n/a | |
| 10 | Help and Documentation | 3 | Drawer hints good |
| Total | | 23/36 (64%) | Acceptable |

## Design Specificity
Brown bar + mark carry the start page's identity (cream on brown ~13.6:1). Account drawer is the default web-app pattern; the bar says "search tool", not "your CV vs the market". Detector: 17 findings, all design-system-* vs stale DESIGN.md (n/a). Fixed during synthesis: light-theme bar colours leaked into the Filters panel (restructuring bug).

## What's Working
- Brand continuity of the brown bar; excellent text contrast.
- 1440+ alignment exact (Filters = first card edge at 1440 and 1920).
- Panel mechanics: under the bar, stacked sub-panels, Esc one level, focus return and trap, reduced motion, filled icon.

## Priority Issues
1. [P1] CV step buried (icon > Account > My account > Add your CV) while Analyzer (not built) gets a labelled bar button. Fix: CV state on the account icon (dot / "Sample CV" pill opening Your CV); Analyzer icon-only or demoted. Cmd: clarify.
2. [P1] Account menu misdescribes and is too deep: "My account"/"Sign out" without accounts; 2-item middle level. Fix: one drawer with Your CV + Theme inline, hide Sign out until accounts exist, header "Your CV & settings". Cmd: distill.
3. [P2] Right group not on the content grid (account icon at x~1891 at 1920 vs list end 1532); 1280-1439 nothing aligns. Fix: right group ends at list's right edge on wide screens; bar padding = page padding below 1440. Cmd: layout.
4. [P2] "Modal" panel not modal; bar stays clickable; Filters could open under the drawer. Fix: close drawer on bar interaction, or non-modal without scrim. Cmd: harden.
5. [P2] Faint control edges (border 1.75:1, field 1.17:1 on brown; dark 1.26 / 1.09); group dot colour-only and not announced; 38px controls (<44 touch). Fix: stronger edge/fill, 44px on phones, state in Filters accessible name. Cmd: polish.

## Persona Red Flags
- Jordan: no CV action in the bar; person icon doesn't say "upload CV"; Analyzer goes nowhere.
- Fast scanner: no "/" shortcut; 460px search in a wide bar.
- Casey: icon-only Filters and Analyzer easy to confuse; drawer leaves a thin strip.
- Sam: modal announced but bar reachable; group state silent; "My account" without an account.

## Minor Observations
- Dark scrim barely visible; dark panel edge 1.10 vs dimmed page.
- Logo-Filters gap ~11px at 1440.
- Avatar in the drawer header repeats the icon.
- Themes' bars feel like two products.

## Questions to Consider
- Why is the search box the bar's identity when the promise is "your CV"?
- Should an unbuilt Analyzer outrank the CV step?
- Does theme need a home under a person icon with System as default?
