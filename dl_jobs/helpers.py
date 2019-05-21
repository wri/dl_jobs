from copy import deepcopy
#
# CONSTANTS
#
FALSEY=['false','none','no','null','f','n','0']



#
# HELPERS
#
def copy_update(data,update,value=None):
    """ copy a dictionary and update values

    Args:
        data<dict>: dictionary to be copied
        update<dict|str>:
            if dict: update copy of data with 'update'
            if str: the key 'update' is set to 'value'
        value:
            value if key is str

    Returns:
        updated dictionary

    """
    data=deepcopy(data)
    if update:
        if isinstance(update,dict):
            data.update(update)
        else: 
            data[update]=value
    return data


def update_list(data,value_list,key=None):
    """ creates list of updated data values
    
    Args:
        data<dict>: dictionary to be copied
        value_list<list<dict|?>>:
            list of update dicts or values to be updated
        key:
            * let value be an element of of value list
            if key:
                update each data-copy by data[key]=value
            else:
                * value must be a dictionary
                update each data-copy by data.update(value)
            
    Returns:
        list where each element is an updated copy of data

    """
    if key:
        return [ copy_update(data,key,v) for v in value_list ]
    else:
        return [ copy_update(data,v) for v in value_list ]


def is_str(value):
    """ is_str method that works for py2 and py3 """
    if isinstance(value,str):
        return True
    else:
        try: 
            is_a_str=isinstance(out,unicode)
        except:
            is_a_str=False
        return is_a_str


def truthy(value):
    """ 
    - returns False if (not value) or a string and
      value.lower() in ['false','none','no','null','f','n','0']
    - else return value (something truthy)
    """
    if isinstance(value,bool) or isinstance(value,int) or (value is None):
        return value
    elif is_str(value):
        value=value.lower()
        return value not in FALSEY
    else:
        raise ValueError('truthy: value must be str,int,bool')