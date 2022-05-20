"""From the old version"""
from asyncio import sleep
from contextlib import suppress
from glob import glob
from os import getcwd, path
import os
from pathlib import Path
import shutil
from typing import Callable, TypeVar

from .utils import err, run, SLEEP
from .config import read_globalcfg
from .log import get_logger

logger = get_logger(__name__)
cfg = read_globalcfg()
T = TypeVar('T', 'Mock', 'RPMBuild')

def _buildsrc(fn: Callable[[T, str, str], list[str]]):
    async def buildsrc(self: T, spec: str, srcdir: str = '', opts: list[str] = []):
        """Builds a source RPM from a spec file"""
        srcdir = srcdir or path.join(self.cfg.get('srcdir', 'build/src'), Path(spec).stem)
        if not path.exists(srcdir):
            logger.warn("No valid srcdir cfg, using cwd")
            srcdir = getcwd()

        logger.info(f"{spec[:-5]}: building from {srcdir}")
        cmd = fn(self, spec, srcdir) + opts

        # mock cannot parse Popen with lists correctly.
        # Thanks mock devs!!!!!!!!111
        cmd = ' '.join([f'"{c}"' if ' ' in c else c for c in cmd])
        
        proc = run(cmd)
        while (rc := proc.poll()) is None:
            await sleep(SLEEP)
        if rc:
            return err('FAIL TO BUILD SRPM', proc, spec=spec, log=logger, cmd=cmd)
        # get the newest file in build/srpm
        files = glob("build/srpm/*.src.rpm")
        with suppress(ValueError):
            return max(files, key=path.getmtime)
        logger.error(f"{spec[:-5]}: No SRPM found")
    return buildsrc

def _buildrpm(fn: Callable[[T, str], list[str]]):
    async def buildRPM(self: T, srpm: str, opts: list[str] = []):
        cmd = fn(self, srpm) + opts
        cmd = ' '.join([f'"{c}"' if ' ' in c else c for c in cmd])
        proc = run(cmd)
        while not (rc := proc.poll()) is None:
            await sleep(SLEEP)
        if rc:
            return err('FAIL TO BUILD RPM', proc, srpm=srpm, log=logger)
        # get the newest file in build/rpm
        files = glob("build/rpm/*.rpm") + glob("build/repo/results/default/**/*.rpm")
        with suppress(ValueError):
            return max(files, key=path.getmtime)
        logger.error(f"{srpm[:-5]}: No RPM found")
    return buildRPM


class RPMBuild:
    def __init__(self, cfg: dict[str, str]):
        self.cfg = cfg

    @_buildsrc
    def buildsrc(self, spec: str, srcdir: str):
        # turn srcdir into an absolute path
        srcdir = path.abspath(srcdir)
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
    @_buildrpm
    def buildRPM(self, srpm: str):
        return [
            "rpmbuild",
            "--rebuild",
            srpm,
            "--define",
            '_rpmdir build/rpm',
            "--define",
            '_srcrpmdir build/srpm',
            "--undefine",
            "_disable_source_fetch",
        ]


class Mock:
    def __init__(self, cfg: dict[str, str]):
        self.cfg = cfg

    @_buildsrc
    def buildsrc(self, spec: str, srcdir: str):
        return [
            "mock",
            "--buildsrpm",
            "--spec",
            spec,
            "--sources",
            srcdir,
            "--resultdir",
            "build/srpm",
            "--enable-network",
        ]

    @_buildrpm
    def buildRPM(self, srpm: str):
        cmd = ["mock"]
        if self.cfg.get("mock_chroot", ''):
            cmd += ["-r", cfg["mock_chroot"]]
        return cmd + [
            "--rebuild",
            srpm,
            "--chain",  #TODO sep this out
            "--localrepo",
            "build/repo",
            "--enable-network",
        ]

def devenv_setup():
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
    run("rpmdev-setuptree")
