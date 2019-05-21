import json


def expand_args(func):
    """ expand arg-list/kwarg-dict to args/kwargs """
    def decorator(args=[],kwargs={}):
        if (not kwargs) and isinstance(args,dict):
            kwargs=args
            args=[]
        return func(*args,**kwargs)
    return decorator


def attempt(func):
    """ catch exception and return exception in dict """
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
    """ convert func output to json """
    def decorator(*args,**kwargs):
        if kwargs:
            return_as_dict=kwargs.pop('return_as_dict',False)
        elif len(args) and isinstance(args[0],dict):
            return_as_dict=args[0].pop('return_as_dict',False)
        else:
            return_as_dict=False
        out=func(*args,**kwargs)
        if return_as_dict or _is_str(out):
            return out
        else:
            if out is None: out={}
            return json.dumps(out)
    return decorator


def _is_str(value):
    if isinstance(value,str):
        return True
    else:
        try: 
            is_str=isinstance(out,unicode)
        except:
            is_str=False
        return is_str