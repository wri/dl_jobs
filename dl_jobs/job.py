from __future__ import print_function
import os,sys
import json
import warnings
from importlib import import_module
import logging
from descarteslabs.client.services.tasks import Tasks, as_completed
import dl_jobs.config as c
import dl_jobs.utils as utils
import dl_jobs.nd_json as nd_json
warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.getcwd())
"""
#
# CONSTANTS/DEFAULTS
#
"""
PLATFORM_JOB=False
DEFAULT_METHOD='task'
NAME_TMPL='dljob_{}'
HEADER_TMPL='DLJob.{}: '
NO_JOB_TMPL='[WARNING] DLJob.run: no job found for {}.{}'
NO_GPUS='[WARNING] (GPUs=0 and cpu_job=False) launching as CPU job'
CPU_JOB_WITH_GPUS='[WARNING] cpu_job with GPUs>0, setting GPUs=0'
TRACE_TMPL='- {}'
CPU_JOB=c.get('cpu_job')
CPU_IMAGE=c.get('cpu_image')
GPU_IMAGE=c.get('gpu_image')
IS_DEV=c.get('is_dev')
NOISY=c.get('noisy')
SAVE_RESULTS=c.get('save_results')
SAVE_ERRORS=c.get('save_errors')
RESULTS_DIR=c.get('results_dir')
ERRORS_DIR=c.get('errors_dir')
LOG=c.get('log')
LOG_DIR=c.get('log_dir')
PRINT_LOGS=c.get('print_logs')
MODULE_DIR=c.get('module_dir')


"""
#
# DLJob: RUNNER
#
"""
def run(
        module_name,
        method_name=DEFAULT_METHOD,
        cpu_job=CPU_JOB,
        cpu_image=CPU_IMAGE,
        gpu_image=GPU_IMAGE,
        args=[],
        kwargs={},
        args_list=[],
        dev=IS_DEV,
        print_logs=PRINT_LOGS,
        noisy=NOISY,
        module_dir=MODULE_DIR):
    if module_dir:
        module_name='.'.join([MODULE_DIR,module_name])
    job_method=DLJob.get_method(module_name,method_name)
    if not kwargs:
        kwargs={}
    kwargs['cpu_job']=cpu_job
    kwargs['cpu_image']=cpu_image
    kwargs['gpu_image']=gpu_image
    kwargs['args_list']=args_list
    kwargs['noisy']=noisy
    jobs=job_method(*args,**kwargs)
    if not isinstance(jobs,list):
        jobs=[jobs]
    nb_jobs=len(jobs)
    for job in jobs:
        if job:
            if dev:
                job.platform_job=(not dev)
            job.run()
            if print_logs:
                job.print_logs()
                if noisy and (nb_jobs>1): 
                    utils.line()
        else:
            print(NO_JOB_TMPL.format(module_name,method_name))




