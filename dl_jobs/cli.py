from __future__ import print_function
import os,sys
sys.path.append(os.environ.get('PROJECT_DIR','..'))
import re
import click
import dl_jobs.job as job
import dl_jobs.config as c
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
TEST_JOB_HELP="""test_job: hello-world tasks to test the DLTask system
Args:
    nb_jobs: number of tasks to launch
    *args
    **kwargs
Returns:
    json object with options, args and kwargs passed to the cli

"""






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
    args,kwargs=_args_kwargs(ctx.args)
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
    '--info',
    '-i',
    is_flag=True,
    help='print current or default config',
    type=bool)
@click.option(
    '--force',
    '-f',
    default=False,
    help='if true overwrite existing config',
    type=bool)
@click.pass_context
def generate_config(ctx,info,force):
    if info:
        print("dl_jobs.config:")
        for key in c.CONFIG:
            print("\t{}: {}".format(key,c.CONFIG[key]))
    else:
        _,kwargs=_args_kwargs(ctx.args)
        c.generate( force=force, **kwargs )




@click.command(
    help=TEST_JOB_HELP,
    context_settings=ARG_KWARGS_SETTINGS ) 
@click.argument('nb_jobs',type=int)
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
def test(ctx,nb_jobs,dev,noisy,print_logs,cpu_job,cpu_image,gpu_image):
    args,kwargs=_args_kwargs(ctx.args)
    args=[nb_jobs]+args
    kwargs['options']={
        'dev': dev,
        'noisy': noisy,
        'print_logs': print_logs,
        'cpu_job': cpu_job,
        'cpu_image': cpu_image,
        'gpu_image': gpu_image
    }
    job.run(
        module_dir=None,
        module_name='dl_jobs.test_jobs',
        cpu_job=cpu_job,
        cpu_image=cpu_image,
        gpu_image=gpu_image,
        args=args,
        kwargs=kwargs,
        dev=dev,
        noisy=noisy,
        print_logs=print_logs )



#
# HELPERS
#
def _args_kwargs(ctx_args):
    args=[]
    kwargs={}
    for a in ctx_args:
        if re.search('=',a):
            k,v=a.split('=')
            kwargs[k]=v
        else:
            args.append(a)
    return args,kwargs


#
# MAIN
#
cli.add_command(run)
cli.add_command(generate_config)
cli.add_command(test)
if __name__ == "__main__":
    cli()

