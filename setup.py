import setuptools

__version__ = "0.3.2"

if __name__ == "__main__":
    setuptools.setup(
        name="umpkg",
        fullname="Ultramarine Packaging Tool",
        description="The Ultramarine Project Manager",
        version=__version__,
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
        package_data={
            "umpkg": ["assets/*"],
        },
        package_dir={"umpkg": "umpkg"},
        python_requires=">=3.10",
        entry_points={
            "console_scripts": [
                "umpkg=umpkg.__main__:main",
            ]
        },
    )
