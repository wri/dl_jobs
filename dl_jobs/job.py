from __future__ import print_function
import os,sys
import warnings
from importlib import import_module
import logging
from descarteslabs.client.services.tasks import Tasks, as_completed
import dl_jobs.config as c
import dl_jobs.utils as utils
warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.getcwd())
"""
#
# CONSTANTS/DEFAULTS
#
"""
PLATFORM_JOB=False
NAME_TMPL='dljob_{}'
HEADER_TMPL='DLJob.{}:'
NO_JOB_TMPL='[WARNING] DLJob.run: no job found for {}.{}'
TRACE_TMPL='- {}'
DL_IMAGE=c.get('dl_image')
IS_DEV=c.get('is_dev')
NOISY=c.get('noisy')
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
        if noisy and (nb_jobs>1): utils.line()
        else:
            print(NO_JOB_TMPL.format(module_name,method_name))




"""
#
# DLJob: CLASS
#
"""
class DLJob(object):
    


    @staticmethod
    def get_method(module_name,method_name):
        module=import_module(module_name)
        return getattr(module,method_name)


    @staticmethod
    def full_method_name(module_name,method_name):
        return '.'.join([module_name,method_name])


    def __init__(self,
            module_name,
            method_name,
            dl_image=None,
            args_list=None,
            modules=None,
            requirements=None,
            data=None,
            gpus=None,
            platform_job=PLATFORM_JOB,
            name=None,
            noisy=True,
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
        self.log=log
        self.log_dir=log_dir
        self.noisy=noisy
        self.dl_image=dl_image
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


    def print_logs(self):
        self._print(
            "logs[{}]".format(len(self.tasks)),
            header=True,
            force=True)
        utils.line('=')
        utils.vspace(1)
        if self.tasks:
            for task in self.tasks:
                self._print(
                    task.log,
                    plain_text=True,
                    force=True)                
                utils.vspace(1)
        elif self.platform_job:
            self._print(
                'WARNING: no tasks found',
                plain_text=True,
                force=True)
            utils.vspace(1)
        else:
            self._print(
                'INFO: no logs (job run locally)',
                plain_text=True,
                force=True)
            utils.vspace(1)
        utils.line('=')
        utils.vspace()



    def local_run(self):
        self.name=self._name(self.name)
        start=self.timer.start()
        self._set_logger(timestamp=start)
        self._print(self.name,header=True)
        self._print("start: {}".format(start))
        self._print("local_run",True)
        func=DLJob.get_method(self.module_name,self.method_name)
        self._response_divider(True)
        if self.args_list:
            out=map(func,self.args_list)
            self._print("{}".format(list(out)))
        else:
            out=func(*self.args,**self.kwargs)
            self._print("{}".format(out))
        self._response_divider()
        self._print("complete: {}".format(self.timer.stop()))
        self._print("duration: {}".format(self.timer.duration()))
        self._close_logger()
        return out


    def platform_run(self):
        self.name=self._name(self.name)
        start=self.timer.start()
        self._set_logger(timestamp=start)
        self._print(self.name,header=True)
        self._print("start: {}".format(start))
        self._print("platform_run",True)
        async_func=self._create_async_func()
        if self.args_list:
            out=self._run_platform_tasks(async_func)
        else:
            out=self._run_platform_task(async_func)
        self._response_divider()
        self._print("complete: {}".format(self.timer.stop()))
        self._print("duration: {}".format(self.timer.duration()))
        self._close_logger()
        return out



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


    def _set_logger(self,timestamp=None):
        if self.log:
            if isinstance(self.log,str):
                log_filename=self.log
            else:
                if not timestamp:
                    timestamp=self.timer.now()
                log_filename='{}_{}.log'.format(self.name,timestamp)
            if self.log_dir:
                if not os.path.exists(self.log_dir):
                    os.makedirs(self.log_dir)
                log_filename='{}/{}'.format(self.log_dir,log_filename)
            self.file_handler=logging.FileHandler(log_filename)
            self.logger=logging.getLogger(__name__)
            self.logger.addHandler(self.file_handler)
            self.logger.setLevel(logging.DEBUG)
            self.logger.info(log_filename)
        else:
            self.logger=False
            self.file_handler=False


    def _close_logger(self):
        if self.file_handler:
            self.logger.removeHandler(self.file_handler)
            self.logger=None
            self.file_handler=None


    def _create_async_func(self):
        return Tasks().create_function(
            self.method,
            name=self.name,
            image=self.dl_image,
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
        self._print(task.result,plain_text=True)


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
                self._print(task.result,plain_text=True)
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


    def _print(self,msg,header=False,plain_text=False,force=False):
        if msg and (not utils.suppress(msg)):
            if (not plain_text) and header:
                if force or self.noisy: utils.vspace()
                msg=HEADER_TMPL.format(msg)
            else:
                msg=TRACE_TMPL.format(msg)
            if force or self.noisy:
                print(msg)
            if self.logger:
                self.logger.info(msg)




