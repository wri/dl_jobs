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
MODULE_DIR=c.get('module_dir')
CONFIG_METHODS='CONFIG_METHODS'


#
# PUBLIC METHODS
#
def launch(module,method='task',dev=IS_DEV,args=[]):
    timer, module, method_name, dev=_setup(module,method,dev)
    func,args,kwargs,args_list=_create_async_func
    if args_list:
        task=_run_tasks(
            timer,
            func,
            dev=dev,
            args_list=args_list )    
    else:
        task=_run_task(
            timer,
            func,
            dev=dev,
            *job.get('args'),
            **job.get('kwargs') )
    return task


#
# INTERNAL METHODS
#
def _setup(module,method,dev):
    timer=utils.Timer()
    module_name='{}.{}'.format(MODULE_DIR,module)
    module=import_module(module_name)
    method_name='{}.{}'.format(module_name,method)
    dev=_is_dev(dev,module)
    utils.vspace()
    print('SETUP TASK: {}'.format(method_name))
    print('- start: {}'.format(timer.start()))
    print('- dev mode: {}'.format(dev))
    return timer, module, method_name, dev


def _get_func(module,method_name,args,dev):
    job=getattr(module,method_name)(*args)
    if isinstance(job,dict):
        if dev:
            func=job['func']
            print("- dev created")
        else:
            func=_create_async_func(timer,job['func'])
            print("- async func created")
    args_list=job.get('args_list')



def _create_async_func(timer,func):
    client = Tasks()
    func = client.create_function(
        func,
        name=method_name,
        image=DL_IMAGE,
        include_data=module.DATA,
        include_modules=module.MODULES,
        requirements=module.REQUIREMENTS,
        gpus=module.GPUS
    )
    return func


def _run_task(timer,func,dev,*args,**kwargs):
    print('RUN TASK:')
    print('- args: {}'.format(args))
    if dev:
        print('- execute dev task:')
        result=func(*args,**kwargs)
        log=False
        task={'DEV':True}
    else:
        print("- submitting a task")
        task=func(*args,**kwargs)
        print("- waiting for the task to complete...")
        result=task.result
        log=task.log.decode('unicode_escape')
    # print the task result and logs
    print('- end: {}'.format(timer.stop()))
    print('- duration: {}'.format(timer.duration()))
    utils.vspace()
    utils.line()
    print("RESULT")
    utils.line()
    pprint(json.loads(result))
    if log:
        utils.vspace()
        utils.line()
        print("LOG")
        utils.line()
        print(log)
    utils.vspace()
    return task


def _run_tasks(timer,func,dev,args_list=[]):
    if isinstance(args_list,int):
        args_list=range(args_list)
    print('RUN TASKS:')
    print("- submitting tasks")
    print('- nb_args_list: {}'.format(len(args_list)))     
    print("- starting to wait for task completions")
    if dev:
        tasks=map(func,args_list)
        print("- dev-mode complete")
    else:
        tasks=func.map(args_list)
        for task in as_completed(tasks):
            if task.is_success:
                print(task.result)
            else:
                print(task.exception)
                print(task.log)
    # print the task result and logs
    print('- end: {}'.format(timer.end()))
    print('- duration: {}'.format(timer.duration()))
    return tasks


def _is_dev(dev,module):
    if dev is None:
        try:
            dev=getattr(module,'IS_DEV')
        except:
            dev=IS_DEV
    return dev

