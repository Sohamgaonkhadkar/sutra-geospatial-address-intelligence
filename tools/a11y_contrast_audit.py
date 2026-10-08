#!/usr/bin/env python3
"""P16 — contrast audit against the *actual* class strings in the workbench source.

    python3 tools/a11y_contrast_audit.py [--quiet]

It reads the colour tokens from `battle_model/src/index.css`, then walks every `.tsx` `className`
literal and, for each text colour that appears together with a surface colour in the same literal,
computes the WCAG 2.1 contrast ratio. Nothing is measured from a screenshot: this checks the pairs
the interface is actually built from, so a failing pair names the file and line.

Exit code 1 when a text/surface pair is below 4.5:1. Hairline tokens (`line`, `line2`, `line3`) are
graphics, not text, and are reported separately.
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "battle_model", "src")
CSS = os.path.join(SRC, "index.css")
THRESHOLD = 4.5


def _lin(c: float) -> float:
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def composite(fg_hex: str, alpha: float, bg_hex: str) -> str:
    """A translucent surface, flattened over its parent — the colour a reader actually sees."""
    f = [int(fg_hex.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(bg_hex.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    return "#%02x%02x%02x" % tuple(round(f[i] * alpha + b[i] * (1 - alpha)) for i in range(3))


def load_tokens() -> dict[str, str]:
    css = open(CSS, encoding="utf-8").read()
    return {m.group(1): m.group(2).lower()
            for m in re.finditer(r"--color-([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", css)}


LINE_TOKENS = {"line", "line2", "line3"}
PARENTS = ("paper", "raised")          # the two surfaces a translucent fill normally sits on


def main() -> int:
    quiet = "--quiet" in sys.argv
    tok = load_tokens()
    fails, checked, graphics = [], 0, []
    for dirpath, _dirs, files in os.walk(SRC):
        for fn in sorted(f for f in files if f.endswith(".tsx")):
            path = os.path.join(dirpath, fn)
            for ln, line in enumerate(open(path, encoding="utf-8"), 1):
                for lit in re.findall(r'"([^"]*)"', line) + re.findall(r"`([^`]*)`", line):
                    fgs = [t for t in re.findall(r"(?:[\w-]+:)*text-([a-z0-9-]+)", lit) if t in tok]
                    bgs = [(b, (int(a) / 100 if a else 1.0))
                           for b, a in re.findall(r"(?:[\w-]+:)*bg-([a-z0-9-]+)(?:/(\d{1,3}))?", lit) if b in tok]
                    for f in fgs:
                        for b, alpha in bgs:
                            checked += 1
                            worst = min(contrast(tok[f], composite(tok[b], alpha, tok[p])) for p in PARENTS)
                            if f in LINE_TOKENS:
                                graphics.append((os.path.relpath(path, ROOT), ln, f"text-{f}", f"bg-{b}", worst))
                            elif worst < THRESHOLD:
                                fails.append((os.path.relpath(path, ROOT), ln, f"text-{f}", f"bg-{b}", worst))
    fails.sort(key=lambda r: r[4])
    if not quiet:
        print(f"tokens       : {len(tok)} colour tokens read from index.css")
        print(f"pairs checked: {checked} text-on-surface combinations found in the source")
        print(f"below {THRESHOLD}:1  : {len(fails)}")
        for path, ln, f, b, r in fails:
            print(f"  {r:5.2f}  {path}:{ln}  {f} on {b}")
        print(f"hairline colours used as text: {len(graphics)}"
              + ("" if not graphics else " → " + ", ".join(f"{p}:{n}" for p, n, *_ in graphics[:5])))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
