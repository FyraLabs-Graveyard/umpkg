# umpkg

Packaging scripts for Ultramarine

`umpkg` is a set of Python scripts that is used for building packages for Ultramarine Linux.
It is a wrapper around Koji, RPMBuild, and the GitLab API.

umpkg is inspired by the likes of fedpkg and Rocky Linux's rockybuild.

The idea originally stemmed from Lapis, a seperate RPM build system initially made as an attempt to replace Koji.

umpkg uses a configuration file called `umpkg.cfg` to define the build environment, specifying where to find the source code, the scripts (or a lack of them) to generate the source files for the package.

umpkg can be used to check out the spec sources from another Git repository, build the package, then upload the package to Koji, similar to the way that fedpkg works.


## Usage
To push a package to Koji, run:
```
umpkg push <package>
```
If the package is not defined, then it will build every single package defined in the configuration file.

You can also build locally by running:
```
umpkg build <package>
```

## Configuration
In order to use umpkg, you need to create a configuration file called `umpkg.cfg` in the same directory as the spec file, or set the path manually in your configuration file, which can be a list.

The example configuration file is as follows:
```
[umpkg]
spec=package.spec
tag=um35 # The Koji tag to push to
build_mode=local # The build mode to use, local will build the SRPM locally, and koji will push the git repo to Koji
build_script=make sources # The script to run before building the SRPM, if any

## Koji mode specific settings
git_repo=https://example.com/example.git # the git repo to push to Koji
git_ref=HEAD # The ref that will be added after the repo link, like #HEAD or #master
```

if the configuration file is not found, umpkg will directly build the package and assume the source files are in the same directory as the spec file.

For a single package, your structure should look like this:
```
package/
├── umpkg.cfg
├── package.spec
├── package-src.tar.gz (optional as umpkg can download it from the internet)
└── package-patch.patch
```

For multiple packages, your config file should look like this:
```
[umpkg]
spec=pkg1.spec pkg2.spec pkg3.spec
tag=um35
build_mode=local
build_script=make sources
```
And your structure should look like this:
```
package/
├── umpkg.cfg
├── pkg1.spec
├── pkg2.spec
├── pkg3.spec
└── sources/
    └── pkg1/
        ├── pkg1-src.tar.gz
        └── pkg1-patch.patch
    └── pkg2/
        ├── pkg2-src.tar.gz
        └── pkg2-patch.patch
    └── pkg3/
        ├── pkg3-src.tar.gz
        └── pkg3-patch.patch
```

And with that, everything's ready to go! Happy packaging!