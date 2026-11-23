---
name: CVMatch
description: Job compatibility engine — a quiet instrument for measuring CV-to-job fit.
colors:
  bench-navy: "#0f172a"
  reagent-teal: "#14b8a6"
  reagent-teal-bright: "#2dd4bf"
  reagent-teal-ink: "#0f766e"
  reagent-teal-wash: "#f0fdfa"
  reagent-teal-wash-deep: "#ccfbf1"
  reagent-teal-edge: "#5eead4"
  apply-green: "#047857"
  apply-green-hover: "#059669"
  paper: "#ffffff"
  bench-floor: "#f8fafc"
  hairline: "#e2e8f0"
  rail-line: "#334155"
  ink: "#0f172a"
  ink-muted: "#64748b"
  rail-text: "#e2e8f0"
  rail-text-muted: "#94a3b8"
  score-weak: "#ef4444"
  score-partial: "#f59e0b"
  score-strong: "#10b981"
  chart-sage: "#7d9c7f"
  chart-terracotta: "#b9846a"
  chart-dusty-blue: "#7f9fb3"
  chart-ochre: "#a8936a"
typography:
  headline:
    fontFamily: "ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1.55
  title:
    fontFamily: "ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.43
  body:
    fontFamily: "ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.43
  caption:
    fontFamily: "ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 400
    lineHeight: 1.33
  label:
    fontFamily: "ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.33
    letterSpacing: "0.05em"
  score:
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
    fontSize: "1.5rem"
    fontWeight: 600
    lineHeight: 1
  data:
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
    fontSize: "0.6875rem"
    fontWeight: 400
    lineHeight: 1.4
rounded:
  sm: "4px"
  md: "6px"
  lg: "8px"
  xl: "12px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
components:
  button-apply:
    backgroundColor: "{colors.apply-green}"
    textColor: "{colors.paper}"
    typography: "{typography.title}"
    rounded: "{rounded.lg}"
    padding: "6px 12px"
  button-apply-hover:
    backgroundColor: "{colors.apply-green-hover}"
  button-rail-ghost:
    textColor: "{colors.rail-text}"
    rounded: "{rounded.lg}"
    padding: "6px 12px"
  button-details:
    backgroundColor: "{colors.reagent-teal-wash}"
    textColor: "{colors.reagent-teal-ink}"
    rounded: "{rounded.sm}"
    padding: "4px 8px"
  button-details-hover:
    backgroundColor: "{colors.reagent-teal-wash-deep}"
  job-card:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "12px"
  job-card-selected:
    backgroundColor: "{colors.reagent-teal-wash}"
  skill-chip:
    backgroundColor: "#f1f5f9"
    textColor: "#475569"
    rounded: "{rounded.sm}"
    padding: "2px 6px"
  search-field:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.full}"
    height: "36px"
  analyzer-card:
    backgroundColor: "{colors.paper}"
    rounded: "{rounded.xl}"
    padding: "16px"
  sidebar:
    backgroundColor: "{colors.bench-navy}"
    textColor: "{colors.rail-text}"
    width: "256px"
---

# Design System: CVMatch

## Overview

**Creative North Star: "The Lab Bench"**

CVMatch is a precise instrument for measuring fit. A dark bench rail on the left holds the controls: the CV, the filters, Apply and Reset, the navigation. A bright, quiet workspace on the right holds the specimens being measured: job cards, the match ring, the analyzer charts. Surfaces stay neutral so that the few colored marks, a teal selection or a red/amber/emerald score, read as results rather than decoration.

The mood is calm, precise and honest. Numbers are set in monospace because they are measurements. Mock and preview data is always labelled as such (a "PREVIEW" tag, grayed sections, "Not available yet" captions): the bench never shows a reading it did not take. Density is compact and practical, an Operate tool rather than a showcase.

**Key Characteristics:**
- Two-zone layout: dark control rail, light measuring area.
- Neutral slate surfaces; color appears only as signal (selection, action, score band, chart series).
- Monospace for every number, score and skill token.
- Flat surfaces separated by hairline borders and tone.
- Small radii, thin borders, compact padding.

## Colors

A cool slate neutral field with one teal signal, one action green, a three-band score scale, and a muted earthy set reserved for charts.

