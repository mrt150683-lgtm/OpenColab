"""Confirmation-only metrics. Import does not access official test."""
import hashlib, numpy as np
import baseline as b,lab
def cases(x):
    rng=np.random.default_rng(20261120)
    image=x.reshape(-1,28,28)
    shifted=np.zeros_like(image)
    shifted[:,:,1:]=image[:,:,:-1]
    noise=rng.standard_normal(x.shape,dtype=np.float32)*np.float32(.1)
    return {'clean':x,'right_1px':shifted.reshape(x.shape),'gauss_0.1':np.clip(x+noise,0,1)}
def metrics(params, datasets, labels):
    out={}
    for name,xx in datasets.items():
        hit=b.pred(xx,params).argmax(1)==labels
        out[name]={'accuracy':float(hit.mean()),'per_class':[float(hit[labels==k].mean()) for k in range(10)]}
    return out
def record(blob,decoded,datasets,labels):
    return {'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'metrics':metrics(decoded,datasets,labels)}
