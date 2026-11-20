# Group-quantization lane
From this directory, with shared lab scripts and canonical data in the parent directory:
```sh
OPENBLAS_NUM_THREADS=2 python verify_codec.py
OPENBLAS_NUM_THREADS=2 python dev.py
python freeze.py
OPENBLAS_NUM_THREADS=2 python confirm.py
```
Dev only reads the training-derived validation split. Freeze uses worst dev seed delta, then mean delta, bytes, recipe string. The row-only comparator is separately selected by the same rule under the cap. After freeze, confirm on shared new checkpoints and fixed clean / shifted / noisy examples. One scale per group; scale chosen either from max absolute value or from a grid of relative clips by training-weight reconstruction MSE (not label-tuned). Quantized symmetric levels are odd integers scaled by group step, so there are 4, 8 or 16 usable levels and no zero level; zero groups are still exact. The final classifier and all biases remain float32. Bytes include every field of the uncompressed GQM1/GQL1 containers. Decode is reference-only and reconstructs float matrices; no speed or runtime-memory inference.

Both globally selected recipes failed confirmation. At 9.51% bytes, clean degradation exceeded 0.5 points for all three confirmation seeds. At 11.94%, the dev gate passed but confirmation missed on two of three seeds. This is evidence against these selected recipes under this setup, not against all grouping or clipping schemes. The row-only diagnostic was sometimes stronger on held-out clean data, but does not pass the all-seed gate either. Group size and bit allocation may interact; this lane does not establish a causal benefit for either.
