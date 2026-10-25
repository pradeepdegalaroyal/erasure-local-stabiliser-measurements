# Research gap

**State of the art.** Experiments now run logical qubits on several platforms: surface-code scaling on superconducting chips (Acharya et al., 2023, doi:10.1038/s41586-022-05434-1; Zobrist et al., 2025, doi:10.1038/s41586-024-08449-y) and logical processors on reconfigurable neutral-atom arrays (Bluvstein et al., 2024, doi:10.1038/s41586-023-06927-3). Bivariate-bicycle (BB) codes promise a high threshold at low overhead (Bravyi et al., 2024, doi:10.1038/s41586-024-07107-7). In atom and photonic platforms, leakage and loss can be flagged, which turns errors into *erasures* with known location. Matsumoto (2027, doi:10.1007/s40314-026-03881-4) notes that a decoder can intuitively skip stabilisers that are irrelevant to the erased qubits, and that this had not been rigorously formalised; the paper does so via quantum local recovery.

**Gap.** What is missing is a *quantitative* comparison of how many stabiliser measurements (and syndrome-extraction two-qubit gates) this idea saves on concrete codes, how the saving depends on the code family (low-weight toric code vs. weight-6 BB code), and what it does when the syndrome bits themselves are noisy. Extra measurements are not free on hardware: each is a source of errors and a use of mid-circuit readout time.

**Hypotheses (falsifiable).**
- H1: measuring only the stabilisers that touch the erased set (`local`) gives the *same* logical failure rate as measuring all of them (`full`) with noiseless readout, shot for shot. Falsified by any shot where the two disagree.
- H2: the saving depends on the code: at fixed erasure rate p, BB codes (each qubit in 6 checks) need a larger fraction of their stabilisers than the toric code (4 checks per qubit).
- H3: a rank-sufficient subset (`minimal`) needs about 2pn measurements, independent of code family.
- H4: with syndrome-bit flips (probability q), `local` has a lower logical-failure-plus-false-alarm rate than `full`.

**Success metric.** Mean measured fraction of stabilisers and of syndrome-extraction controlled-NOT gates (CNOTs) vs. `full`, and logical failure rate, over 4 seeds. Scale: classical simulation of erasure + syndrome linear algebra over Galois field of two elements, GF(2), n = 32 to 144 qubits. No hardware claim.
