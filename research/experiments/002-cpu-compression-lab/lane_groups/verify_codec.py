import numpy as np
from group_quant import *
rng=np.random.default_rng(713)
for bits in (2,3,4):
    for n in range(1,51):
        q=rng.integers(0,1<<bits,n,dtype=np.uint8)
        b=pack_codes(q,bits)
        assert len(b)==(n*bits+7)//8
        np.testing.assert_array_equal(q,unpack_codes(b,n,bits))
    w=rng.normal(size=(4,784)).astype(np.float32)
    w[3]=0
    for g in (28,56,112,784):
        a=encode_layer(w,bits,g,'maxabs')
        b=encode_layer(w,bits,g,'clip')
        assert len(a)==len(b)==LH.size+4*w.size//g+(bits*w.size+7)//8
        aa,bb=decode_layer(a),decode_layer(b)
        assert aa.shape==bb.shape==w.shape and not np.any(bb[3])
        assert np.sum((bb-w)**2)<=np.sum((aa-w)**2)
print('Variable-length bitpacking, true byte counts, zero groups and clipping objective all pass.')
