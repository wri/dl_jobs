from __future__ import print_function
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from dl_jobs.job import DLJob
import dl_jobs.helpers as h
from dl_jobs.decorators import as_json, expand_args


""" RUN METHODS

    NOTES:
        * all run methods must return instance(s) of DLJob

"""
MODULES=[
    'dl_jobs'
]
def task(nb_jobs,*args,**kwargs):
    print("\ndl_jobs.test_jobs.task: create DLJob instance\n")
    base_args=_base_args(nb_jobs,*args,**kwargs)
    platform_job=h.truthy(kwargs.get('platform',False))
    cpu_job=h.truthy(kwargs.get('cpu',True))
    noisy=h.truthy(kwargs.get('noisy',True))
    gpus=int(kwargs.get('gpus',0))
    if nb_jobs==1:
        args_list=None
        args=[nb_jobs]
        kwargs=base_args
    else:
        args_list=h.update_list(base_args,range(nb_jobs),'task_id')
        args=[]
        kwargs={}
    job=DLJob(
        module_name='dl_jobs.test_jobs',
        method_name='return_args',
        args=args,
        kwargs=kwargs,
        args_list=args_list,
        platform_job=platform_job,
        cpu_job=cpu_job,
        modules=MODULES,
        gpus=gpus,
        noisy=noisy,
        log=False )
    return job


#
# INTERNAL METHODS
#
def _base_args(*args,**kwargs):
    options=kwargs.pop('options',None)
    return {
        'args': args,
        'kwargs': kwargs,
        'options': options
    }




""" TASK METHODS

    NOTES:
        * typically task-methods will be a separate module from the run methods
        * decorators:
            - @as_json: converts returned dict to json for dl-tasks-api
            - @expand_args: allows you to pass args/kwargs as list/dict
"""
@as_json
@expand_args
def return_args(*args,**kwargs):
    """ a hello-world task

    Just return the passed data

    """
    print("dl_jobs.test_jobs.return_args: doing work\n")
    return {
        'args': args,
        'kwargs': kwargs
    }



