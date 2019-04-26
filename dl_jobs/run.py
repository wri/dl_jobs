from __future__ import print_function
import os,sys
import warnings
from importlib import import_module
import json
from pprint import pprint
from descarteslabs.client.services.tasks import Tasks, as_completed
import dl_jobs.config as c
import dl_jobs.utils as utils
warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.getcwd())

#
# DEFAULTS
#
DL_IMAGE=c.get('dl_image')
IS_DEV=c.get('is_dev')
NOISY=c.get('noisy')
MODULE_DIR=c.get('module_dir')
PRINT_LOGS=c.get('print_logs')

#
# PUBLIC METHODS
#
def launch(
        module_name,
        method_name='task',
        dl_image=DL_IMAGE,
        args=[],
        kwargs={},
        args_list=[],
        dev=IS_DEV,
        print_logs=PRINT_LOGS,
        noisy=NOISY):
    job_method=_get_job_method(module_name,method_name)
    if not kwargs:
        kwargs={}
    kwargs['dl_image']=dl_image
    kwargs['args_list']=args_list
    kwargs['noisy']=noisy
    job=job_method(*args,**kwargs)
    if dev is not None:
        job.platform_job=dev
    job.run()
    if print_logs:
        job.print_logs()


#
# INTERNAL METHODS
#
def _get_job_method(module_name,method_name):
    module_name='{}.{}'.format(MODULE_DIR,module_name)
    module=import_module(module_name)
    return getattr(module,method_name)



