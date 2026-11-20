import gzip, hashlib, itertools, json, sys, time, struct
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b).hexdigest()
def idx(f):
 p=P/'data'/f
 b=p.read_bytes()
 raw=gzip.decompress(b)
 magic,n=struct.unpack('>II',raw[:8])
 if magic==2051:
  h,w=struct.unpack('>II',raw[8:16])
  assert (h,w)==(28,28)
  out=np.frombuffer(raw[16:],np.uint8).reshape(n,784).astype(np.float32)/255
 else:
  assert magic==2049
  out=np.frombuffer(raw[8:],np.uint8)
 assert len(out)==n
 return out,sha(b)
def pred(x,p):
 for w,b in zip(p[:3],p[3:]):
  x=x@w.T+b
  if w.shape[0]!=10: x=np.maximum(x,0)
 return x
def train(x,y,seed):
 rng=np.random.default_rng(seed)
 dims=[784,256,256,10]
 p=[(rng.standard_normal((b,a),dtype=np.float32)*np.float32(np.sqrt(2/a))) for a,b in zip(dims,dims[1:])]+[np.zeros(a,np.float32) for a in dims[1:]]
 m=[np.zeros_like(z) for z in p]
 v=[np.zeros_like(z) for z in p]
 t=0
 for epoch in range(20):
  order=rng.permutation(len(x))
  for j in range(0,len(x),128):
   ix=order[j:j+128]; a=x[ix]
   u=np.maximum(a@p[0].T+p[3],0); z=np.maximum(u@p[1].T+p[4],0)
   o=z@p[2].T+p[5]; o=np.exp(o-o.max(1,keepdims=True)); o/=o.sum(1,keepdims=True)
   o[np.arange(len(ix)),y[ix]]-=1; o/=len(ix)
   g2=o@p[2]*(z>0); g1=g2@p[1]*(u>0)
   grads=[g1.T@a,g2.T@u,o.T@z,g1.sum(0),g2.sum(0),o.sum(0)]
   t+=1
   for a1,m1,v1,g in zip(p,m,v,grads):
    m1*=.9; m1+=.1*g
    v1*=.999; v1+=.001*g*g
    a1-= (.001/(1-.9**t))*m1/(np.sqrt(v1/(1-.999**t))+1e-8)
  print(f'seed {seed} epoch {epoch+1}',file=sys.stderr,flush=True)
 return p
def f32(a): return np.asarray(a,dtype='<f4').tobytes()
def read(b,shape): return np.frombuffer(b,'<f4').reshape(shape)
def layer(b,shape):
 m,n=shape; t=b[0]; b=b[1:]
 if t==0:return read(b,shape)
 if t==1:
  k,=struct.unpack('<H',b[:2]); b=b[2:]
  return read(b[:4*m*k],(m,k))@read(b[4*m*k:],(k,n))
 if t in (4,8):
  s=read(b[:4*m],(m,1)); c=np.frombuffer(b[4*m:],np.uint8)
  if t==4: c=(np.stack([c&15,c>>4],1).reshape(-1).astype('int8')-8)
  else: c=c.view(np.int8)
  return c.reshape(shape)*s
 assert t==2
 h,w,k=struct.unpack('<HHH',b[:6]); b=b[6:]; r,c=m//h,n//w
 a=read(b[:4*r*c],(r,c)); b=b[4*r*c:]
 bb=read(b[:4*h*w],(h,w)); b=b[4*h*w:]
 out=np.kron(a,bb)
 ids=np.frombuffer(b[:2*k],'<u2')
 vals=read(b[2*k:],(k,h,w))
 for i,tile in zip(ids,vals):
  i,j=divmod(int(i),c); out[i*h:(i+1)*h,j*w:(j+1)*w]+=tile
 return out
def choices(w,x,tile):
 m,n=w.shape; h,l=tile; r,c=m//h,n//l
 mat=w.reshape(r,h,c,l).transpose(0,2,1,3).reshape(r*c,h*l)
 u,s,v=np.linalg.svd(mat,full_matrices=False); a=(u[:,0]*np.sqrt(s[0])).reshape(r,c); b=v[0].reshape(h,l)*np.sqrt(s[0])
 e=w-np.kron(a,b); es=e.reshape(r,h,c,l).transpose(0,2,1,3).reshape(r*c,h,l)
 # E[x x^T], training only. Equivalent to explicit activation score in prior smoke test.
 cov=x.T@x/len(x); s2=[]
 for t,z in enumerate(es):
  i,j=divmod(t,c); sl=slice(j*l,(j+1)*l)
  s2.append(2*np.sum((e[i*h:(i+1)*h]@cov[:,sl])*z)-np.sum((z@cov[sl,sl])*z))
 o={}
 for label,score in [('frob',np.sum(es*es,(1,2))),('aware',s2)]:
  ids=np.argsort(-np.asarray(score),kind='stable')
  o[label]={k:b'\x02'+struct.pack('<HHH',h,l,k)+f32(a)+f32(b)+ids[:k].astype('<u2').tobytes()+f32(es[ids[:k]]) for k in (0,4,8,16,24,32,48,64,96)}
 u,s,v=np.linalg.svd(w,full_matrices=False)
 o['svd']={k:b'\x01'+struct.pack('<H',k)+f32(u[:,:k]*s[:k])+f32(v[:k]) for k in (4,8,16,24,32,48,64)}
 o['quant']={}
 for t in (4,8):
  hi=(1<<(t-1))-1; s=np.max(np.abs(w),axis=1,keepdims=True)/hi
  s=np.where(s>0,s,1).astype('float32')
  q=np.rint(w/s).clip(-hi,hi).astype('int8').reshape(-1)
  if t==4:
   q=q.astype('uint8')+8
   q=q[::2] | (q[1::2]<<4)
  o['quant'][t]=bytes([t])+f32(s)+q.tobytes()
 return o
