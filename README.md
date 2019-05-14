#### DL JOBS (WIP)

_CLI and Helper modules for managing [DLTasks](https://docs.descarteslabs.com/guides/tasks.html)_

---

##### CLI

```bash
# generate config 
$ dl_jobs config ...

# run job
$ dl_jobs run module[.methods] ...
```

```bash
$ dl_jobs --help
Usage: dl_jobs [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  config  generate config file
  run     method: module_name or full method <module_name.method_name>



$ dl_jobs run --help
Usage: dl_jobs run [OPTIONS] METHOD

  method: module_name or full method <module_name.method_name>

Options:
  --dev BOOLEAN         <bool> Execute without DLPlatform
  --noisy BOOLEAN       <bool> be noisy
  --print_logs BOOLEAN  <bool> print log after execution
  --image TEXT          <str> dl image
  --help                Show this message and exit.
```

---

##### MODULE

```python
job=DLJob(...)
job.run()
```

---

##### HELPERS

- `dl_jobs.decorators`
- `dl_jobs.image_io`
- `dl_jobs.utils`  