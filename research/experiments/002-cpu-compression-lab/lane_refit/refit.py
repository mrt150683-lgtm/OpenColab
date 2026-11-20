"""Weight-only packed affine quantization, optional straight-through refitting."""
import sys,struct,hashlib,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import lab,baseline as b
import numpy as np
CFG=((2,2),(2,3),(2,4),(3,2),(3,3))
def params(w,bits):
    top=(1<<bits)-1
    scale=np.maximum(np.max(np.abs(w),axis=1,keepdims=True),1e-10)*np.float32(2/top)
    offset=scale*np.float32(-top/2)
    ids=np.rint((w-offset)/scale).clip(0,top).astype(np.uint8)
    return scale.astype('<f4'),offset.astype('<f4'),ids
def payload(q,bits):
    s,o,ids=q
    packed=np.packbits((ids.ravel()[:,None]>>np.arange(bits,dtype=np.uint8))&1,bitorder='little')
    return s.tobytes()+o.tobytes()+packed.tobytes()
def inverse(blob,shape,bits):
    m,n=shape
    s=np.frombuffer(blob[:4*m],'<f4')[:,None]
    o=np.frombuffer(blob[4*m:8*m],'<f4')[:,None]
    raw=np.frombuffer(blob[8*m:],np.uint8)
    assert len(raw)==(m*n*bits+7)//8
    flat=np.unpackbits(raw,bitorder='little',count=m*n*bits).reshape(-1,bits)
    ids=flat@(1<<np.arange(bits,dtype=np.uint8))
    return ids.reshape(shape)*s+o
def make(p,config):
    blobs=[payload(params(p[i],bits),bits) for i,bits in enumerate(config)]
    return struct.pack('<4sBBII',b'OCQ2',*config,*(len(z) for z in blobs))+b''.join(blobs)+b.f32(p[2])+b''.join(map(b.f32,p[3:]))
def decode(blob):
    magic,x,y,n,m=struct.unpack('<4sBBII',blob[:14]); assert magic==b'OCQ2'
    w=[inverse(blob[14:14+n],b.SH[0],x),inverse(blob[14+n:14+n+m],b.SH[1],y)]
    rest=blob[14+n+m:]
    w.append(b.read(rest[:10240],b.SH[2])); rest=rest[10240:]
    bias=[]
    for count,_ in b.SH:
        bias.append(b.read(rest[:count*4],(count,)));rest=rest[count*4:]
    assert not rest
    return w+bias
def fit(p,config,x,y,seed,epochs=3):
    p=[a.copy() for a in p]
    # Frozen row scales avoid changing the representation while its float shadows learn.
    q=[params(p[i],bit)[:2] for i,bit in enumerate(config)]
    def freeze(a):
        ans=list(a)
        for i,bit in enumerate(config):
            s,o=q[i];ids=np.rint((a[i]-o)/s).clip(0,(1<<bit)-1)
            ans[i]=ids*s+o
        return ans
    def artifact():
        blocks=[]
        for i,bit in enumerate(config):
            s,o=q[i]
            ids=np.rint((p[i]-o)/s).clip(0,(1<<bit)-1).astype(np.uint8)
            blocks.append(payload((s,o,ids),bit))
        blob=struct.pack('<4sBBII',b'OCQ2',*config,*(len(z) for z in blocks))+b''.join(blocks)+b.f32(p[2])+b''.join(map(b.f32,p[3:]))
        for a,z in zip(decode(blob),freeze(p)):np.testing.assert_array_equal(a,z)
        return blob
    yield (0,artifact())
    rng=np.random.default_rng(seed+9000)
    mom=[np.zeros_like(a) for a in p]
    var=[np.zeros_like(a) for a in p]
    steps=0
    for ep in range(1,epochs+1):
        ix=rng.permutation(len(x))[:16384]
        for start in range(0,len(ix),256):
            k=ix[start:start+256];a=x[k]
            w0,w1,w2,b0,b1,b2=freeze(p)
            u=np.maximum(a@w0.T+b0,0)
            z=np.maximum(u@w1.T+b1,0)
            o=z@w2.T+b2
            o=np.exp(o-o.max(1,keepdims=True));o/=o.sum(1,keepdims=True)
            o[np.arange(len(k)),y[k]]-=1;o/=len(k)
            g2=o@w2*(z>0);g1=g2@w1*(u>0)
            steps+=1
            for aa,mm,vv,g in zip(p,mom,var,[g1.T@a,g2.T@u,o.T@z,g1.sum(0),g2.sum(0),o.sum(0)]):
                mm*=.9;mm+=.1*g;vv*=.999;vv+=.001*g*g
                aa-= (.0003/(1-.9**steps))*mm/(np.sqrt(vv/(1-.999**steps))+1e-8)
        yield (ep,artifact())
def metrics(blob,x,y):
    p=decode(blob);pred=b.pred(x,p).argmax(axis=1); hit=pred==y
    return dict(accuracy=float(hit.mean()),worst_class=float(min(hit[y==c].mean() for c in range(10))),
                per_class=[float(hit[y==c].mean()) for c in range(10)],bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
def go(mode,seeds):
    x,y,v,w=lab.data()
    out={}
    for seed in seeds:
        p=lab.load(seed);out[seed]={}
        for cfg in CFG:
            if len(make(p,cfg))>0.12*len(lab.dense(p)):continue
            for ep,blob in fit(p,cfg,x,y,seed):
                tag=f"{cfg[0]}{cfg[1]}-e{ep}"
                out[seed][tag]=metrics(blob,v,w)
                if mode=="dev-and-save": (Path(__file__).parent/f'{seed}-{tag}.ocq').write_bytes(blob)
        print(seed, sorted(out[seed].items(),key=lambda e:-e[1]['accuracy'])[:2],flush=True)
        (Path(__file__).parent/'dev.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__': go(sys.argv[1],list(map(int,sys.argv[2:])))
