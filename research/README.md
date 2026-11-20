# Research index

This is the entry point for finding a project, its experiments, and the evidence behind its conclusions. Add links here in the same pull request as a new record. Link related records in both directions where they help readers follow the evidence.

## Where records go

| Directory | Contents |
| --- | --- |
| [proposals/](proposals/) | One-page hypotheses and test plans. Copy the body of the [proposal template](../.github/ISSUE_TEMPLATE/proposal.md) into the repository after discussion or submit it directly for review. |
| [experiments/](experiments/) | Original experiments, independent reproductions, and follow-up runs. Use the [paper template](../templates/research-paper.md) and keep small, shareable evidence next to its record or link to versioned artifacts. |
| [verified-findings/](verified-findings/) | Scoped claims backed by independent reproduction under the [peer-review process](../docs/peer-review.md). Link the experiment, reproduction, and review that support each claim. |
| [negative-results/](negative-results/) | Reviewed evidence that a hypothesis failed its stated test or a tested approach fell short of its target. State the conditions, threshold, and observed result. |
| [cross-discoveries/](cross-discoveries/) | Reviewed connections across projects and links to proposals that test the combination. Follow the [cross-discovery process](../docs/cross-discovery.md). |

Use unique lowercase filenames with hyphens. The filename stem is the record ID within its directory. For related experiments, start the name with the proposal ID and add a distinguishing suffix such as `001-weight-compression-pilot.md` or `001-weight-compression-reproduction-lee.md`. Use a same-named folder if a record needs multiple files and put its entry point in `README.md`.

Include contributors, date, a short statement of the question or claim, current outcome, and links to the issue, evidence, or reviews that apply. Put outcomes such as *exploratory*, *inconclusive*, and *blocked* in the experiment record. Keep earlier evidence and disputed results linked if a later run changes the conclusion. Use commit permalinks for the versions reviewed or reproduced.

Use the [credit record](../docs/credit.md) to capture each contributor's chosen GitHub handle and role. Add explicit source records in `builds_on` when documenting work that materially draws on earlier contributions. [Contributor credit by outcome](../CONTRIBUTORS.md#credit-by-outcome) follows those links.

## Proposals

| ID | Question | Status |
| --- | --- | --- |
| [001-weight-compression](proposals/001-weight-compression.md) | Can a structured mathematical representation compress weights while preserving task performance? | Open example challenge |

## Experiments

Awaiting the first run.

## Verified findings

Awaiting independently reproduced evidence.

## Negative results

Awaiting reviewed findings.

## Cross-discoveries

Awaiting proposed connections.
