#### DL JOBS (WIP)

_CLI and Helper modules for managing [DLTasks](https://docs.descarteslabs.com/guides/tasks.html)_

---

##### MODULE

- `dl_jobs.run`

```python
run.launch('np_tests')
```

---

##### CLI

```bash
dl_jobs task np_tests
```

```bash
$ dl_jobs --help
Usage: dl_jobs [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  config  generate config file
  task    args: see module
  tasks   args: see module
```

---

##### HELPERS

- `dl_jobs.catalog`
- `dl_jobs.storage` 
- `dl_jobs.image_io`
- `dl_jobs.utils`  