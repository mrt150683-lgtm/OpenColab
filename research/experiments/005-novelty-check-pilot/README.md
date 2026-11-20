# 005 pilot · Would a literature search have caught "solved" problems that were already solved?

<!-- open-colab-credit
{
  "contributors": [
    { "handle": "mrt150683-lgtm", "role": "experiment", "agent": "Claude" }
  ],
  "builds_on": ["research/proposals/005-novelty-check-before-solved.md"]
}
-->

**Outcome after round 2: the decision rule is met, but only just, and the result is still exploratory.** On an extended, double-labelled benchmark of 54 items, the pipeline named the correct earlier paper for **21 of 30 (70%)** problems whose answer was already in the literature. It wrongly flagged **0 of 24** genuinely new results. The threshold is 70%, so one fewer hit would fail it. Two controls did much worse. The no-restatement control found 8 of 30, with 1 false flag, and the one-search baseline found 2 of 20 on the items it covered. That gap suggests that most of the pipeline's advantage comes from translating a problem into standard terminology and from the model's background knowledge, not from searching more. Every labeller and searcher was from the same model family, and the sandbox blocked the open indexes. *Round 1, below, was inconclusive on its own, because it had 39 items and the rule needs 40.*

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

## Round 2: extended benchmark and no-restatement control

The protocol for this round was registered before any round-2 search: see [`round2/PROTOCOL-v2.md`](round2/PROTOCOL-v2.md). The key's SHA-256 is `94a43310…`.

- **Second labeller.** An independent agent checked all 39 round-1 items against Tao's wiki and erdosproblems.com. It agreed with 37 labels and was unsure of 2 (281, 1091). It also found one wrong paraphrase (1217) and corrected several citations. Those 3 items were dropped. The agent added 18 new items (10 PRIOR, 8 NEW), giving **54 items: 30 PRIOR and 24 NEW**. The full check is in `round2/label_check.json`.
- **Pipeline.** The 36 kept items reuse their round-1 verdicts unchanged. The 18 new items got a fresh blind run, which used at least 3 searches per statement this time.
- **No-restatement control.** For all 54 items, the agent used up to 4 searches built only from the statement's own words. It could read pages but not name papers from memory: a citation had to appear in something it retrieved. This separates "search harder" from "know what to search for".

| Condition | Items | PRIOR found | NEW wrongly flagged |
| --- | --- | --- | --- |
| Pipeline | 54 | **21 / 30 (70%)** | **0 / 24** |
| No-restatement control | 54 | 8 / 30 (27%) | 1 / 24 |
| Pipeline | 36 (round-1 items kept) | 15 / 20 (75%) | 0 / 16 |
| One-search baseline | 36 | 2 / 20 (10%) | 0 / 16 |
| No-restatement control | 36 | 6 / 20 (30%) | 0 / 16 |
| Pipeline, S47 removed (sensitivity) | 53 | 21 / 29 (72%) | 0 / 24 |

Run `python round2/score_v2.py` to reproduce every row.

**Things a reviewer should know:**

- **Agents shared a tool limit.** The agents shared an hourly page-fetch limit, and it ran out partway through round 2. Later verdicts rest on search snippets only. Most no-restatement statements got 1–3 searches rather than 4.
- **S23 was excluded from the control.** The control agent itself reported that its S23 hit came from a query naming authors it had not yet seen in any result, which breaks the rule. That hit is not counted.
- **S47 conflicts with the search rule.** Its labelled prior work is a 2025 arXiv paper, but searchers were told to count only work from before 2025. The pipeline correctly found nothing earlier. The sensitivity row shows the result without it.
- **S45 rests on a deduction.** The pipeline's hit cites the labelled paper (Rödl 1982), but the agent rated it at 50% confidence and derived the answer itself rather than reading it.
- **New misses.** The pipeline missed 4 of the 10 new PRIOR items: Konieczny 2016, Vose 1984, Lazebnik–Ustimenko–Woldar 1994, and the out-of-window S47.

## Interpretation and limitations

- **Memory versus retrieval.** The pipeline agents often "recognised" a classical result and confirmed it with one search. That is what a careful expert does, but it cannot be separated from training-data knowledge of the same episodes. The searchers may have seen discussion of these cases during training. A fair test needs problems whose AI episode postdates the model's training cutoff, or a model with a known cutoff.
- **Selection bias.** PRIOR items are mostly classical, well-cited problems, which are easier to find. The NEW items are newer and more obscure.
- **The ablation came in round 2.** The no-restatement control (round 2, above) found 27% against the pipeline's 70%. Restating the problem in standard terminology, together with the model's background knowledge, accounts for most of the gap. The two cannot be separated without a model that has a known training cutoff.
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
