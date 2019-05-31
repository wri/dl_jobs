from __future__ import print_function
""" CONSTANTS
"""
#
# DL_IMAGES
#
PY27='us.gcr.io/dl-ci-cd/images/tasks/public/py2/default:v2019.04.18-13-g565aebde'
PY27_GPU='us.gcr.io/dl-ci-cd/images/tasks/public/py2-gpu/default:v2019.04.18-13-g565aebde'
PY36='us.gcr.io/dl-ci-cd/images/tasks/public/py3.6/default:v2019.04.18-13-g565aebde'
PY36_GPU='us.gcr.io/dl-ci-cd/images/tasks/public/py3.6-gpu/default:v2019.04.18-13-g565aebde'
PY37='us.gcr.io/dl-ci-cd/images/tasks/public/py3.7/default:v2019.02.12'

IMAGES={
    'py27': PY27,   
    'py27_gpu': PY27_GPU,   
    'py36': PY36,   
    'py36_gpu': PY36_GPU,   
    'py37': PY37,   
}

#
# USER CONFIG:
#
CPUS=1
GPUS=0
CPU_JOB=True
CPU_IMAGE=PY36
GPU_IMAGE=PY36_GPU
DLS_ROOT='dl_jobs'
IS_DEV=True
NOISY=True
MODULE_DIR='run'
PRINT_LOGS=True
DEFAULT_METHOD='task'
SUPPRESS=['DeprecationWarning']
SAVE_RESULTS=True
SAVE_ERRORS=True
RESULTS_DIR='results'
ERRORS_DIR='errors'
LOG=True
LOG_DIR='logs'


#
# DL_JOBS CONFIG:
#
DL_JOBS_CONFIG_PATH='dl_jobs.config.yaml'
DL_JOBS_CONFIG_COMMENT="dl_jobs: config"
DL_JOBS_CONFIG_EXISTS="dl_jobs.config.yaml exists.  use force=True to overwrite."
DL_JOBS_CONFIG_CREATED="dl_jobs.config.yaml created. edit file to change configuration"

