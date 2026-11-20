"""Self-contained packed quantizer. Matrix orientation: [out, in]."""
import struct
import numpy as np

LH=struct.Struct('<4sIIHB')
def pack_codes(c,bits):
    c=np.asarray(c,np.uint8).reshape(-1)
    return np.packbits((c[:,None] >> np.arange(bits,dtype=np.uint8)) & 1,bitorder='little').tobytes()

def unpack_codes(blob,n,bits):
    if len(blob)!=(n*bits+7)//8: raise ValueError('bad packed length')
    z=np.unpackbits(np.frombuffer(blob,np.uint8),count=n*bits,bitorder='little')
    return (z.reshape(n,bits) << np.arange(bits,dtype=np.uint8)).sum(1,dtype=np.uint8)

def encode_layer(weight,bits,group,fit):
    if bits not in (2,3,4) or fit not in ('maxabs','clip'):
        raise ValueError('supported: bits 2/3/4 and fit maxabs/clip')
    a=np.asarray(weight,np.float32)
    m,n=a.shape; g=n if group in ('row',0) else int(group)
    if not (0 < g <= n and n%g==0): raise ValueError('group does not divide layer input')
    x=a.reshape(-1,g)
    # evenly spaced odd signed levels. All 2**b codes used, zero not a level.
    limit=(1<<bits)-1
    mag=np.max(np.abs(x),axis=1,keepdims=True)
    base=mag/limit
    # All-zero groups decode exactly to zero (scale zero and any code).
    best_err=np.full((len(x),1),np.inf,np.float32)
    best_scale=np.zeros_like(base)
    best_q=np.zeros_like(x,dtype=np.uint8)
    for f in (1.,) if fit=='maxabs' else (1.,.95,.90,.85,.80,.75,.70,.65,.60,.55,.50):
        s=base*np.float32(f)
        norm=x/np.where(s>0,s,1.)
        q=np.rint((norm+limit)/2).clip(0,limit).astype(np.uint8)
        z=(q.astype(np.float32)*2-limit)*s
        err=np.sum((z-x)**2,axis=1,keepdims=True)
        use=err<best_err
        best_err=np.where(use,err,best_err)
        best_scale=np.where(use,s,best_scale)
        best_q=np.where(use,q,best_q)
    return LH.pack(b'GQL1',m,n,g,bits)+best_scale.astype('<f4').tobytes()+pack_codes(best_q,bits)

def decode_layer(blob):
    magic,m,n,g,bits=LH.unpack_from(blob)
    if magic!=b'GQL1' or bits not in (2,3,4) or not m or not n or not g or n%g:
        raise ValueError('malformed layer header')
    k=LH.size+4*m*n//g
    s=np.frombuffer(blob[LH.size:k],'<f4').reshape(-1,1)
    q=unpack_codes(blob[k:],m*n,bits).astype(np.float32).reshape(-1,g)
    return ((q*2-((1<<bits)-1))*s).reshape(m,n)

def encode_model(p,config):
    a,b=(encode_layer(w,**c) for w,c in zip(p[:2],config,strict=True))
    # Shapes of all fixed layers/biases specified by GQM1.
    if [x.shape for x in p]!=[(256,784),(256,256),(10,256),(256,),(256,),(10,)]:
        raise ValueError('unexpected architecture')
    return struct.pack('<4sII',b'GQM1',len(a),len(b))+a+b+b''.join(np.asarray(w,'<f4').tobytes() for w in p[2:])

def decode_model(blob):
    magic,a,b=struct.unpack_from('<4sII',blob)
    if magic!=b'GQM1': raise ValueError('bad model magic')
    return [decode_layer(blob[12:12+a]),decode_layer(blob[12+a:12+a+b])]+_decode_fixed(blob[12+a+b:])

def _decode_fixed(blob):
    z=np.frombuffer(blob,'<f4')
    if len(z)!=3082: raise ValueError('bad bias/output length')
    return [z[:2560].reshape(10,256),z[2560:2816],z[2816:3072],z[3072:]]
