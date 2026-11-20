# Packed quantization plus low-rank residual (CPU exploratory lane)

**Neither cap passed** the clean ≤0.50 percentage-point loss on every confirmation seed. Compared with deleting the residual at the **same bit mix and quantizer**, the residual materially helped some seeds but did not win universally. The no-residual control uses fewer bytes and is not an exact-size control. The independently selected plain all-3-bit recipe offers another budget comparison.

## Method

For each frozen dense checkpoint, quantize each row to four or eight affine levels; use a fixed clipping/re-fit grid. Search plain, diagonal activation-aware and full activation-aware residual fits. The latter two fit the quantizer with mean-square input-channel weighting. Full whitening fits the residual via truncated SVD of E L, where E is weight error and L is the Cholesky factor of a ridge-regularized activation Gram. Serialize both residual factors as FP16. Training calibration uses the first 2,048 examples of the shared training split and dense activations only; no label-based refit. Rank and bit width vary by layer. Choose one recipe per cap across all three development seeds using the shared protocol's max-min dense-relative criterion, with mean, bytes and deterministic order as tie-breaks. Both frozen hybrid winners use full whitening.

The OR01 byte stream includes magic, layer length headers, per-layer bit/rank tags, FP32 row zero offsets and scales, contiguous little-endian packed codes, FP16 residual factors, and FP32 biases. Architecture and decoder are fixed by this benchmark and not charged as artifact bytes. Evaluation reconstructs dense FP32 matrices. This is evidence about serialized model storage only; it does not imply an inference speed or memory reduction.

## Confirmation, clean accuracy (absolute %, dense-relative delta in pp)

| Recipe | Bytes | Seed 101 | Seed 103 | Seed 107 |
|---|---:|---:|---:|---:|
| Dense | 1,077,307 | 89.25 | 88.53 | 88.79 |
| ≤10% hybrid (9.6352%) | 103,801 | 88.01 (−1.24) | 87.35 (−1.18) | 87.90 (−0.89) |
| Same quantizer/mix without residual | 82,001 | 84.85 (−4.40) | 84.97 (−3.56) | 86.88 (−1.91) |
| ≤12% hybrid (11.5838%) | 124,793 | 89.01 (−0.24) | 87.80 (−0.73) | 88.72 (−0.07) |
| Same quantizer/mix without residual | 107,089 | 87.41 (−1.84) | 87.54 (−0.99) | 89.03 (+0.24) |
| Selected plain 3-bit, no residual | 107,089 | 88.07 (−1.18) | 87.59 (−0.94) | 88.61 (−0.18) |

Hybrid robustness deltas versus dense: at ≤10%, right-shift −1.45/−2.43/−1.83 pp and Gaussian noise −2.05/−2.00/−1.44 pp. At ≤12%, shift −0.85/−1.43/−1.12 pp and noise −1.09/−0.80/−0.74 pp. Full per-class metrics and SHA-256 hashes are in the confirmation JSON. Confirmation seeds were new, but original test examples were reused. This is a small Fashion-MNIST MLP, not a result on LLMs. No retuning followed confirmation.

## Reproduce

From this directory with the original benchmark and lab dependencies in place:

```sh
export OPENBLAS_NUM_THREADS=2
python -c 'from residual import selftest;selftest()'
python residual.py > run.log
python summarize.py > summary.log
cmp dev-summary.json frozen.json
sha256sum -c freeze.sha256
python confirm.py
```

The low-precision-plus-low-rank family is established prior art: [CALDERA](https://arxiv.org/abs/2405.18886). This lane is a small independent ablation, not an implementation or replication of CALDERA.
