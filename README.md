#### DL JOBS (WIP)

_CLI and Helper modules for managing [DLTasks](https://docs.descarteslabs.com/guides/tasks.html)_

---

This code base is a simple wrapper for the [DLTasks API](https://docs.descarteslabs.com/guides/tasks.html) which includes:

1. A [CLI](#cli) that can be used to launch DLTasks
2. A [DLJob Class](#dljob) that simplifies the boilerplate code for creating/running/monitoring/logging tasks and saving results.
3. Allows you to easily switch back and forth between running your tasks locally or as a DLTask, making development quicker and easier.

<a name="overview"/>

##### OVERVIEW

Creating a `DLJob` looks a lot like creating a `DLTask`.  Consider the DescartesLabs [GPU example](https://docs.descarteslabs.com/guides/tasks.html#gpu-enabled-task-example)

```python
client = Tasks()
async_function = client.create_function(
    "task_examples.gpu.gpu_tf_ex",
    image=IMG,
    name='gpu_tf_ex',
    gpus=1,
    include_modules=['task_examples']
)
print("submitting a task")
task = async_function(3)
print("waiting for the task to complete")
async_function.wait_for_completion(show_progress=True)
print(task.result)
```

will become:

```python
job=DLJob(
        module_name='task_examples.gpu',
        method_name='gpu_tf_ex',
        args=[3],
        platform_job=True,
        cpu_job=False,
        modules=['task_examples'],
        gpus=1 )
job.run()
```

Looks pretty similar, except in the `DLJob` example we are writing logs to a file and writing the results to a `ndjson` file.  

Here are some modifications you can make:

  - replacing `args=[3]` with `args_list=[range(10)]` turns it into a multi-task job
  - changing `platform_job=True` to `platform_job=False` will run the task on your local machine rather than as a `DLTask`
  - for more interesting async functions you can pass kwargs (for a single-task job) or a list of kwarg dicts as your args_list (for multi-task jobs)

Its also super easy to build a CLI. Assume you have a module `run.task_examples`:

```python
# run.task_examples
from dl_jobs.job import DLJob

def gpu(value):
  return DLJob(
      module_name='task_examples.gpu',
      method_name='gpu_tf_ex',
      args=[value],
      platform_job=True,
      cpu_job=False,
      modules=['task_examples'],
      gpus=1 )
```

Then your can run this from your projects root directory like so

```bash
$ dl_jobs run task_examples.gpu 3
```

The CLI takes an unspecified number of args and kwargs so its easy to extend this.   

```python
# run.task_examples-2
from dl_jobs.job import DLJob
import dl_jobs.helpers as h

def gpu(value,method_name,**kwargs):
  platform_job=h.truthy(kwargs.get('platform',True)
  gpus=int(kwargs.get('gpus',1))
  return DLJob(
      module_name='task_examples.gpu',
      method_name=method_name,
      args=[value],
      platform_job=platform_job,
      cpu_job=False,
      modules=['task_examples'],
      gpus=gpus )
```
```bash
$ dl_jobs run task_examples.gpu 3 gpu_tf_ex platform_job=false
```

As a side note, the CLI has a number of optional params.  For example passing `platform_job=false` is (almost) equivalent to

```bash
$ dl_jobs run task_examples.gpu 3 gpu_tf_ex --dev true
```

Finally, there are a number of [decorators](#decorators) and [helper methods](#helpers) to make it easy to incorporate `dl_jobs` into your existing code base, along with a light-weight [ndjson](https://github.com/wri/dl_jobs/blob/master/dl_jobs/nd_json.py) reader-writer and a handy [timer](#timer).

Have Fun!

---

<a name="cli"/>

##### CLI

The CLI has three methods:

1. [`dl_jobs run ...`](#run): this is the main cli method and enables you to run jobs in your code base as DLTasks.
2. [`dl_jobs config ...`](#config): used to generate a config file to store defaults (such as which dl-image to run the job)
3. [`dl_jobs test ...`](#test): launches a hello-world style script. Its here as an example, a way to test the DL-platform, and show how cli args, kwargs, and options are handled.

When passing boolean OPTIONS to the CLI values of `false,none,no,null,f,n` and `0` evaluate to `False`, all others `True`. If you want the same for specific args or kwargs use `dl_jobs.helpers.truthy`,


<a name="run"/>

###### RUN

```bash
Usage: dl_jobs run [OPTIONS] METHOD [ARGS] [KWARGS]

  method: module_name or full method <module_name.method_name> 
  args: list of args (ie. arg1 arg2 arg3)
  kwargs: list of kwargs (ie. kwarg1=value1 kwarg2=value2)

Options:

  NOTE: 
    * All these options can be set through the config file
    * values false,none,no,null,f,n and 0 evaluate to False, all others True

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

```bash
Usage: dl_jobs config [OPTIONS] [KWARGS]

  generates config file
  pass kwargs to preset defaults in config file (ie `noisy=False`)

Options:
  --force BOOLEAN  if true overwrite existing config
```

**DEFAULT CONFIG:**

```
cpu_image: us.gcr.io/dl-ci-cd/images/tasks/public/py3.6/default:v2019.04.18-13-g565aebde
gpu_image: us.gcr.io/dl-ci-cd/images/tasks/public/py3.6-gpu/default:v2019.04.18-13-g565aebde
cpu_job: True
is_dev: True
default_method: 'task'
dls_root: 'dl_jobs'
module_dir: 'run'
results_dir: 'results'
errors_dir: 'errors'
log_dir: 'logs'
save_results: True
save_errors: True
log: True
print_logs: True
noisy: True
suppress: ['DeprecationWarning']
```

###### TEST

This command launches a DLTask(s) that simply returns the args,kwargs and options as JSON. It has 1 required argument (nb_jobs) which specifies the number of tasks to launch. As an example try running:

```bash
$ dl_jobs test 2 a b c hello=world --dev True
```

---

<a name="dljob"/>

##### DL-JOB

[dl_jobs.job](https://github.com/wri/dl_jobs/blob/master/dl_jobs/job.py) contains a class `DLJob`, and a `run` method that creates a instances of DLJob and launches them.  The main purpose of `run` is for the CLI.


```
    DLJob: a simple wrapper for the DLTasks-API

    NOTES: only `module_name` is required. The others have 
    defaults (most of which can be set in the config file).

    Args:
        module_name<str>: module path (ie module_name.submodule_name )
        method_name<str>: method name (defaults to 'task')
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

```

---

<a name="decorators"/>

##### DECORATORS

* expand_args: expand arg-list/kwarg-dict to args/kwargs
* attempt: catch exception and return exception in dict
* as_json: convert func output to json 

Thanks to the above decorators
1. The dictionary result gets converted to json so it can returned to a DLTask.
2. If there is an exception it will get caught and returned in json format (along with the args/kwargs calling the method).
3. Instead of passing (arg1,arg2,kwarg1='...',kwarg2='...') we can pass it two arguments: a list of args ( [arg1,arg2] ), and a kwarg dictionary ({ 'kwarg1':'...', 'kwarg1':'...' }).  This is useful when passing an `arg_list` to launch multiple jobs

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

* update_list
* copy_update
* is_str
* truthy

`update_list` is most important as it helps you construct arg_lists for launching multiple DLTasks. The method takes a list of values and dictionary and returns a list where the elements are (deep)copies of the dictionary with values updated by the elements of the list of values.

Here's an example:

```python
import dl_jobs.helpers as h
base={ 'action':'hello-world' }

print('key-value example:',"\nh.update_list(base,id_list,'system_id')\n")
id_list=range(3)
pprint(h.update_list(base,id_list,'system_id'))

print()

print('dict example:',"\nh.update_list(base,args_list)\n")
args_list=[{'system_id':1, 'out': 11},{'system_id':2, 'out': 22},{'system_id':3, 'out': 33}]
pprint(h.update_list(base,args_list))

"""output

key-value example: 
h.update_list(base,id_list,'system_id')

[{'action': 'hello-world', 'system_id': 0},
 {'action': 'hello-world', 'system_id': 1},
 {'action': 'hello-world', 'system_id': 2}]

dict example: 
h.update_list(base,args_list)

[{'action': 'hello-world', 'out': 11, 'system_id': 1},
 {'action': 'hello-world', 'out': 22, 'system_id': 2},
 {'action': 'hello-world', 'out': 33, 'system_id': 3}]

"""
```
 

<a name="timer"/>

###### TIMER

```python
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




