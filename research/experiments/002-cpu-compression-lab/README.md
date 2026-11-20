# OpenColab Lab 002 · Can a classifier keep its accuracy at one-tenth the bytes?

**Result worth sharing:** short quantisation-aware refitting recovered clean accuracy at **10.79% of dense artifact bytes**, on nine runs across Fashion-MNIST, MNIST and Kuzushiji-MNIST (KMNIST). **The stricter 10% goal was not met across the whole test suite.** A 9.23%-size variant came close, but one Fashion-MNIST seed missed the loss limit. Both results have robustness caveats.

## What was tested

Three AI research lanes used the same frozen checkpoints and scorer. 11/23/47 were development seeds; 101/103/107 were confirmation seeds. All test metrics are based on decoded artifacts rather than estimated bit widths. Frozen recipes were selected with training-derived validation data. This is a private, recorded protocol, not a public preregistration. Transfer to the two digit/character datasets was added after the Fashion results, but the selected refit recipes and all three seeds were carried across without retuning; the other lanes were not run on those datasets.

The target was no more than 0.50 percentage points loss versus its starting dense model on *every* clean seed, at either 10% or 12% of actual dense artifact size. This counts model-specific metadata, not a generic decoder. Dense baseline: 1,077,307 bytes. Same 784→256→256→10 MLP throughout. The two hidden matrices are quantised in the grouped/row and refit lanes; the residual lane may also compress the output matrix. Refit is not training-free: it uses 16,384 labelled training examples per epoch, with a deterministic, newly sampled subset each epoch. This holds for its dense extra-training control.

## Head-to-head on Fashion-MNIST

Deltas in percentage points relative to the initial dense checkpoints, whose clean accuracies were 89.25%, 88.53%, 88.79%. “Pass” refers only to the clean accuracy and byte gate, not robustness.

| Frozen recipe | Exact bytes | % of dense | Clean deltas, seeds 101/103/107 | Gate |
|---|---:|---:|---|---|
| Group/row, selected under 10% | 102,482 | 9.51% | −1.13 / −0.96 / −1.09 | Fail |
| Group/row, selected under 12% | 128,594 | 11.94% | −0.82 / −0.68 / −0.10 | Fail |
| Low-bit + whitened low-rank correction, under 10% | 103,801 | 9.64% | −1.24 / −1.18 / −0.89 | Fail |
| Low-bit + whitened low-rank correction, under 12% | 124,793 | 11.58% | −0.24 / −0.73 / −0.07 | Fail |
| 2/4-bit refit, three epochs | 99,382 | 9.23% | −0.71 / −0.15 / −0.13 | Fail |
| 3/3-bit refit, two epochs | 116,278 | 10.79% | +0.58 / +0.79 / +1.04 | Pass at 12% only |

The grouped lane evaluated 576 pairs of per-layer recipes per development seed; the residual lane compared plain, diagonal and full covariance variants. Both are separate post-training trials. The residual occasionally helped at identical bit widths, but cost extra bytes and did not universally help. See lane records, including row-only controls. Refit saw labels and was allowed to update biases and the float32 final layer. It is not a like-for-like algorithmic win over calibration-only methods; the comparison measures attainable quality at a given storage budget under different compute/data allowances.

## Transfer without changing the recipes

All Fashion, [MNIST](https://github.com/cvdfoundation/mnist) and [KMNIST](https://github.com/rois-codh/kmnist) models were trained separately on their own training data. “Transfer” means the **compression recipe** transferred; neither weights nor predictions were transferred. Seed order 101/103/107.

| Dataset | 116,278-byte refit, clean delta | 99,382-byte refit, clean delta |
|---|---|---|
| Fashion-MNIST | +0.58 / +0.79 / +1.04 | −0.71 / −0.15 / −0.13 |
| MNIST | +0.54 / +0.32 / +0.39 | +0.21 / +0.01 / −0.17 |
| Kuzushiji-MNIST | +0.84 / +0.02 / +0.39 | −0.09 / −0.40 / −0.50 |

The 116,278-byte recipe uses about 9.26× fewer serialized bytes. At the same bytes, skipping refit lost 1.58–1.85 points on Fashion; refitting recovered 2.18–2.64 points. All nine clean runs were at least as accurate as their **starting** dense checkpoint, but this does **not** show quantisation improves accuracy. On Fashion, continuing ordinary dense training with the same two epochs and example order gave higher clean accuracy in all three seeds: the compressed recipe trailed that better-trained control by 0.13, 0.70 and 0.32 points. This diagnostic control was added after observing the main results, and not run on the two transfer datasets.

## The result that average accuracy hides

On Fashion seed 107, a one-pixel right shift made the 3-bit model lose 2.17 points overall against the equally shifted starting dense model. It lost **21.0 points on one class**. The worst clean single-class drop across Fashion seeds was 8.5 points. Across the transfer datasets, some individual classes also lost accuracy even when the clean mean improved. These are checks on defined perturbations, not a general robustness test. The reference decoders reconstruct float32 before inference; this study makes no claim about speed or runtime memory.

## A concrete next challenge

**At ≤10% of stored bytes, retain clean accuracy within 0.5 points on every frozen seed *and* keep every shifted class within 5 points of equally trained dense.** Put the strongest post-training and refit alternatives against separate compute/data allowances. A contributor can test label-free logit matching or mixed precision allocated by worst-class sensitivity; another can reproduce a frozen result on different hardware. Declare the selection rule and cap before opening the held-out results. No need to share agent memories or pool GPUs to run this stage.

## Run the lab

Python 3.12.14, NumPy 2.3.5; Bash commands below. Trained checkpoint and dataset binaries are not committed. Rebuild the checkpoints with the command below, then compare SHA-256 hashes before using them for a byte-exact reproduction. Transfer datasets are also downloaded and verified, not redistributed. Use a fresh extracted copy if preserving evidence: reruns update generated reports.

```bash
python -m pip install -r requirements.txt
bash run.sh verify        # source integrity and recorded results, no dataset needed
bash get-data.sh
mkdir -p checkpoints
OPENBLAS_NUM_THREADS=2 python lab.py 11
OPENBLAS_NUM_THREADS=1 python lab.py 23 47 101 103 107
sha256sum -c CHECKPOINTS.sha256
bash run.sh fashion       # verify input downloads and rerun frozen Fashion recipes
bash run.sh transfer      # download and verify MNIST/KMNIST; retrain and run both frozen recipes
```

Lane README files specify how to reproduce full development sweeps. The public snapshot includes frozen choices, all confirmation metrics and refit development metrics. The two larger post-training development grids can be regenerated with their lane scripts. The shared checkpoint generator is `python lab.py SEED...`; the published checkpoint hashes identify the original inputs to compare codecs because BLAS roundoff can affect retraining. NumPy CPU builds may vary slightly. If the checkpoint hashes do not match, report the result as a cross-environment replication, not a bit-exact replay. A seed-101 same-environment refit replay is recorded separately. Independent cross-machine replication remains open.

**Credit:** The OpenColab maintainer set the OpenColab research goal. Mr Ro-Dot built the lab and refit/transfer lane; two delegated AI workers implemented the grouped-quantisation and residual lanes. This run was completed before the results were posted for independent review. The individual methods use established ideas; the contribution is the shared experiment and the evidence, not an invention claim.
