# umpkg: The Ultramarine Linux development tool

`umpkg` is a CLI tool for developing, and managing Ultramarine Linux packages.

umpkg is a Git repository manager and RPM build tool for managing Ultramarine Linux projects.

It uses a project-based structure, where each project is a Git repository. an RPM package has a `umpkg.toml` file in the root of the repository that can be used to quickly build the project using `umpkg build`.

The `umpkg.toml` file is a TOML file that can be used to configure the project.

## Structure

The `umpkg.toml` file dictates how the project will be built.


## Usage

Install these packages:
```
sudo dnf install python3-typer+all koji mock python3-arrow
```

Then install the project:

```
pip install .
```
