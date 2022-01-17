import os
import umpkg_cli.util as util
import umpkg_cli.cfg as config
import typer

cfg = config.readGlobalConfig()
pkgconfig = config.read_config()

app = typer.Typer()
# Yet another Koji CLI wrapper, this time made specifically for UMPKG
@app.command()
def build(tag,path):
    command =[
        'koji'
    ]
    if cfg['koji_profile'] != '':
        command.append(f'--profile={cfg["koji_profile"]}')
    command += [
        'build',
        tag,
        path,
    ]
    print(command)
    return os.system(' '.join(command))
@app.command()
def add(tag,package):
    command =[
        'koji',
    ]
    if cfg['koji_profile'] != '':
        command.append(f'--profile={cfg["koji_profile"]}')
    command += [
        'add-pkg',
        tag,
        package,
    ]
    if cfg['username'] == '':
        # get username from environment
        cfg['username'] = os.environ['USER']
    command.append(f'--owner={cfg["username"]}')
    return os.system(' '.join(command))
