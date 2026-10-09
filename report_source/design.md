# SUTRA Report — Design System (harmonised with the live product)

Derived from battle_model/src/index.css (the served workbench) and the notebook's seaborn palette.
Warm-paper, ink, restrained burnt-orange identity. NO navy-on-white AI default.

## Palette
- paper        #F4F0E4  (page background tint for panels; page base #FBF9F2)
- panel        #F8F5EC
- ink          #211D14  (primary text, headings)
- ink2         #4A4433  (secondary text)
- mute         #60584B  (metadata)
- line         #E0D9C5  (rules, table hairlines)
- line2        #C9C0A6  (stronger rules)
- accent       #C4501B  (SUTRA orange — production/implemented elements, SERVE)
- accent-deep  #A63E12
- accent-soft  #F5E0CF
- ok           #3B7449  (field evidence, warm regime, positive)
- ok-soft      #E3EBDA
- warn         #8D6117  (limitations, VERIFY_FIRST, withheld)
- warn-soft    #F3E9D2
- crit         #B23A2B  (refusal, contested, negative evidence)
- crit-soft    #F4DDD5
- cool         #51616C  (cold/static/official arms, oracle ceilings)
- cool-soft    #E2E5E4
- plum         #6D4F6E  (memory, co-location, special states)
- plum-soft    #ECE0EA

Color semantics (held constant across all diagrams):
- orange  = implemented production component / product policy
- cool    = cold, static, official-only candidate arms & ceilings
- ok/green= field evidence, warm regime
- plum    = memory / place identity
- warn    = limitations, guards, withheld
- crit    = refusal / negative evidence / contested

## Type
- Headings/body: serif for display numerals & chapter titles (IBM Plex Serif family; render with "Source Serif"/fallback), sans for body (IBM Plex Sans), mono for diagnostics, version strings, coordinates (IBM Plex Mono).
- Typst fonts: use a bundled/installed serif (e.g. "Noto Serif" / "Source Serif Pro" if present) with sans "Noto Sans" + mono "Noto Mono" fallbacks; verify fc-list before build.

## Layout
- A4, margins 18 mm; running header: chapter title left, "SUTRA — Semantic Utility for Traceable Resolution of Addresses" right; footer: page number + frozen-config hash excerpt.
- Chapter openers: mono kicker ("CHAPTER 07 · MODELING"), large serif title, 2-line lead, hairline rule; no stock imagery.
- Tables: hairline rules only (no zebra overload), mono digits right-aligned, n and population in header row, source line under every table.
- Figures: caption "Figure N.M —" in mono small caps with population annotation; white/panel background, despine, no gradients.
- Cover: paper background, faint local-metric-plane grid motif (graph grid + mono coordinate ticks), wordmark, subtitle, metadata block (versions, as-of, n, hash), original architecture strip.
