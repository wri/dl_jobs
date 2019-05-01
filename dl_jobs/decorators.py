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
        if kwargs:
            return_as_dict=kwargs.pop('return_as_dict',False)
        elif len(args) and isinstance(args[0],dict):
            return_as_dict=args[0].pop('return_as_dict',False)
        else:
            return_as_dict=False
        out=func(*args,**kwargs)
        if return_as_dict or isinstance(out,str) or isinstance(out,unicode):
            return out
        else:
            if out is None: out={}
            return json.dumps(out)
    return decorator