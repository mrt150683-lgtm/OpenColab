"""Confirm already-frozen recipes on untouched training seeds and fixed cases."""
import json,sys
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent))
import evaluate,lab
from group_quant import encode_model,decode_model
def main():
    frozen=json.loads((H/'frozen.json').read_text())
    assert tuple(frozen['seeds'])==lab.DEV
    *_,xt,yt=lab.data(test=True); ds=evaluate.cases(xt)
    rows={}
    for s in lab.CONFIRM:
        p=lab.load(s); raw=lab.dense(p); d=evaluate.record(raw,p,ds,yt)
        r={'dense':d}
        for cap,t in frozen['caps'].items():
            r[cap]={}
            for name in ('winner','row_only'):
                spec=t[name]
                if spec is None:continue
                blob=encode_model(p,spec['config'])
                assert len(blob)==spec['bytes'] and len(blob)/len(raw)<=float(cap)
                o=evaluate.record(blob,decode_model(blob),ds,yt)
                o.update(config=spec['config'],ratio=len(blob)/len(raw))
                for key in o['metrics']:
                    met=o['metrics'][key]; base=d['metrics'][key]
                    met['delta']=met['accuracy']-base['accuracy']
                    met['per_class_delta']=[a-b for a,b in zip(met['per_class'],base['per_class'])]
                r[cap][name]=o
        rows[str(s)]=r
    dest=H/'confirmation.json'
    dest.write_text(json.dumps(rows,indent=2)+'\n')
    for s,r in rows.items():
        print('seed',s,'dense',r['dense']['metrics']['clean']['accuracy'])
        for cap in frozen['caps']:
            for n,o in r[cap].items():
                print(cap,n,o['bytes'],[(k,round(v['accuracy']*100,2),round(v['delta']*100,2)) for k,v in o['metrics'].items()])
if __name__=='__main__':main()
