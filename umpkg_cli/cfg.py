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
