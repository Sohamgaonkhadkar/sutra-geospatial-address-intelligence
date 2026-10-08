# SUTRA — Accessibility review of the workbench (2026-10-08)

Scope: `battle_model/` — the interface a judge or a field supervisor actually opens. This review covers
what can be *measured from the source and the running build*; it does not claim a screen-reader
certification, and the last section says exactly what was not tested.

Everything below is enforced by an automated check, not by a one-off reading.

## 1 · What was checked, and how

| Property | Method | Where it lives |
|---|---|---|
| Contrast of every text colour on every surface it is used on | `tools/a11y_contrast_audit.py` — reads the colour tokens from `battle_model/src/index.css`, walks every `className` literal in the `.tsx` sources, and computes WCAG 2.1 ratios for the pairs that actually occur. Translucent fills (`bg-*/50`) are composited over their parent surface first. | `tests/test_accessibility_v1.py::test_every_text_colour_used_on_a_surface_clears_wcag_aa` |
| A visible keyboard focus ring | the ring is defined once in `index.css`; no control may suppress it | `::test_a_visible_keyboard_focus_ring_exists_and_is_never_suppressed` |
| Every control with no visible text has an accessible name | source scan: JSX `<button>` elements whose contents render no text must carry `aria-label` (or `title`) | `::test_a_control_with_no_visible_text_carries_an_accessible_name` |
| Every input has an accessible name | source scan: `aria-label`, or its own `id` matched by a `<label htmlFor=…>` | `::test_every_input_carries_an_accessible_name` |

## 2 · What the audit found, and what it cost to fix

The first run measured **84 text-on-surface pairs** in the source: **16 were below 4.5:1**, in 9
distinct colour pairs. The palette is a curated paper/graphite/orange set, so the failures were
structural rather than accidental — a short ladder of greys that reads well at poster size and badly
at 8.5 px monospace, which is exactly the size this interface uses for its tables.

| Pair | Before | After | Fix |
|---|---|---|---|
| `text-faint` on `bg-paper` / `bg-raised` | 2.47 / 2.74 | 4.84 / 5.38 | `--color-faint` `#a2987f` → `#6e6756` |
| `text-mute` on `bg-sunk` / `bg-panel` | 3.83 / 4.24 | 5.6 / 6.4 | `--color-mute` `#7c7260` → `#60584b` |
| `text-ok` on `bg-ok-soft` | 4.19 | 4.54 | `--color-ok` `#3e7a4c` → `#3b7449` |
| `text-warn` on `bg-warn-soft` | 3.34 | 4.51 | `--color-warn` `#a9741b` → `#8d6117` |
| `text-paper` on `bg-accent` (3 primary buttons) | 3.60 | 5.45 / 6.20 | the fill moved to `bg-accent-deep` with `bg-accent-dark` on hover; bright orange stays for marks, not for text-bearing fills |
| `line3` used as an informative graphic (legend rule, landmark ring) | 2.02 | 3.00 | `--color-line3` `#b3a988` → `#92896f` |

Two decisions worth recording, because they are judgement calls and not measurements:

1. **The grey ladder was rebuilt, not flattened.** `faint` and `mute` both had to clear 4.5:1, which
   would have made them identical if both had been pushed to the threshold. They are now spaced —
   `ink` 14.5:1, `ink2` 8.4:1, `mute` 6.0:1, `faint` 4.6:1 on paper — so the hierarchy survives with
   every step legible.
2. **Orange carries meaning only where it is a fill or a mark.** `--color-accent` (`#d2541e`) still
   draws the selected point, the map crosshair and borders, where 3:1 is the applicable bar; wherever
   orange *is* the text it is `--color-accent-deep` (6.06:1), and the three text-bearing primary
   buttons use `--color-accent-deep` with a new `--color-accent-dark` hover.

Two controls also gained names that they never had:

- the six text inputs (address intake, place filter, evidence filter, decision note ×2, reviewer)
  now carry `aria-label`s, or — for the reviewer field — an existing `<label htmlFor="reviewer">`;
- the ✕ on a shell notice is now `aria-label="Dismiss this notice"`, and the three map controls
  (zoom in / zoom out / fit) already had names.

Focus: no control suppresses the outline any more (six `focus:outline-none` utilities were removed),
and one `:focus-visible` rule draws a 2 px `--color-accent-deep` ring with a 1 px offset — visible on
paper, on raised panels and on sunk rows. The colour change on the border that the inputs already had
is kept as a secondary cue, never the only one.

## 3 · Status is never colour-only

Checked by reading the rendered interface at judge viewport (`screenshots/bm-01…bm-13`):

- polarity pills carry words — `POSITIVE`, `ADDRESS NOT TRACEABLE` — and the evidence timeline states
  "carries no coordinate claim" in text;
- the decision is a word in the header (`SERVE`, `VERIFY FIRST`, `REFUSE`) and in the ticket headline,
  not a green/amber/red dot;
- on the metric plane, field check-ins are diamonds (dashed when negative) and the legend names every
  marker class in words, so the map is readable without colour vision;
- the four Method & Trust labels (`IMPLEMENTED`, `DESIGNED`, `NOT YET IMPLEMENTED`, `NOT MEASURED`) are
  words, and the status bars beside them are labelled with the population they describe.

## 4 · Loading, empty and error states

Every panel that reads the service states its state in words: `reading runtime status…` while a
request is in flight, a plain sentence when a read fails with a retry control (Method & Trust was
fixed in this pass — it previously stopped at "reading runtime status…" when `/health` failed), and
explicit empty states (`No field evidence yet`, `Not served for this purpose`, `Nothing to review`).
Destructive and irreversible actions are visually separated from the safe ones: `Not true` and
`Reopen` sit apart from `Confirm`, and every decision is labelled with what it does to the store
("writes an adjudication, closes the case").

## 5 · What was NOT measured

- **Screen-reader behaviour.** No NVDA/JAWS/VoiceOver run in this environment; the checks are
  structural (names present, roles used, state in text), not a listen-through.
- **Browser zoom / OS text scaling beyond 900 px width.** One narrow-viewport check exists
  (check 20 of the browser smoke, 900 px, no horizontal overflow); 200 % zoom at a small window was
  not exercised.
- **Third-party audit tooling.** No axe-core/pa11y run — no network egress is permitted in this
  environment and no such dependency is bundled. The four source-level checks above are the substitute,
  and they are the ones that run on every `pytest`.

*Sources:* [S95] (data policy + guards: what may appear in the interface at all) · [U12]–[U14] (dense
tables and progressive disclosure, the reason the small-type ladder matters) · [U18]–[U20] (calibrated
trust: state a decision, never a confidence figure; the contrast work serves the same end) ·
[U6] (uncertainty circles: always pair the ring with its number — the legend rule that this audit keeps
legible).
