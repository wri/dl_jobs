import json
import re
from types import GeneratorType

FMT_RGX=r'\\n\\r\\t'


def read(path):
    with open(path,'r') as file:
        lines=file.readlines()
    return [ _load_line(l) for l in lines ]


def write(ndjsn,path,overwrite=False,func=None,**kwargs):
    if overwrite:
        mode='w'
    else:
        mode='a'
    with open(path,mode) as f:
        if isinstance(ndjsn,GeneratorType):
            for l in ndjsn:
                f.write('{}\n'.format(_exec(l,func,**kwargs)))
        else:
            f.write('{}\n'.format(_exec(ndjsn,func,**kwargs)))
            

def apply(path,func,postprocess=None,postprocess_kwargs={},**kwargs):
    out=[]
    with open(path,'r') as file:
        for line in file:
            line=_load_line(line)
            out.append(func(line,**kwargs))
    if postprocess:
        out=postprocess(out,**postprocess_kwargs)
    return out
    
    
def _load_line(jsn):
    if isinstance(jsn,str):
        return json.loads(_clean(jsn))
    else:
        return jsn


def _clean(json_str):
    return re.sub(FMT_RGX,'',json_str)


def _exec(obj,func=None,**kwargs):
    if func:
        obj=func(obj,**kwargs)
    return obj