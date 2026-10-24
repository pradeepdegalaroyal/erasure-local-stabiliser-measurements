# Method

**Model.** Each qubit is erased with probability p; an erased qubit carries a uniformly random Pauli (X and Z parts independent, probability 1/2). X parts are seen by Z checks, Z parts by X checks, so each CSS sector is solved separately.

**Measurement policies** (the ablation is over how much locality is used):
- `full` (standard baseline): measure all stabilisers, solve the GF(2) system on the erased columns by Gaussian elimination. Any syndrome the erased set cannot explain flags a failure.
- `local`: measure only stabilisers whose support meets the erased set.
- `minimal`: from the `local` rows, keep a greedy subset with the same rank on the erased columns.

**Recovery and failure.** Pick one solution of H_E c = s. The shot fails logically if the residual error is not in the stabiliser group of the other type. Flagged inconsistencies (only possible with noisy readout) count as failures.

**Classical comparison.** Policies are paired: the same RNG seed gives identical erasure patterns, so H1 is checked shot by shot. The classical reference is the GF(2) decoder itself; no quantum speed-up is involved.

**Codes.** Toric code (n = 32, 72, 128), BB [[72,12,6]], BB [[144,12,12]].

**Metrics.** Measurements, syndrome-extraction CNOTs (sum of check weights), logical failure rate.

**Robustness sweep.** Each measured syndrome bit is flipped with probability q in {0, 0.001, 0.003, 0.01, 0.03} at p = 0.1. `minimal` has no redundancy, so its noise-induced failures are silent; `full` and `local` are flagged when inconsistent.

**Seeds.** 4 seeds x 150 shots per point (mean ± std over seeds). p in {0.02, 0.05, 0.1, 0.15, 0.2, 0.3}.
