import asyncio
from os import chdir
import sys
from os.path import join
from subprocess import getoutput
from typing import Any

from typer import Argument, Option, Typer

from umpkg.build import Build
from umpkg.utils import err

from .config import read_cfg, read_globalcfg
from .git import clone
from .log import get_logger
from .monogatari import Session
from .rpm_util import devenv_setup

from .config import read_cfg, write_cfg, dft_cfg

sys.argv = [val if val != "-h" else "--help" for val in sys.argv]
logger = get_logger(__name__)
app = Typer()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


@app.command()
def build(path: str = Argument(".", help="The path to the package.")):
    """Builds a package from source."""
    chdir(path)
    cfgs = read_cfg(join(path, "umpkg.toml"))
    tasks: list[asyncio.Task[Any]] = []
    builds: list[Build] = []
    for cfg in cfgs.values():
        b = Build(path, cfg, cfg["spec"])
        tasks.append(loop.create_task(b.rpm()))
        builds.append(b)
    loop.run_until_complete(
        asyncio.gather(*(tasks + [t for b in builds for t in b.tasks]))
    )
    num = sum(t.result() for t in tasks)
    logger.info(f"Built {num} packages")


@app.command()
def buildsrc(path: str = Argument(".", help="The path to the package.")):
    """Builds source RPM from a spec file."""
    cfgs = read_cfg(join(path, "umpkg.toml"))
    tasks: list[asyncio.Task[Any]] = []
    builds: list[Build] = []
    for cfg in cfgs.values():
        b = Build(path, cfg, cfg["spec"])
        tasks.append(loop.create_task(b.src()))
        builds.append(b)
    loop.run_until_complete(
        asyncio.gather(*(tasks + [t for b in builds for t in b.tasks]))
    )
    num = sum(bool(t.result()) for t in tasks)
    logger.info(f"Built {num} packages")

@app.command()
def bs(path: str = Argument(".", help="The path to the package.")):
    """Run build scripts"""
    cfgs = read_cfg(join(path, "umpkg.toml"))
    for name, cfg in cfgs.items():
        


@app.command()
def push(
    tag: str = Argument(..., help="The koji tag to push"),
    branch: str = Option(None, "--branch", "-b", help="The branch to push from", show_default='same as the tag'),
    repo: str = Option("origin", "--repo", "-r"),
<<<<<<< Updated upstream
    dir: str = Option(".", "--dir", "-d", help="Where umpkg.toml is located"),
    scratch: bool = Option(False, "--scratch", "-s", help="Use scratch build"),
=======
    dir: str = Option(".", "--dir", "-d", help="Where umpkg.toml is located", callback=chdir),
>>>>>>> Stashed changes
):
    """Push a package to koji."""
    cfg = [x for i, x in enumerate(read_cfg().values()) if not i][0]
    link = cfg["git_repo"] or getoutput(f"git remote get-url {repo}").strip()
    if link.startswith("fatal"):
        return err("ERROR FROM GIT", link, logger)
    link = "git+" + link
    branch = branch or tag
    commit = getoutput(f"git rev-parse {branch}").strip()
    if commit == branch:
        return logger.error(f"Branch {branch} not found")
    link += "#" + commit
    logger.info(f"{link=}")
    if getoutput(f"git cherry -v {repo}/{branch}"):
        return logger.error(
            f"{branch} has not been pushed to {repo}, please push it first."
        )

    profile = cfg.get("koji_profile", "ultramarine")
    # TODO: Make this cleaner, we should use try/except tbh
    if scratch:
        if Session().build(link, branch, {"profile": profile, "scratch": True}):
            logger.info("Build successful")
    else:
        logger.error(
            'Build was not successful, '
            f'try running "koji build --{profile=} {tag} {branch}" yourself'
        )
    if Session().build(link, branch, {"profile": profile}):
        logger.info("Build successful")
    else:
        logger.error(
            'Build was not successful, '
            f'try running "koji build --{profile=} {tag} {branch}" yourself'
        )


@app.command()
def add(
    tag: str = Argument(..., help="The koji tag to add"),
    dir: str = Option(".", "--dir", "-d", help="Where umpkg.toml is located", callback=chdir),
):
    """Add a package to koji."""
    cfg = [x for i, x in enumerate(read_cfg().items()) if not i][0]
    name = cfg[0]
    if Session().add(tag, name):
        logger.info(f"Successfully added {name} to koji.")
    else:
        profile = cfg[1].get("koji_profile", "ultramarine")
        logger.error(
            f"Failed to add {name} to koji, "
            f'try running "koji add-pkg --{profile=} {tag} {name}" yourself'
        )


@app.command()
def version():
    """Shows the version and exit."""
    import setup

    return print(setup.__version__)

@app.command()
def init(name: str = Argument(..., help="Name of the project")):
    """Initializes a umpkg project."""
    # TODO: generate a spec file for ultramarine
    write_cfg(dft_cfg)

@app.command()
def get(
    repo: str = Argument(..., help="Name of the repository"),
    dir: str = Option(None, '--dir', '-d', "The directory to clone to", show_default='name of the repo')
):
    """Clone a git repo."""
    url = read_globalcfg()['repourl']
    if not url.endswith('/'): url += '/'
    url += repo
    clone(url, dir or repo)

@app.command()
def setup():
    """Sets up a umpkg development environment."""
    devenv_setup()


def main():
    # run help if no arguments are passed
    if len(sys.argv) == 1:
        logger.debug("no args detected; calling --help")
        return app(args=["--help"])
    app()


if __name__ == "__main__":
    main()
