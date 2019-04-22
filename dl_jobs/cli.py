import os,sys
sys.path.append(os.environ.get('PROJECT_DIR','..'))
import click
import dl_jobs.run as run
import dl_jobs.config as c
#
# DEFAULTS
#
IS_DEV=c.get('is_dev')



#
# CLI INTERFACE
#
@click.group()
def cli():
    pass


@click.command(help='args: see module')
@click.argument('module',type=str)
@click.option(
    '--method',
    help=f'method name',
    default='task',
    type=str)
@click.option(
    '--dev',
    help=f'<bool> run method outside of DL TASK',
    default=IS_DEV,
    type=bool)
@click.argument('args',type=int,nargs=-1)
def task(module,method,dev,args):
    run.launch(
        module=module,
        method=method,
        dev=dev,
        args=args)


@click.command(help='args: see module')
@click.argument('module',type=str)
@click.option(
    '--method',
    help=f'method name',
    default='task',
    type=str)
@click.option(
    '--dev',
    help=f'<bool> run method outside of DL TASK',
    default=IS_DEV,
    type=bool)
@click.argument('args',type=int,nargs=-1)
def tasks(module,method,dev,args_list):
    run.launch_tasks(
        module=module,
        method=method,
        dev=dev,
        args_list=args_list)


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
def generate_config(dl_image,dls_root,is_dev,noisy,force):
    c.generate(
        dl_image=dl_image,
        dls_root=dls_root,
        is_dev=is_dev,
        noisy=noisy,
        force=force)


#
# MAIN
#
cli.add_command(task)
cli.add_command(tasks)
cli.add_command(generate_config)
if __name__ == "__main__":
    cli()

