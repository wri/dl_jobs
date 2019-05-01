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
DL_IMAGE=c.get('dl_image')
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
# kwargs
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
    '--image',
    help=DL_IMAGE_HELP,
    default=DL_IMAGE,
    type=str)
@click.pass_context
def run(ctx,method,dev,noisy,print_logs,image):
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
        dl_image=image,
        args=args,
        kwargs=kwargs,
        dev=dev,
        noisy=noisy,
        print_logs=print_logs )




@click.command(name='config',help='generate config file')
@click.argument('dl_image',default=c.get('dl_image'))
@click.argument('dls_root',default=c.get('dls_root'))
@click.argument('is_dev',default=c.get('is_dev'))
@click.argument('noisy',default=c.get('noisy'))
@click.option(
    '--force',
    default=False,
    help='if true overwrite existing config',
    type=bool)
@click.pass_context
def generate_config(ctx,dl_image,dls_root,is_dev,noisy,force):
    c.generate(
        dl_image=dl_image,
        dls_root=dls_root,
        is_dev=is_dev,
        noisy=noisy,
        force=force)


#
# MAIN
#
cli.add_command(run)
cli.add_command(generate_config)
if __name__ == "__main__":
    cli()