"""
#
# DLJob: CLASS
#
"""
class DLJob(object):
    """ DLJob: a simple wrapper for the DLTasks-API

    NOTES: only `module_name` is required. The others have 
    defaults (most of which can be set in the config file).

    Args:
        module_name<str>: module path (ie module_name.submodule_name )
        method_name<str>: method name 
        cpu_job<bool>:
            - if true: job will always run on cpu-image.
            - if false: job will run on the gpu-image unless gpus=0 
        cpu_image: address for cpu dl-image
        gpu_image: address for gpu dl-image
        args_list<list|None>: 
            Use when running multiple jobs. A list of args-lists or kwarg-dicts
            to pass to the job-method referred to in method_name. 
        modules<list|None>: list of modules to include when creating async_func
        requirements<list|str|None>: 
            list of requirements, or path to requirements.txt, to include 
            when creating async_func
        data<list|None>: list of modules to include when creating async_func
        gpus<int|None>: Number of GPUs
        platform_job<bool>:
            - if true: run as DLTask.  Note the CLI can override this by passing
            option (--dev True)
            - if false: run locally
        name<str>: name used in naming tasks and log/results files. defaults to method_name.
        noisy<bool>: more logs/print-outs when noisy
        save_results<bool|str>: 
            save (non-error) results as ndjson. if str: use str as filename
        save_errors<bool|str>: 
            save "errors-results" as ndjson. if str: use str as filename
            "error-results" are:
                - strings that begin with ERROR
                - dicts that contain ERROR=True at the top level
        results_dir<str>: directory to save results  
        errors_dir<str>: directory to save errors  
        results_timestamp<bool>: add timestamp to results filename
        log<bool|str>: write logs. if str: use str as filename
        log_dir<str>: log directory 
        *args: args for method when launching a single job (otherwise use args_list)
        **kwargs: kwargs for method when launching a single job (otherwise use args_list)

    Methods:
        run: launches DLTask(s)
        ...

    """
    @staticmethod
    def get_method(module_name,method_name):
        module=import_module(module_name)
        return getattr(module,method_name)


    @staticmethod
    def full_method_name(module_name,method_name):
        return '.'.join([module_name,method_name])


    def __init__(self,
            module_name,
            method_name=DEFAULT_METHOD,
            cpu_job=CPU_JOB,
            cpu_image=CPU_IMAGE,
            gpu_image=GPU_IMAGE,
            args_list=None,
            modules=None,
            requirements=None,
            data=None,
            gpus=None,
            platform_job=PLATFORM_JOB,
            name=None,
            noisy=True,
            save_results=SAVE_RESULTS,
            save_errors=SAVE_ERRORS,
            results_dir=RESULTS_DIR,            
            errors_dir=ERRORS_DIR,
            results_timestamp=True,
            log=LOG,
            log_dir=LOG_DIR,
            *args,
            **kwargs):
        self.timer=utils.Timer()
        self.module_name=module_name
        self.method_name=method_name
        self.method=DLJob.full_method_name(
            self.module_name,
            self.method_name)
        self.name=self._name(name,False)  
        self.save_results=save_results
        self.save_errors=save_errors
        self.results_dir=results_dir
        self.errors_dir=errors_dir
        self.results_timestamp=results_timestamp
        self.log=log
        self.log_dir=log_dir
        self.noisy=noisy
        self.cpu_job=cpu_job
        self.cpu_image=cpu_image
        self.gpu_image=gpu_image
        self.args, self.kwargs=self._args(args,kwargs)
        self.args_list=self._args_list(args_list)
        self.modules=modules
        self.requirements=self._requirements(requirements)
        self.data=data
        self.gpus=gpus
        self.platform_job=platform_job
        self.tasks=[]


    def run(self):
        if self.platform_job:
            return self.platform_run()
        else:
            return self.local_run()


    def local_run(self):
        self.name=self._name(self.name)
        start=self.timer.start()
        self.results_path=self._get_path(
            path=self.save_results,
            ext='nd_json',
            directory=self.results_dir,
            timestamp=start,
            add_timestamp=self.results_timestamp)
        self.errors_path=self._get_path(
            path=self.save_errors,
            ext='nd_json',
            directory=self.errors_dir,
            timestamp=start,
            add_timestamp=self.results_timestamp)
        self._set_loggers(timestamp=start)
        self._print(self.name,header=True)
        self._print("start: {}".format(start))
        self._print("local_run",True)
        func=DLJob.get_method(self.module_name,self.method_name)
        self._response_divider(True)
        if self.args_list:
            out=map(func,self.args_list)
            for o in list(out):
                self._print_result(o)
        else:
            out=func(*self.args,**self.kwargs)
            self._print_result(out)
        self._response_divider()
        self._print("complete: {}".format(self.timer.stop()))
        self._print("duration: {}".format(self.timer.duration()))
        self._close_loggers()
        return out


    def platform_run(self):
        self.name=self._name(self.name)
        start=self.timer.start()
        self.results_path=self._get_path(
            path=self.save_results,
            ext='nd_json',
            directory=self.results_dir,
            timestamp=start,
            add_timestamp=self.results_timestamp)
        self.errors_path=self._get_path(
            path=self.save_errors,
            ext='nd_json',
            directory=self.errors_dir,
            timestamp=start,
            add_timestamp=self.results_timestamp)
        self._set_loggers(timestamp=start)
        self._print(self.name,header=True)
        self._print("start: {}".format(start))
        self._print("platform_run",header=True)
        async_func=self._create_async_func()
        if self.args_list:
            out=self._run_platform_tasks(async_func)
        else:
            out=self._run_platform_task(async_func)
        self._response_divider()
        self._print("complete: {}".format(self.timer.stop()))
        self._print("duration: {}".format(self.timer.duration()))
        self._close_loggers()
        return out


    def print_logs(self):
        self._print(
            "logs[{}]".format(len(self.tasks)),
            header=True,
            force=True)
        if self.tasks:
            utils.line('=')
            utils.vspace(1)
            for task in self.tasks:
                task_log=task.log
                if not task_log.isspace():
                    self._print(
                        task_log,
                        plain_text=True,
                        force=True)                
                    utils.vspace(1)
            utils.line('=')
            utils.vspace()         
        elif self.platform_job:
            utils.line('=')
            self._print(
                'WARNING: no tasks found',
                plain_text=True,
                force=True)
            utils.line('=')
            utils.vspace()        



    #
    # INTERNAL
    #
    def _args(self,args,kwargs):
        """TODO: IF STR READ FROM FILE """
        return args, kwargs


    def _args_list(self,args_list):
        """TODO: IF STR READ FROM FILE """
        if isinstance(args_list,int):
            args_list=range(args_list)
        return args_list


    def _requirements(self,requirements):
        if isinstance(requirements,str) and os.path.isdir(requirements):
            requirements="{requirements}/requirements.txt"
        return requirements


    def _name(self,name,job_type=True):
        if not name:
            name=NAME_TMPL.format(self.method)
        if job_type:
            if self.platform_job:
                typ='platform'
            else:
                typ='local'
            name='{}-{}'.format(name,typ)
        return name


    def _get_path(self,path,ext=None,directory=None,timestamp=None,add_timestamp=True):
        if path:
            if not isinstance(path,str):
                path=self.name
                if add_timestamp:
                    if not timestamp:
                        timestamp=self.timer.now()
                        timestamp=re.sub(' ','.',timestamp)
                    path='{}_{}'.format(path,timestamp)
                if directory:
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    path='{}/{}'.format(directory,path)
                if ext:
                    path='{}.{}'.format(path,timestamp,ext)
            return path


    def _set_loggers(self,timestamp=None):
        if self.log:
            self.log_file=self._get_path(self.log,'log',self.log_dir,timestamp)
            self.log_handler=logging.FileHandler(self.log_file)
            self.logger=logging.getLogger(__name__)
            self.logger.addHandler(self.log_handler)
            self.logger.setLevel(logging.DEBUG)
            self.logger.info(self.log_file)
        else:
            self.log_file=None
            self.log_handler=False
            self.logger=False


    def _close_loggers(self):
        if self.log_handler:
            self.logger.removeHandler(self.log_handler)
            self.logger=None
            self.log_handler=None


    def _create_async_func(self):
        if self.cpu_job:
            image=self.cpu_image
            if self.gpus:
                self._print(CPU_JOB_WITH_GPUS)
                self.gpus=0
            else:
                self._print('cpu-job')
        elif (not self.gpus):
            image=self.cpu_image
            self._print(NO_GPUS,header=True)
        else:
            image=self.gpu_image
            self.gpus=int(self.gpus)
            self._print('gpu-job [{}]'.format(self.gpus))
        self._print("image: {}".format(image))
        return Tasks().create_function(
            self.method,
            name=self.name,
            image=image,
            include_data=self.data,
            include_modules=self.modules,
            requirements=self.requirements,
            gpus=self.gpus )


    def _run_platform_task(self,async_func):
        task=async_func(*self.args,**self.kwargs)
        self._print("group_id: {}".format(task.guid))
        self._print("task_id: {}".format(task.tuid))
        self.tasks=[task]
        self._response_divider(True)
        self._print_result(task.result)


    def _run_platform_tasks(self,async_func):
        self.tasks=async_func.map(self.args_list)
        nb_tasks=len(self.tasks)
        sample_ids=[t.tuid for t in self.tasks[:4]]
        if nb_tasks>4:
            elps=['...']
        else:
            elps=[]
        self._print("group_id: {}".format(self.tasks[0].guid))
        self._print("nb_tasks: {}".format(nb_tasks))
        self._print("task_ids: {}".format(sample_ids+elps))
        self._response_divider(True,False)
        for task in as_completed(self.tasks):
            if self.noisy: utils.vspace(1)
            if task.is_success:
                self._print_result(task.result)
            else:
                utils.line("*")
                self._print(task.exception,plain_text=True)
                self._print(task.log,plain_text=True)
                utils.line("*")


    def _response_divider(self,head=False,last_space=True):
        if head:
            self._print("running...")
        if self.noisy:
            utils.vspace(1)
            utils.line()
            if last_space: 
                utils.vspace(1)


    def _print_result(self,results):
        if results:
            results=json.loads(results)
            if isinstance(results,list):
                for result in results:
                    self._print(
                        self._as_json(result),
                        plain_text=True,
                        result=True,
                        error=self._is_error(result))
            else:
                self._print(
                    self._as_json(results),
                    plain_text=True,
                    result=True,
                    error=self._is_error(results))


    def _print(
            self,
            msg,
            header=False,
            plain_text=False,
            result=False,
            error=False,
            force=False):
        if msg: 
            if result and self.results_path:
                if error and self.errors_path:
                    nd_json.write(msg,self.errors_path)
                else:
                    nd_json.write(msg,self.results_path)
            if not utils.suppress(msg):
                if (not plain_text) and header:
                    if force or self.noisy: utils.vspace()
                    msg=HEADER_TMPL.format(msg)
                else:
                    msg=TRACE_TMPL.format(msg)
                if force or self.noisy:
                    print(msg)
                if self.logger:
                    self.logger.info(msg)


    def _as_json(self,value):
        if isinstance(value,str):
            return value
        else:
            return json.dumps(value)


    def _is_error(self,value):
        if isinstance(value,str):
            return re.search(r'^ERROR',value)
        else:
            return value.get('ERROR',False)





