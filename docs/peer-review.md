# Peer review and reproduction

Anyone can review research through a GitHub pull request. Humans and AI agents use the same evidence requirements. If you work with an agent, describe its role and record the model or tool version when it could affect the result.

## Review a claim

1. **Choose a claim and revision.** Comment on the proposal's issue or pull request with the claim you intend to check. Link the proposal and paper at the exact commit reviewed. State any role in the original work or other relevant conflict. An independent reviewer had no role in designing, implementing or reporting the work under review. A second agent can qualify even if it uses the same model. It needs its own assessment and independently obtained evidence for any rerun it reports.
2. **Critique the work.** Use PR review comments for specific issues and a summary comment for your assessment. Check the assumptions and mathematics, experimental controls, measurement and uncertainty, evidence provenance, and whether the conclusions stay within the tested scope. Cite the relevant file, equation or result and describe what would resolve each blocking concern.
3. **Rerun or replicate.** For a reproduction, run the original protocol from the pinned inputs and source in an environment you control. For an independent replication, rebuild the test and document differences in implementation, inputs or environment. Keep a separate record under `research/experiments/` using the [paper template](../templates/research-paper.md). Include commands, environment, measured values, deviations and links to the evidence. Report matching, partly matching, conflicting or blocked outcomes against the original decision rule. A critique alone establishes no rerun result.
4. **Follow up.** Authors can address comments with revised evidence or explain a disagreement. Anyone can submit an improvement as a linked PR with the proposed change and its test plan. Preserve earlier records and explain which claims or revisions the follow-up affects.

## Record the outcome

Maintainers record the decision in the PR and link it from the relevant [research entry](../research/README.md). A verified finding names the exact claim and tested conditions. It needs inspectable evidence, independent review and at least one documented independent reproduction or replication that supports it. Resolve blocking methodological concerns before marking it verified.

A negative result documents a completed test that failed its stated threshold or found evidence against the hypothesis. It needs a quality review of the controls, method and scope. State whether anyone has reproduced it independently. A missing input, failed setup or result too imprecise to classify belongs in the experiment record with the reason it remains inconclusive. Link material disagreements and conflicting runs where readers encounter the claim. If later evidence changes the conclusion, link the revised finding and keep the original decision traceable.

With the reviewer's agreement, the author or maintainer can record substantial PR feedback as `peer review` in the reviewed record and link the feedback. Credit reproductions and replications in their own experiment records. Findings carry earlier credit through links to the supporting records. [Contribution credit](credit.md)

## Review comment

Copy this into a PR summary comment and fill in the fields that apply.

```markdown
Claim and exact revision reviewed
Reviewer, contributor roles and conflicts
Public credit preference and approved handle, if applicable
Checks performed and evidence links
Blocking concerns and proposed checks
Rerun or replication record, if performed
Assessment and scope
```
