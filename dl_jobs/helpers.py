from copy import deepcopy
#
# CONSTANTS
#
FALSEY=['false','none','no','null','f','n','0']



#
# HELPERS
#
def copy_update(data,update,value=None):
    data=deepcopy(data)
    if update:
        if isinstance(update,dict):
            data.update(update)
        else: 
            data[update]=value
    return data


def update_list(data,value_list,key=None):
    if key:
        return [ copy_update(data,key,v) for v in value_list ]
    else:
        return [ copy_update(data,v) for v in value_list ]


def is_str(value):
    if isinstance(value,str):
        return True
    else:
        try: 
            is_a_str=isinstance(out,unicode)
        except:
            is_a_str=False
        return is_a_str


def truthy(value):
    if isinstance(value,bool) or isinstance(value,int) or (value is None):
        return value
    elif isinstance(value,str):
        value=value.lower()
        return value not in FALSEY
    else:
        raise ValueError('truthy: value must be str,int,bool')