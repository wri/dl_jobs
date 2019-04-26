import json


def as_json(func):
    def decorator(*args,**kwargs):
        out=func(*args,**kwargs)
        if isinstance(out,str):
            return out
        else:
            return json.dumps(out)
    return decorator