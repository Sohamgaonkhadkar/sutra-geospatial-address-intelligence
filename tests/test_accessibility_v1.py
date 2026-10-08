"""P16 — the four accessibility properties the workbench is built to, checked against the source.

These are source-level checks on purpose: they fail on the file and line that introduces the problem,
and they cannot drift from the interface the way a screenshot would. What is asserted:

  1 · every text colour used on a surface clears WCAG 2.1 AA (4.5:1) — `tools/a11y_contrast_audit.py`
  2 · a visible keyboard focus ring exists, in palette (and no control suppresses it)
  3 · a control with no visible text carries an accessible name
  4 · an input carries an accessible name (aria-label or a <label for=…> of its own)
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "battle_model", "src")


def _sources():
    for dirpath, _dirs, files in os.walk(SRC):
        for fn in sorted(f for f in files if f.endswith(".tsx")):
            path = os.path.join(dirpath, fn)
            yield path, open(path, encoding="utf-8").read()


def _opening_tag_end(src: str, i: int) -> int:
    """Index just past the `>` closing the tag starting at `i`, ignoring braces and quotes."""
    depth, quote = 0, None
    while i < len(src):
        ch = src[i]
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'`":
            quote = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        elif ch == ">" and depth == 0:
            return i + 1
        i += 1
    return -1


def test_every_text_colour_used_on_a_surface_clears_wcag_aa():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "a11y_contrast_audit.py"), "--quiet"],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, "a text-on-surface pair is below 4.5:1\n" + (r.stdout or "") + (r.stderr or "")


def test_a_visible_keyboard_focus_ring_exists_and_is_never_suppressed():
    css = open(os.path.join(SRC, "index.css"), encoding="utf-8").read()
    assert re.search(r":focus-visible\s*\{[^}]*outline:", css), "no visible focus ring is defined"
    suppressed = [(os.path.relpath(p, ROOT), n) for p, s in _sources()
                  for n, line in enumerate(s.splitlines(), 1) if "focus:outline-none" in line]
    assert not suppressed, f"a control suppresses the focus outline: {suppressed[:3]}"


def test_a_control_with_no_visible_text_carries_an_accessible_name():
    textless = []
    for path, src in _sources():
        for m in re.finditer(r"<button\b", src):
            end = _opening_tag_end(src, m.end())
            if end < 0:
                continue
            close = src.find("</button>", end)
            tag, inner = src[m.start():end], src[end:close if close > 0 else len(src)]
            inner = re.sub(r"</?[A-Za-z][^>]*?/?>", "", inner)      # drop icon elements
            if re.search(r"[A-Za-z]{2,}", inner) or "{" in inner:
                continue                                            # renders text at runtime
            textless.append((os.path.relpath(path, ROOT), tag))
    assert textless, "the scanner found no controls at all — it has stopped working"
    unnamed = [p for p, tag in textless if "aria-label" not in tag and "title=" not in tag]
    assert not unnamed, f"a textless control has no accessible name: {unnamed}"


def test_every_input_carries_an_accessible_name():
    unnamed = []
    for path, src in _sources():
        labelled = set(re.findall(r'htmlFor="([^"]+)"', src)) | set(re.findall(r'htmlFor=\{"([^"]+)"\}', src))
        for m in re.finditer(r"<(input|textarea|select)\b", src):
            end = _opening_tag_end(src, m.end())
            tag = src[m.start():end]
            has_own_id = re.search(r'id="([^"]+)"', tag)
            if "aria-label" in tag or (has_own_id and has_own_id.group(1) in labelled):
                continue
            unnamed.append((os.path.relpath(path, ROOT), " ".join(tag.split())[:70]))
    assert not unnamed, f"an input has no accessible name: {unnamed}"
