import koji
import os
import re
import sys
import umpkg_cli.cfg as config
import glob

def clone_repo(repo):
    """
    Clones a git repository into a temporary directory
    """
    path = os.path.join('/tmp', 'umpkg')
    os.makedirs(path, exist_ok=True)
    os.chdir(path)
    os.system(f'git clone {repo}')
    # filter the repo name from the URL
    repo_name = re.sub(r'^.*/', '', repo).split('.')[0]
    print(f'Cloned {repo_name} into {path}/{repo_name}')
    return path

def push_srpm(tag, path):
    """
    Submits the SRPM to Koji
    """
    return os.system(f'koji build {tag} {path}')

def build_src(path):
    """
    Builds an SRPM
    """
    cfg = config.read_config()
    src = cfg['srcdir']
    os.makedirs('build/srpm', exist_ok=True)
    os.makedirs('build/rpm', exist_ok=True)
    # if src is an empty string or pwd
    if src == '' or src == None or src == '$PWD' or src == '.':
        src = os.getcwd()
    # else if source is defined
    elif os.path.exists(src):
        # get the spec file name without the .spec
        specfile = os.path.basename(src).split('.')[0]
        print (f'Building {specfile}')

    args = [
        '--define', f'\"_sourcedir {src}/{path}\"',
        '--define', f'\"_specdir $PWD\"',
        '--define', f'\"_srcrpmdir build/srpm\"',
        '--define', f'\"_rpmdir build/rpm\"',
        '--undefine _disable_source_fetch',
    ]
    args = ' '.join(args)
    os.system(f'rpmbuild -bs {path} {args}')
    # get the newest file in build/srpm
    filelist = glob.glob('build/srpm/*.src.rpm')
    try:
        newest = max(filelist, key=os.path.getmtime)
        return newest
    except ValueError:
        print('No SRPM found')
        sys.exit(1)


def push(tag, pkg):
    """
    Builds and pushes the SRPM to Koji
    """
    cfg = config.read_config()
    src = cfg['srcdir']
    if not pkg:
        # split the spec names by space
        specs = cfg['spec'].split(' ')
        for spec in specs:
            # add .spec to the spec name if it's not already there
            if not spec.endswith('.spec'):
                spec += '.spec'
            srpm = build_src(spec)
            os.system(f'koji build {tag} {srpm}')
    else:
        if not pkg.endswith('.spec'):
            pkg += '.spec'
        srpm = build_src(pkg)
        os.system(f'koji build {tag} {srpm}')