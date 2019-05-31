from __future__ import print_function
import os.path
import warnings
import yaml
import dl_jobs.constants as c
from copy import deepcopy


warnings.filterwarnings("ignore", category=DeprecationWarning)
#
# DEFALUTS 
#
_DEFAULTS={
    'cpus': c.CPUS,
    'gpus': c.GPUS,
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
    'save_errors': c.SAVE_ERRORS,
    'results_dir': c.RESULTS_DIR,
    'errors_dir': c.ERRORS_DIR,
    'log': c.LOG,
    'log_dir': c.LOG_DIR
}


#
# LOAD CONFIG
#
CONFIG=deepcopy(_DEFAULTS)
if os.path.exists(c.DL_JOBS_CONFIG_PATH):
    CONFIG.update(yaml.safe_load(open(c.DL_JOBS_CONFIG_PATH)))


def get(key):
    """ get value
    """
    return CONFIG[key]


def generate(
        cpus=c.CPUS,
        gpus=c.GPUS,
        cpu_job=c.CPU_JOB,
        cpu_image=c.CPU_IMAGE,
        gpu_image=c.GPU_IMAGE,
        dls_root=c.DLS_ROOT,
        is_dev=c.IS_DEV,
        module_dir=c.MODULE_DIR,
        noisy=c.NOISY,
        suppress=c.SUPPRESS,
        save_results=c.SAVE_RESULTS,
        save_errors=c.SAVE_ERRORS,
        results_dir=c.RESULTS_DIR,
        errors_dir=c.ERRORS_DIR,
        log=c.LOG,
        log_dir=c.LOG_DIR,
        print_logs=c.PRINT_LOGS,
        default_method=c.DEFAULT_METHOD,
        force=False):
    """ generate config file
    """
    config={
        'cpus': cpus,
        'gpus': gpus,
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
        'save_errors': save_errors,
        'results_dir': results_dir,
        'errors_dir': errors_dir,
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
def _truthy(value):
    """ duplicate of dl_jobs.helpers.truthy
    """
    if isinstance(value,bool) or isinstance(value,int) or (value is None):
        return value
    elif is_str(value):
        value=value.lower()
        return value not in FALSEY
    else:
        raise ValueError('truthy: value must be str,int,bool')


def _get_image(image):
    """ dl_image from dl_image or image-key (py27,py27_gpu,py36,...) """
    return c.IMAGES.get(image,image)


def _to_arr(value):
    if isinstance(value,str):
        return value.split(',')
    else:
        return value


def _log(msg,noisy,level='INFO'):
    if noisy:
        print("[{}] DL_JOBS: {}".format(level,msg))



