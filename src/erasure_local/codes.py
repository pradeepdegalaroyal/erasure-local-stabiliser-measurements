"""CSS code constructions. Rows of parity-check matrices are Python ints (bit i = qubit i)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _pack(mat: np.ndarray) -> list[int]:
    return [int("".join(str(int(b)) for b in row[::-1]), 2) for row in mat]


@dataclass
class CSSCode:
    """CSS code with X checks ``hx`` and Z checks ``hz`` (bit-packed rows)."""

    name: str
    n: int
    hx: list[int]
    hz: list[int]

    def check_commutation(self) -> bool:
        """True if every X check commutes with every Z check."""
        return all(bin(x & z).count("1") % 2 == 0 for x in self.hx for z in self.hz)

    def cnots_per_round(self) -> int:
        """Two-qubit gates for one full syndrome-extraction round (sum of check weights)."""
        return sum(bin(r).count("1") for r in self.hx + self.hz)


def toric_code(L: int) -> CSSCode:
    """Toric code on an L x L lattice, n = 2 L^2 qubits."""
    n = 2 * L * L
    h = lambda i, j: (i % L) * L + (j % L)  # horizontal edge
    v = lambda i, j: L * L + (i % L) * L + (j % L)  # vertical edge
    hx = np.zeros((L * L, n), dtype=np.uint8)  # vertex checks
    hz = np.zeros((L * L, n), dtype=np.uint8)  # plaquette checks
    for i in range(L):
        for j in range(L):
            r = i * L + j
            for q in (h(i, j), h(i, j - 1), v(i, j), v(i - 1, j)):
                hx[r, q] ^= 1
            for q in (h(i, j), h(i + 1, j), v(i, j), v(i, j + 1)):
                hz[r, q] ^= 1
    return CSSCode(f"toric-{n}", n, _pack(hx), _pack(hz))


def bb_code(l: int, m: int, a: list[tuple[str, int]], b: list[tuple[str, int]], name: str) -> CSSCode:
    """Bivariate bicycle code with A=sum x^i/y^j terms, B likewise; n = 2 l m."""
    N = l * m
    x = np.kron(np.roll(np.eye(l, dtype=np.uint8), 1, axis=1), np.eye(m, dtype=np.uint8))
    y = np.kron(np.eye(l, dtype=np.uint8), np.roll(np.eye(m, dtype=np.uint8), 1, axis=1))

    def poly(terms: list[tuple[str, int]]) -> np.ndarray:
        out = np.zeros((N, N), dtype=np.uint8)
        for var, p in terms:
            out ^= np.linalg.matrix_power(x if var == "x" else y, p) % 2
        return out % 2

    A, B = poly(a), poly(b)
    hx = np.hstack([A, B]) % 2
    hz = np.hstack([B.T, A.T]) % 2
    return CSSCode(name, 2 * N, _pack(hx), _pack(hz))


def bb72() -> CSSCode:
    """[[72,12,6]] bivariate bicycle code."""
    return bb_code(6, 6, [("x", 3), ("y", 1), ("y", 2)], [("y", 3), ("x", 1), ("x", 2)], "bb-72")


def bb144() -> CSSCode:
    """[[144,12,12]] bivariate bicycle code."""
    return bb_code(12, 6, [("x", 3), ("y", 1), ("y", 2)], [("y", 3), ("x", 1), ("x", 2)], "bb-144")
