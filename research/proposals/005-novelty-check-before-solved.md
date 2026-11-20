# Challenge 005 · Check the literature before calling a problem solved

**Status** Proposed on 2026-11-20 · [Research directory](../README.md) · [Background snapshot](../../docs/ai-math-landscape-2026-11.md)

<!-- open-colab-credit
{
  "contributors": [
    { "handle": "mrt150683-lgtm", "role": "proposal", "agent": "Claude" }
  ]
}
-->

## Question and hypothesis

Two of the most visible AI-mathematics failures were not wrong proofs. They were old results presented as new. In October 2025 a claim that GPT-5 had solved 10 open Erdős problems was withdrawn after the problems turned out to have existing solutions ([Bloom](https://x.com/thomasfbloom/status/1979254235075059732)). In December 2025, Erdős #333 was posted as "autonomously solved" and then traced to a 1977 paper. As AI output grows, for example the roughly 720 manuscripts in [openai/math](https://github.com/openai/math), reviewers need a cheap first filter.

**Hypothesis.** An open retrieval pipeline can flag prior literature for at least **70%** of "solved" claims that were later shown to be known, while flagging at most **20%** of genuinely new results, using only open indexes ([arXiv](https://arxiv.org/), [OpenAlex](https://openalex.org/), [zbMATH Open](https://zbmath.org/)) and an open-weight model. The pipeline needs three stages: restate the claim in several equivalent forms, run citation and full-text search, then rank and justify candidate prior results.

## Potential benefit and prior work

Every mathematician and editor screening AI-generated claims would save time, and so would anyone screening claimed discoveries in other sciences. Literature search is the step that helped OpenAI staff find existing Erdős solutions in 2025. That episode showed the search is useful, but only when it runs before the announcement. [Tao's AI-contributions wiki](https://github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erd%C5%91s-problems) and [erdosproblems.com](https://www.erdosproblems.com/) give public ground truth on which claims were new.

## Smallest useful test

1. Build a frozen benchmark from public records dated before 2026-11-20. Include at least 25 claims later found in prior literature and 25 confirmed-new results, each with its source and the reason it is classified that way. Ask a second contributor to check the labels before any runs.
2. Run the pipeline using only literature dated before each claim, so the answer cannot leak through later discussion of the claim itself. Exclude erdosproblems.com forum threads and news about the claim from the search.
3. Baselines: a single keyword search on Google Scholar or zbMATH, and the pipeline without the restatement step.
4. Budget: one laptop evening plus free API tiers.

## Decision criteria

Supported if the pipeline meets both thresholds and beats both baselines on detection at equal or lower false-flag rate. A flag counts only if it names a specific prior paper that a reviewer agrees contains the result or an immediate consequence. Detected label leakage, or fewer than 40 usable benchmark items, makes the test inconclusive. A complete run that misses a threshold is a negative result.

## Reproduction and contributions

Share the benchmark with labels and sources, prompts, raw search logs, model version and scoring script. Useful next steps for contributors:

- extend the benchmark beyond Erdős problems, for example to items in [openai/math](https://github.com/openai/math), and report candidate prior work to the original authors before publishing;
- package the pipeline as a pre-announcement checklist that any lab or individual can run.

**Runs so far:** an [exploratory pilot](../experiments/005-novelty-check-pilot/README.md) on 2026-11-20 by the proposer, using web search in place of open indexes. It found 15/21 prior results with 0/18 false flags, against 2–4/21 for one search per problem. Labels and matches still need human review.
