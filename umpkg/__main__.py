import glob
import os
from posixpath import abspath, dirname
import shutil
import sys
from os import chdir
from os.path import join, exists, isdir, dirname, abspath
from subprocess import getoutput

from typer import Argument, Option, Typer

from .build import Build
from .config import read_cfg, read_globalcfg, get_logger, toml
from .git import clone, initrepo
from .monogatari import Session
from .rpm_util import devenv_setup
from .utils import err, run

sys.argv = [val if val != "-h" else "--help" for val in sys.argv]
logger = get_logger(__name__)
app = Typer()


@app.command()
def build(path: str = Argument(".", help="The path to the package.")):
    """Builds a package from source."""
    logger.info(f"Downloading sources")
    run(["spectool", "-g", f"{path}/{glob.glob1(path, '*.spec')[0]}"])
    cfgs = read_cfg(join(path, "umpkg.toml"))
    num = 0
    for name, cfg in cfgs.items():
        num += Build(path, cfg, name).rpm()
    logger.info(f"Built {num} packages")


@app.command()
def buildsrc(path: str = Argument(".", help="The path to the package.")):
    """Builds source RPM from a spec file."""
    # Fetch sources, so we won't need to undefine _disable_source_fetch
    run(["spectool", "-g", f"{path}/{glob.glob1(path, '*.spec')[0]}"])
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
def koji_prepare():
    """Prepare Koji build environment"""
    bs(".")
    logger.info("Copying spec file for Koji")
    cfgs = read_cfg(join(".", "umpkg.toml"))
    repo_name = os.path.basename(os.getcwd())
    if f"{repo_name}.spec" not in glob.glob("*.spec"):
        for cfg in cfgs.values():
            # get the spec file name from the config
            spec = cfg["spec"]
            newspec = repo_name + ".spec"
            shutil.copy(spec, newspec)
    run(["spectool", "-g", f"{repo_name}.spec"])


@app.command()
def push(
    tag: str = Argument(..., help="The koji tag to push"),
    branch: str = Argument(None, help="Where to push to", show_default="same as tag"),
    repo: str = Option("origin", "--repo", "-r"),
    scratch: bool = Option(False, "--scratch", "-s", help="Use scratch build"),
    _=Option(".", "--dir", "-d", help="Where umpkg.toml is located", callback=chdir),
    prf: str = Argument("ultramarine", help="Koji Profile"),
):
    """Push a package to koji."""
    cfg = [x for i, x in enumerate(read_cfg().values()) if not i][0]
    link = cfg["git_repo"] or getoutput(f"git remote get-url {repo}").strip()
    if link.startswith("fatal"):
        return err("ERROR FROM GIT", link, logger)
    link = "git+" + link
    # I'm sorry windowsboy this is a very ugly hack -cappy
    branch = tag if branch is None else branch
    commit = getoutput(f"git rev-parse {branch}").strip()
    if commit == branch:
        return logger.error(f"Branch {branch} not found")
    link += "#" + commit
    logger.info(f"{link=}")
    if getoutput(f"git cherry -v {repo}/{branch}"):
        return logger.error(
            f"{branch} has not been pushed to {repo}, please push it first."
        )

    profile = cfg.get("koji_profile", prf)
    try:
        assert Session(prf).build(link, tag, {"profile": profile, "scratch": scratch})
        logger.info("Build successful")
        sys.exit(0)
    except AssertionError:
        logger.error(
            "Build was not successful, "
            f'try running "koji build --{profile=} {tag} {link}" yourself'
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
def init(
    name: str = Argument(..., help="Name of the project"),
    type: str = Option("spec", help="Type of the project"),
):
    """Initializes a umpkg project."""
    match type:
        case "spec":
            return repo_init(name)
        case "rust":
            repo_init(f"rust-{name}")
            # os.chdir(name)
            run(["rust2rpm", name])
            # rename the spec file
            #os.rename(f"rust-{name}.spec", f"{name}.spec")


def repo_init(name: str):
    if not isdir(name) and exists(name):
        return logger.error(f"{name} exists not as a directory.")
    url = initrepo(name)
    chdir(name)
    if not exists("umpkg.toml"):
        logger.info("Writing umpkg.toml")
        cfg = {
            name: {
                "spec": f"{name}.spec",
                "build_script": "",
                "build_method": "mock",
                "owner": read_globalcfg().get("owner", ""),
                "git_repo": url,
            }
        }
        toml.dump(cfg, open("umpkg.toml", "w+"))
    if not exists(f"{name}.spec"):
        logger.info(f"Writing {name}.spec")
        f = open(dirname(abspath(__file__)) + "/assets/template.spec")
        content = f.read().replace("<name>", name)
        f.close()
        f = open(f"{name}.spec", "w")
        f.write(content)
        f.close()
    if not exists(".gitignore"):
        logger.info("Writing .gitignore")
        # copy the template
        with open(dirname(abspath(__file__)) + "/assets/gitignore.in", "r") as f:
            content = f.read()
        with open(".gitignore", "w") as f:
            f.write(content)


@app.command()
def get(
    repo: str = Argument(..., help="Repository name"),
    dir: str = Argument(None, help="Output directory", show_default="repo name"),
):
    """Clone a git repo."""
    url = read_globalcfg()["repo"]
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
