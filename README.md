#### DL JOBS (WIP)

_CLI and Helper modules for managing [DLTasks](https://docs.descarteslabs.com/guides/tasks.html)_

---

This code base is a simple wrapper for the [DLTasks API](https://docs.descarteslabs.com/guides/tasks.html) which includes:

1. A simple [CLI](#cli) that can be used to launch DLTasks
2. A [DLJob Class](#dljob) that simplifies the boilerplate code for creating/running/monitoring/logging tasks and saving results.
3. Allows you to easily switch back and forth between running your tasks locally or as a DLJob, making development quicker and easier.

In addition there are a number of [decorators](https://github.com/wri/dl_jobs/blob/master/dl_jobs/decorators.py) and [helper methods](https://github.com/wri/dl_jobs/blob/master/dl_jobs/helpers.py) to make it easy to incorporate `dl_jobs` into your existing code base, along with a light-weight [ndjson](https://github.com/wri/dl_jobs/blob/master/dl_jobs/nd_json.py) reader-writer and a handy [timer](https://github.com/wri/dl_jobs/blob/master/dl_jobs/utils.py).

Have Fun!

---

<a name="cli"/>
##### CLI

The CLI has three methods:

1. [`$dl_jobs run ...`](#run): this is the main cli method and enables you to run jobs in your code base as DLTasks.
2. `$dl_jobs config ...`: used to generate a config file to store defaults (such as which dl-image to run the job)
3. `$dl_jobs test ...`: launches a hello-world style script. Its here as an example, a way to test the DL-platform, and show how cli args, kwargs, and options are handled.

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


---

<a name="dljob"/>
##### DL-JOB

```python
job=DLJob(...)
job.run()
```

---

<a name="helpers"/>
##### HELPERS

---

<a name="decorators"/>
##### DECORATORS


