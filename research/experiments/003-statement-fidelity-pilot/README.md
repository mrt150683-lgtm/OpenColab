# 003 pilot · Can AI reviewers catch Lean statements that say the wrong thing?

<!-- open-colab-credit
{
  "contributors": [
    { "handle": "mrt150683-lgtm", "role": "experiment", "agent": "Claude" }
  ],
  "builds_on": ["research/proposals/003-formal-statement-fidelity.md"]
}
-->

**Outcome: exploratory pilot, with a partly negative finding for the proposal.** A single AI reviewer, reading the informal statement next to the Lean statement, caught almost every corrupted statement in both rounds and raised no false alarms:

- Round 1, simple corruptions: 28 of 28 caught, 0 of 30 false alarms.
- Round 2, subtle corruptions written by an adversary: 19 of 20 caught, 0 of 20 false alarms.

This meets the proposal's thresholds of at least 80% detection and at most 10% false alarms. However, combining it with back-translation added nothing, and the proposal says the hypothesis fails if one check alone matches the combination. **On this benchmark, the combined protocol is not supported.** The benchmark was too easy to separate the methods. Every model involved is the same model family, so shared blind spots are not tested. Lean was not run, so the equivalence-proof check was not attempted.

## Summary and provenance

- Run on 2026-11-20 by Claude (Anthropic) agents through Claude Code, at the request of `mrt150683-lgtm`. The same orchestrating agent wrote the proposal, so this is not independent work. No human has checked the labels.
- Proposal: [003-formal-statement-fidelity](../../proposals/003-formal-statement-fidelity.md).
- Source statements: [google-deepmind/formal-conjectures](https://github.com/google-deepmind/formal-conjectures) at commit `d8d031d4998c78575159ccab9a7a9e95ce043883` (Apache-2.0). These are Erdős problem files with a docstring, a single `theorem … := by sorry`, no local definitions, and no `answer(…)` placeholder. 579 statements qualified.
- **Deviation:** the planned 30 + 30 Mathlib/formal-conjectures mix became formal-conjectures only. A timed human baseline was not available, and Lean was not installed in the sandbox, so independent re-formalization with equivalence proofs (check 2) was not run.

## Hypothesis and decision rule

The registered rule is the one in the proposal:

- the combined protocol must detect at least 80% of corrupted statements, with at most 10% false alarms;
- it must beat each single check;
- the hypothesis fails if one check alone matches the combination.

"Combined" means a statement is flagged if any check flags it. That rule was fixed before scoring.

## Methodology

Every auditor was a separate agent. Each was allowed to read exactly one input file and was forbidden web access, the shell and all other files, so it could not look up the source repository or the answer key. Auditors were told that some items were corrupted, but not how many.

- **Direct judge:** sees the informal docstring and the Lean statement, and answers faithful or unfaithful.
- **Back-translation:** one agent translates the Lean statement into literal English without seeing the docstring. A second agent compares that translation with the docstring.

**Round 1 (syntactic).** `round1/mutate.py` (seeds 2026, 7, 99) took 60 top-level statements, left 30 unchanged and applied one operator to each of the other 30. The operators were ∀↔∃, an added or removed ¬, < ↔ ≤, ∧ → ∨, atTop → atBot, and a numeric literal +1. The answer key's SHA-256 was recorded before any auditor ran (`579be154…`).

**Round 2 (adversarial).** A separate adversary agent was given 40 different statements. It corrupted 20 of them with realistic Lean pitfalls and wrote down why each change is not equivalent. The pitfalls included:

- ℕ division or subtraction truncation;
- off-by-one ranges;
- floor vs ceiling;
- quantifier order;
- eventually vs frequently;
- `Set.Infinite` → `Set.Nonempty`;
- junk values (`ncard` of an infinite set is 0);
- swapped arguments.

A script confirmed that the 20 untouched items match the source byte for byte.

## Results

Reproduce these numbers with `python score.py`.

| Round | Check | Corrupted caught | False alarms on unchanged |
| --- | --- | --- | --- |
| 1, all 60 | Direct judge | 29 / 30 | 0 / 30 |
| 1, all 60 | Back-translation | 27 / 30 | 0 / 30 |
| 1, all 60 | Either | 29 / 30 | 0 / 30 |
| 1, two equivalent mutants removed | Direct judge | 28 / 28 | 0 / 30 |
| 1, two equivalent mutants removed | Back-translation | 27 / 28 | 0 / 30 |
| 2, adversarial | Direct judge | 19 / 20 | 0 / 20 |
| 2, adversarial | Back-translation | 19 / 20 | 1 / 20 |
| 2, adversarial | Either | 19 / 20 | 1 / 20 |

Notes on the individual cases:

- **Our own mutation script produced 2 equivalent "corruptions" out of 30.** Q45 changed `1 ≤ n` to `1 < n` inside a natural-density statement, which does not change the density. Q09 changed `2 ≤ g` to `2 < g`, but the g = 3 case implies the g = 2 case. The auditors were right to pass them. A mutation benchmark needs an equivalence check of its own.
- **The one round-2 miss (T01)** changed "eventually" to "frequently" inside a negated statement. The adversary had itself flagged this as the weakest corruption: the result is weaker, but it is still true.
- **The one false alarm (T29, erdos_1077)** is an unchanged statement that asserts a negative answer. Its docstring poses an open-sounding question without saying the answer, although the file's metadata marks it "research solved". This is a gap in the docstring rather than a misformalization, but it is the kind of thing a fidelity audit should report to the source repository.

## Interpretation and limitations

- **For the tested change types, current models are already strong single reviewers.** That is useful: a cheap first-pass fidelity check on public AI proofs is realistic today. It does not show the combined protocol adds value, because the benchmark could not separate the methods.
- **Every agent is the same model family:** adversary, translators and judges alike. The adversary may produce corruptions in a style its own family finds easy to spot. A cross-family run, and a human-written adversarial set, are the obvious next tests.
- Telling auditors that corruptions exist raises their vigilance. Real reviews of a 600,000-line Lean library start from a much lower prior, with far longer statements and local definitions. This pilot excluded local definitions to keep statements self-contained, and those are exactly where real fidelity problems hide.
- The labels are only as good as the adversary's reasoning about non-equivalence, which no human has checked.

## Reproduce

Everything needed is in this folder: the inputs, prompts as embedded in the blind files, raw agent outputs, the key and the scorer. Run `python score.py` with Python 3.9+ and no dependencies. To rerun with other models, give the blind files to new auditors under the same no-tools rule and replace the verdict files. To regenerate round 1, clone formal-conjectures at the commit above as `fc/`, then run `round1/extract.py` and `round1/mutate.py` from the folder containing `fc/`.

## Review and follow-up

The most useful next runs are:

1. Have a human Lean user write 20 corruptions, and a human try to beat the AI judge with a time limit.
2. Use auditors from a different model family.
3. Run statements with local definitions, as in real proof releases.
4. Run the equivalence-proof check in Lean.
5. Run the frozen protocol as a dry run on a small, already reviewed public AI proof release.
