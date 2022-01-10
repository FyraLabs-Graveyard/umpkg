import koji
import os
import re
import sys
import umpkg_cli.cfg as config
import glob
import gitlab
import umpkg_cli.rpm_util as rpm_util
import umpkg_cli.koji_util as koji_util

class Command:
    def pushSRPM(tag, path):
        """
        Submits the SRPM to Koji
        """
        return os.system(f'koji build {tag} {path}')

    def push(self,tag, pkg):
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
                # specs is now a list of spec files, so get the first one
                specs = [specs[0]]
                print(specs)
            else:
                for spec in specs:
                    # add .spec to the spec name if it's not already there
                    if not spec.endswith('.spec'):
                        spec += '.spec'
                    srpm = self.buildSrc(spec)
                    rpm = rpm_util.RPM.analyzeRPM(srpm)
                    print(f"Adding {rpm['name']} to Koji in case it's not already there")
                    koji_util.add(tag,rpm['name'])
                    print(f"Pushing {rpm['name']} to Koji")
                    koji_util.build(tag,srpm)
        else:
            if not pkg.endswith('.spec'):
                pkg += '.spec'
            # check if the spec file exists
            if os.path.exists(pkg):
                srpm = self.buildSrc(pkg)
                rpm = rpm_util.RPM.analyzeRPM(srpm)
                print(f"Adding {rpm['name']} to Koji in case it's not already there")
                koji_util.add(tag,rpm['name'])
                print(f"Pushing {rpm['name']} to Koji")
                koji_util.build(tag,srpm)
            else:
                print(f'Spec {pkg} not found')
                sys.exit(1)

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
            srpm = rpm_util.Mock.buildSrc(spec)
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