SH=[(256,784),(256,256),(10,256)]
def pack(a,b,c,bias):
 return b'OC01'+struct.pack('<III',len(a),len(b),len(c))+a+b+c+bias
def unpack(a):
 assert a[:4]==b'OC01'
 p=16; out=[]
 for n,shape in zip(struct.unpack('<III',a[4:16]),SH):
  out.append(layer(a[p:p+n],shape)); p+=n
 for n,_ in SH:
  out.append(read(a[p:p+4*n],(n,)));p+=4*n
 assert p==len(a)
 return out
def run(p,cal,xv,yv,xt,yt,seed):
 bias=b''.join(map(f32,p[3:])); base=[b'\0'+f32(w) for w in p[:3]]
 dense=pack(*base,bias); maxb=len(dense)*30//100
 np.testing.assert_array_equal(pred(xv[:16],p),pred(xv[:16],unpack(dense)))
 ch=[choices(p[0],cal,(16,28)),choices(p[1],np.maximum(cal@p[0].T+p[3],0),(16,16))]
 def artifact(method,k):
  return pack(ch[0][method][k[0]],ch[1][method][k[1]],base[2],bias)
 def record(blob,accuracy,k):
  return dict(bytes=len(blob),ratio=len(blob)/len(dense),accuracy=float(accuracy),settings=k,sha256=sha(blob))
 def score(blob,x,y):
  return np.mean(pred(x,unpack(blob)).argmax(1)==y)
 rows={}; best={}
 for method in ['frob','aware','svd','quant']:
  rows[method]=[]
  for k in itertools.product(ch[0][method],ch[1][method]):
   blob=artifact(method,k)
   if len(blob)<=maxb: rows[method].append(record(blob,score(blob,xv,yv),k))
  best[method]=min(rows[method],key=lambda o:(-o['accuracy'],o['bytes'],o['settings']))
 # All validation-selected settings fixed before touching held-out test.
 (P/f'seed-{seed}-frozen.json').write_text(json.dumps(best,indent=2))
 blobs={'dense':dense,'kron':artifact('frob',(0,0)),
        'aware_matched':artifact('aware',best['frob']['settings'])}
 for m in best: blobs[m]=artifact(m,best[m]['settings'])
 for t in (4,8): blobs[f'quant{t}']=artifact('quant',(t,t))
 test={m:record(b,score(b,xt,yt),best[m]['settings'] if m in best else best['frob']['settings'] if m=='aware_matched' else None) for m,b in blobs.items()}
 assert test['aware_matched']['bytes']==test['frob']['bytes']
 return dict(budget=maxb,validation=rows,selected=best,test=test)
def main():
 files=['train-images-idx3-ubyte.gz','train-labels-idx1-ubyte.gz','t10k-images-idx3-ubyte.gz','t10k-labels-idx1-ubyte.gz']
 (x,y,xt,yt),hashes=zip(*(idx(f) for f in files)); assert (len(x),len(y),len(xt),len(yt))==(60000,60000,10000,10000)
 perm=np.random.default_rng(20261120).permutation(len(x)).astype('<i8'); iv,it=perm[:5000],perm[5000:]
 cal=x[it[:2048]]; xv=x[iv]; yv=y[iv]; nx=x[it]; ny=y[it]
 for seed in map(int,sys.argv[1:] or (11,23,47)):
  t=time.monotonic()
  p=train(nx,ny,seed)
  result=run(p,cal,xv,yv,xt,yt,seed)
  result.update(seed=seed,seconds=time.monotonic()-t,dataset_hashes=dict(zip(files,hashes)),split_sha256=sha(perm.tobytes()),
                code_sha256=sha(Path(__file__).read_bytes()),python=sys.version,numpy=np.__version__)
  (P/f'seed-{seed}.json').write_text(json.dumps(result,indent=2))
  print(json.dumps(result['test']),flush=True)
if __name__=='__main__': main()
