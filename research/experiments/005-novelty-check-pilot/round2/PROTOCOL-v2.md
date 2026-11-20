# 005 pilot, round 2 protocol (registered 2026-11-20 22:29 UTC, before any round-2 search)

Benchmark v2: 54 items (30 PRIOR, 24 NEW).
- The 39 round-1 items, minus three that a second labeller disputed:
  - 281 and 1091: label unsure;
  - 1217: paraphrase wrong.
  That leaves 36 items, with their round-1 IDs (S01–S39 with gaps).
- 18 new items (S40–S57) added by the second labeller.
- SHA-256 of key_v2.json: 94a43310947d26dbb120a3ec706c42bdfb451ddde6778b518d5502c5d03b18c7.

Conditions:
1. **Pipeline** (same prompt as round 1). The 36 kept items reuse their round-1 verdicts unchanged. The 18 new items get a fresh blind run.
2. **No-restatement ablation** (new). Each agent:
   - uses up to 4 searches per statement, built only from the statement's own words;
   - may read result pages;
   - may not reformulate into standard terminology;
   - may not name papers from background knowledge (a citation must appear in a page or snippet it actually retrieved).
   All 54 items, split across two agents.
3. **One-search baseline:** round-1 verdicts for the 36 kept items only. It is not rerun on the new items. It is reported on the 36, not on all 54.

Primary metric: detection on PRIOR items, counting a flag only if the cited paper matches the labelled prior work (judged by hand, listed in score_v2.py), and the false-flag rate on NEW items.

Decision rule (from the proposal): supported if the pipeline reaches ≥ 70% detection and ≤ 20% false flags on all 54 items, and beats the baselines on detection at equal or lower false-flag rate. The ablation shows how much restating and background knowledge contribute.
