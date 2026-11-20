"""Shared checkpoint and data contract. Confirmation test stays unused until freeze."""
import hashlib,json,sys,os
from pathlib import Path
import numpy as np
import baseline as b
ROOT=Path(__file__).resolve().parent
FILES=('train-images-idx3-ubyte.gz','train-labels-idx1-ubyte.gz','t10k-images-idx3-ubyte.gz','t10k-labels-idx1-ubyte.gz')
EXPECTED=('3aede38d61863908ad78613f6a32ed271626dd12800ba2636569512369268a84','a04f17134ac03560a47e3764e11b92fc97de4d1bfaf8ba1a3aa29af54cc90845','346e55b948d973a97e58d2351dde16a484bd415d4595297633bb08f03db6a073','67da17c76eaffca5446c3361aaab5c3cd6d1c2608764d35dfb1850b086bf8dd5')
DEV=(11,23,47)
CONFIRM=(101,103,107)
def data(test=False):
    loaded=[b.idx(f) for f in FILES[:4 if test else 2]]
    assert tuple(h for _,h in loaded)==EXPECTED[:len(loaded)]
    x,y=(z for z,_ in loaded[:2])
    t=np.random.default_rng(20261120).permutation(len(x))
    v,train=t[:5000],t[5000:]
    a=(x[train],y[train],x[v],y[v])
    return a+tuple(z for z,_ in loaded[2:]) if test else a
def load(seed):
    return b.unpack((ROOT/'checkpoints'/f'{seed}.oc01').read_bytes())
def dense(p):
    return b.pack(*(b'\0'+b.f32(w) for w in p[:3]),b''.join(map(b.f32,p[3:])))
def train(seed):
    x,y,_,_=data()
    payload=dense(b.train(x,y,seed))
    out=ROOT/'checkpoints'/f'{seed}.oc01'; out.parent.mkdir(exist_ok=True); tmp=out.with_suffix('.tmp')
    tmp.write_bytes(payload);tmp.replace(out)
    print(seed,len(payload),hashlib.sha256(payload).hexdigest(),flush=True)
if __name__=='__main__':
    for s in map(int,sys.argv[1:]):
        train(s)
