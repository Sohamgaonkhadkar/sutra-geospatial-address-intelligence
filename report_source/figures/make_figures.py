"""SUTRA final report — figure generation from canonical repository artifacts.
Every number below is read from a repo artifact at build time where possible;
hard-coded values match report_source/evidence_ledger.md exactly."""
import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.ticker as mtick

ROOT = Path(__file__).resolve().parents[2]
DER = ROOT / "data" / "derived"
OUT = Path(__file__).resolve().parent

# ── report palette (battle_model/src/index.css) ──────────────────────────────
P = dict(paper="#FBF9F2", panel="#F4F0E4", ink="#211D14", ink2="#4A4433", mute="#60584B",
         line="#E0D9C5", line2="#C9C0A6", accent="#C4501B", accentd="#A63E12",
         ok="#3B7449", oksoft="#E3EBDA", warn="#8D6117", warnsoft="#F3E9D2",
         crit="#B23A2B", critsoft="#F4DDD5", cool="#51616C", coolsoft="#E2E5E4",
         plum="#6D4F6E", plumsoft="#ECE0EA")

plt.rcParams.update({
    "figure.facecolor": P["paper"], "axes.facecolor": P["paper"], "axes.edgecolor": P["line2"],
    "axes.labelcolor": P["ink2"], "xtick.color": P["ink2"], "ytick.color": P["ink2"],
    "text.color": P["ink"], "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": P["line"], "grid.linewidth": 0.7, "axes.axisbelow": True,
    "font.family": "DejaVu Sans", "font.size": 9.5, "axes.titlesize": 11.5,
    "axes.titleweight": "bold", "axes.titlecolor": P["ink"],
    "figure.dpi": 110, "savefig.dpi": 220, "savefig.bbox": "tight", "savefig.pad_inches": 0.12,
})

def title(ax, t, sub=None):
    ax.set_title(t, loc="left", pad=26 if sub else 12)
    if sub:
        ax.text(-0.005, 1.055, sub, transform=ax.transAxes, fontsize=8.2, color=P["mute"],
                va="bottom", family="monospace")

def src(ax, s):
    ax.text(0.0, -0.16, s, transform=ax.transAxes, fontsize=7.4, color=P["mute"], family="monospace")

# ── 6.1 vendor error by declared precision (surveyed truth, n=100) ───────────
def fig_vendor_strata():
    df = pd.read_csv(DER / "eda_baseline_error_by_stratum.csv")
    order = ["rooftop", "street", "locality", "pincode"]
    df = df.set_index("stratum").loc[order].reset_index()
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    y = np.arange(len(df))[::-1]
    cols = [P["ok"], P["cool"], P["warn"], P["crit"]]
    for i, r in df.iterrows():
        ax.barh(y[i], r["median_m"], color=cols[i], height=0.62, zorder=3)
        ax.barh(y[i], r["p90_m"], color=cols[i], alpha=0.30, height=0.62, zorder=2)
        ax.text(r["p90_m"] + 90, y[i], f"median {r['median_m']:.0f} m · p90 {r['p90_m']:.0f} m · n={int(r['n'])}",
                va="center", fontsize=8.6, color=P["ink2"], family="monospace")
    ax.set_yticks(y); ax.set_yticklabels([s.upper() for s in order])
    ax.set_xlim(0, 5200); ax.set_xlabel("distance to surveyed truth (m)")
    title(ax, "Vendor pins: declared precision is not accuracy",
          "S-EVAL surveyed truth · n=100 · bar = median, faint = p90")
    src(ax, "source: data/derived/eda_baseline_error_by_stratum.csv")
    fig.savefig(OUT / "fig06_01_vendor_strata.png")

