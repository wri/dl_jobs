from __future__ import print_function
import os.path
import yaml
import dl_jobs.utils as utils
import dl_jobs.constants as c
#
# DEFALUTS 
#
_DEFAULTS={
    'dl_image': c.DL_IMAGE,
    'dls_root': c.DLS_ROOT,
    'is_dev': c.IS_DEV,
    'module_dir': c.MODULE_DIR,
    'noisy': c.NOISY
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
        dl_image=c.DL_IMAGE,
        dls_root=c.DLS_ROOT,
        is_dev=c.IS_DEV,
        module_dir=c.MODULE_DIR,
        noisy=c.NOISY,
        force=False):
    """ generate config file
    """
    config={
        'dl_image': dl_image,
        'dls_root': dls_root,
        'is_dev': is_dev,
        'module_dir': module_dir,
        'noisy': noisy }
    if not force and os.path.exists(c.DL_JOBS_CONFIG_PATH):
        utils.log(c.DL_JOBS_CONFIG_EXISTS,True,level="ERROR")
    else:
        with open(c.DL_JOBS_CONFIG_PATH,'w+') as file:
            file.write("# {}\n".format(c.DL_JOBS_CONFIG_COMMENT))
            file.write(yaml.safe_dump(config, default_flow_style=False))
        utils.log(c.DL_JOBS_CONFIG_CREATED,noisy)


