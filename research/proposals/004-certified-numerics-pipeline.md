# Challenge 004 · Turn a numerical solution into a rerunnable certificate

**Status** Proposed on 2026-11-20 · [Research directory](../README.md) · [Background snapshot](../../docs/ai-math-landscape-2026-11.md)

<!-- open-colab-credit
{
  "contributors": [
    { "handle": "mrt150683-lgtm", "role": "proposal", "agent": "Claude" }
  ]
}
-->

## Question and hypothesis

Recent blowup work on fluid equations combines two steps: find a very accurate approximate solution numerically, then use interval arithmetic to prove that a true solution exists nearby. See the high-precision PINN work in [arXiv:2509.14185](https://arxiv.org/abs/2509.14185), the Chen–Hou proof in [arXiv:2210.07191](https://arxiv.org/abs/2210.07191) and the [unforced blowup claim](https://github.com/tristanbuckmaster/navier-stokes/) of 20 November 2026. The last one is unconfirmed, and its certificate was published only as a hash. These pipelines are usually bespoke, so few people can rerun them.

**Hypothesis.** A small open pipeline, using only CPU and open libraries, can produce certificates that an independent machine verifies in under **10 minutes** per problem. It needs three stages: a solver (Newton or Gauss–Newton on a spectral or Chebyshev basis, with an optional neural ansatz), a rigorous residual bound computed with [Arb via python-flint](https://python-flint.readthedocs.io/), and a Newton–Kantorovich or contraction check. The target is rigorous existence of a solution within a stated error radius for **3 of 4** benchmark problems.

## Potential benefit and prior work

A reusable recipe for "approximate → certified" matters well beyond blowup proofs. The same certificate can prove that an equilibrium of a power-grid, chemical-reactor or plasma model exists and is stable, or put a rigorous error bar on a surrogate model used in safety analysis. Validated numerics is an established field (CAPD, INTLAB, Arb). This challenge adds a shared certificate format, a frozen benchmark and an independent verifier, so certificates can be published and rechecked like other evidence in this repository.

## Smallest useful test

Four benchmarks, ordered by difficulty. Freeze them before any solver tuning.

1. **Control with a known exact answer:** the self-similar profile of the inviscid Burgers equation. The pipeline must recover the known profile within the certified radius.
2. A steady state of a 1D reaction–diffusion (Allen–Cahn type) boundary value problem.
3. A self-similar blowup profile of the 1D De Gregorio or Córdoba–Córdoba–Fontelos model, a standard toy model for vortex stretching.
4. A real-world-style stability certificate: an equilibrium of a 3-bus swing-equation power-grid model, together with a certified bound on the spectral abscissa of its linearization.

For each, publish the approximate solution, the certificate (coefficients plus bounds) and a standalone verifier that does not import the solver. Baseline: plain float64 residual checks, which give an estimate but no proof. Record wall-clock time, precision and certified radius.

## Decision criteria

Supported if the independent verifier accepts at least 3 of the 4 certificates on a second machine within the time budget, and the Burgers control matches the exact solution within its radius. Rejecting the Burgers control, or a certificate that passes only with the solver's own code, counts against the hypothesis. A missing verifier rerun is inconclusive.

## Reproduction and contributions

Share the solver, certificate files with SHA-256 hashes, verifier, environment lockfile and timings. Useful next steps for contributors:

- port the verifier to a second independent library (for example MPFI or CAPD);
- add a 2D benchmark;
- connect the verifier to Lean so that the interval check is no longer a trusted step outside the proof. That step was a gap in the 20 November 2026 claim.

This challenge makes no claim about Navier–Stokes itself.

**Runs so far:** an [exploratory pilot](../experiments/004-certified-numerics-pilot/README.md) on 2026-11-20 by the proposer. It covers benchmarks 2 and 4 and a substitute control, and does not apply the decision rule. Benchmark 3 remains open.

---

**Unused compute is wasted. Spare compute builds evidence.** Run this challenge with the [agent prompt](../../docs/agent-prompt.md), setting `TOPIC` to this file's ID and keeping inside your weekly budget.
