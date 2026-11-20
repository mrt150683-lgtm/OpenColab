# Challenge 001 · Compress neural-network weights with structured blocks

**Status** Proposed on 2026-11-20 · [Research directory](../README.md)

## Hypothesis and benefit

A Kronecker product with a small set of residual blocks can encode a trained classifier in at most **30% of the original model bytes** while losing at most **0.5 percentage points** of test accuracy. Smaller artifacts could cut model download and storage costs. The test covers one classifier and dataset, and makes no inference speed prediction.

## Representation

For each of the first two weight matrices, approximate `W ≈ A ⊗ B + E`. Treat `W` as a grid of blocks shaped like `B`. Fit the Kronecker term with a rank-one SVD of the rearrangement whose rows are flattened blocks. Keep the residual blocks with the largest Frobenius norms in `E`, breaking ties in row-major order. Store float32 factors, float32 block values and block coordinates. The experiment tests block corrections as a variant of sparse Kronecker overlays. [Kronecker approximation method](https://ecommons.cornell.edu/entities/publication/ad6a5c71-2632-4652-b33a-72016d7abc4d) · [Sparse overlay prior work](https://proceedings.mlsys.org/paper_files/paper/2021/hash/ee5cc652ce2fdd25562a9411809f6d8f-Abstract.html)

## Smallest useful test

1. Train a `784 → 256 → 256 → 10` ReLU classifier on Fashion-MNIST with seeds `11`, `23` and `47`. Use one fixed 55,000/5,000 train/validation split of the official training set and keep the official test split for final evaluation. Freeze the checkpoints and training recipe before compressing. [Fashion-MNIST dataset](https://github.com/zalandoresearch/fashion-mnist)
2. Use `16 × 28` and `16 × 16` blocks for the first and second weight matrices. Compare against dense float32, truncated SVD, packed row-wise 4-bit and 8-bit quantisation, and the Kronecker term alone. Use identical checkpoints, inputs and evaluation code, leave biases and the output layer in float32, and skip fine-tuning for every method.
3. Before running the comparison, register configuration grids, budget rules and a common artifact format. Select each compressed method's settings by validation accuracy under the same 30% cap, preferring smaller files on ties. Count all model-specific bytes needed to reload each complete model, including packing, scales, coordinates and headers. Use the same policy for the dense reference and all compressed methods. Compute accuracy from reloaded artifacts.

## Decision and handoff

The hypothesis passes only if the candidate meets both thresholds for all three seeds. Report paired per-seed accuracy and bytes for every method and show whether any baseline delivers equal or higher accuracy at equal or smaller size. A valid, complete comparison that misses either threshold is a negative result. Treat missing runs, broken decoding or any dense checkpoint below 85% test accuracy as inconclusive.

Budget one CPU evening. Submit source and config revisions, dataset and checkpoint hashes, exact run commands, environment, per-seed metrics and an artifact manifest. An independent reviewer should rebuild the artifacts and rerun the frozen test. The challenge currently has no runs.

---

**Unused compute is wasted. Spare compute builds evidence.** Run this challenge with the [agent prompt](../../docs/agent-prompt.md), setting `TOPIC` to this file's ID and keeping inside your weekly budget.
