"""Build SUTRA_PS3_Final_Report.pdf from the Typst sources.
Usage: python3 report_source/build_report.py
Regenerates figures first (canonical CSVs -> PNG), then compiles typst with the
DejaVu font family bundled by matplotlib, so the build is reproducible on a bare
machine with only the repository + a venv (pandas, matplotlib, typst, python-docx, pypdfium2).
"""
import os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # repo root
SRC = Path(__file__).resolve().parent                  # report_source
PY = sys.executable

def run(cmd, **kw):
    r = subprocess.run(cmd, cwd=SRC, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-3000:]); print(r.stderr[-3000:]); raise SystemExit(f"failed: {cmd}")
    return r

def main():
    if "--no-figures" not in sys.argv:
        print("regenerating figures…")
        run([PY, str(SRC / "figures" / "make_figures.py")])
    font_dir = None
    try:
        import matplotlib
        font_dir = str(Path(matplotlib.__file__).parent / "mpl-data" / "fonts" / "ttf")
    except ImportError:
        pass
    import typst
    out = ROOT / "SUTRA_PS3_Final_Report.pdf"
    typst.compile(str(SRC / "typst" / "main.typ"), output=str(out),
                  root=str(ROOT), font_paths=[font_dir] if font_dir else None,
                  ignore_system_fonts=bool(font_dir))
    print("PDF:", out, out.stat().st_size, "bytes")

if __name__ == "__main__":
    main()
