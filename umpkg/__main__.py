import sys
from os import chdir, mkdir
from os.path import join, exists, isdir
from subprocess import getoutput

from typer import Argument, Option, Typer

from .build import Build
from .config import read_cfg, read_globalcfg, write_cfg
from .git import clone
from .log import get_logger
from .monogatari import Session
from .rpm_util import devenv_setup
from .utils import err, run

sys.argv = [val if val != "-h" else "--help" for val in sys.argv]
logger = get_logger(__name__)
app = Typer()


@app.command()
def build(path: str = Argument(".", help="The path to the package.")):
    """Builds a package from source."""
    cfgs = read_cfg(join(path, "umpkg.toml"))
    num = 0
    for name, cfg in cfgs.items():
        num += Build(path, cfg, name).rpm()
    logger.info(f"Built {num} packages")


@app.command()
def buildsrc(path: str = Argument(".", help="The path to the package.")):
    """Builds source RPM from a spec file."""
    cfgs = read_cfg(join(path, "umpkg.toml"))
    num = 0
    for name, cfg in cfgs.items():
        num += bool(Build(path, cfg, name).src())
    logger.info(f"Built {num} packages")


@app.command()
def bs(path: str = Argument(".", help="The path to the package.")):
    """Run build scripts"""
    cfgs = read_cfg(join(path, "umpkg.toml"))
    for name, cfg in cfgs.items():
        if bs := cfg.get("build_script", ""):
            logger.info(f"Running bs for {name}: {bs}")
            run(bs)


@app.command()
def push(
    tag: str = Argument(..., help="The koji tag to push"),
    branch: str = Argument(None, help="Where to push to", show_default="same as tag"),
    repo: str = Option("origin", "--repo", "-r"),
    scratch: bool = Option(False, "--scratch", "-s", help="Use scratch build"),
    _=Option(".", "--dir", "-d", help="Where umpkg.toml is located", callback=chdir),
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
            sys.exit(0)
        else:
            logger.error(
                "Build was not successful, "
                f'try running "koji build --{profile=} {tag} {branch}" yourself'
            )
            sys.exit(1)
    if Session().build(link, branch, {"profile": profile}):
        logger.info("Build successful")
        sys.exit(0)
    else:
        logger.error(
            "Build was not successful, "
            f'try running "koji build --{profile=} {tag} {branch}" yourself'
        )
        sys.exit(1)


@app.command()
def add(
    tag: str = Argument(..., help="The koji tag to add"),
    _=Option(".", "--dir", "-d", help="Where umpkg.toml is", callback=chdir),
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
    if not exists(name):
        mkdir(name)
    elif not isdir(name):
        return logger.error(f'{name} exists not as a directory.')
    if exists(f'{name}/umpkg.toml'):
        return logger.error(f'{name}/umpkg.toml already exists.')
    repo = read_globalcfg()['repo']
    if not repo.endswith('/'):
        repo += '/'
    repo += name
    cfg = {
        name: {
            'spec': f'{name}.spec',
            'build_script': '',
            'build_method': 'mock',
            'owner': 'your koji username',
            'git_repo': repo
        }
    }
    write_cfg(cfg, f'{name}/umpkg.toml')


@app.command()
def get(
    repo: str = Argument(..., help="Repository name"),
    dir: str = Argument(None, help="Output directory", show_default="repo name"),
):
    """Clone a git repo."""
    url = read_globalcfg()["repourl"]
    if not url.endswith("/"):
        url += "/"
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
