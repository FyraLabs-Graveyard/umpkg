# Set up modules for the package
import setuptools
import os
setuptools.setup(
    name="umpkg",
    version="1.0",
    author="Cappy Ishihara",
    install_requires=[
        'typer',
        'koji',
    ]
)
