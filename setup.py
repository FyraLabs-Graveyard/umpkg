# Set up modules for the package
from importlib.metadata import entry_points
import setuptools
import os

setuptools.setup(
    name="umpkg",
    fullname="Ultramarine Packaging Tool",
    version="0.2.1",
    author="Cappy Ishihara",
    install_requires=[
        "typer",
        "koji",
        "python-gitlab",
        "configparser",
        "python-gitlab",
        "pygit2",
    ],
    include_dirs=["umpkg"],
    include_package_data=True,
    packages=["umpkg"],
    package_dir={"umpkg": "umpkg"},
    python_requires=">=3.10",
    # run __main__.py
    entry_points={"console_scripts": [
        "umpkg=umpkg.__main__:entrypoint",
        "umpkg-repo=umpkg.repo:app",
        ]},
)
