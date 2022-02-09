import os
import glob
import sys
import rpm

import umpkg.cfg as config

cfg = config.readGlobalConfig()
pkgconfig = config.read_config()

# Ported over from Lapis Utils
class RPM:
    def analyzeRPM(rpm_path: str):
        """[summary]
        Analyze an RPM to get its metadata
        """
        ts = rpm.TransactionSet()
        ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES)
        fdno = os.open(rpm_path, os.O_RDONLY)
        hdr = ts.hdrFromFdno(fdno)
        os.close(fdno)
        return hdr


class RPMBuild:
    def buildSrc(spec: str, source_dir: str = None, opts: list = None):
        """
        Builds a source RPM from a spec file
        """

        if source_dir is None:
            # check if srcdir is set
            if pkgconfig["srcdir"] == "":
                # if not set, use pwd
                source_dir = os.getcwd()
            else:
                # if set use that + the spec name without .spec
                source_dir = (
                    pkgconfig["srcdir"] + "/" + spec.split("/")[-1].split(".")[0]
                )
                # check if the directory exists
                if not os.path.exists(source_dir):
                    # if not, use $PWD
                    print(f"{source_dir} not found, using current directory")
                    source_dir = os.getcwd()
        # build the source
        print(f"Building source RPM from {source_dir}")
        command = [
            "rpmbuild",
            "-bs",
            spec,
            "--define",
            f'"_sourcedir {source_dir}"',
            "--define",
            f'"_srcrpmdir build/srpm"',
            "--define",
            f'"_rpmdir build/rpm"',
            "--undefine",
            "_disable_source_fetch",
        ]
        if opts is not None:
            command += opts
        command = " ".join(command)
        try:
            builder = os.system(command)
            if builder != 0:
                print(f"Error building {spec}")
                sys.exit(1)
        except:
            print("Error building source RPM")
            sys.exit(1)
        # get the newest file in build/srpm
        filelist = glob.glob("build/srpm/*.src.rpm")
        try:
            newest = max(filelist, key=os.path.getmtime)
            return newest
        except ValueError:
            print("No SRPM found")
            sys.exit(1)

    def buildRPM(srpm, opts=None):
        """
        Builds an RPM from an SRPM
        """
        command = [
            "rpmbuild",
            "-bb",
            srpm,
            "--define",
            '"_sourcedir ."',
            "--define",
            '"_rpmdir build/rpm"',
            "--define",
            '"_srcrpmdir build/srpm"',
            "--undefine",
            "_disable_source_fetch",
        ]
        if opts is not None:
            command += opts  # Opts should be an array of strings
        command = " ".join(command)
        try:
            builder = os.system(command)
            if builder != 0:
                print(f"Error building {srpm}")
                sys.exit(1)
        except:
            print("Error building RPM")
            sys.exit(1)
        # get the newest file in build/rpm
        filelist = glob.glob("build/rpm/*.rpm")
        try:
            newest = max(filelist, key=os.path.getmtime)
            return newest
        except ValueError:
            print("No RPM found")
            sys.exit(1)


class Mock:
    def buildSrc(self, spec: str, source_dir: str = None, opts: list = None):
        """
        Builds a source RPM from a spec file
        """

        if source_dir is None:
            # check if srcdir is set
            if pkgconfig["srcdir"] == "":
                # if not set, use pwd
                source_dir = os.getcwd()
            else:
                # if set use that + the spec name without .spec
                source_dir = (
                    pkgconfig["srcdir"] + "/" + spec.split("/")[-1].split(".")[0]
                )
                # check if the directory exists
                if not os.path.exists(source_dir):
                    # if not, use $PWD
                    print(f"{source_dir} not found, using current directory")
                    source_dir = os.getcwd()
        # build the source
        command = [
            "mock",
        ]
        if cfg["mock_chroot"] != "":
            command += ["-r", cfg["mock_chroot"]]
        command += [
            "--buildsrpm",
            "--spec",
            spec,
            "--sources",
            source_dir,
            "--resultdir",
            "build/srpm",
            "--enable-network",
        ]
        if opts is not None:
            command += opts

        command = " ".join(command)
        try:
            builder = os.system(command)
            if builder != 0:
                print(f"Error building {spec}")
                sys.exit(1)
        except:
            print("Error building source RPM")
            sys.exit(1)
        # get the newest file in build/srpm
        filelist = glob.glob("build/srpm/*.src.rpm")
        try:
            newest = max(filelist, key=os.path.getmtime)
            return newest
        except ValueError:
            print("No SRPM found")
            sys.exit(1)

    def buildRPM(self, srpm, opts=None):
        """
        Builds an RPM from an SRPM
        """
        command = [
            "mock",
        ]
        if cfg["mock_chroot"] != "":
            command += ["-r", cfg["mock_chroot"]]
        command += [
            "--rebuild",
            srpm,
            "--chain",
            "--localrepo",
            "build/repo",
            "--enable-network",
        ]
        if opts is not None:
            command += opts
        command = " ".join(command)
        try:
            builder = os.system(command)
        except OSError:
            print("Error building RPM")
            sys.exit(1)
