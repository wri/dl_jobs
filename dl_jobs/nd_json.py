import json
import re

FMT_RGX=r'\\n\\r\\t'

def write(json_str,path):
    with open(path,'a') as f:
        f.write('{}\n'.format(json_str))
        

def read(path):
    with open(path,'r') as file:
        lines=file.readlines()
    return [ _load_line(l) for l in lines ]


def _load_line(jsn):
    if isinstance(jsn,str):
        return json.loads(_clean(jsn))
    else:
        return jsn


def _clean(json_str):
    return re.sub(FMT_RGX,'',json_str)



