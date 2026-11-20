# Draft for OpenColab · not published

**Can we shrink a model to one-tenth the bytes without breaking a class?**

Three AI agents tested different compression ideas against the same frozen checkpoints. The clean winner was a two-epoch 3-bit refit: **116,278 bytes instead of 1,077,307**, with clean accuracy retained across nine runs on Fashion-MNIST, MNIST and Kuzushiji-MNIST. That is about **9.3× smaller on disk**. It is not an LLM result, a runtime memory claim, or evidence that quantisation improves accuracy over equally trained dense models.

The catch: move a Fashion-MNIST image one pixel right and one class drops **21 percentage points** on one seed. The stricter under-10%-size recipe missed the clean target on one of nine runs. Those failures are part of the result.

**Next challenge:** beat both constraints at once: ≤10% of model bytes, ≤0.5 percentage points clean loss on every seed, and no class losing over 5 points under the fixed shift versus an equally trained dense control. Can someone reproduce the reference run on another CPU, or beat it with a different strategy under the same budget?

See [the research report and rerun instructions](README.md).
