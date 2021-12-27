import configparser
import os
import sys
# Read the config file, everything is optional
defaults = {
    "srcdir": '$PWD', # Default to CWD
    "git_repo": '', # Default to no git repo
    "git_ref": '', # Default to no git ref
    "build_script": '', # specify a command to run to generate source
    "build_mode": 'local', # Builds the SRPM locally, then uploads it to Koji
    "tag": '', # Default to no tag
    "spec": '', # Default to no spec
}


config = configparser.ConfigParser()
globalConfig = configparser.ConfigParser()
# make the default section
config.add_section('umpkg')
for key, value in defaults.items():
    config.set('umpkg', key, value)


def read_config():
    # read the config file then override the defaults
    if os.path.exists('./umpkg.cfg'):
        config.read('./umpkg.cfg')
    else:
        print("No config file found, using defaults")
        return dict(config.items('umpkg'))
    for key, value in defaults.items():
        if config.has_option('umpkg', key):
            defaults[key] = config.get('umpkg', key)
    # convert the values into a dict becuase it's a list of tuples
    return dict(config.items('umpkg'))


#### Global Configurations ####
globalDefaults = {
    "koji_profile": 'ultramarine',
    "username": '',
    "build_method": 'rpmbuild',
    "mock_chroot": '',

}

def readGlobalConfig():

    homedir = os.path.expanduser('~')
    # read the config file then override the defaults
    if os.path.exists(f'{homedir}/.config/umpkg.cfg'):
        globalConfig.read(f'{homedir}/.config/umpkg.cfg')
    else:
        os.makedirs(f'{homedir}/.config', exist_ok=True)
        globalConfig.add_section('umpkg_global')
        for key, value in globalDefaults.items():
            globalConfig.set('umpkg_global', key, value)
        with open(f'{homedir}/.config/umpkg.cfg', 'w') as configfile:
            globalConfig.write(configfile)
    for key, value in defaults.items():
        if globalConfig.has_option('umpkg_global', key):
            defaults[key] = globalConfig.get('umpkg_global', key)
    # convert the values into a dict becuase it's a list of tuples
    return dict(globalConfig.items('umpkg_global'))

def setGlobalConfig(key, value):
    homedir = os.path.expanduser('~')
    globalConfig.set('umpkg_global', key, value)
    with open(f'{homedir}/.config/umpkg.cfg', 'w') as configfile:
        globalConfig.write(configfile)