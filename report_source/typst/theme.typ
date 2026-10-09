// ── SUTRA report theme ────────────────────────────────────────────────────────
#let pal = (
  paper: rgb("#FBF9F2"), panel: rgb("#F4F0E4"), sunk: rgb("#ECE7D8"),
  ink: rgb("#211D14"), ink2: rgb("#4A4433"), mute: rgb("#60584B"),
  line: rgb("#E0D9C5"), line2: rgb("#C9C0A6"),
  accent: rgb("#C4501B"), accentd: rgb("#A63E12"), accentsoft: rgb("#F5E0CF"),
  ok: rgb("#3B7449"), oksoft: rgb("#E3EBDA"),
  warn: rgb("#8D6117"), warnsoft: rgb("#F3E9D2"),
  crit: rgb("#B23A2B"), critsoft: rgb("#F4DDD5"),
  cool: rgb("#51616C"), coolsoft: rgb("#E2E5E4"),
  plum: rgb("#6D4F6E"), plumsoft: rgb("#ECE0EA"),
)

#set page(paper: "a4",
  margin: (top: 19mm, bottom: 17mm, x: 17mm),
  fill: pal.paper,
)
#set par(justify: true, leading: 0.6em)
#set text(font: ("DejaVu Sans", "Noto Sans"), size: 8.9pt, fill: pal.ink)
#set heading(numbering: "1.")
#show heading.where(level: 1): set text(font: ("DejaVu Serif",), size: 19pt, fill: rgb("#211D14"), weight: "bold")
#show heading.where(level: 2): set text(size: 11.5pt, fill: rgb("#4A4433"), weight: "bold")
#show heading.where(level: 3): set text(size: 9.6pt, fill: rgb("#4A4433"), weight: "bold")

#let mono = text.with(font: ("DejaVu Sans Mono",), size: 0.86em)
#let mono-small = text.with(font: ("DejaVu Sans Mono",), size: 6.9pt)
#let serifd = text.with(font: ("DejaVu Serif",), weight: "bold")

// running header / footer — applied after the cover via #set page(header: page-hdr, footer: page-ftr)
#let page-hdr = context {
  if counter(heading).get().at(0) > 0 [
    #grid(columns: (1fr, 1fr),
      mono-small(fill: pal.mute)[SUTRA · SEMANTIC UTILITY FOR TRACEABLE RESOLUTION OF ADDRESSES],
      mono-small(fill: pal.mute)[CREDITNIRVANA PS3 · FROZEN CONFIG 9abebb8f… · as-of 2026-06-01T00:00Z],
    )
    #v(-2pt) #line(length: 100%, stroke: 0.6pt + pal.line)
  ]
}
#let page-ftr = context [
  #line(length: 100%, stroke: 0.6pt + pal.line) #v(3pt)
  #grid(columns: (1fr, auto, 1fr),
    mono-small(fill: pal.mute)[resolve → verify → learn → resolve better],
    mono-small(fill: pal.ink2)[#counter(page).display()],
    align(right, mono-small(fill: pal.mute)[official PS3 data only · zero outbound calls]),
  )
]

// chapter opener
#let chapter(t, lead: none) = {
  counter("sec").step()
  v(6pt)
  context [ #mono-small(fill: pal.accent, tracking: 1.2pt)[SECTION #counter("sec").display("1")] ]
  v(4pt)
  heading(level: 1, t)
  if lead != none [
    #set text(size: 9.3pt, fill: pal.ink2, style: "italic")
    #lead
    #set text(size: 8.9pt, fill: pal.ink, style: "normal")
  ]
  v(-4pt)
  line(length: 100%, stroke: 1.1pt + pal.accent)
  v(8pt)
}

#let h2(t) = heading(level: 2, t)
#let h3(t) = heading(level: 3, t)

// panels and callouts
#let panel(title, body, tint: pal.panel, edge: pal.line2) = block(
  width: 100%, fill: tint, stroke: 0.7pt + edge, inset: 9pt,
  [
    #if title != none [ #mono-small(fill: pal.ink2, weight: "bold", title) #v(4pt) ]
    #body
  ]
)

#let callout(kind, body) = {
  let conf = (
    acc: (pal.accentsoft, pal.accent, "PRODUCTION"),
    ok: (pal.oksoft, pal.ok, "EVIDENCE"),
    warn: (pal.warnsoft, pal.warn, "LIMITATION"),
    crit: (pal.critsoft, pal.crit, "SAFETY"),
    cool: (pal.coolsoft, pal.cool, "COLD / OFFICIAL"),
    plum: (pal.plumsoft, pal.plum, "MEMORY"),
  ).at(kind)
  block(width: 100%, fill: conf.at(0), stroke: (left: 2.2pt + conf.at(1)), inset: 8pt,
    [#mono-small(fill: conf.at(1), weight: "bold", conf.at(2)) #h(6pt) #body])
}

// source line under tables/figures
#let srcline(s) = block(above: 1pt, mono-small(fill: pal.mute)[source: #s])

// metric chip for headline panels
#let metric(label, value, sub, c: pal.ink) = block(
  fill: pal.paper, stroke: 0.7pt + pal.line2, inset: (x: 8pt, y: 7pt),
  [
    #mono-small(fill: pal.mute, label) \
    #serifd(size: 15pt, fill: c, value) \
    #mono-small(fill: pal.mute, sub)
  ]
)

// compact table styling
#let tt(..args) = {
  set table(
    stroke: (x: none, y: none, top: 0.9pt + pal.line2, bottom: 0.9pt + pal.line2),
    fill: (x, y) => if y == 0 { pal.sunk } else { none },
    inset: (x: 6pt, y: 4pt),
  )
  set table(align: (x, y) => if x == 0 { left } else { right })
  table(..args)
}
#let th(t) = mono-small(fill: pal.ink2, weight: "bold", t)
#let td(t) = text(size: 8.3pt, t)
#let tmono(t) = mono-small(fill: pal.ink2, t)

#let figframe(path, caption, source, w: 92%) = figure(
  image(path, width: w),
  caption: [
    #text(size: 8.2pt, fill: pal.ink2, caption)
    #srcline(source)
  ],
)

#show figure: set block(breakable: false)
#set figure(gap: 4pt)