### Primary
- **Reagent Teal** (`reagent-teal`): the marker for "this is selected / this is the focus". Selected job card ring, focus outlines, the active nav item on the rail, filter counts, the matching-tab dot. **Reagent Teal Ink** carries teal text on light surfaces (card titles on hover, "Show job details"), because the bright teal fails contrast as text. **Reagent Teal Wash** and **Wash Deep** fill the selected card and the "View details" button; **Reagent Teal Edge** is the hover border on cards; **Reagent Teal Bright** marks checked filter boxes and focus rings on the dark rail.

### Secondary
- **Apply Green** (`apply-green`): the single committing action, Apply filters. Chosen darker than the default emerald so white text keeps about 5.5:1 contrast.

### Neutral
- **Bench Navy** (`bench-navy`): the sidebar rail, and at 6% / 12% opacity the header fill and border of analyzer cards.
- **Paper** (`paper`): job cards, the match panel, popups, analyzer cards.
- **Bench Floor** (`bench-floor`): the workspace background under the card grid.
- **Hairline** (`hairline`): borders between workspace surfaces. **Rail Line** does the same on the navy rail.
- **Ink** / **Ink Muted**: primary and secondary text on light surfaces. **Rail Text** / **Rail Text Muted** on the rail.

### Score bands
- **Weak** (`score-weak`, below 40), **Partial** (`score-partial`, 40 to 70), **Strong** (`score-strong`, above 70). Each band has a matching tinted badge (50 fill, 300 border, 700 text) and is always paired with a word label ("Weak match", "Partial match", "Strong match").

### Chart series
- **Sage**, **Terracotta**, **Dusty Blue**, **Ochre**: one color per analyzer chart (experience level, domain, city, skills). Muted on purpose so charts sit beside the score bands without competing.

### Named Rules
**The Signal-Only Rule.** Color means something or it is not there. Teal means selection or focus, green means commit, red/amber/emerald means a score band, earthy tones mean a chart series. Neutral surfaces carry everything else.

**The Word-and-Color Rule.** A score band is never shown by color alone; the label or the number travels with it.

## Typography

**Body Font:** system UI sans (Tailwind default stack)
**Data Font:** system UI monospace (Tailwind default stack)

**Character:** A plain, legible sans for reading and controls, with monospace marking every value that was measured or counted. No display face; the instrument does not shout.

### Hierarchy
- **Headline** (600, 18px, 1.55): match panel heading, page titles ("Analyzer").
- **Title** (600, 14px): job card titles, analyzer card titles, button labels.
- **Body** (400, 14px): filter options, popup content, search input.
- **Caption** (400, 12px): company names, card metadata, hints and explanatory notes.
- **Label** (600, 12px, 0.05em tracking, uppercase): sidebar section headings ("YOUR CV", filter group titles), analyzer section headings.
- **Score** (mono 600, 24px, line-height 1): the percentage inside the match ring.
- **Data** (mono 400, 10–13px): score badges, skill chips, salary values, chart values and counts.

### Named Rules
**The Measured-Value Rule.** If it is a number the engine or the database produced (score, share, count, salary), it is set in monospace.

## Layout

A fixed two-zone screen. The left rail is 256px wide, full height, with its own scroll for the filter list and the navigation pinned at the bottom. The right workspace fills the rest at full viewport height: a white match panel strip across the top (padding 16px × 24px, ring centered between two flexible columns), then the job area on the bench floor with 24px side padding.

The job grid uses 1 column by default, 2 from the `md` breakpoint (768px), 3 from `xl` (1280px), with a 12px gap. The search bar header uses the same columns, so the search field is exactly one card wide. Cards keep fixed-height rows (metadata, skills, salary) so a row of cards stays even.

Spacing follows a 4px rhythm: 4 / 8 / 12 / 16 / 24px. The rail uses 16px section padding; cards use 12px; popups and analyzer cards 16–20px.

The rail itself does not yet collapse on small screens (open item L1 in `FE_NOTES.md`).

## Elevation & Depth

Flat by default. Surfaces are separated by hairline borders and tone: paper on the bench floor, navy rail against the workspace, a 6% navy tint on analyzer card headers. Job cards carry only a hairline-weight shadow that reads as an edge, not as lift. Real elevation is reserved for what floats above the page: the job details popup, over a 30% navy scrim.

### Shadow Vocabulary
- **Edge** (Tailwind `shadow-sm`): job cards at rest. Treat it as part of the border.
- **Float** (Tailwind `shadow-2xl`): the job details popup only.

