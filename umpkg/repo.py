"""
umpkg test repository function

the repo module is a set of tools that can be used to build the entire Ultramarine package ecosystem from scratch.
you can use this module to literally fork all Ultramarine repositories and build them from scratch.
This may not reuse all the umpkg routines as we are going to be pretty specific about what we are doing.
"""
import gitlab
import os
import sys
import subprocess
import typer
import pygit2
import shutil
import umpkg.util as util
import umpkg.cfg as cfg
import glob

config = cfg.readGlobalConfig()

gl = gitlab.Gitlab("https://gitlab.ultramarine-linux.org", private_token="")

app = typer.Typer()
# get group by id
if "repo_dir" not in config:
    typer.echo(
        "You have to set a repo_dir in your config file to use this tool! Exiting..."
    )
    sys.exit(1)
else:
    repo_dir = os.path.expanduser(config["repo_dir"])

# list all projects in group


# utility functions
def buildsrpm(project: str):
    """
    Builds an SRPM from a project
    """
    gl_group = gl.groups.get(id=8)
    projects = gl_group.projects.list(all=True)
    typer.echo(f"Building SRPM for {project}")
    os.makedirs(repo_dir + "/" + "srpm", exist_ok=True)
    os.chdir(f"{repo_dir}/{project}")
    cmd = util.Command()
    cmd.buildSrc(f"{project}.spec")
    srpms = glob.glob("build/srpm/*.src.rpm")
    for srpm in srpms:
        # move the srpm to the srpm directory
        # replace if it already exists
        shutil.move(srpm, f"{repo_dir}/srpm/{os.path.basename(srpm)}")
    typer.echo(f"SRPM built for {project}")
    os.chdir("..")


@app.command()
def list_projects():
    """Lists all projects in the Ultramarine Repositories"""
    gl_group = gl.groups.get(id=8)
    projects = gl_group.projects.list(all=True)
    for p in projects:
        print(f"{p.path_with_namespace.split('/')[1]}")


@app.command()
def get(project: str):
    """Fetches a project from Gitlab"""
    gl_group = gl.groups.get(id=8)
    projects = gl_group.projects.list(all=True)
    for p in projects:
        if p.name == project:
            print(f"Found {project}")
            # clone the project
            try:
                pygit2.clone_repository(
                    p.http_url_to_repo,
                    repo_dir + "/" + p.path_with_namespace.split("/")[1],
                )
            except ValueError:
                typer.echo(f"{project} already exists, skipping...")
            except pygit2.GitError as e:
                typer.echo(f"{project} failed to clone! {e}")
            return os.getcwd() + "/" + project
    print(f"{project} not found")
    return False


@app.command()
def get_all():
    """Fetches all projects from Gitlab"""
    choice = input(
        "This will clone and initialize all packages in the Ultramarine repositories. Are you sure? [y/N] "
    )
    gl_group = gl.groups.get(id=8)
    projects = gl_group.projects.list(all=True)
    if choice.lower() == "y":
        pass
    else:
        return
    for p in projects:
        typer.echo(f"Cloning {p.path_with_namespace.split('/')[1]}")
        get(p.path_with_namespace.split("/")[1])


@app.command()
def build_all():
    """Builds all packages in the localrepo directory"""
    choice = input(
        "This will build all packages in the Ultramarine repositories. Are you sure? [y/N] "
    )
    gl_group = gl.groups.get(id=8)
    if choice.lower() == "y":
        pass
    else:
        return
    dirs = os.listdir(repo_dir)
    excludes = ["repo", "build", "srpm", "rpm", "src", "tmp"]
    for d in dirs:
        if d in excludes:
            continue
        typer.echo(f"Building {d}")
        buildsrpm(d)
    command = [
        "mock",
        "--rebuild",
        "--chain",
        repo_dir + "/" + "srpm/*",
        "-c",
        "--localrepo",
        repo_dir + "/" + "repo",
    ]
    print(command)
    os.system(" ".join(command))


@app.command()
def build(project: str):
    gl_group = gl.groups.get(id=8)
    """Builds a package in the localrepo directory"""
    buildsrpm(project)
    command = [
        "mock",
        "--rebuild",
        "--chain",
        repo_dir + "/" + f"srpm/{project}*.src.rpm",
        "-c",
        "--localrepo",
        repo_dir + "/" + "repo",
    ]
    print(command)
    os.system(" ".join(command))


if __name__ == "__main__":
    app()
