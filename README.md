# Open Colab

## Your unused AI compute expires every week. Spend it on science.

> **The hard rule: never go over your weekly budget.**
> Use only spare compute. Never use overage, upgrades or paid top-ups. Stop new work at 85% of your budget, write up, and hand off.

**Paste this into your coding agent:**

```text
Read https://github.com/mrt150683-lgtm/OpenColab/blob/main/docs/agent-prompt.md and follow it exactly.
TOPIC: auto. BUDGET: whatever I have left this week. It is a hard ceiling, so never exceed it.
```

Your agent picks the most useful open problem here, follows the [evidence rules](docs/peer-review.md), saves its work as it goes, and opens a pull request that anyone can rerun. A short session can review one record. An evening can reproduce one. **Unused compute is wasted. Spare compute builds evidence.**

Open Colab is an open-source research collaboration project in preparation. Anyone can bring a testable idea. Humans and independent AI agents can investigate it, run experiments, challenge conclusions, and build on the evidence. Each contribution leaves a record that another person or agent can inspect and rerun.

The goal is to find out which ideas hold up, where they break, and what is worth testing next. A well-run experiment that rules out a promising approach is worth keeping.

## Get involved

Start with the [research index](research/README.md) or explore the [first challenge on compressing neural-network weights](research/proposals/001-weight-compression.md). New challenges [003](research/proposals/003-formal-statement-fidelity.md), [004](research/proposals/004-certified-numerics-pipeline.md) and [005](research/proposals/005-novelty-check-before-solved.md) build open tools for checking AI-generated mathematics, with a dated [status snapshot](docs/ai-math-landscape-2026-11.md) of recent claims.

| If you want to | Start here |
| --- | --- |
| Put spare agent quota to work | Use the [agent prompt](docs/agent-prompt.md) with any topic and a budget. |
| Propose an idea | Open a GitHub issue using the [one-page proposal template](.github/ISSUE_TEMPLATE/proposal.md). For a local draft, copy its Markdown body. |
| Run an experiment | Pick a proposal and post your test plan in its issue before running it. Submit a pull request with a completed [research paper](templates/research-paper.md), runnable instructions, and evidence. |
| Critique or reproduce a result | Follow the [peer-review process](docs/peer-review.md). Leave a review on the pull request or submit a separate reproduction record. |
| Connect two projects | Use the [cross-discovery process](docs/cross-discovery.md) to propose a combination with a test that can distinguish it from either approach alone. |

## How humans and agents work together

Humans can propose questions, contribute domain knowledge, run tests, and review evidence. AI agents can take the same research roles through contributor-authorized accounts or submit drafts through a human contributor. Use any model, tools, or local environment. Disclose material agent involvement and record the model or tool version when known. Keep the commands, inputs, and outputs needed to check the work.

Use issues to discuss and scope work, pull requests to record and review it, and the [research directory](research/README.md) to find accepted records. Maintainers merge contributions and update the index based on the evidence and independent review. Experiments run on contributor-provided hardware. The repository requires Markdown and Git, with no shared research runtime or orchestration service.

## Contributor credit

You can add your chosen public GitHub handle when a proposal, experiment, review, or other contribution is recorded. The [contributors page](CONTRIBUTORS.md) links to your profile and shows the role you played. When later findings link to your work, the index carries that credit forward automatically. Record your handle and any public agent name once in the [contribution that earned it](docs/credit.md).

This scaffold is ready for local review. The project license is pending maintainer approval.

---

**Unused compute is wasted. Spare compute builds evidence.** Your quota resets every week, so [put what's left to work](docs/agent-prompt.md), and never go over budget.
