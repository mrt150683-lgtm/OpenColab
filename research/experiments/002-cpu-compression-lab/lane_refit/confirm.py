import refit
from refit import lab,b,np,metrics,Path,json,fit
import evaluate,hashlib
p=Path(__file__).parent
dev=json.loads((p/'dev.json').read_text())
assert set(map(int,dev))==set(lab.DEV)
x,y,v,vy=lab.data()
dense={str(s):float((b.pred(v,lab.load(s)).argmax(1)==vy).mean()) for s in lab.DEV}
freeze={}
for cap in (10,12):
    common=set.intersection(*(set(d) for d in dev.values()))
    recipes=[]
    for k in common:
        a=[dev[s][k]['accuracy']-dense[s] for s in dev]
        size=max(dev[s][k]['bytes'] for s in dev)
        if size<=1077307*cap//100:
            recipes.append((-min(a),-np.mean(a),size,k))
    rec=min(recipes)
    freeze[str(cap)]={'recipe':rec[-1],'bytes':rec[2],'min_dev_delta':-rec[0],'mean_dev_delta':-rec[1]}
(p/'frozen.json').write_text(json.dumps(freeze,indent=2))
print(json.dumps(freeze),flush=True)
x,y,_,_,xt,yt=lab.data(test=True)
ds=evaluate.cases(xt);results={}
for seed in lab.CONFIRM:
    dense_p=lab.load(seed)
    dense_blob=lab.dense(dense_p)
    rows={'dense':evaluate.record(dense_blob,dense_p,ds,yt)}
    # Original row-wise symmetric quantization control, unchanged.
    blocks=[]
    for w in dense_p[:2]:
        s=np.maximum(np.abs(w).max(axis=1,keepdims=True)/7,1e-10)
        ids=np.rint(w/s).clip(-7,7).astype(np.int8).reshape(-1).astype(np.uint8)+8
        blocks.append(bytes([4])+b.f32(s)+(ids[::2]|(ids[1::2]<<4)).tobytes())
    qb=b.pack(*blocks,b'\0'+b.f32(dense_p[2]),b''.join(map(b.f32,dense_p[3:])))
    rows['baseline4']=evaluate.record(qb,b.unpack(qb),ds,yt)
    for cap,q in freeze.items():
        k=q['recipe'];cfg=tuple(map(int,k[:2]));epochs=int(k.split('e')[1])
        for ep,blob in fit(dense_p,cfg,x,y,seed,epochs):
            if ep in (0,epochs):
                key=f'cap{cap}-{k[:2]}-e{ep}'; rows[key]=evaluate.record(blob,refit.decode(blob),ds,yt)
                if ep==epochs:(p/f'{seed}-{key}.ocq').write_bytes(blob)
    results[seed]=rows
    print(seed,{k:(r['bytes'], r['metrics']['clean']['accuracy']) for k,r in rows.items()},flush=True)
    (p/'confirm.json').write_text(json.dumps(results,indent=2))
