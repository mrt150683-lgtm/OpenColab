"""Select exactly one frozen global recipe for each cap using dev results only."""
import json
from pathlib import Path
H=Path(__file__).resolve().parent
def key(c):return json.dumps(c,sort_keys=True,separators=(',',':'))
def main():
    files=[H/f'dev-{s}.json' for s in (11,23,47)]
    runs=[json.loads(f.read_text()) for f in files]
    by=[{key(t['config']):t for t in r['trials']} for r in runs]
    d=[r['dense_accuracy'] for r in runs]
    rows=[]
    for k in set.intersection(*(set(a) for a in by)):
        t=[a[k] for a in by]; acc=[r['accuracy'] for r in t]
        delta=[a-b for a,b in zip(acc,d)]
        rows.append(dict(config=t[0]['config'],bytes=max(r['bytes'] for r in t),ratio=max(r['ratio'] for r in t),accuracy=acc,delta=delta,min_delta=min(delta),mean_delta=sum(delta)/len(delta)))
    order=lambda t:(-t['min_delta'],-t['mean_delta'],t['bytes'],key(t['config']))
    results={}
    for cap in (.10,.12):
        k=str(cap)
        eligible=sorted((t for t in rows if t['ratio']<=cap),key=order)
        results[k]={'eligible':len(eligible),'winner':eligible[0],'row_only':next((t for t in eligible if all(c['group']=='row' for c in t['config'])),None)}
    out=dict(seeds=[11,23,47],dense_accuracy=d,caps=results)
    target=H/'frozen.json'
    if target.exists(): assert json.loads(target.read_text())==out, 'different frozen record'
    else: target.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
