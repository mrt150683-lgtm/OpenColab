# [Research title]

Copy this template into `research/experiments/` following the [research index](../research/README.md). Remove this paragraph and replace the prompts with evidence or explain any gaps. Keep links to earlier versions and preserve raw records. See [contribution credit](../docs/credit.md) for the optional credit block.

## Summary and provenance

- Describe the human and AI contributions and any conflicts of interest. Include tool or model identifiers where they affected the research.
- Record approved credit for new contributions once in the optional credit block. Use `builds_on` for earlier research records that this work used.
- Link the source proposal, protocol and related work. Use commit permalinks for the exact versions tested. State the run date and whether this is an original test, reproduction or independent replication.
- State the question, hypothesis, expected benefit and the result in a few sentences. Scope the claim to the conditions tested.

## Hypothesis and decision rule

State the predicted outcome and the conditions that would count as support, lack of support or an inconclusive test. Define the comparison, primary metric, units, practical effect threshold and handling of uncertainty. Link the protocol agreed before testing and identify any exploratory analysis.

## Mathematical model or rationale

Define symbols, terms, assumptions and units. Show the equations, derivation or algorithm needed to evaluate the claim. Describe boundary conditions and any approximations. Identify which pieces are inherited and cite their source. For research without equations, specify the reasoning and assumptions behind the test.

## Methodology

Describe the inputs and their provenance, selection criteria and splits, interventions, controls and baselines. Specify which settings are held fixed, how parameters were chosen, and how tuning was kept separate from evaluation. State sample sizes or run counts, seeds, compute budget, and how you estimated uncertainty. Record deviations from the initial protocol with reasons and their timing.

## Evidence

Link to the raw observations, derived tables, logs and scripts that produced them. Identify the source revision, input versions, artifact checksums where relevant, and the conditions for accessing and reusing third-party materials. Map each main claim to its supporting evidence. State what may limit inspection or reuse.

## Results

Show measured values for the baseline and each tested condition, including sample or run counts and variability or intervals where appropriate. Report failed runs and exclusions with their reasons. Link the raw records and analysis for each result. Apply the stated decision rule and identify results that came from exploratory analysis.

| Condition | Metric and unit | Value and uncertainty | Runs or samples | Evidence |
| --- | --- | --- | --- | --- |
| [Baseline or test] | [Name and unit] | [Estimate and interval] | [Count] | [Artifact link] |

## Interpretation and limitations

Explain what the evidence supports and which assumptions or settings bound the conclusion. Consider competing explanations, sources of bias and potential failure modes. Describe the tests that would resolve remaining uncertainties or establish a wider scope.

## Reproduce the experiment

1. Give the exact source commit, operating system, runtime, dependencies and hardware used. Include a lockfile or the dependency versions where applicable.
2. Give commands to acquire and verify the inputs, with upstream versions, checksums and preparation steps. Record expected storage, runtime, and whether a CPU is sufficient.
3. Give executable setup, experiment and analysis commands in the order they run. Include required arguments, configurations, seeds, and where outputs are written. Specify any manual steps or expected nondeterminism.
4. List expected output files and the values or tolerance a reproducer should check. Link a small smoke test where useful and keep its purpose clear.

## Review and follow-up

Link the review thread, any independent experiment records, the stated decision and related corrections or extensions. Describe discrepancies and which version or conditions each applies to. Follow `docs/peer-review.md` when recording the outcome.
