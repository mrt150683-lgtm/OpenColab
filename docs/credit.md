# Contribution credit

Record credit once in the accepted research record where the work belongs. The contribution can start with a proposal, an experiment, a review or a connection between projects. Later records point to that work through `builds_on`. The generated contributor index follows those links and keeps each credit tied to its source and role. [Contributors](../CONTRIBUTORS.md)

## Record your contribution

1. Agree on the public GitHub handle and role before adding credit. Humans and AI agents use the same roles. For work done with an agent, use the approved handle responsible for the contribution and optionally include an approved public agent name. Anyone may choose to leave their identity out.
2. Add one credit block to the research record. This can be a Markdown file directly in a research category or the `README.md` in a direct child folder for a multi-file record. Add each new contribution here and use `builds_on` for earlier records whose work you used.
3. Keep the evidence and review links in the visible record. For a substantial review submitted in PR comments, the author or maintainer can add a `peer review` credit to the reviewed record with the reviewer's agreement and link to the actual comment. A reproduction or replication earns its own credit in its experiment record.

A role describes who did which part of the work. Read the paper and review for the authorship of claims, strength of evidence and reviewers' assessments.

## Credit block

Use a single HTML comment with the marker and JSON shown below. The comment is hidden in rendered Markdown, and its contents are public in the source. Both JSON fields are optional. Use the plain GitHub handle without an `@`. The contributor index links to the profile.

```markdown
<!-- open-colab-credit
{
  "contributors": [
    { "handle": "github-user", "role": "experiment", "agent": "Optional public agent name" }
  ],
  "builds_on": ["research/proposals/001-weight-compression.md"]
}
-->
```

Use one entry for each agreed contribution role. The available roles are `proposal`, `experiment`, `analysis`, `implementation`, `peer review`, `reproduction`, `replication`, `improvement`, `synthesis` and `cross-discovery`.

Each `builds_on` entry is the exact path of a source record from the repository root, using forward slashes. A finding based on an experiment and a reproduction links both records. The experiment can in turn link its proposal. Add any links back to later work in the visible text. Use commit permalinks when the version is part of the evidence.

## Refresh the index

With Python 3.9 or later, run `python tools/update_credits.py` from the repository root. Include any generated changes to `CONTRIBUTORS.md` in the same PR. To verify that the index matches the records, run `python tools/update_credits.py --check`. Correct the source block and regenerate the index if a credit needs to change.

## Optional automatic refresh on GitHub

The [credit workflow](../.github/workflows/contributor-credits.yml) ships disabled. To opt in after publication, change the first condition in its `refresh` job from `false` to `true` in a pull request. Once enabled, it regenerates the index when the default branch advances and commits `CONTRIBUTORS.md` only when its content changes. Maintainers can also run it manually on that branch.

The refresh uses GitHub's built-in repository token and depends on the branch rules permitting its commit. Use the same-PR command above for branches that require all changes through pull requests. [GitHub workflow token](https://docs.github.com/en/actions/concepts/security/github_token)
