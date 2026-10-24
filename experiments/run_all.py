"""Reproduce every result: python experiments/run_all.py [--quick]"""
from __future__ import annotations

import argparse
import random
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from erasure_local import POLICIES, simulate_trial  # noqa: E402
from erasure_local.codes import bb72, bb144, toric_code  # noqa: E402


def run(code, p, policy, q, seeds, shots):
    rows = []
    for s in range(seeds):
        rng = random.Random(1000 * s + int(p * 1e4) + int(q * 1e6) + 7)
        # same RNG seed for all policies -> identical erasure patterns (paired comparison)
        res = [simulate_trial(code, p, policy, q, rng) for _ in range(shots)]
        rows.append({"code": code.name, "n": code.n, "p": p, "q": q, "policy": policy, "seed": s,
                     **{k: float(np.mean([r[k] for r in res])) for k in res[0]}})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    seeds, shots = (2, 20) if a.quick else (4, 150)
    codes = [toric_code(4), toric_code(6), bb72()] if a.quick else [toric_code(4), toric_code(6), toric_code(8), bb72(), bb144()]
    ps = [0.05, 0.2] if a.quick else [0.02, 0.05, 0.1, 0.15, 0.2, 0.3]
    qs = [0.0, 0.01] if a.quick else [0.0, 0.001, 0.003, 0.01, 0.03]
    out = ROOT / ("results_quick" if a.quick else "results")
    figs = ROOT / ("figures_quick" if a.quick else "figures")
    out.mkdir(exist_ok=True); figs.mkdir(exist_ok=True)
    t0 = time.time()
    for c in codes:
        assert c.check_commutation(), c.name
    sweep = [r for c in codes for p in ps for pol in POLICIES for r in run(c, p, pol, 0.0, seeds, shots)]
    pd.DataFrame(sweep).to_csv(out / "erasure_sweep.csv", index=False)
    noise = [r for c in codes for q in qs for pol in POLICIES for r in run(c, 0.1, pol, q, seeds, shots)]
    pd.DataFrame(noise).to_csv(out / "measurement_noise_sweep.csv", index=False)

    df = pd.DataFrame(sweep)
    agg = df.groupby(["code", "n", "p", "policy"]).agg(["mean", "std"])[["meas", "cnots", "fail"]]
    agg.columns = ["_".join(c) for c in agg.columns]
    agg = agg.reset_index(); agg.to_csv(out / "erasure_sweep_summary.csv", index=False)
    dn = pd.DataFrame(noise).groupby(["code", "n", "q", "policy"]).agg(["mean", "std"])[["meas", "fail", "detected"]]
    dn.columns = ["_".join(c) for c in dn.columns]
    dn = dn.reset_index(); dn.to_csv(out / "measurement_noise_summary.csv", index=False)

    col = {"full": "tab:gray", "local": "tab:blue", "minimal": "tab:red"}
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    for c in codes:
        for pol in ("local", "minimal"):
            d = agg[(agg.code == c.name) & (agg.policy == pol)]
            full = agg[(agg.code == c.name) & (agg.policy == "full")]
            nchk = len(c.hx) + len(c.hz)
            ax[0].errorbar(d.p, d.meas_mean / nchk, d.meas_std / nchk, marker="o", ls="-" if pol == "local" else "--",
                           label=f"{c.name} {pol}", alpha=.8)
    ax[0].set_xlabel("erasure probability p"); ax[0].set_ylabel("fraction of stabilisers measured"); ax[0].legend(fontsize=6)
    for c in codes:
        d = agg[(agg.code == c.name) & (agg.policy == "local")]
        f = agg[(agg.code == c.name) & (agg.policy == "full")]
        ax[1].errorbar(f.p, f.fail_mean, f.fail_std, marker="s", ls=":", label=f"{c.name} full")
        ax[1].errorbar(d.p, d.fail_mean, d.fail_std, marker="o", label=f"{c.name} local")
    ax[1].set_xlabel("erasure probability p"); ax[1].set_ylabel("logical failure rate"); ax[1].legend(fontsize=6)
    fig.tight_layout(); fig.savefig(figs / "measurement_savings.png", dpi=200); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    for c in codes:
        for pol, ls in (("full", ":"), ("local", "-"), ("minimal", "--")):
            d = dn[(dn.code == c.name) & (dn.policy == pol)]
            ax[0].errorbar(d.q + 1e-4, d.fail_mean, d.fail_std, ls=ls, marker="o", ms=3, label=f"{c.name} {pol}")
    ax[0].set_xscale("log"); ax[0].set_xlabel("syndrome-bit flip probability q (+1e-4)")
    ax[0].set_ylabel("logical failure (incl. flagged) at p=0.1"); ax[0].legend(fontsize=5)
    for c in codes:
        d = agg[(agg.code == c.name) & (agg.policy == "local") & (agg.p == 0.1 if 0.1 in ps else True)]
        ax[1].plot(d.p, d.cnots_mean, marker="o", label=c.name)
    ax[1].set_xlabel("erasure probability p"); ax[1].set_ylabel("two-qubit gates, local policy"); ax[1].legend(fontsize=6)
    fig.tight_layout(); fig.savefig(figs / "noise_and_cost.png", dpi=200); plt.close(fig)
    print(f"done in {time.time() - t0:.1f}s -> {out}")


if __name__ == "__main__":
    main()
