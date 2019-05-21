#### DL JOBS (WIP)

_CLI and Helper modules for managing [DLTasks](https://docs.descarteslabs.com/guides/tasks.html)_

---

This code base is a simple wrapper for the [DLTasks API](https://docs.descarteslabs.com/guides/tasks.html) which includes:

1. A simple [CLI](#cli) that can be used to launch DLTasks
2. A [DLJob Class](#dljob) that simplifies the boilerplate code for creating/running/monitoring/logging tasks and saving results.
3. Allows you to easily switch back and forth between running your tasks locally or as a DLJob, making development quicker and easier.

In addition there are a number of [decorators](#decorators) and [helper methods](#helpers) to make it easy to incorporate `dl_jobs` into your existing code base, along with a light-weight [ndjson](https://github.com/wri/dl_jobs/blob/master/dl_jobs/nd_json.py) reader-writer and a handy [timer](#timer).

Have Fun!

---

<a name="cli"/>

##### CLI

The CLI has three methods:

1. [`$dl_jobs run ...`](#run): this is the main cli method and enables you to run jobs in your code base as DLTasks.
2. [`$dl_jobs config ...`](#config): used to generate a config file to store defaults (such as which dl-image to run the job)
3. [`$dl_jobs test ...`](#test): launches a hello-world style script. Its here as an example, a way to test the DL-platform, and show how cli args, kwargs, and options are handled.

<a name="run"/>

###### RUN

```
Usage: dl_jobs run [OPTIONS] METHOD [ARGS] [KWARGS]

  method: module_name or full method <module_name.method_name> 
  args: list of args (ie. arg1 arg2 arg3)
  kwargs: list of kwargs (ie. kwarg1=value1 kwarg2=value2)

Options:

  NOTE: All these options can be set through the config file

  --dev BOOLEAN         <bool> Execute without DLPlatform
  --noisy BOOLEAN       <bool> be noisy
  --print_logs BOOLEAN  <bool> print log after execution
  --cpu_job TEXT        <str> dl image
  --cpu_image TEXT      <str> dl image
  --gpu_image TEXT      <str> dl image
```


<a name="config"/>

###### CONFIG

NOTE: for most values its probably easiest to first generate the config (yaml) file and the edit the values.  However when setting the GPU/CPU Images you can pass one of `[py27, py27_gpu, py36, py36_gpu, py37]` instead of including the whole dl-image address.

```
Usage: dl_jobs config [OPTIONS] [KWARGS]

  generates config file
  pass kwargs to preset defaults in config file (ie `noisy=False`)

Options:
  --force BOOLEAN  if true overwrite existing config
```

###### TEST

This command launches a DLTask(s) that simply returns the args,kwargs and options as JSON. It has 1 required argument (nb_jobs) which specifies the number of tasks to launch. As an example try running:

```
$ dl_jobs test 2 a b c hello=world --dev True
```

---

<a name="dljob"/>

##### DL-JOB

[dl_jobs.job](https://github.com/wri/dl_jobs/blob/master/dl_jobs/job.py) contains a class `DLJob`, and a `run` method that creates a instances of DLJob and launches them.  The main purpose of `run` is for the CLI.


```DLJob: a simple wrapper for the DLTasks-API

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
        save_results<bool|str>: save results as ndjson. if str: use str as filename
        results_dir<str>: directory to save results  
        results_timestamp<bool>: add timestamp to results filename
        log<bool|str>: write logs. if str: use str as filename
        log_dir<str>: log directory 
        *args: args for method when launching a single job (otherwise use args_list)
        **kwargs: kwargs for method when launching a single job (otherwise use args_list)

    Methods:
        run: launches DLTask(s)
        ...
```

---

<a name="decorators"/>

##### DECORATORS

* expand_args: expand arg-list/kwarg-dict to args/kwargs
* attempt: catch exception and return exception in dict
* as_json: convert func output to json 

Thanks to the above decorators
1. The dictionary result gets converted to json so it can be returned used for a DLTask.
2. If there is an exception it will get caught and returned in json format (along with the args/kwargs calling the method).
3. Instead of passing (arg1,arg2,kwarg1='...',kwarg2='...') we can pass it two arguments: a list of args ( [arg1,arg2] ), and a kwarg dictionary ({ 'kwarg1':'...', 'kwarg1':'...' }).  This is useful because when passing an `arg_list` to launch multiple jobs

```python
# example:

@as_json
@attempt
@expand_args
def do_work(arg1,arg2,kwarg1='value1',kwarg2='value2'):
    ... doing stuff ...
    return {
        'results': [1,2,3,4,5,6,7,8,9],
        'success': True
    }


```

---

<a name="other"/>

##### OTHER

<a name="helpers"/>

###### HELPERS

* copy_update
* update_list
* is_str
* truthy

<a name="timer"/>

###### TIMER

```
>>> from dl_jobs.utils import Timer
>>> t=Timer()
>>> t.start()
'May 20 2019 21:47:30'
>>> t.end()
>>> t.stop()
'May 20 2019 21:47:44'
>>> t.duration()
'0:00:14'
```




