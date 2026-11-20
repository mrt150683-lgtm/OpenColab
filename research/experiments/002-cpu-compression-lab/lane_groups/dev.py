"""Development-only grid. Does not load Fashion-MNIST test files."""
import hashlib,itertools,json,os,sys
from pathlib import Path
import numpy as np
from group_quant import decode_model,encode_layer,decode_layer
import struct
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent))
import baseline as b
C=H.parent/'checkpoints'
SEEDS=(11,23,47)

def options(g):
    return [dict(bits=q,group=n,fit=f) for q,n,f in itertools.product((2,3,4),g,('maxabs','clip'))]

def run(file,x,y):
    dense=file.read_bytes()
    p=b.unpack(dense)
    x=x.astype(np.float32)
    o1=options(('row',28,56,112))
    o2=options(('row',16,32,64))
    a=[encode_layer(p[0],**c) for c in o1]
    z=[encode_layer(p[1],**c) for c in o2]
    fixed=b''.join(np.asarray(w,'<f4').tobytes() for w in p[2:])
    z2=[decode_layer(blob) for blob in z]
    rows=[]
    for cc,blob in zip(o1,a):
        z1=np.maximum(x@decode_layer(blob).T+p[3],0)
        for dd,bb,ww in zip(o2,z,z2):
            data=struct.pack('<4sII',b'GQM1',len(blob),len(bb))+blob+bb+fixed
            score=np.mean((np.maximum(z1@ww.T+p[4],0)@p[2].T+p[5]).argmax(1)==y)
            rows.append(dict(config=[cc,dd],bytes=len(data),ratio=len(data)/len(dense),accuracy=float(score),sha256=b.sha(data)))
    # Prove the optimized grid evaluates the real decoded artifact.
    np.testing.assert_array_equal(b.pred(x,decode_model(data)).argmax(1),
        (np.maximum(z1@ww.T+p[4],0)@p[2].T+p[5]).argmax(1))
    return dict(dense_sha256=b.sha(dense),dense_accuracy=float(np.mean(b.pred(x,p).argmax(1)==y)),trials=rows)

def main():
    x,ix=b.idx('train-images-idx3-ubyte.gz'); y,iy=b.idx('train-labels-idx1-ubyte.gz')
    perm=np.random.default_rng(20261120).permutation(len(x)).astype('<i8')
    iv=perm[:5000]
    for seed in map(int,sys.argv[1:] or SEEDS):
        assert seed in SEEDS
        path=C/f'{seed}.oc01'
        report=run(path,x[iv],y[iv]); report.update(seed=seed,split_sha256=b.sha(perm.tobytes()),dataset_hashes=[ix,iy])
        (H/f'dev-{seed}.json').write_text(json.dumps(report,indent=2)+'\n')
        print(seed,report['dense_accuracy'],len(report['trials']),flush=True)
if __name__=='__main__':main()
