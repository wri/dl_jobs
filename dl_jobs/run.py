from __future__ import print_function
import os,sys
import warnings
import json
from pprint import pprint
from descarteslabs.client.services.tasks import Tasks, as_completed
import dl_jobs.config as c
import dl_jobs.utils as utils
from dl_jobs.job import DLJob
warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.getcwd())

#
# DEFAULTS
#
DL_IMAGE=c.get('dl_image')
IS_DEV=c.get('is_dev')
NOISY=c.get('noisy')
PRINT_LOGS=c.get('print_logs')
MODULE_DIR=c.get('module_dir')


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
    if MODULE_DIR:
        module_name='.'.join([MODULE_DIR,module_name])
    job_method=DLJob.get_method(module_name,method_name)
    if not kwargs:
        kwargs={}
    kwargs['dl_image']=dl_image
    kwargs['args_list']=args_list
    kwargs['noisy']=noisy
    job=job_method(*args,**kwargs)
    if dev is not None:
        job.platform_job=(not dev)
    job.run()
    if print_logs:
        job.print_logs()



