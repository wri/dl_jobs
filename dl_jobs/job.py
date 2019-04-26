import os.path
from descarteslabs.client.services.tasks import Tasks, as_completed
from utils.timer import Timer


PLATFORM_JOB=False
NAME_TMPL='dljob_{}-{}'
HEADER_TMPL='DLJob.{}:'
TRACE_TMPL='- {}'

class DLJob(object):
    

    def __init__(self,
            func,
            dl_image,
            args=[],
            kwargs={},
            args_list=[],
            modules=None
            requirements=None,
            data=None,
            gpus=None
            platform_job=PLATFORM_JOB,
            name=None,
            noisy=True,
            log=None ):
        self.timer=Timer()
        self.func=func
        self.dl_image=dl_image
        self.args, self.kwargs=self._args(args,kwargs)
        self.args_list=self._args_list(args_list):
        self.modules=modules
        self.requirements=self._requirements(requirements)
        self.data=data
        self.gpus=gpus
        self.platform_job=platform_job
        self.name=self._name(name)
        self.noisy=noisy
        self.logger=self._logger(log)
        self.tasks=[]
        self._print(self.name,True)
        self._print("start: {}".format(self.timer.start()))


    def run(self):
        if self.platform_job:
            return self.local_run()
        else:
            return self.platform_run()


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
        else:
            self._print(
                'WARNING: no tasks found',
                plain_text=True,
                force=True)
            utils.vspace(1)
        utils.line('=')
        utils.vspace()



    def local_run(self):
        self._print("local_run",True)
        self._print("timestamp: {}".format(self.timer.now()))
        if self.args_list:
            out=map(self.func,self.args_list)
        else:
            out=self.func(*self.args,**self.kwargs)
        self._print("end: {}".format(self.timer.stop()))
        self._print("duration: {}".format(self.timer.duration()))
        return out


    def platform_run(self):
        self._print("platform_run",True)
        self._print("timestamp: {}".format(self.timer.now()))
        self.async_func=self._create_async_func()
        if self.args_list:
            out=self._run_platform_tasks()
        else:
            out=self._run_platform_task()
        if self.noisy: utils.vspace(1)
        if self.noisy: utils.line()
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


    def _name(self,name):
        if not name:
            if self.platform_job:
                typ='platform'
            else:
                typ='local'
            name=NAME_TMPL.format(self.func.__name__,typ)
        return name


    def _logger(self,log):
        if log:
            """ TODO: SET UP LOGGER """
            log=None
        return log


    def _create_async_func(timer,func):
        return Tasks().create_function(
            self.func,
            name=self.name,
            image=self.dl_image,
            include_data=self.data,
            include_modules=self.modules,
            requirements=self.requirements,
            gpus=self.gpus )


    def _run_platform_task(self):
        self._print("submit_task",True)
        task=self.func(*args,**kwargs)
        self.tasks=[task]
        self._print("running...")
        if self.noisy: utils.line()
        if self.noisy: utils.vspace(1)
        self._print(task.result,plain_text=True)


    def _run_platform_tasks(self):
        if self.noisy: utils.vspace()
        self._print("submit_task",True)
        self.tasks=func.map(self.args_list)
        self._print("running...")
        if self.noisy: utils.line()
        for task in as_completed(tasks):
            if self.noisy: utils.vspace(1)
            if task.is_success:
                self._print(task.result,plain_text=True)
            else:
                nb.line("*")
                self._print(task.exception,plain_text=True)
                self._print(task.log,plain_text=True)
                nb.line("*")


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