### Named Rules
**The Flat-By-Default Rule.** Nothing on the page lifts. Only an overlay that sits above the page gets a real shadow.

## Shapes

Small, consistent radii and thin 1px borders. Skill chips and small buttons use 4px; filter inputs and avatars 6px; job cards, rail buttons and the CV drop zone 8px; analyzer cards and the popup 12px. Fully round shapes are kept for pills: the search field, score badges, filter counts, progress bars. Dashed borders mean "empty or not yet available": the CV upload zone, the placeholder box for a missing endpoint, the divider before preview sections.

**The Dashed-Means-Pending Rule.** A dashed border marks something waiting for input or for data. Finished content uses solid borders.

## Components

### Buttons
Precise and restrained.
- **Shape:** 8px on the rail, 4px for small in-card buttons.
- **Apply (primary):** Apply Green fill, white 14px semibold label, 6px × 12px padding; hover lightens. Disabled at 40% opacity when there is nothing to apply.
- **Rail ghost (Reset):** transparent with a Rail Line border, slate hover fill.
- **Details (in-card):** Reagent Teal Wash fill, Teal Ink 12px label, Wash Deep border; hover deepens the wash and switches to Teal Edge border.
- **Text link button:** Teal Ink 12px semibold, underline on hover ("Show job details").
- **Focus:** 2px teal outline, offset 2px on filled buttons. Keyboard focus is always visible.

### Chips
- **Skill chip:** slate-100 fill, slate-600 mono 10px text, 4px radius; overflow shown as "+N more" in muted text.
- **Score badge:** pill, band-tinted fill, border and text, mono 13px.
- **Filter count:** pill, teal at 20% on the rail, teal-300 mono 10px.
- **Status tags:** 1px slate border, 9–10px semibold uppercase ("PREVIEW", "NOT IN ESCO").

### Cards / Containers
- **Job card:** paper, 1px hairline border, 8px radius, 12px padding, edge shadow. Hover: Teal Edge border. Selected: Teal Wash fill, Reagent Teal border plus 2px ring. Company avatar is a 32px tile with initials on one of five pastel pairs, picked by company name so it stays stable.
- **Analyzer card:** paper, hairline border, 12px radius, 16px padding, 14px semibold title over a 12px muted note.
- **Preview section:** content grayed (45% opacity, 80% grayscale) until hover or focus, under a dashed divider and a PREVIEW tag.

### Inputs / Fields
- **Search field:** 36px tall pill, white, 1px mid-grey border, 16px search icon, borderless inner input; an options button opens a panel for sort and search fields.
- **Rail inputs:** dark slate-900 fill, slate-600 border, teal border and ring on focus.
- **Checkboxes (rail):** 16px, slate-500 border on slate-900; checked shows a teal-bright tick, no fill.
- **Error:** red-300 12px text under the field on the rail, announced as an alert.

### Navigation
Two equal buttons pinned to the bottom of the rail, icon plus 14px semibold label. Inactive: muted slate, lighter on hover. Active Jobs: slate-800 fill, white text. Active Analyzer: teal at 15% with a teal-300 label. (The two active styles differ, open item L3.) Analyzer sub-sections use underlined tabs with a 2px bottom border.

### Match Ring (signature)
A 128px ring, 10px stroke, slate-200 track, score-band arc with a rounded cap, animated over 500ms. In the center the score in mono 24px and a 11px word caption. With no CV, no job or no real score it shows an em dash and says why ("No job selected", "Not available yet").

## Do's and Don'ts

### Do:
- **Do** keep surfaces neutral (paper, bench floor, bench navy) and spend color only on signal.
- **Do** pair every score color with its number or word label.
- **Do** set scores, counts, shares and salaries in monospace.
- **Do** label mock or preview data visibly (PREVIEW tag, grayed section, "Not available yet").
- **Do** use Reagent Teal Ink, not Reagent Teal, for teal text on light backgrounds.
- **Do** keep a visible 2px teal focus outline on every interactive element.

### Don't:
- **Don't** add shadows to surfaces that sit in the page; only overlays float.
- **Don't** introduce a fourth score band; the three bands are a recorded decision.
- **Don't** use the chart colors for UI state, or the score colors for chart series.
- **Don't** use a display or serif face; the app keeps its system sans (the mock's Fraunces was declined).
- **Don't** show a score, metric or count that the engine did not produce.
