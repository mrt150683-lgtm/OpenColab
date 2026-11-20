"""Summarize shipped JSON. No training and no dataset needed."""
import json
from pathlib import Path
from statistics import mean
p=Path(__file__).resolve().parent
read=lambda f:json.loads((p/f).read_text())
def row(v,d):
    base=d['bytes']
    diff=lambda k:100*(v['metrics'][k]['accuracy']-d['metrics'][k]['accuracy'])
    worst=min(100*(a-b) for k in v['metrics'] for a,b in zip(v['metrics'][k]['per_class'],d['metrics'][k]['per_class']))
    return (100*v['bytes']/base,diff('clean'),diff('right_1px'),diff('gauss_0.1'),worst)
rq=read('lane_refit/confirm.json')
dc=read('lane_refit/dense-control.json')
rs=read('lane_residual/confirmation.json')
g=read('lane_groups/confirmation.json')
print("Groups JSON top keys:",list(g))
print("Main rows: each seed gives percent bytes, clean PP, shift PP, noise PP, worst class PP against dense.")
def fmt(v):return '/'.join(f'{z:.2f}' for z in v)
for k in [a for a in rq['101'] if a!='dense']:
    print(k, *(fmt(row(rq[s][k],rq[s]['dense'])) for s in rq))
print('3-bit refit vs continuing dense training with same labelled examples:')
print(*(fmt(row(rq[s]['cap12-33-e2'],dc[s]['2'])) for s in rq))
for k in [a for a in rs['101'] if a!='dense']:
    print(k,*(fmt(row(rs[s][k],rs[s]['dense'])) for s in rs))
for f in sorted(p.glob('*-data-*.json')):
    d=json.loads(f.read_text()); print(f.name,*(f'{k} {fmt(row(z,d["dense"]))}' for k,z in d.items() if isinstance(z,dict) and 'metrics' in z and k!='dense'),sep=' | ')