# ── 6.2 visit outcomes: counts + dwell/pin geometry ──────────────────────────
def fig_visit_outcomes():
    oc = pd.read_csv(DER / "eda_visit_outcomes.csv")
    og = pd.read_csv(DER / "eda_visit_outcome_geometry.csv").set_index("outcome")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.2, 4.3), gridspec_kw={"width_ratios": [1.15, 1]})
    oc = oc.sort_values("n", ascending=True)
    cols = [P["crit"] if o == "address_not_traceable" else (P["ok"] if o.startswith(("met", "cash")) else P["warn"]) for o in oc["outcome"]]
    a1.barh(oc["outcome"], oc["n"], color=cols, height=0.66, zorder=3)
    for i, r in oc.iterrows():
        a1.text(r["n"] + 18, list(oc["outcome"]).index(r["outcome"]), f"{int(r['n']):,}", va="center", fontsize=8.4, family="monospace")
    a1.set_xlabel("visits (n=5,578)")
    title(a1, "Field-visit outcomes", "all 5,578 visits")
    key = ["met_borrower", "met_family", "locked_premises", "address_not_traceable"]
    lab = ["met borrower", "met family", "locked premises", "not traceable"]
    x = np.arange(len(key)); w = 0.36
    dwell = [og.loc[k, "med_dwell_min"] for k in key]
    pin = [og.loc[k, "med_d_to_pin_m"] for k in key]
    a2b = a2
    b1 = a2b.bar(x - w/2, dwell, w, color=P["cool"], label="median dwell (min)", zorder=3)
    a2b.bar(x + w/2, [p/10 for p in pin], w, color=P["accent"], label="median dist to pin (×10 m)", zorder=3)
    for xi, (d, p) in zip(x, zip(dwell, pin)):
        a2b.text(xi - w/2, d + max(dwell)*0.02, f"{d:.1f}", ha="center", fontsize=7.6, family="monospace")
        a2b.text(xi + w/2, p/10 + max(dwell)*0.02, f"{p:.0f} m", ha="center", fontsize=7.6, family="monospace")
    a2b.set_xticks(x); a2b.set_xticklabels(lab, fontsize=8.4)
    a2b.legend(frameon=False, fontsize=8.2, loc="upper left")
    title(a2b, "Dwell and pin-proximity by outcome", "failed visits are brief and sit near our pin")
    src(a2b, "source: data/derived/eda_visit_outcome_geometry.csv")
    fig.tight_layout()
    fig.savefig(OUT / "fig06_02_visit_outcomes.png")

# ── 9.1 retrieval v1 vs v2 ────────────────────────────────────────────────────
def fig_retrieval():
    fig, ax = plt.subplots(figsize=(8.8, 4.4))
    labs = ["oracle <500 m", "ranked top-1 <500 m", "locality-candidate\nmedian err (m, ÷10)"]
    v1 = [87.67, 83.9, 811.9/10]
    v2 = [91.44, 83.9, 319.6/10]
    x = np.arange(3); w = 0.34
    ax.bar(x - w/2, v1, w, color=P["cool"], label="retrieval-v1 (shared token, pin outvotes text)")
    ax.bar(x + w/2, v2, w, color=P["accent"], label="retrieval-v2 (full coverage + rarest token)")
    for xi, a, b in zip(x, v1, v2):
        ax.text(xi - w/2, a + 1.2, f"{a:.1f}", ha="center", fontsize=8.2, family="monospace")
        ax.text(xi + w/2, b + 1.2, f"{b:.1f}", ha="center", fontsize=8.2, family="monospace")
    ax.set_xticks(x); ax.set_xticklabels(labs)
    ax.set_ylim(0, 105)
    ax.legend(frameon=False, fontsize=8.4, loc="lower left")
    title(ax, "Retrieval-v2 raises the ceiling; the ranked answer does not move",
          "supervision pool n=292 · % within 500 m except noted · top-1 identical at 83.9%")
    src(ax, "source: data/derived/precision_optimization_report.md §1")
    fig.savefig(OUT / "fig09_01_retrieval.png")

# ── 8.1 challenger scoreboard (final frozen) ─────────────────────────────────
def fig_challengers():
    rows = [("RULE (shipped)", 84.06, 249.0, 0.9670, P["accent"]),
            ("LOGISTIC", 81.16, 258.0, 0.9516, P["cool"]),
            ("LAMBDAMART", 84.06, 249.0, 0.9640, P["cool"]),
            ("PAIRWISE", 84.06, 249.0, 0.9653, P["cool"]),
            ("SHUFFLED (control)", 56.52, 398.3, 0.8090, P["line2"])]
    fig, ax = plt.subplots(figsize=(8.8, 4.2))
    y = np.arange(len(rows))[::-1]
    for i, (name, p500, med, ndcg, c) in enumerate(rows):
        ax.barh(y[i], p500, color=c, height=0.6, zorder=3)
        ax.text(p500 + 1, y[i], f"{p500:.2f}% · med {med:.0f} m · nDCG@5 {ndcg:.4f}", va="center", fontsize=8.4, family="monospace")
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows])
    ax.set_xlim(0, 118); ax.set_xlabel("S-VAL top-1 within 500 m (%)")
    title(ax, "Model selection: no learned challenger cleared the gate",
          "S-VAL n=69 · paired grouped bootstrap, 10k resamples, seed 7")
    src(ax, "source: final frozen Experiment-D scoreboard (PS3_IMPLEMENTATION_PHASE_REPORT §3.7)")
    fig.savefig(OUT / "fig08_01_challengers.png")

