"""Post-Fashion transfer test: run frozen refit recipes unchanged, with no model selection."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
import lab,baseline as b,evaluate
from lane_refit.refit import fit,decode
dataset=sys.argv[1]
assert dataset in ('mnist-data','transfer-data')
seed=int(sys.argv[2]); assert seed in lab.CONFIRM
base=Path(__file__).resolve().parent
frozen=(base/'lane_refit/frozen.json').read_bytes()
assert hashlib.sha256(frozen).hexdigest()=='4dea49f0cefa86283c08974528d3f6b234bcb4026d6df5697acdeee86aa3d834'
b.P=base/dataset
# baseline.idx expects a data/ child. Point to the dataset via a local layout.
def read(f):
    import gzip,struct
    data=(b.P/f).read_bytes()
    u=gzip.decompress(data)
    magic,n=struct.unpack('>II',u[:8])
    if magic==2051:
        assert struct.unpack('>II',u[8:16])==(28,28)
        x=np.frombuffer(u[16:],np.uint8).reshape(n,784).astype(np.float32)/255
    else:
        assert magic==2049
        x=np.frombuffer(u[8:],np.uint8)
    assert len(x)==n
    return x,hashlib.sha256(data).hexdigest()
(x,y,xt,yt),h=zip(*(read(f) for f in lab.FILES))
assert (len(x),len(y),len(xt),len(yt))==(60000,60000,10000,10000)
s=np.random.default_rng(20261120).permutation(len(x))[5000:]
x,y=x[s],y[s]; ds=evaluate.cases(xt)
p=b.train(x,y,seed); blob=lab.dense(p)
out={'dataset':dataset,'dataset_hashes':dict(zip(lab.FILES,h)),'seed':seed,
     'recipes_sha256':hashlib.sha256(frozen).hexdigest(),
     'dense':evaluate.record(blob,b.unpack(blob),ds,yt)}
for cap,q in json.loads(frozen).items():
    k=q['recipe'];cfg=tuple(map(int,k[:2]));epochs=int(k.split('e')[1])
    for ep,blob in fit(p,cfg,x,y,seed,epochs):
        if ep in (0,epochs):
            out[f'cap{cap}-{k[:2]}-e{ep}']=evaluate.record(blob,decode(blob),ds,yt)
(base/f'{dataset}-{seed}.json').write_text(json.dumps(out,indent=2))
print(dataset,seed,{k:v['metrics']['clean']['accuracy'] for k,v in out.items() if isinstance(v,dict) and 'metrics' in v})
