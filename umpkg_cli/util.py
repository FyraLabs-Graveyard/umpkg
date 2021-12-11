import koji
import os
import re
import sys
import umpkg_cli.cfg as config
import glob
#profile = koji.get_profile_module('ultramarine')

#session = koji.ClientSession(profile.config.server) # TODO: use this instead of wrapping the CLI


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

def build_srpm(tag, path):
    """
    Submits the SRPM to Koji
    """
    return os.system(f'koji build {tag} {path}')

def build_src(tag, path):
    """
    Builds the source RPM from the config file
    """
    os.chdir(path)
    cfg = config.read_config()
    src = cfg['srcdir']
    os.makedirs('build/srpm', exist_ok=True)
    os.makedirs('build/rpm', exist_ok=True)
    spec = cfg['spec'].split(' ')

    # if spec is empty
    if spec == ['']:
        print('No spec file specified in config file, finding the first possible spec file')
        try:
            specfile = glob.glob('*.spec')[0].split('.')[0]
            spec = [specfile + '.spec']
        except IndexError:
            print('No spec file found in current directory')
            sys.exit(1)
        print(f'Found {spec}')


    # add .spec to each entry if it doesn't have it
    for i in range(len(spec)):
        if not spec[i].endswith('.spec'):
            spec[i] = spec[i] + '.spec'


    for s in spec:
        # if file doesn't exist
        if not os.path.isfile(s):
            print(f'Spec file {s} not found')
            sys.exit(1)

    print(spec)
    # check if the spec option has multiple values split by a space
    print(f'Building {spec}')
    if len (spec) > 1:
        for s in spec:
            # get the file name and remove .spec from the end
            sr = s.split('/')[-1].split('.')[0]
            print(f'Building {s}')
            args = [
                '--define', f'\"_sourcedir {src}/{sr}\"',
                '--define', f'\"_specdir $PWD\"',
                '--define', f'\"_srcrpmdir build/srpm\"',
                '--define', f'\"_rpmdir build/rpm\"',
            ]
            args = ' '.join(args)
            print(f'rpmbuild {args} {s}')
            os.system(f'rpmbuild -bs {s}.spec {args}')
            # get the path to the latest SRPM
            srpm_list = glob.glob('build/srpm/*')
            try:
                srpm = max(srpm_list, key=os.path.getctime)
            except ValueError:
                print('No SRPMs found')
                return
            if not srpm: # additional check for empty list
                return 255
            print('Pushing {srpm} to Koji...')
            os.system(f'koji build --nowait {tag} {srpm}')
            return


    else:
        # let's assemble the arguments for RPMBuild by making it a list
        args = [
            '--define', f'\"_sourcedir {src}\"',
            '--define', f'\"_specdir $PWD\"',
            '--define', f'\"_srcrpmdir build/srpm\"',
            '--define', f'\"_rpmdir build/rpm\"',
        ]
        args = ' '.join(args)
        spec = spec[0]


        build = os.system(f'rpmbuild -bs {spec} {args}')
        # get the exit code of the build
        # if code is not 0, exit with error
        if build != 0:
            print(f'Error building {spec}')
            return os.error
        # except the command exiting with an error code
        srpm_list = glob.glob('build/srpm/*')
        srpm = max(srpm_list, key=os.path.getctime)
        print(f'Pushing {srpm} to Koji...')
        os.system(f'koji build {tag} {srpm}')

