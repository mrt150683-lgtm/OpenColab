# 005 pilot · Would a literature search have caught "solved" problems that were already solved?

<!-- open-colab-credit
{
  "contributors": [
    { "handle": "mrt150683-lgtm", "role": "experiment", "agent": "Claude" }
  ],
  "builds_on": ["research/proposals/005-novelty-check-before-solved.md"]
}
-->

**Outcome: exploratory pilot that met both of the proposal's numeric thresholds, with serious caveats.** The benchmark has 39 Erdős problems where an AI contribution is documented: 21 had their answer in earlier literature and 18 were genuinely new. A multi-search agent pipeline named the correct prior paper for **15 of 21 (71%)** of the first group. It flagged **0 of 18** genuinely new results. The one-search baseline found 2 to 4 of 21.

The thresholds were 70% detection and at most 20% false flags. However, the open indexes named in the proposal were unreachable from the sandbox and were replaced by general web search, and the pipeline agents did not keep to their search budget. Most hits probably came from the model's own memory of classical papers rather than retrieval. The labels were also made by an agent from the same model family. Treat this as evidence that the idea is worth a proper run, not as a verified finding.

## Summary and provenance

- Run on 2026-11-20 by Claude (Anthropic) agents through Claude Code, at the request of `mrt150683-lgtm`. The same orchestrating agent wrote the proposal. No human has checked the labels or the matches.
- Proposal: [005-novelty-check-before-solved](../../proposals/005-novelty-check-before-solved.md).
- Ground truth: [Tao's AI-contributions wiki](https://github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erd%C5%91s-problems) (its banner says updates stopped on 2026-06-30) and individual [erdosproblems.com](https://www.erdosproblems.com/) pages.

## Benchmark

`benchmark-labels.json` has 39 items. Each has the Erdős number, a paraphrased statement, a label, the prior work, sources and notes.

- **PRIOR (21):** the AI claim turned out to be in earlier literature. This includes the October 2025 cases and #333.
- **NEW (18):** no prior literature was found.

A labelling agent built the set and excluded six ambiguous problems, with reasons. It also listed its own weak labels: 281, 397, 223, 1129 and 494 among the PRIOR items, and 1091, 1141 and 741 among the NEW items. Several prior-work titles were written from memory. The statements were stripped of problem numbers and of any mention of AI or the problem's status, then shuffled (seed 505) into `blind-statements.txt`.

## Method

Every searcher read only the rules (`search-rules.txt`) and the blind statements. Each searcher had to:

- block erdosproblems.com, GitHub, X, Reddit, Hacker News, OpenAI, Tao's blog and news sites in every search;
- ignore any source dated 2025 or later, or any source discussing AI solving the problem, and record it as a leak;
- name a specific paper published before 2025 for any PRIOR verdict.

The two methods were:

- **Pipeline** (two agents, about 20 statements each): restate the problem in standard terminology, then run several searches and read the results. The method asked for 3 to 6 searches per statement. The agents used 1 to 5 and said so.
- **Baseline** (one agent): exactly one keyword search per statement, a verdict from snippets only, and no background knowledge.

**Scoring:** `score.py`. A flag counts only if the item is PRIOR and the cited paper matches a labelled prior work. That match was judged by hand against the key and is listed in the script, so a reviewer can dispute each one.

## Results

| Method | PRIOR items caught | NEW items wrongly flagged |
| --- | --- | --- |
| Pipeline | 15 / 21 (71%), every one naming a labelled prior paper | 0 / 18 |
| One-search baseline | 2 / 21 strict, 4 / 21 counting a survey and a related paper | 0 / 18 |

The pipeline missed six PRIOR items:

- #897 (Wirsing 1981)
- **#333 (Erdős–Newman 1977, the best-known public failure)**
- #1043 (Pommerenke 1961)
- #397 (a 2012 China TST problem)
- #481 (Klarner 1982)
- #281 (follows from classical results rather than stating them)

Several of these are exactly the hard case the proposal is about: a result buried in an old paper under different wording, or in a competition problem.

**Leaks.** Searchers reported many 2025–2026 papers that discuss the AI results. Examples are arXiv 2604.06609, 2605.00301 and 2603.29961, plus an erdosproblems mirror on a domain that was not blocked. Their verdicts say these were not counted. The block list should add mirrors such as erdosproblems.ai.

## Interpretation and limitations

- **Memory versus retrieval.** The pipeline agents often "recognised" a classical result and confirmed it with one search. That is what a careful expert does, but it cannot be separated from training-data knowledge of the same episodes. The searchers may have seen discussion of these cases during training. A fair test needs problems whose AI episode postdates the model's training cutoff, or a model with a known cutoff.
- **Selection bias.** PRIOR items are mostly classical, well-cited problems, which are easier to find. The NEW items are newer and more obscure.
- **No ablation.** The planned "pipeline without restatement" control was not run. The gap between the pipeline and the baseline mixes the effect of restating, more searches, reading pages and background knowledge.
- **Same model family throughout.** Labeller and searchers were the same family. Label errors would likely be correlated with search errors.
- **Index deviation.** The arXiv, OpenAlex and zbMATH Open APIs were blocked by the sandbox proxy, so general web search stood in for open indexes.

Even so, the practical lesson is clear. A routine multi-search check, costing roughly two to three web searches per problem, would have caught most of the publicised "already known" cases. That includes 9 of the 10 October 2025 problems in the benchmark, though not #333.

## Reproduce

Run `python score.py` to recompute the table from the committed outputs. To rerun the search with another model or tool, give it `search-rules.txt` and `blind-statements.txt` only, and save its JSON in the same format. The labels are in `benchmark-labels.json`, so keep that file away from the searcher.

## Review and follow-up

1. Have a human check every label and every match against the source pages.
2. Run on claims dated after the searching model's training cutoff.
3. Run the restatement ablation and a version restricted to open indexes.
4. Grow the benchmark beyond Erdős problems, for example to items in [openai/math](https://github.com/openai/math). Report any prior work you find to the original authors before publishing it.
