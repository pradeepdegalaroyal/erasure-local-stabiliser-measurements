import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from erasure_local import POLICIES, simulate_trial, toric_code  # noqa: E402
from erasure_local.codes import bb72  # noqa: E402


def test_codes_commute():
    assert toric_code(4).check_commutation()
    c = bb72()
    assert c.n == 72 and c.check_commutation()


def test_policies_agree_without_noise():
    code = toric_code(4)
    for p in (0.1, 0.3):
        fails = {}
        for pol in POLICIES:
            rng = random.Random(5)
            fails[pol] = [simulate_trial(code, p, pol, 0.0, rng)["fail"] for _ in range(60)]
        assert fails["full"] == fails["local"] == fails["minimal"]


def test_measurement_ordering():
    code = toric_code(6)
    m = {}
    for pol in POLICIES:
        rng = random.Random(1)
        m[pol] = sum(simulate_trial(code, 0.05, pol, 0.0, rng)["meas"] for _ in range(30))
    assert m["minimal"] <= m["local"] < m["full"]


def test_no_erasure_no_failure():
    assert simulate_trial(toric_code(4), 0.0, "local", 0.0, random.Random(0))["fail"] == 0.0
