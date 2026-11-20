import sys,struct,itertools,json
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import baseline as b
def packcodes(q,t):
 return np.packbits(((q.ravel()[:,None]>>np.arange(t))&1).astype(np.uint8).ravel(),bitorder='little').tobytes()
def codes(blob,t,m,n):
 x=np.unpackbits(np.frombuffer(blob,np.uint8),bitorder='little',count=m*n*t)
 return (x.reshape(-1,t)@(1<<np.arange(t))).astype(np.float32).reshape(m,n)
def affine(w,t,x):
 M=(1<<t)-1
 # Select clipping by weighted row MSE on training-calibration RMS, then fit affine levels.
 wt=np.ones((1,w.shape[1]),np.float32) if x is None else np.mean(x*x,axis=0,keepdims=True)+1e-6
 lo=np.min(w,axis=1,keepdims=True); hi=np.max(w,axis=1,keepdims=True); mid=(lo+hi)*.5
 best=np.full_like(lo,np.inf); bo=np.zeros_like(lo); bs=np.ones_like(lo); bq=np.zeros_like(w,dtype=np.uint8)
 for clip in (.55,.7,.85,1.):
  o=mid+(lo-mid)*clip; s=np.maximum((hi-lo)*clip/M,1e-12)
  for _ in range(5):
   q=np.clip(np.rint((w-o)/s),0,M)
   qm=(wt*q).sum(1,keepdims=True)/wt.sum(); wm=(wt*w).sum(1,keepdims=True)/wt.sum()
   cq=q-qm
   s=np.maximum((wt*cq*(w-wm)).sum(1,keepdims=True)/np.maximum((wt*cq*cq).sum(1,keepdims=True),1e-12),1e-12); o=wm-s*qm
  q=np.clip(np.rint((w-o)/s),0,M).astype(np.uint8)
  err=(wt*(w-o-s*q)**2).sum(1,keepdims=True)
  use=err<best; best=np.where(use,err,best); bo=np.where(use,o,bo); bs=np.where(use,s,bs); bq=np.where(use,q,bq)
 return bo,bs,bq
def choices(w,x,t,kind,rs):
 m,n=w.shape
 o,s,q=affine(w,t,x if kind!='plain' else None)
 head=b.f32(o)+b.f32(s)+packcodes(q,t)
 e=w-o-s*q
 if kind=='full':
  c=x.T@x/len(x); c=c+np.eye(n,dtype=c.dtype)*(1e-3*np.trace(c)/n+1e-8)
  l=np.linalg.cholesky(c)
  u,sv,vt=np.linalg.svd(e@l,full_matrices=False)
  v=np.linalg.solve(l.T,vt[:max(rs)].T).T
 else:
  d=np.sqrt(np.mean(x*x,axis=0)+1e-6) if kind=='diag' else np.ones(n,np.float32)
  u,sv,vt=np.linalg.svd(e*d,full_matrices=False); v=vt[:max(rs)]/d
 return {r:struct.pack('<BH',t,r)+head+(u[:,:r]*sv[:r]).astype('<f2').tobytes()+v[:r].astype('<f2').tobytes() for r in rs}
def decode(blob,shape):
 m,n=shape;t,r=struct.unpack('<BH',blob[:3]); assert t in (2,3) and r<=min(m,n)
 end=3+8*m+(m*n*t+7)//8
 assert len(blob)==end+2*r*(m+n)
 o=b.read(blob[3:3+4*m],(m,1)); s=b.read(blob[3+4*m:3+8*m],(m,1))
 a=np.frombuffer(blob[end:end+2*m*r],'<f2').astype(np.float32).reshape(m,r)
 v=np.frombuffer(blob[end+2*m*r:],'<f2').astype(np.float32).reshape(r,n)
 return o+s*codes(blob[3+8*m:end],t,m,n)+a@v
def pack(xs,bias):
 return b'OR01'+struct.pack('<III',*(len(x) for x in xs))+b''.join(xs)+bias
