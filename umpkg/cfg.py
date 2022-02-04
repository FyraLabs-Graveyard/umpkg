import configparser
import os
import sys
import typer  # config subcommand

# Read the config file, everything is optional
defaults = {
    "srcdir": "$PWD",  # Default to CWD
    "git_repo": "",  # Default to no git repo
    "git_ref": "",  # Default to no git ref
    "build_script": "",  # specify a command to run to generate source
    "build_mode": "local",  # Builds the SRPM locally, then uploads it to Koji
    "tag": "",  # Default to no tag
    "spec": "",  # Default to no spec
}


config = configparser.ConfigParser()
globalConfig = configparser.ConfigParser()
# make the default section
config.add_section("umpkg")
for key, value in defaults.items():
    config.set("umpkg", key, value)


def read_config():
    # read the config file then override the defaults
    if os.path.exists("./umpkg.cfg"):
        config.read("./umpkg.cfg")
    else:
        # print("No config file found, using defaults")
        return dict(config.items("umpkg"))
    for key, value in defaults.items():
        if config.has_option("umpkg", key):
            defaults[key] = config.get("umpkg", key)
    # convert the values into a dict becuase it's a list of tuples
    return dict(config.items("umpkg"))


#### Global Configurations ####
globalDefaults = {
    "koji_profile": "ultramarine",
    "username": "",
    "build_method": "rpmbuild",
    "mock_chroot": "",
    "repo_dir": "~/.umpkg/repo"
}


def readGlobalConfig():

    homedir = os.path.expanduser("~")
    # read the config file then override the defaults
    if os.path.exists(f"{homedir}/.config/umpkg.cfg"):
        globalConfig.read(f"{homedir}/.config/umpkg.cfg")
    else:
        os.makedirs(f"{homedir}/.config", exist_ok=True)
        globalConfig.add_section("umpkg_global")
        for key, value in globalDefaults.items():
            globalConfig.set("umpkg_global", key, value)
        with open(f"{homedir}/.config/umpkg.cfg", "w") as configfile:
            globalConfig.write(configfile)
    for key, value in defaults.items():
        if globalConfig.has_option("umpkg_global", key):
            defaults[key] = globalConfig.get("umpkg_global", key)
    # convert the values into a dict becuase it's a list of tuples
    return dict(globalConfig.items("umpkg_global"))


def setGlobalConfig(key, value):
    homedir = os.path.expanduser("~")
    globalConfig.set("umpkg_global", key, value)
    with open(f"{homedir}/.config/umpkg.cfg", "w") as configfile:
        globalConfig.write(configfile)


#### Subcommands for the CLI ####
app = typer.Typer()


@app.command(help="List the current configuration keys")
def list(
    # option for global or local config
    global_config: bool = typer.Option(False, help="Use the global config"),
    local_config: bool = typer.Option(False, help="Use the local config"),
):
    """[summary]
    List the config options
    Args:
        global_config (bool, optional): [description]. Defaults to typer.Option(False, help="Use the global config").
        local_config (bool, optional): [description]. Defaults to typer.Option(False, help="Use the local config").
    """
    if global_config and local_config:
        typer.echo(
            "You can only specify one configuration paradigm! Choose one or the other."
        )
        sys.exit(1)
    elif global_config:
        cfg = readGlobalConfig()
    elif local_config:
        cfg = read_config()
    else:
        cfg = read_config()

    for key, value in cfg.items():
        typer.echo(f"{key}: {value}")


@app.command(help="Gets the value of a config key")
def get(
    key: str,
    global_config: bool = typer.Option(False, help="Use the global config"),
    local_config: bool = typer.Option(False, help="Use the local config"),
):
    """[summary]
    Get the config options
    Args:
        global_config (bool, optional): [description]. Defaults to typer.Option(False, help="Use the global config").
        local_config (bool, optional): [description]. Defaults to typer.Option(False, help="Use the local config").
    """
    if global_config and local_config:
        typer.echo(
            "You can only specify one configuration paradigm! Choose one or the other."
        )
        sys.exit(1)
    elif global_config:
        cfg = readGlobalConfig()
    elif local_config:
        cfg = read_config()
    else:
        cfg = read_config()

    if key in cfg:
        typer.echo(cfg[key])
    else:
        typer.echo(f"{key} not found in config")


@app.command(help="Sets the value of a config key")
def set(
    key: str,
    value: str,
    global_config: bool = typer.Option(False, help="Use the global config"),
    local_config: bool = typer.Option(False, help="Use the local config"),
):
    """[summary]
    Set the config options
    Args:
        key (str): [description]
        value (str): [description]
        global_config (bool, optional): [description]. Defaults to typer.Option(False, help="Use the global config").
        local_config (bool, optional): [description]. Defaults to typer.Option(False, help="Use the local config").
    """
    if global_config and local_config:
        typer.echo(
            "You can only specify one configuration paradigm! Choose one or the other."
        )
        sys.exit(1)
    elif global_config:
        cfg = readGlobalConfig()
        cfg[key] = value
        setGlobalConfig(key, value)
    elif local_config:
        cfg = read_config()
        cfg[key] = value
        with open("./umpkg.cfg", "w") as configfile:
            cfg.write(configfile)
    else:
        cfg = read_config()
        cfg[key] = value
        with open("./umpkg.cfg", "w") as configfile:
            cfg.write(configfile)
