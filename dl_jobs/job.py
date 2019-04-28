import os.path
from importlib import import_module
from descarteslabs.client.services.tasks import Tasks, as_completed
import dl_jobs.utils as utils


PLATFORM_JOB=False
NAME_TMPL='dljob_{}'
HEADER_TMPL='DLJob.{}:'
TRACE_TMPL='- {}'


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
            dl_image,
            args_list=None,
            modules=None,
            requirements=None,
            data=None,
            gpus=None,
            platform_job=PLATFORM_JOB,
            name=None,
            noisy=True,
            log=None,
            *args,
            **kwargs):
        self.timer=utils.Timer()
        self.module_name=module_name
        self.method_name=method_name
        self.method=DLJob.full_method_name(
            self.module_name,
            self.method_name)
        self.name=self._name(name,False)
        self.logger=self._logger(log)
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
        self._print(self.name,header=True)
        self._print("start: {}".format(self.timer.start()))
        self._print("local_run",True)
        func=DLJob.get_method(self.module_name,self.method_name)
        self._print("running...")
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
        return out


    def platform_run(self):
        self.name=self._name(self.name)
        self._print(self.name,header=True)
        self._print("start: {}".format(self.timer.start()))
        self._print("platform_run",True)
        async_func=self._create_async_func()
        if self.args_list:
            out=self._run_platform_tasks(async_func)
        else:
            out=self._run_platform_task(async_func)
        self._response_divider()
        self._print("complete: {}".format(self.timer.stop()))
        self._print("duration: {}".format(self.timer.duration()))
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


    def _logger(self,log):
        if log:
            """ TODO: SET UP LOGGER """
            log=None
        return log


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
        self._print("nb_tasks: {}".format(len(self.tasks)))
        self._response_divider(True,False)
        for task in as_completed(self.tasks):
            if self.noisy: utils.vspace(1)
            if task.is_success:
                self._print(task.result,plain_text=True)
            else:
                nb.line("*")
                self._print(task.exception,plain_text=True)
                self._print(task.log,plain_text=True)
                nb.line("*")


    def _response_divider(self,head=False,last_space=True):
        if head:
            self._print("running...")
        if self.noisy:
            utils.vspace(1)
            utils.line()
            if last_space: 
                utils.vspace(1)


    def _print(self,msg,header=False,plain_text=False,force=False):
        if (not plain_text) and header:
            if force or self.noisy: utils.vspace()
            msg=HEADER_TMPL.format(msg)
        else:
            msg=TRACE_TMPL.format(msg)
        if force or self.noisy:
            print(msg)
        if self.logger:
            pass




