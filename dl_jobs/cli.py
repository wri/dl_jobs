from __future__ import print_function
import os,sys
sys.path.append(os.environ.get('PROJECT_DIR','..'))
import re
import click
import dl_jobs.job as job
import dl_jobs.config as c
import dl_jobs.utils as utils
#
# DEFAULTS
#
IS_DEV=c.get('is_dev')
NOISY=c.get('noisy')
PRINT_LOG=c.get('print_logs')
CPU_JOB=c.get('cpu_job')
CPU_IMAGE=c.get('cpu_image')
GPU_IMAGE=c.get('gpu_image')
DEFAULT_METHOD=c.get('default_method')
DEV_HELP='<bool> Execute without DLPlatform'
NOISE_HELP='<bool> be noisy'
PRINT_LOGS_HELP='<bool> print log after execution'
DL_IMAGE_HELP='<str> dl image'
ARG_KWARGS_SETTINGS={
    'ignore_unknown_options': True,
    'allow_extra_args': True
}






#
# CLI INTERFACE
#
@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj={}


@click.command(
    help='method: module_name or full method <module_name.method_name>',
    context_settings=ARG_KWARGS_SETTINGS ) 
@click.argument('method',type=str)
@click.option(
    '--dev',
    help=DEV_HELP,
    default=IS_DEV,
    type=bool)
@click.option(
    '--noisy',
    help=NOISE_HELP,
    default=NOISY,
    type=bool)
@click.option(
    '--print_logs',
    help=PRINT_LOGS_HELP,
    default=PRINT_LOG,
    type=bool)
@click.option(
    '--cpu_job',
    help=DL_IMAGE_HELP,
    default=CPU_JOB,
    type=str)
@click.option(
    '--cpu_image',
    help=DL_IMAGE_HELP,
    default=CPU_IMAGE,
    type=str)
@click.option(
    '--gpu_image',
    help=DL_IMAGE_HELP,
    default=GPU_IMAGE,
    type=str)
@click.pass_context
def run(ctx,method,dev,noisy,print_logs,cpu_job,cpu_image,gpu_image):
    if re.search(r'\.',method):
        parts=method.split('.')
        method=parts[-1]
        module='.'.join(parts[:-1])
    else:
        module=method
        method=DEFAULT_METHOD
    args,kwargs=utils.args_kwargs(ctx.args)
    job.run(
        module_name=module,
        method_name=method,
        cpu_job=cpu_job,
        cpu_image=cpu_image,
        gpu_image=gpu_image,
        args=args,
        kwargs=kwargs,
        dev=dev,
        noisy=noisy,
        print_logs=print_logs )




@click.command(
    name='config',    
    help='generate config file: pass kwargs (ie $dl_jobs config dl_image=py36 dev=true)',
    context_settings=ARG_KWARGS_SETTINGS ) 
@click.option(
    '--force',
    default=False,
    help='if true overwrite existing config',
    type=bool)
@click.pass_context
def generate_config(ctx,force):
    _,kwargs=utils.args_kwargs(ctx.args)
    c.generate( force=force, **kwargs )


#
# MAIN
#
cli.add_command(run)
cli.add_command(generate_config)
if __name__ == "__main__":
    cli()

