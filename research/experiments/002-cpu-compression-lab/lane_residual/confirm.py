import json,sys
from pathlib import Path
import residual as r
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import lab,evaluate
def main():
  frozen=json.loads(Path('frozen.json').read_text())
  a,_,_,_,xt,yt=lab.data(test=True)
  ds=evaluate.cases(xt)
  results={}
  for s in lab.CONFIRM:
   p=lab.load(s); dense=lab.dense(p)
   out={'dense':evaluate.record(dense,p,ds,yt)}
   for name,z in frozen.items():
    if not isinstance(z,dict): continue
    blob=r.build(p,a[:2048],z['kind'],z['knobs'])
    assert len(blob)==z['size']
    out[name]=evaluate.record(blob,r.unpack(blob),ds,yt)
   results[s]=out
  Path('confirmation.json').write_text(json.dumps(results,indent=2)+'\n')
if __name__=='__main__':main()
