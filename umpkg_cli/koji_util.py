import os
import umpkg_cli.util as util
import umpkg_cli.cfg as config

cfg = config.readGlobalConfig()
pkgconfig = config.read_config()


# Yet another Koji CLI wrapper, this time made specifically for UMPKG

def build(tag,path):
    command =[
        'koji',
        'build',
        tag,
        path,
    ]
    if cfg['koji_profile'] != '':
        command.append(f'--profile={cfg["koji_profile"]}')

    return os.system(' '.join(command))

def add(tag,package):
    command =[
        'koji',
        'add-pkg',
        tag,
        package,
    ]
    if cfg['koji_profile'] != '':
        command.append(f'--owner={cfg["koji_profile"]}')
    if cfg['username'] == '':
        # get username from environment
        cfg['username'] = os.environ['USER']
    command.append(f'--owner={cfg["username"]}')
    return os.system(' '.join(command))
