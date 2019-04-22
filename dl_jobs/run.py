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
    timer=utils.Timer()
    func=_setup(timer,module,method=method,dev=dev)
    task=_run_task(timer,func,dev=dev,args=args)
    print(task)


def launch_tasks(module,method='task',dev=IS_DEV,args_list=[]):
    timer=utils.Timer()
    func=_setup(timer,module,method=method,dev=dev)
    task=_run_tasks(timer,func,dev=dev,args=args_list)
    print(task)




#
# INTERNAL METHODS
#
def _setup(timer,module,method='task',dev=IS_DEV):
    full_method=f'{MODULE_DIR}.{module}.{method}'
    utils.vspace()
    print(f"SETUP TASK: {full_method}")
    print(f"- start: {timer.start()}")
    print(f"- dev mode: {dev}")
    print(f"- creating function: {full_method}")
    # create task group
    # task_module=getattr(run,module)
    print(f'{MODULE_DIR}.{module}')
    task_module=import_module(f'{MODULE_DIR}.{module}')
    if dev:
        func=getattr(task_module,method)
    else:
        client = Tasks()
        func = client.create_function(
            full_method,
            name=full_method,
            image=DL_IMAGE,
            include_data=task_module.DATA,
            include_modules=task_module.MODULES,
            requirements=task_module.REQUIREMENTS,
            gpus=task_module.GPUS
        )
    return func


def _run_task(timer,func,dev=IS_DEV,args=[]):
    print(f"RUN TASK:")
    print(f"- args: {args}")
    if dev:
        print(f"- execute dev task: ")
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
    print(f"- end: {timer.stop()}")
    print(f"- duration: {timer.duration()}")
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
    print(f"RUN TASKS:")
    print("- submitting tasks")
    print(f"- args_list: {args_list}")        
    tasks = func.map(args_list)
    # print the shape of the image array returned by each task
    print("- starting to wait for task completions")
    if dev:
        print("- dev-mode complete")
        print(tasks)
    else:
        for task in as_completed(tasks):
            if task.is_success:
                print(task.result)
            else:
                print(task.exception)
                print(task.log)
    # print the task result and logs
    print(f"- end: {timer.end()}")
    print(f"- duration: {timer.duration()}")


