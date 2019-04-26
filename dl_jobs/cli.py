from __future__ import print_function
import os,sys
sys.path.append(os.environ.get('PROJECT_DIR','..'))
import re
import click
import dl_jobs.run
import dl_jobs.config as c
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
ARGS_LIST_HELP='<bool> True if multi-task job. Can also set via kwarg' 
ARG_KWARGS_SETTINGS={
    'ignore_unknown_options': True,
    'allow_extra_args': True
}
FALSEY=['false','none','no','null','f','n','0']



#
# HELPERS
#
def args_kwargs(ctx_args):
    args=[]
    kwargs={}
    for a in ctx_args:
        if re.search('=',a):
            k,v=a.split('=')
            kwargs[k]=v
        else:
            args.append(a)
    return args,kwargs


def truthy(value):
    if isinstance(value,bool) or isinstance(value,int):
        return value
    elif isinstance(value,str):
        value=value.lower()
        return value not in FALSEY
    else:
        raise ValueError('truthy: value must be str,int,bool')


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
@click.option(
    '--args_list',
    help=ARGS_LIST_HELP,
    default=False,
    type=bool)
@click.pass_context
def run(ctx,method,dev,noisy,print_logs,image,args_list):
    if re.search(r'\.',method):
        parts=method.split('.')
        method=parts[-1]
        module='.'.join(parts[:-1])
    else:
        module=method
        method=DEFAULT_METHOD
    args,kwargs=args_kwargs(ctx.args)
    args_list=args_list or kwargs.pop('args_list',False)
    if truthy(args_list):
        args_list=args
        args=[]
    dl_jobs.run.launch(
        module_name=module,
        method_name=method,
        dl_image=image,
        args=args,
        kwargs=kwargs,
        args_list=args_list,
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

