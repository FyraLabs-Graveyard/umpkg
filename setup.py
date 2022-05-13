from importlib.metadata import entry_points
import setuptools
import os

setuptools.setup(
    name="umpkg",
    fullname="Ultramarine Packaging Tool",
    description="The Ultramarine Project Manager",
    version="0.3.0",
    install_requires=[
        "typer",
        "koji",
        "pygit2",
        "toml",
        "arrow",
    ],
    include_dirs=["umpkg"],
    include_package_data=True,
    packages=["umpkg"],
    package_dir={"umpkg": "umpkg"},
    python_requires=">=3.10",
    entry_points={"console_scripts": [
        "umpkg=umpkg.__main__:main",
        ]},
)