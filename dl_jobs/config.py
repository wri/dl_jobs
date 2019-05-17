from __future__ import print_function
import os.path
import warnings
import yaml
import dl_jobs.constants as c
warnings.filterwarnings("ignore", category=DeprecationWarning)
#
# DEFALUTS 
#
_DEFAULTS={
    'cpu_job': c.CPU_JOB,
    'cpu_image': c.CPU_IMAGE,
    'gpu_image': c.GPU_IMAGE,
    'dls_root': c.DLS_ROOT,
    'is_dev': c.IS_DEV,
    'module_dir': c.MODULE_DIR,
    'print_logs': c.PRINT_LOGS,
    'default_method': c.DEFAULT_METHOD,
    'noisy': c.NOISY,
    'suppress': c.SUPPRESS,
    'save_results': c.SAVE_RESULTS,
    'results_dir': c.RESULTS_DIR,
    'log': c.LOG,
    'log_dir': c.LOG_DIR
}


#
# LOAD CONFIG
#
if os.path.exists(c.DL_JOBS_CONFIG_PATH):
    _CONFIG=yaml.safe_load(open(c.DL_JOBS_CONFIG_PATH))
else:
    _CONFIG={}


def get(key):
    """ get value
    """
    return _CONFIG.get(key,_DEFAULTS[key])


def generate(
        cpu_job=c.CPU_JOB,
        cpu_image=c.CPU_IMAGE,
        gpu_image=c.GPU_IMAGE,
        dls_root=c.DLS_ROOT,
        is_dev=c.IS_DEV,
        module_dir=c.MODULE_DIR,
        noisy=c.NOISY,
        suppress=c.SUPPRESS,
        save_results=c.SAVE_RESULTS,
        results_dir=c.RESULTS_DIR,
        log=c.LOG,
        log_dir=c.LOG_DIR,
        print_logs=c.PRINT_LOGS,
        default_method=c.DEFAULT_METHOD,
        force=False):
    """ generate config file
    """
    config={
        'cpu_job': cpu_job,
        'cpu_image': _get_image(cpu_image),
        'gpu_image': _get_image(gpu_image),
        'dls_root': dls_root,
        'is_dev': _truthy(is_dev),
        'module_dir': module_dir,
        'print_logs': _truthy(print_logs),
        'default_method': default_method,
        'noisy': _truthy(noisy),
        'suppress': _to_arr(suppress),
        'save_results': save_results,
        'results_dir': results_json,
        'log': log,
        'log_dir': log_dir }
    if not force and os.path.exists(c.DL_JOBS_CONFIG_PATH):
        _log(c.DL_JOBS_CONFIG_EXISTS,True,level="ERROR")
    else:
        with open(c.DL_JOBS_CONFIG_PATH,'w+') as file:
            file.write("# {}\n".format(c.DL_JOBS_CONFIG_COMMENT))
            file.write(yaml.safe_dump(config, default_flow_style=False))
        _log(c.DL_JOBS_CONFIG_CREATED,noisy)


#
# INTERNAL
#
_FALSEY=['false','none','no','null','f','n','0']


def _get_image(image):
    """ dl_image from dl_image or image-key (py27,py27_gpu,py36,...) """
    return c.IMAGES.get(image,image)


def _truthy(value):
    if isinstance(value,str):
        value=value.lower()
        return value not in _FALSEY
    else:
        raise value


def _to_arr(value):
    if isinstance(value,str):
        return value.split(',')
    else:
        return value


def _log(msg,noisy,level='INFO'):
    if noisy:
        print("[{}] DL_JOBS: {}".format(level,msg))



