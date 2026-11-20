from pathlib import Path
import json,statistics
import residual as r
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import lab
def select(rows,budget,include_residual=True):
 keyed=[{(z['kind'],tuple(map(tuple,z['knobs']))):z for z in s['rows'] if z['ratio']<=budget and (include_residual or sum(k[1] for k in z['knobs'])==0)} for s in rows]
 combos=[]
 for key in set.intersection(*(set(k) for k in keyed)):
  zz=[k[key] for k in keyed]
  combos.append(dict(kind=key[0],knobs=key[1],size=zz[0]['size'],ratio=zz[0]['ratio'],accuracies=[z['accuracy'] for z in zz],nlls=[z['nll'] for z in zz],min_acc_delta=min(z['accuracy']-s['dense_dev']['accuracy'] for z,s in zip(zz,rows)),mean_accuracy=statistics.mean(z['accuracy'] for z in zz),mean_nll=statistics.mean(z['nll'] for z in zz)))
 return min(combos,key=lambda r:(-round(r['min_acc_delta'],12),-round(r['mean_accuracy'],12),r['size'],r['kind'],r['knobs']))
if __name__=='__main__':
 rows=[json.loads(Path(f'dev-{seed}.json').read_text()) for seed in lab.DEV]
 a,_,_,_=lab.data()
 report={'dense_dev':[s['dense_dev'] for s in rows]}
 for budget in (.10,.12):
  for res in (True,False):
   best=select(rows,budget,res); k=f'{budget:g}-'+('hybrid' if res else 'q-only')
   best['sha256']={}
   for s in lab.DEV:
    blob=r.build(lab.load(s),a[:2048],best['kind'],best['knobs'])
    assert len(blob)==best['size']
    best['sha256'][str(s)]=r.b.sha(blob)
   report[k]=best
 for budget in (.10,.12):
  recipe=report[f'{budget:g}-hybrid']; kind=recipe['kind']
  knobs=[[t,0] for t,_ in recipe['knobs']]
  c=[next(z for z in s['rows'] if z['kind']==kind and z['knobs']==knobs) for s in rows]
  report[f'{budget:g}-same-bit-mix-control']={'kind':kind,'knobs':knobs,'size':c[0]['size'],'accuracies':[z['accuracy'] for z in c]}
 Path('dev-summary.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
