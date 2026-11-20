# 004 pilot · Rerunnable interval-arithmetic certificates on a laptop CPU

<!-- open-colab-credit
{
  "contributors": [
    { "handle": "mrt150683-lgtm", "role": "experiment", "agent": "Claude" }
  ],
  "builds_on": ["research/proposals/004-certified-numerics-pipeline.md"]
}
-->

**Outcome: exploratory pilot, not the frozen test.** The same agent wrote the proposal, the benchmarks, the solver and the verifier on the same evening, so nothing here is independent yet. A standalone verifier accepted all five certificates on two different machines and gave identical bounds. It also rejected all seven deliberately corrupted certificates. Benchmark 3 of the proposal (a De Gregorio / CCF blowup profile) was **not attempted**. The Burgers control was replaced by a manufactured-solution control; the reason is given below. **The proposal's decision rule is therefore not applied.**

## Summary and provenance

- Run on 2026-11-20 by Claude (Anthropic), driven through Claude Code, at the request of `mrt150683-lgtm`. No human has checked the mathematics yet.
- Source proposal: [004-certified-numerics-pipeline](../../proposals/004-certified-numerics-pipeline.md). Background: [status snapshot](../../../docs/ai-math-landscape-2026-11.md).
- Question: can a small open pipeline turn float64 solutions into certificates that a separate program checks rigorously in seconds on an ordinary CPU?
- Result on these toy problems: yes. Every certificate was verified in under one second per problem on both machines. It is not evidence about the hard benchmarks, which are where the real difficulty lies.

## What is certified

