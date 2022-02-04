# umpkg

Packaging scripts for Ultramarine, based on the old makefiles for the Ultramarine release packages.

`umpkg` is a set of Python scripts that is used for building packages for Ultramarine Linux.
It is a wrapper around Koji, RPMBuild, Mock, and the GitLab API.

umpkg is inspired by the likes of `fedpkg` and Rocky Linux's `rockybuild`, minus the usage of dist-git.

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
umpkg build <spec file>
```

To fetch an existing package from Ultramarine GitLab's package sources repository, run:
```
umpkg get <package>
```

umpkg also supports the ability to generate a full git mirror of the package sources repository, and an ability to generate a local repository of the built packages for testing.

To do this, check out `umpkg repo --help` for more information.

### umpkg Local Repository mode

You can use the Local Repository mode to fetch, build, and generate a test repository within the configured folder in `~/.config/umpkg.cfg`.

Use `umpkg repo get-all` to clone all packages from the Ultramarine GitLab repository, and `umpkg repo build-all` to build all of them. (This will take a toll on the GitLab server and your internet, so be careful.)

Or you can use `umpkg repo get <package>` to clone a single package, and `umpkg repo build <package>` to build it.


## Configuration
In order to use umpkg, you need to create a configuration file called `umpkg.cfg` in the same directory as the spec file, or set the path manually in your configuration file, which can be a list.

To generate a configuration file, run:
```
umpkg init
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

You can find out more about umpkg by running `umpkg <command> --help`.

And with that, everything's ready to go! Happy packaging!