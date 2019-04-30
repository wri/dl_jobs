import json






def expand_args(func):
    def decorator(args=[],kwargs={}):
        if (not kwargs) and isinstance(args,dict):
            kwargs=args
            args=[]
        return func(*args,**kwargs)
    return decorator


def attempt(func):
    def decorator(*args,**kwargs):
        try:
            out=func(*args,**kwargs)
            return out
        except Exception as e:
            return {
                'ERROR': str(e), 
                'ARGS': args,
                'KWARGS': kwargs }
    return decorator


def as_json(func):
    def decorator(*args,**kwargs):
        out=func(*args,**kwargs)
        if isinstance(out,str):
            return out
        else:
            if out is None: out={}
            return json.dumps(out)
    return decorator