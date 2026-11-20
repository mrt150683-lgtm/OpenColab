# AI-assisted mathematics: status snapshot, 20 November 2026

This page gives background for challenges [003](../research/proposals/003-formal-statement-fidelity.md), [004](../research/proposals/004-certified-numerics-pipeline.md) and [005](../research/proposals/005-novelty-check-before-solved.md). It records what was publicly claimed up to the date above and how far each claim had been checked. **It is a dated snapshot, not a verified finding.** Several claims are hours or weeks old. Correct this page with a linked source when the status changes, and keep the earlier wording traceable in Git history.

The research was compiled by AI agents (Claude) using web search on 2026-11-20. Some primary pages blocked automated fetching, so a few details come from news coverage or archive copies. Those are marked *second-hand*.

## Status labels

- **Confirmed**: independent experts checked the work and reported no blocking error.
- **Contested**: there is a public, specific dispute about correctness, fidelity or priority.
- **Unconfirmed**: backed only by its authors or vendor so far, or too recent to have been checked.
- **Retracted**: withdrawn or shown to be prior literature.

## Claims and their status

| Date | Claim | Who | Method | Status | Source |
| --- | --- | --- | --- | --- | --- |
| 2025-07 | IMO 2025 gold-level score, natural-language proofs | OpenAI | Informal proofs, no tools | Unconfirmed by the IMO. Proofs are public | [proofs](https://github.com/aw31/openai-imo-2025-proofs/) |
| 2025-10 | "GPT-5 solved 10 Erdős problems" | OpenAI staff post, later deleted | Literature search | Retracted. The problems had existing solutions | [Bloom](https://x.com/thomasfbloom/status/1979254235075059732) |
| 2026-01 to 2026-04 | Several Erdős problems (e.g. #728, #729, #1196) | Outside users with GPT-5.x, some with Lean checks via Aristotle | Informal proof, then Lean | Mostly confirmed on erdosproblems.com | [Tao's AI-contributions wiki](https://github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erd%C5%91s-problems), [arXiv:2601.07421](https://arxiv.org/abs/2601.07421) |
| 2026-05 | Counterexample to Erdős's unit-distance conjecture | OpenAI internal model | Informal construction from algebraic number theory | Confirmed, with companion remarks by Alon, Wood and Bloom | [remarks](https://cdn.openai.com/pdf/74c24085-19b0-4534-9c90-465b8e29ad73/unit-distance-remarks.pdf) |
| 2026-08 | Ten open problems with Lean certificates | OpenAI | Lean 4, no `sorry` | Unconfirmed. Statement fidelity not yet audited | [openai/ten-proofs](https://github.com/openai/ten-proofs) |
| 2026-09-07 | Finite-time blowup with smooth forcing for IPM, 2D Boussinesq and 3D Euler | Buckmaster and Alpöge, with AI help | Analytic construction, Lean-checked | Lean-checked. Papers and peer review pending | [Tao](https://terrytao.wordpress.com/2026/09/07/finite-time-blowup-with-smooth-forcing-term-for-the-incompressible-porous-medium-boussinesq-and-incompressible-euler-equations) |
| 2026-09-08 | 3D Navier–Stokes blowup with a smooth, compactly supported force | OpenAI, multi-agent run | 166-page paper plus Lean | **Contested.** An independent paper reports the Lean proof does not match the written proof. There is also a priority dispute | [paper](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf), [arXiv:2610.08144](https://arxiv.org/abs/2610.08144), [Clay statement](https://www.claymath.org/news/navier-stokes-announcement) |
| 2026-10 | `openai/math`: about 720 manuscripts, about 42% of main results in Lean | OpenAI | Mixed | Unconfirmed as a whole. No systematic outside audit | [openai/math](https://github.com/openai/math) |
| 2026-10-26 | Kakeya/local smoothing in all dimensions, ETH disproof, 4D Yang–Mills existence | OpenAI | Partly Lean | Unconfirmed. Under expert review | [OpenAI post](https://openai.com/index/building-scientific-understanding-with-academic-communities/) |
| 2026-11-20 | **Unforced** finite-time blowup for 3D Navier–Stokes, and for 3D Euler | Alpöge, Buckmaster (and Coiculescu for Euler); first proof drafted by Anthropic models per the authors | Conditional theorem plus a numerical certificate checked by 128-bit interval arithmetic (Arb), plus a large Lean library | **Unconfirmed.** Hours old. The certificate is withheld except for a hash, and the interval check sits outside Lean | [code](https://github.com/tristanbuckmaster/navier-stokes/), [Euler paper](https://cims.nyu.edu/~tristanb/cc.pdf), [Tao](https://terrytao.wordpress.com/2026/11/20/unforced-euler-singularity-unforced-navier-stokes-singularity-and-the-generalized-riemann-hypothesis/) |
| 2026-11-20 | Proof of RH and GRH, Lean code as "main reference" | Levent Alpöge, working with Claude | Lean formalization; human-readable write-up "to come" | **Unconfirmed.** Lean experts are auditing. Early comments say the formal statement is GRH (second-hand) | [note](https://alpo.ge/remark.pdf), [Tao](https://terrytao.wordpress.com/2026/11/20/unforced-euler-singularity-unforced-navier-stokes-singularity-and-the-generalized-riemann-hypothesis/) |
| 2026-11-20 | Independent proposed proof of GRH, "all human, no AI" | Alessandro Masullo, announced by Ravi Vakil | Informal draft, reviewed for months by Brian Conrad | **Unconfirmed.** Draft unpolished, community asked to check and formalize | [Vakil's post](https://math216.wordpress.com/2026/11/20/hurried-announcement-alessandro-masullo-grh/) |

No Millennium Prize problem had been recognized as solved by the Clay Mathematics Institute at the time of writing. Clay requires publication and two years of general acceptance.

## What the pattern suggests

Three lessons recur across these episodes. Each one is a gap that open, low-cost work can help close.

1. **A compiling proof is not the same as the right theorem.** Lean guarantees that a proof establishes its formal statement. It does not guarantee that the formal statement says what the paper claims. The contested Navier–Stokes case turned on this. → [Challenge 003](../research/proposals/003-formal-statement-fidelity.md)
2. **Numerical certificates sit between computation and proof.** The newest blowup claims depend on an approximate solution that interval arithmetic turns into a rigorous bound. The same recipe can certify equilibria and stability in engineering models, but only if the certificate and checker are published and rerunnable. → [Challenge 004](../research/proposals/004-certified-numerics-pipeline.md)
3. **"Solved" often meant "already in the literature".** The two best-known public failures were problems with existing solutions. A cheap, systematic novelty check would have caught both. → [Challenge 005](../research/proposals/005-novelty-check-before-solved.md)

None of these challenges tries to prove or disprove RH or Navier–Stokes. They build the shared, open checking tools that would let many more people trust or reject such claims quickly.

## Background references

- Mathlib's statement of RH: `RiemannHypothesis` in `Mathlib/NumberTheory/LSeries/RiemannZeta`.
- Google DeepMind's [formal-conjectures](https://github.com/google-deepmind/formal-conjectures) repository of formal statements of open problems.
- Discovery of unstable singularities with high-precision PINNs and Gauss–Newton: [arXiv:2509.14185](https://arxiv.org/abs/2509.14185). These are numerical discoveries, not proofs.
- Chen–Hou computer-assisted blowup proof for axisymmetric Euler with boundary: [arXiv:2210.07191](https://arxiv.org/abs/2210.07191).
- AlphaEvolve bounds on 67 problems: [arXiv:2511.02864](https://arxiv.org/abs/2511.02864).
