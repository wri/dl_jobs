import json


def as_json(func):
    def decorator(*args,**kwargs):
        out=func(*args,**kwargs)
        if isinstance(out,str):
            return out
        else:
            if out is None: out={}
            return json.dumps(out)
    return decorator