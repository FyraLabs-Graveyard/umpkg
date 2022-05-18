"""From the old version"""
from asyncio import sleep
from contextlib import suppress
from glob import glob
from os import getcwd, path
import os
from pathlib import Path
import shutil
from typing import Callable

from .utils import err, run
from .config import read_cfg, read_globalcfg
from .log import get_logger

logger = get_logger(__name__)
cfg = read_globalcfg()
pkgconfig = read_cfg()
SLEEP = 0.2  # sleep interval

def _buildsrc(fn: Callable[[str, str], list[str]]):
    async def buildsrc(spec: str, srcdir: str = '', opts: list[str] = []):
        """Builds a source RPM from a spec file"""
        srcdir = srcdir or path.join(pkgconfig['srcdir'], Path(spec).stem)
        if not path.exists(srcdir):
            logger.warn("No valid srcdir cfg, using cwd")
            srcdir = getcwd()

        logger.info(f"{spec[:-5]}: building from {srcdir}")
        cmd = fn(spec, srcdir) + opts
        
        proc = run(cmd)
        while not (rc := proc.poll()):
            await sleep(SLEEP)
        if rc:
            return err('FAIL TO BUILD SRPM', proc, spec=spec, log=logger)
        # get the newest file in build/srpm
        files = glob("build/srpm/*.src.rpm")
        with suppress(ValueError):
            return max(files, key=path.getmtime)
        logger.error(f"{spec[:-5]}: No SRPM found")
    return buildsrc

def _buildrpm(fn: Callable[[str], list[str]]):
    async def buildRPM(srpm: str, opts: list[str] = []):
        cmd = fn(srpm) + opts
        proc = run(cmd)
        while not (rc := proc.poll()):
            await sleep(SLEEP)
        if rc:
            return err('FAIL TO BUILD RPM', proc, srpm=srpm, log=logger)
        # get the newest file in build/rpm
        files = glob("build/rpm/*.rpm")
        with suppress(ValueError):
            return max(files, key=path.getmtime)
        logger.error(f"{srpm[:-5]}: No RPM found")
    return buildRPM


class RPMBuild:
    @staticmethod
    @_buildsrc
    def buildsrc(spec: str, srcdir: str):
        return [
            "rpmbuild",
            "-bs",
            spec,
            "--define",
            f'_sourcedir {srcdir}',
            "--define",
            '_srcrpmdir build/srpm',
            "--define",
            '_rpmdir build/rpm',
            "--undefine",
            "_disable_source_fetch",
        ]

    #? idk if we should have this but I've done it anyway
    @staticmethod
    @_buildrpm
    def buildRPM(srpm: str):
        return [
            "rpmbuild",
            "-bb",
            srpm,
            "--define",
            '_sourcedir .',  #! this looks... huh?
            "--define",
            '_rpmdir build/rpm',
            "--define",
            '_srcrpmdir build/srpm',
            "--undefine",
            "_disable_source_fetch",
        ]


class Mock:
    @staticmethod
    @_buildsrc
    def buildsrc(spec: str, srcdir: str):
        return [
            "--buildsrpm",
            "--spec",
            spec,
            "--sources",
            srcdir,
            "--resultdir",
            "build/srpm",
            "--enable-network"
        ]

    @staticmethod
    @_buildrpm
    def buildRPM(srpm: str):
        cmd = ["mock"]
        if cfg["mock_chroot"]:
            cmd += ["-r", cfg["mock_chroot"]]
        return cmd + [
            "--rebuild",
            srpm,
            "--chain",  #TODO sep this out
            "--localrepo",
            "build/repo",
            "--enable-network",
        ]

def _devenv_setup():
    """Sets up a developer environment for Ultramarine"""
    logger.info("Setting up Koji profile")
    # make ~/.koji
    if not path.exists(path.expanduser("~/.koji/config.d/")):
        os.makedirs(path.expanduser("~/.koji/config.d/"))
    shutil.copyfile(
        os.path.dirname(os.path.abspath(__file__)) + "/assets/ultramarine.conf",
        path.expanduser("~/.koji/config.d") + "/ultramarine.conf"
    )
    logger.info("Setting up RPM build environment")
    run(["rpmdev-setuptree"])