# ── 10.1 trace-tail estimator ─────────────────────────────────────────────────
def fig_trace():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.1))
    kinds = ["within 100 m (%)", "within 250 m (%)"]
    chk = [76.39, 92.70]; tail = [86.27, 93.99]
    x = np.arange(2); w = 0.34
    a1.bar(x - w/2, chk, w, color=P["cool"], label="single check-in")
    a1.bar(x + w/2, tail, w, color=P["ok"], label="median of last-3 fixes")
    for xi, a, b in zip(x, chk, tail):
        a1.text(xi - w/2, a + 1, f"{a:.1f}", ha="center", fontsize=8.4, family="monospace")
        a1.text(xi + w/2, b + 1, f"{b:.1f}", ha="center", fontsize=8.4, family="monospace")
    a1.set_xticks(x); a1.set_xticklabels(kinds); a1.set_ylim(0, 105)
    a1.legend(frameon=False, fontsize=8.4)
    title(a1, "Visit-coordinate hit rate", "non-circular cross-cut evaluation")
    meds = [28.7, 7.6]
    a2.bar(["check-in", "tail-3 median"], meds, color=[P["cool"], P["ok"]], width=0.5, zorder=3)
    for xi, m in zip([0, 1], meds):
        a2.text(xi, m + 0.8, f"{m} m", ha="center", fontsize=9, family="monospace")
    a2.set_ylabel("median coordinate error (m)")
    title(a2, "Median error 28.7 m → 7.6 m", "n=233 · judged across the T0 cut")
    src(a2, "source: final_precision_config.json coordinate_policy.measured · precision report §5b")
    fig.tight_layout()
    fig.savefig(OUT / "fig10_01_trace_tail.png")

# ── 14.1 three S-EVAL regimes ─────────────────────────────────────────────────
def fig_regimes():
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    thr = ["<100 m", "<250 m", "<500 m"]
    cold = [9, 35, 71]; warm = [83.87, 93.55, 96.77]; prod = [33, 55, 76]
    x = np.arange(3); w = 0.26
    ax.bar(x - w, cold, w, color=P["cool"], label="cold start (n=100) med 375.8 m")
    ax.bar(x, warm, w, color=P["ok"], label="warm / evidence (n=31) med 12.4 m")
    ax.bar(x + w, prod, w, color=P["accent"], label="product lane (n=100) med 202.2 m")
    for xi, c, wa, p in zip(x, cold, warm, prod):
        ax.text(xi - w, c + 1.2, f"{c:.0f}", ha="center", fontsize=8.2, family="monospace")
        ax.text(xi, wa + 1.2, f"{wa:.1f}", ha="center", fontsize=8.2, family="monospace")
        ax.text(xi + w, p + 1.2, f"{p:.0f}", ha="center", fontsize=8.2, family="monospace")
    ax.set_xticks(x); ax.set_xticklabels(thr); ax.set_ylim(0, 108)
    ax.set_ylabel("share within threshold (%)")
    ax.legend(frameon=False, fontsize=8.4, loc="upper left")
    title(ax, "Three operating regimes — never one blended number",
          "locked S-EVAL · frozen config 9abebb8f… · warm = eligible evidence-backed answers only")
    src(ax, "source: data/derived/precision_optimization_report.md §6")
    fig.savefig(OUT / "fig14_01_regimes.png")

