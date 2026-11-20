# Challenge 003 · Catch formal statements that prove the wrong theorem

**Status** Proposed on 2026-11-20 · [Research directory](../README.md) · [Background snapshot](../../docs/ai-math-landscape-2026-11.md)

<!-- open-colab-credit
{
  "contributors": [
    { "handle": "mrt150683-lgtm", "role": "proposal", "agent": "Claude" }
  ]
}
-->

## Question and hypothesis

AI systems now publish long Lean proofs of headline results, including the contested September 2026 Navier–Stokes claim and the 20 November 2026 RH/GRH claim. Lean checks that a proof establishes its formal statement. A reader still has to check that the statement means what the paper says. An independent paper reported a mismatch of this kind in the Navier–Stokes case ([arXiv:2610.08144](https://arxiv.org/abs/2610.08144)).

**Hypothesis.** An open, model-agnostic audit protocol can flag at least **80%** of deliberately corrupted formal statements, with at most **10%** false alarms on faithful ones, on a frozen benchmark of research-level statements. The protocol combines three checks:

1. **Back-translation.** A model that never saw the informal statement translates the Lean statement into prose, and a separate judge compares it with the original.
2. **Independent re-formalization.** A second model or person formalizes the informal statement from scratch. The two formal statements are compared by attempting proofs of equivalence or implication in each direction.
3. **Sanity probes.** Automated checks for trivially true or vacuous statements, such as hypotheses that are unsatisfiable, quantifiers that collapse, and definitions that differ from Mathlib's.

The hypothesis is wrong if a careful single human reviewer with the same time budget does as well, or if any one check alone matches the combination.

## Potential benefit and prior work

A cheap, shared fidelity audit would let mathematicians triage AI-generated proofs in hours instead of weeks, and would apply equally to verified software and safety certificates. Prior work includes autoformalization benchmarks and DeepMind's [formal-conjectures](https://github.com/google-deepmind/formal-conjectures). This test adds a mutation benchmark that measures *detection of wrong statements*, which existing benchmarks do not report.

## Smallest useful test

1. Freeze 60 faithful statements: 30 from formal-conjectures and 30 from Mathlib theorems with clear textbook sources. Record commit hashes.
2. Create 60 corrupted twins with a registered mutation list, applied by someone who will not run the audit: a dropped hypothesis, a weakened conclusion, a changed quantifier order, a replaced definition, a vacuous hypothesis, and an off-by-one domain. Publish only the hash of the answer key until the audit is frozen.
3. Run each check alone and in combination under a fixed budget. Suggested budget: under USD 20 of API cost or one consumer GPU evening per configuration. Record model names and versions.
4. Baseline: one human with Lean experience, 3 minutes per statement, blind to the key.

## Decision criteria

Supported if the combined protocol meets both thresholds and beats each single check and the timed human baseline on detection at equal or lower false-alarm rate. A complete run that misses either threshold is a negative result worth recording. Missing models, leaked answer keys or fewer than 100 scored statements make the test inconclusive.

## Reproduction and contributions

Share the frozen statement list, mutation script, answer key (revealed after the audit freezes), prompts, raw model outputs and scoring script. Useful next steps for contributors:

- add harder mutations taken from real disputes;
- run the frozen protocol on a public, already-reviewed AI proof as a dry run, and only then on a live claim such as the public [RH/GRH Lean release](https://alpo.ge/remark.pdf) or [openai/ten-proofs](https://github.com/openai/ten-proofs). Report results as an audit of the statement's fidelity, not as a verdict on the proof.

Respect the licenses of the source repositories and do not redistribute withheld material.

**Runs so far:** an [exploratory pilot](../experiments/003-statement-fidelity-pilot/README.md) on 2026-11-20 by the proposer. The direct judge alone met both thresholds, so the combination showed no added value on that benchmark. Harder, human-written and cross-model rounds are the open next step.
