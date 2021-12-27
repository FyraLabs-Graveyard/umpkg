import koji
import os
import re
import sys
import umpkg_cli.cfg as config
import glob

import gitlab

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
    else:
        specfile = os.path.splitext(os.path.basename(path))[0]
        print(specfile)
        src = os.path.join(os.getcwd(), src)
    # get file name without extension

    # if there's a build script defined
    if cfg['build_script'] != '':
        # build the source
        os.system(cfg['build_script'])

    args = [
        '--define', f'\"_sourcedir {src}\"',
        '--define', f'\"_srcrpmdir build/srpm\"',
        '--define', f'\"_rpmdir build/rpm\"',
        '--undefine _disable_source_fetch',
    ]
    args = ' '.join(args)
    print(args)
    os.system(f'rpmbuild -bs {path} {args}')
    #print(src)
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
        if specs == ['']:
            # find the first spec file in the current directory
            specs = glob.glob('*.spec')
            print(specs)
        for spec in specs:
            # add .spec to the spec name if it's not already there
            if not spec.endswith('.spec'):
                spec += '.spec'
            srpm = build_src(spec)
            os.system(f'koji build {tag} {srpm}')
    else:
        if not pkg.endswith('.spec'):
            pkg += '.spec'
        # check if the spec file exists
        if os.path.exists(pkg):
            srpm = build_src(pkg)
            os.system(f'koji build {tag} {srpm}')
        else:
            print(f'Spec {pkg} not found')
            sys.exit(1)

def pullGitlab(project: str):
    """
    Fetches a package from Ultramarine GitLab, then clone it
    """
    # list all projects in the dist-pkgs group using public API
    gl = gitlab.Gitlab('https://gitlab.ultramarine-linux.org/')
    print(f"Finding {project} in GitLab")
    group = gl.groups.get('dist-pkgs')
    projects = group.projects.list(all=True)
    for p in projects:
        path = p.path_with_namespace
        if path == f"dist-pkgs/{project}":
            print(f'Found {project}')
            # clone the project
            os.system(f'git clone {p.ssh_url_to_repo}')
            return os.getcwd() + '/' + project
        else:
            continue

    print(f'{project} not found')