# ── 14.2 temporal holdout ─────────────────────────────────────────────────────
def fig_temporal():
    fig, ax = plt.subplots(figsize=(9.0, 4.4))
    lanes = ["cold", "warm", "product", "promoted-only"]
    h500 = [84.72, 98.67, 98.69, 100.0]
    h100 = [12.23, 85.78, 85.15, 94.79]
    med = [271.2, 7.5, 7.9, 6.1]
    n = [229, 225, 229, 96]
    x = np.arange(4); w = 0.34
    cols = [P["cool"], P["ok"], P["accent"], P["plum"]]
    ax.bar(x - w/2, h500, w, color=cols, zorder=3)
    ax.bar(x + w/2, h100, w, color=cols, alpha=0.45, zorder=3)
    for xi, a, b, m, nn in zip(x, h500, h100, med, n):
        ax.text(xi, max(a, b) + 2.2, f"med {m} m\nn={nn}", ha="center", fontsize=7.8, family="monospace")
    ax.set_xticks(x); ax.set_xticklabels(lanes)
    ax.set_ylim(0, 118); ax.set_ylabel("hit rate (%)")
    ax.text(0.02, 0.97, "solid = <500 m · faint = <100 m", transform=ax.transAxes, fontsize=8.2, color=P["mute"])
    title(ax, "Trusted evidence changes the operating regime (temporal holdout)",
          "T0 = 2026-05-15 · candidates strictly before T0, labels = promoted check-ins after T0")
    src(ax, "source: data/derived/precision_optimization_results.csv block=temporal")
    fig.savefig(OUT / "fig14_02_temporal.png")

# ── 11.1 memory integrity policy ──────────────────────────────────────────────
def fig_memory():
    fig, ax = plt.subplots(figsize=(9.0, 4.3))
    thr = ["<100 m", "<250 m", "<500 m"]
    p0 = [57.78, 75.56, 82.22]; fz = [83.87, 93.55, 96.77]
    x = np.arange(3); w = 0.32
    ax.bar(x - w/2, p0, w, color=P["plum"], alpha=0.55, label="P0 shipped (n=45 answered, pin-derived memory emitted)")
    ax.bar(x + w/2, fz, w, color=P["ok"], label="frozen emp-v1 (n=31 answered, evidence-derived only)")
    for xi, a, b in zip(x, p0, fz):
        ax.text(xi - w/2, a + 1, f"{a:.1f}", ha="center", fontsize=8.2, family="monospace")
        ax.text(xi + w/2, b + 1, f"{b:.1f}", ha="center", fontsize=8.2, family="monospace")
    ax.set_xticks(x); ax.set_xticklabels(thr); ax.set_ylim(0, 108)
    ax.set_ylabel("warm-lane hit rate on answered rows (%)")
    ax.legend(frameon=False, fontsize=8.3, loc="lower right")
    title(ax, "Memory integrity: fewer answers, better evidence",
          "locked S-EVAL · product lane bit-identical (76% <500 m, 202.2 m) · 14 withheld = vendor pin re-wrapped")
    src(ax, "source: data/derived/evidence_memory_policy_report.md §7")
    fig.savefig(OUT / "fig11_01_memory_policy.png")

# ── 5.1 failure taxonomy ──────────────────────────────────────────────────────
def fig_taxonomy():
    fig, ax = plt.subplots(figsize=(8.8, 4.0))
    rows = [("OK (resolved <500 m)", 245, P["ok"]),
            ("ranker choice (better candidate existed)", 22, P["accent"]),
            ("weak/coarse only (nothing within 500 m)", 19, P["warn"]),
            ("retrieval (pincode-coarse / street pin)", 6, P["cool"])]
    y = np.arange(len(rows))[::-1]
    for i, (name, n, c) in enumerate(rows):
        ax.barh(y[i], n, color=c, height=0.6, zorder=3)
        ax.text(n + 3, y[i], str(n), va="center", fontsize=8.6, family="monospace")
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=8.6)
    ax.set_xlabel("addresses (supervision pool n=292)")
    title(ax, "Where the remaining error actually lives", "taxonomy of the 47 unresolved pool rows")
    src(ax, "source: data/derived/precision_optimization_report.md §2")
    fig.savefig(OUT / "fig05_01_taxonomy.png")

for f in [fig_vendor_strata, fig_visit_outcomes, fig_retrieval, fig_challengers,
          fig_trace, fig_regimes, fig_temporal, fig_memory, fig_taxonomy]:
    f()
    print("wrote", f.__name__)
