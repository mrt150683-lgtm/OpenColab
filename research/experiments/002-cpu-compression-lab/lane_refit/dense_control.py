"""Post-hoc matched extra-training control; not used to select recipes."""
from refit import lab,b,np,Path,json
import evaluate
x,y,_,_,xt,yt=lab.data(test=True)
ds=evaluate.cases(xt); results={}
for seed in lab.CONFIRM:
 p=[a.copy() for a in lab.load(seed)]
 rng=np.random.default_rng(seed+9000); m=[np.zeros_like(a) for a in p];v=[np.zeros_like(a) for a in p];t=0
 rows={}
 for ep in range(1,4):
  ix=rng.permutation(len(x))[:16384]
  for start in range(0,len(ix),256):
   k=ix[start:start+256];a=x[k]
   w0,w1,w2,b0,b1,b2=p
   u=np.maximum(a@w0.T+b0,0);z=np.maximum(u@w1.T+b1,0)
   o=z@w2.T+b2;o=np.exp(o-o.max(1,keepdims=True));o/=o.sum(1,keepdims=True)
   o[np.arange(len(k)),y[k]]-=1;o/=len(k)
   g2=o@w2*(z>0);g1=g2@w1*(u>0);t+=1
   for aa,mm,vv,g in zip(p,m,v,[g1.T@a,g2.T@u,o.T@z,g1.sum(0),g2.sum(0),o.sum(0)]):
    mm*=.9;mm+=.1*g;vv*=.999;vv+=.001*g*g
    aa-= (.0003/(1-.9**t))*mm/(np.sqrt(vv/(1-.999**t))+1e-8)
  if ep in (2,3):
   blob=lab.dense(p);rows[ep]=evaluate.record(blob,b.unpack(blob),ds,yt)
 results[seed]=rows
 print(seed,{i:r['metrics']['clean']['accuracy'] for i,r in rows.items()},flush=True)
 (Path(__file__).parent/'dense-control.json').write_text(json.dumps(results,indent=2))