All bounds use [Arb](https://arblib.org/) ball arithmetic at 128-bit precision through `python-flint`. Every float in a certificate is read as the exact binary number it denotes.

| Certificate | Statement proved, if the verifier is correct | Radius | Verify time (A / B) |
| --- | --- | --- | --- |
| `control-manufactured` | `ε u'' + u − u³ = f` on (0, π), with `u(0) = u(π) = 0`, `ε = 1/10` and `f` made from `u* = 0.8 sin x + 0.1 sin 3x`, has exactly one solution within `r` of `ū` in the norm `Σ|a_k|`. That ball contains `u*`. | 1e−12 | 0.01 s / 0.02 s |
| `control-manufactured-seed05` | The same forced problem has a **second** solution, more than 0.36 from `u*`. | 1e−10 | 0.01 s / 0.02 s |
| `allen-cahn-eps0.1` | `ε u'' + u − u³ = 0`, Dirichlet, `ε = 1/10`, has a unique solution within `r` of a 64-mode sine series with `ū(π/2) ≈ 0.996`. | 1e−12 | 0.07 s / 0.14 s |
| `allen-cahn-eps0.02` | The same with `ε = 1/50` and 160 modes, which gives thinner boundary layers. | 1e−12 | 0.54 s / 0.89 s |
| `grid3-swing` | A 3-bus swing-equation model (bus 1 slack) has a unique equilibrium in the stated angle box. Every linearization over that box has all eigenvalues with real part below −0.225. | 1e−12 rad | <0.01 s |

The sup-norm error of `u` is at most the radius, since `|sin kx| ≤ 1`.

## Mathematical model or rationale

**Sine-series problems.** Write `u = Σ_{k≥1} a_k sin kx` and `F(a)_k = (1 − εk²) a_k − (u³)_k − f_k`. Work in ℓ¹ with weight ν = 1. Sine coefficients of a product of three sine series are `−¼ (s * s * s)` of their odd extensions, which gives `‖trilinear(x, y, z)‖ ≤ ‖x‖‖y‖‖z‖`. With `A` equal to a float inverse of the N-mode Jacobian plus `1/(1 − εk²)` on modes `k > N`, the verifier encloses:

- `Y0 ≥ ‖A F(ā)‖`, which is exact because `F(ā)` has finitely many modes;
- `Z1 ≥ ‖I − A DF(ā)‖`, using columns `j ≤ 3N` explicitly and the bound `3ω / |1 − ε(N+1)²|` for `j > 3N`, where `ω = ¼‖s * s‖`;
- `Z(r) = Z1 + 3‖A‖ r (2‖ā‖ + r)`.

It accepts if `Y0 + (Z(r) − 1) r < 0` and `Z(r) < 1`. By the contraction mapping theorem applied to `x ↦ x − A F(x)`, this gives a unique zero in the ball. It is the standard radii-polynomial method (for example Lessard and collaborators). The ℓ¹ solution is continuous, and a standard bootstrap gives a classical solution; the verifier does not check this step.

**Grid.** The model is `M_i θ_i'' + D_i θ_i' = P_i − Σ_j B_ij sin(θ_i − θ_j)`, i = 2, 3, with θ₁ = 0. The parameters are in `solver.py`. Decimal inputs such as `0.1` are taken as the nearest binary double, so the certificate is about that exactly specified model.

- **Existence:** a Krawczyk operator test on the box shows a unique equilibrium.
- **Stability:** a float Lyapunov matrix `P` for `J + αI` is checked by Sylvester's criterion on interval matrices. Every leading-minor enclosure of `P` and of `−((J+αI)ᵀP + P(J+αI))` must be strictly positive for every `J` in the box. That implies all eigenvalues have real part below `−α`. The numerical spectral abscissa is −0.25 (both buses have D/2M = 0.25), and the certified α is 90% of that.

## Methodology

1. `solver.py` (NumPy, float64) runs Newton's method on each problem and writes JSON certificates. They hold the coefficients, the approximate inverse, the claimed radius, and for the grid the equilibrium, preconditioner, α and Lyapunov matrix.
2. `verify.py` uses only `python-flint` and the standard library and does not import the solver. It recomputes every bound and exits non-zero if any certificate is rejected.
3. `tamper_test.py` changes one thing in a copied certificate and requires a rejection. Cases:
   - the approximation moved by 1e−6;
   - a different ε;
   - the preconditioner scaled ×3;
   - the forcing changed;
   - a claimed α of 0.26, above the true 0.25;
   - the equilibrium moved by 1e−6;
   - an injection of 2.5 p.u.
4. The verifier and tamper tests were run on machine A, where the certificates were made, and again on machine B from a tarball whose SHA-256 hashes were checked first.

**Deviations and decisions made after seeing results.** These are listed so a reviewer can judge them:

- **The Burgers control was replaced** by a manufactured solution. The Burgers self-similar profile is defined implicitly (`y = −U − U³`) and grows at infinity, so it does not fit the bounded-domain sine machinery without extra work. A manufactured solution keeps the property that matters: an exact answer known in advance.
- **The control first converged to the wrong solution.** Seeded at `0.5 sin x`, Newton's method found a different solution of the same forced problem. It was certified at a radius of 1e−12, rejected (`Y0 ≈ 9.4e−12`), and accepted after the radius was raised to 1e−10. It is reported as a second certificate. The main control uses the seed `0.75 sin x + 0.1 sin 3x`, chosen after this observation. This is the clearest lesson of the pilot: **a certificate proves a solution exists near the approximation, not that it is the solution you meant.**
- **One tamper case was wrong, not the verifier.** Scaling the preconditioner by 0.5 was first expected to fail, but it still gives `Z < 1` and therefore a valid proof. It was replaced with ×3.
- Benchmark sizes (N = 24, 64, 160) and radii were chosen by the author without a registered grid.

## Evidence

- `certificates/*.json`: the five certificates.
- `verify-output-machine-a.txt` and `tamper-output-machine-a.txt`: Intel Xeon @ 2.10 GHz, 4 vCPU, Linux 6.18, Python 3.13.18, python-flint 0.9.0, NumPy 2.5.3.
- `verify-output-machine-b.txt`: AMD Ryzen 5 5500U, Linux 6.8 (Ubuntu 22.04 VM), Python 3.10.12, python-flint 0.9.0 installed offline from the PyPI wheel. The file includes the input hashes.
- `MANIFEST.sha256`: hashes of the source and certificates as committed.

Apart from timings, the accept/reject lines and every printed bound are **identical** on both machines. The check strips the `seconds` field and diffs the output.

## Results

| Condition | Metric | Machine A | Machine B |
| --- | --- | --- | --- |
| Five certificates | Accepted | 5 / 5 | 5 / 5 |
| Corrupted certificates | Rejected | 7 / 7 | 7 / 7 |
| Slowest certificate (`allen-cahn-eps0.02`, N = 160) | Wall-clock seconds | 0.54 | 0.89 |
| Control | Upper bound on distance to `u*` | 6.95e−17 (inside r = 1e−12) | same |
| Grid | Certified decay rate α | 0.225 | same |

## Interpretation and limitations

- These are **easy** problems. All are smooth, one-dimensional or tiny, and need only a few hundred modes. The proposal's hard benchmark, a self-similar blowup profile, involves non-compact domains, singular weights and stability of the profile. Published versions of such proofs (for example Chen–Hou, [arXiv:2210.07191](https://arxiv.org/abs/2210.07191)) needed far more machinery. This pilot shows only that the plumbing works: certificate format, separate verifier and cross-machine rerun.
- **The verifier is unreviewed code, written by the same agent as the solver.** A bug in the norm bounds would make every acceptance meaningless. The tamper tests catch gross errors, not subtle ones. The derivation above should be checked by a person, and ideally the verifier should be ported to an independent library (MPFI or CAPD) or to Lean.
- The grid model is a textbook toy, not a real network. Its value is showing that the same certificate pattern gives a *proved* stability margin rather than an eigenvalue estimate.

## Reproduce the experiment

```bash
cd research/experiments/004-certified-numerics-pilot
python -m pip install -r requirements.txt   # python-flint 0.9.0, numpy
sha256sum -c MANIFEST.sha256
python verify.py certificates/*.json         # expect 5 ACCEPT lines, exit code 0
python tamper_test.py                        # expect 7/7 rejected
python solver.py certificates-new            # optional: regenerate; floats may differ by platform
python verify.py certificates-new/*.json
```

The run needs a CPU only, takes under 2 seconds and uses under 1 MB of input. Regenerated certificates can differ in their last bits across BLAS builds. The committed certificates are the evidence.

## Review and follow-up

The most useful next contributions are:

1. An independent review of the bounds in `verify.py`, in particular the Z1 tail and the trilinear constant.
2. A second verifier in another library.
3. An attempt at benchmark 3, the De Gregorio profile, under a frozen protocol.
4. A Lean-checked version of the sine-series inequality, so that the interval step is no longer trusted outside a proof.