def unpack(blob):
 assert blob[:4]==b'OR01'
 i=16; mats=[]
 for n,shape in zip(struct.unpack('<III',blob[4:16]),b.SH):
  mats.append(decode(blob[i:i+n],shape));i+=n
 for m,_ in b.SH:
  mats.append(b.read(blob[i:i+4*m],(m,)));i+=4*m
 assert i==len(blob)
 return mats
def metrics(o,y):
 z=o-o.max(1,keepdims=True)
 return {'accuracy':float((o.argmax(1)==y).mean()),'nll':float(np.mean(np.log(np.exp(z).sum(1))-z[np.arange(len(y)),y]))}
def eval_seed(p,cal,x,y,seed):
 xs=[cal]
 for i in range(2): xs.append(np.maximum(xs[-1]@p[i].T+p[3+i],0))
 bias=b''.join(map(b.f32,p[3:])); dense=len(b.pack(*[b'\0'+b.f32(w) for w in p[:3]],bias))
 ds=[]
 # Frozen finite development lattice. Tied weighting objective across layers, but independent bits/ranks.
 for kind in ('plain','diag','full'):
  pools=[]
  for i,(w,xx) in enumerate(zip(p[:3],xs)):
   pool={}
   for t in (2,3):
    for r,code in choices(w,xx,t,kind,[0,2,4,8] if i<2 else [0,2,4]).items(): pool[t,r]=(code,decode(code,b.SH[i]))
   pools.append(pool)
  for k0,(z0,w0) in pools[0].items():
   a=np.maximum(x@w0.T+p[3],0)
   for k1,(z1,w1) in pools[1].items():
    c=np.maximum(a@w1.T+p[4],0)
    for k2,(z2,w2) in pools[2].items():
     size=16+len(z0)+len(z1)+len(z2)+len(bias)
     if size>dense*12//100:continue
     row=dict(kind=kind,knobs=[k0,k1,k2],size=size,ratio=size/dense,**metrics(c@w2.T+p[5],y))
     ds.append(row)
 return {'seed':seed,'dense_bytes':dense,'dense_dev':metrics(b.pred(x,p),y),'rows':ds}
if __name__=='__main__':
 sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
 import lab
 a,_,x,y=lab.data()
 for seed in lab.DEV:
  p=lab.load(seed)
  result=eval_seed(p,a[:2048],x,y,seed)
  Path(f'dev-{seed}.json').write_text(json.dumps(result,indent=2))
  for budget in (.10,.12):
   print(seed,budget,sorted([r for r in result['rows'] if r['ratio']<=budget],key=lambda r:(-r['accuracy'],r['nll'],r['size']))[0],flush=True)

def build(p,cal,kind,knobs):
 """Recreate fitted artifact from a frozen recipe using training-only activations."""
 xs=[cal]
 for i in range(2): xs.append(np.maximum(xs[-1]@p[i].T+p[3+i],0))
 parts=[choices(w,xx,int(t),kind,[int(r)])[int(r)] for w,xx,(t,r) in zip(p[:3],xs,knobs,strict=True)]
 return pack(parts,b''.join(map(b.f32,p[3:])))

def selftest():
 rng=np.random.default_rng(154)
 for t in (2,3):
  q=rng.integers(0,2**t,(5,19),dtype=np.uint8)
  packed=packcodes(q,t)
  assert len(packed)==(q.size*t+7)//8
  np.testing.assert_array_equal(codes(packed,t,*q.shape),q)
 p=[rng.normal(size=s).astype('float32') for s in b.SH]+[rng.normal(size=m).astype('float32') for m,_ in b.SH]
 x=rng.normal(size=(64,784)).astype('float32')
 for kind in ('plain','diag','full'):
  blob=build(p,x,kind,[(2,2),(3,2),(2,0)])
  out=unpack(blob)
  assert [a.shape for a in out]==[a.shape for a in p]
  assert all(np.isfinite(a).all() for a in out)
  assert all(np.array_equal(a,c) for a,c in zip(p[3:],out[3:]))
  assert len(blob)==16+sum(3+8*m+(m*n*t+7)//8+2*r*(m+n)+4*m for (m,n),(t,r) in zip(b.SH,[(2,2),(3,2),(2,0)]))
 print('bitstream, serialization budget, and finite model roundtrips passed')
