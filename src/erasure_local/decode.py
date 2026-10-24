"""Erasure recovery with three measurement policies.

Policies
--------
full     : measure every stabiliser; decoder uses all syndromes (standard baseline).
local    : measure only stabilisers whose support meets the erased set.
minimal  : measure a greedy rank-sufficient subset of the local stabilisers.
"""
from __future__ import annotations

import random

from .codes import CSSCode

POLICIES = ("full", "local", "minimal")


def _reduce(basis: dict[int, int], v: int) -> int:
    """Reduce v by an echelon basis keyed by leading bit."""
    while v:
        top = v.bit_length() - 1
        if top not in basis:
            return v
        v ^= basis[top]
    return 0


def _span_basis(rows: list[int]) -> dict[int, int]:
    basis: dict[int, int] = {}
    for r in rows:
        r = _reduce(basis, r)
        if r:
            basis[r.bit_length() - 1] = r
    return basis


def _select_rows(rows: list[int], mask: int, policy: str) -> list[int]:
    """Indices of rows to measure for one sector."""
    if policy == "full":
        return list(range(len(rows)))
    touch = [i for i, r in enumerate(rows) if r & mask]
    if policy == "local":
        return touch
    basis: dict[int, int] = {}
    keep = []
    for i in touch:
        r = _reduce(basis, rows[i] & mask)
        if r:
            basis[r.bit_length() - 1] = r
            keep.append(i)
    return keep


def _solve(rows: list[int], syn: list[int], mask: int) -> int | None:
    """Find error c supported on mask with parity(row & c) = syn; None if inconsistent."""
    # eliminate on columns of mask; each entry: (restricted row, syndrome bit, ) with pivot
    piv: dict[int, tuple[int, int]] = {}
    for r, s in zip(rows, syn):
        r &= mask
        while r:
            top = r.bit_length() - 1
            if top not in piv:
                piv[top] = (r, s)
                break
            pr, ps = piv[top]
            r ^= pr
            s ^= ps
        else:
            if s:
                return None
    sol = 0
    for top in sorted(piv):  # ascending: lower pivots first
        r, s = piv[top]
        low = r & ~(1 << top)
        val = s ^ (bin(low & sol).count("1") & 1)
        if val:
            sol |= 1 << top
    return sol


def _sector(checks: list[int], other: list[int], err: int, mask: int, policy: str,
            q: float, rng: random.Random) -> tuple[int, bool, bool]:
    """One CSS sector. Returns (#measurements, logical_fail, detected_inconsistency)."""
    idx = _select_rows(checks, mask, policy)
    rows = [checks[i] for i in idx]
    syn = [(bin(r & err).count("1") & 1) ^ (1 if q > 0 and rng.random() < q else 0) for r in rows]
    sol = _solve(rows, syn, mask)
    if sol is None:
        return len(idx), True, True
    resid = err ^ sol
    fail = _reduce(_span_basis(other), resid) != 0
    return len(idx), fail, False


def simulate_trial(code: CSSCode, p: float, policy: str, q: float, rng: random.Random) -> dict[str, float]:
    """One erasure shot: erase each qubit w.p. p, uniform Pauli on erased, measure, recover."""
    mask = ex = ez = 0
    for i in range(code.n):
        if rng.random() < p:
            mask |= 1 << i
            if rng.random() < 0.5:
                ex |= 1 << i
            if rng.random() < 0.5:
                ez |= 1 << i
    # X errors flagged by Z checks; residual must lie in rowspace(Hx), and vice versa.
    mz, fz, dz = _sector(code.hz, code.hx, ex, mask, policy, q, rng)
    mx, fx, dx = _sector(code.hx, code.hz, ez, mask, policy, q, rng)
    meas = mx + mz
    # CNOT cost of measured checks
    sel_z = _select_rows(code.hz, mask, policy)
    sel_x = _select_rows(code.hx, mask, policy)
    cnots = sum(bin(code.hz[i]).count("1") for i in sel_z) + sum(bin(code.hx[i]).count("1") for i in sel_x)
    return {"meas": meas, "cnots": cnots, "fail": float(fz or fx), "detected": float(dz or dx)}
