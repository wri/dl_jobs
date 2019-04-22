import os,sys
from importlib import import_module
import json
from datetime import datetime
from pprint import pprint
from descarteslabs.client.services.tasks import Tasks, as_completed
import dl_jobs.config as c
sys.path.append(os.getcwd())


#
# DEFAULTS
#
DL_IMAGE=c.get('dl_image')
IS_DEV=c.get('is_dev')
MODULE_DIR=c.get('module_dir')
TS_FMT="%b %d %Y %H:%M:%S"



#
# HELPERS
#
def _duration(end,start):
    return str(end-start).split('.')[0]


def _vspace(n=2):
    print("\n"*n)


def _line(char='-',length=100):
    print(char*length)


#
# METHODS
#
def setup(module,method='task',dev=IS_DEV):
    full_method=f'{MODULE_DIR}.{module}.{method}'
    _vspace()
    print(f"SETUP TASK: {full_method}")
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


def run_task(func,dev=IS_DEV,args=[]):
    start=datetime.now()
    print(f"RUN TASK:")
    print(f"- start: {start.strftime(TS_FMT)}")
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
    end=datetime.now()
    # print the task result and logs
    print(f"- end: {end.strftime(TS_FMT)}")
    print(f"- duration: {_duration(end,start)}")
    _vspace()
    _line()
    print("RESULT")
    _line()
    pprint(json.loads(result))
    if log:
        _vspace()
        _line()
        print("LOG")
        _line()
        print(log)
    _vspace()
    return task



def launch(module,method='task',dev=IS_DEV,args=[]):
    func=setup(module,method=method,dev=dev)
    task=run_task(func,dev=dev,args=args)
    print(task)


def launch_tasks(module,method='task',dev=IS_DEV,args_list=[]):
    print(f"RUN TASKS:")
    func=setup(module,method=method,dev=dev)
    start=datetime.now()
    print(f"- start: {start.strftime(TS_FMT)}")
    print("- submitting tasks")
    if isinstance(args_list,int):
        args_list=range(args_list)
    tasks = func.map(args_list)
    # print the shape of the image array returned by each task
    print("- starting to wait for task completions")
    if dev:
        print("done")
        print(tasks)
    else:
        for task in as_completed(tasks):
            if task.is_success:
                print(task.result)
            else:
                print(task.exception)
                print(task.log)
    end=datetime.now()
    # print the task result and logs
    print(f"- end: {end.strftime(TS_FMT)}")
    print(f"- duration: {_duration(end,start)}")


