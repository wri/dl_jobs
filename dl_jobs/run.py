from __future__ import print_function
import os,sys
from importlib import import_module
import json
from pprint import pprint
from descarteslabs.client.services.tasks import Tasks, as_completed
import dl_jobs.config as c
import dl_jobs.utils as utils
sys.path.append(os.getcwd())
#
# DEFAULTS
#
DL_IMAGE=c.get('dl_image')
IS_DEV=c.get('is_dev')
MODULE_DIR=c.get('module_dir')



#
# PUBLIC METHODS
#
def launch(module,method='task',dev=IS_DEV,args=[]):
    timer, module, method_name, dev=_setup(module,method,dev)
    func=_create_func(timer,module,method_name,dev,method=method)
    task=_run_task(timer,func,dev=dev,args=args)
    return task


def launch_tasks(module,method='task',dev=IS_DEV,args_list=[]):
    timer, module, method_name, dev=_setup(module,method,dev)
    func=_create_func(timer,module,method_name,dev,method=method)
    tasks=_run_tasks(timer,func,dev=dev,args=args_list)
    return tasks


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


def _create_func(timer,module,method_name,dev,method='task'):
    print("CREATE FUNCTION:")
    print('- name: {}'.format(method_name))
    # create task group
    if dev:
        func=getattr(module,method)
        print("- dev created")
    else:
        client = Tasks()
        func = client.create_function(
            method_name,
            name=method_name,
            image=DL_IMAGE,
            include_data=module.DATA,
            include_modules=module.MODULES,
            requirements=module.REQUIREMENTS,
            gpus=module.GPUS
        )
        print("- async func created")
    return func


def _run_task(timer,func,dev,args=[]):
    print('RUN TASK:')
    print('- args: {}'.format(args))
    if dev:
        print('- execute dev task:')
        result=func(*args)
        log=False
        task={'DEV':True}
    else:
        print("- submitting a task")
        task=func(*args)
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


def _run_tasks(timer,func,dev=IS_DEV,args_list=[]):
    if isinstance(args_list,int):
        args_list=range(args_list)
    print('RUN TASKS:')
    print("- submitting tasks")
    print('- args_list: {}'.format(args_list))        
    tasks = func.map(args_list)
    # print the shape of the image array returned by each task
    print("- starting to wait for task completions")
    if dev:
        print("- dev-mode complete")
    else:
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
            print(module)
            print(dir(module))
            dev=getattr(module,'IS_DEV')
            print('boom')
        except:
            print('bop')
            1/0
            dev=IS_DEV
    return dev

