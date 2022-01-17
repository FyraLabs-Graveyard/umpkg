import koji
import os
import re
import sys
import umpkg_cli.cfg as config
import glob
import gitlab
import umpkg_cli.rpm_util as rpm_util
import umpkg_cli.koji_util as koji_util
import subprocess
class Command:
    def pushSRPM(tag, path):
        """
        Submits the SRPM to Koji
        """
        return os.system(f'koji build {tag} {path}')

    def push(self,tag, branch=None):
        """
        Pushes a git repository to Koji
        """
        # Rewritten becuase I just realized non-admins cannot push SRPMs to Koji, thus we will push SCM links to Koji instead
        # check if the SCM link is set in the config file
        cfg = config.read_config()
        if cfg['git_repo'] != '':
            # if it is, use the SCM link to push the package to Koji
            gitLink = cfg['git_repo']
        else:
            # else use git to get the remote URL
            gitLink = subprocess.run(['git', 'remote', 'get-url', 'origin'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
        # now let's prepend git+ to the URL so Koji can understand it
        gitLink = 'git+' + gitLink

        if not branch:
            # assume the branch name is the same as the tag name
            # get the latest commit hash of the branch
            branch = tag
        gitCommit = subprocess.run(['git', 'rev-parse', branch], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
        if gitCommit == branch:
            print(f'Branch {branch} not found')
            sys.exit(1)
        # append #gitCommit to the gitLink
        gitLink = gitLink + '#' + gitCommit
        print(gitLink)

        # check if the git repo has been pushed to origin
        if not subprocess.run(['git', 'cherry', '-v', 'origin/' + branch], stdout=subprocess.PIPE).stdout.decode('utf-8').strip() == '':
            # if it's not been pushed, error out
            print(f'Branch {branch} not pushed to origin, please push it first')
            sys.exit(1)

        return koji_util.build(tag,gitLink)


    def pullGitlab(self,project: str):
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
        return False

    def buildSrc(self,spec: str):
        """
        Builds the source RPM from the spec file
        """
        # first, check the config file for the build method
        cfg = config.read_config()
        # check if build_script is set in the config file
        if cfg['build_script'] != '':
            # run the build script as a subprocess
            subprocess.run(cfg['build_script'], shell=True)
        globalcfg = config.readGlobalConfig()
        try:
            build_method = cfg['build_method']
        except KeyError:
            build_method = globalcfg['build_method']
        if build_method == 'rpmbuild':
            # use rpmbuild to build the source RPM
            srpm = rpm_util.RPMBuild.buildSrc(spec)
            return srpm
        elif build_method == 'mock':
            # use mock to build the source RPM
            rpm_mock = rpm_util.Mock()
            srpm = rpm_mock.buildSrc(spec)
            return srpm

    def buildRPM(self,srpm):
        """
        Builds the binary RPM from the source RPM
        """
        # first, check the config file for the build method
        cfg = config.read_config()
        globalcfg = config.readGlobalConfig()
        try:
            build_method = cfg['build_method']
        except KeyError:
            build_method = globalcfg['build_method']
        if build_method == 'rpmbuild':
            # use rpmbuild to build the binary RPM
            rpm = rpm_util.RPMBuild.buildRPM(srpm)
            return rpm
        elif build_method == 'mock':
            # use mock to build the binary RPM
            rpm = rpm_util.Mock.buildRPM(srpm)
            return rpm