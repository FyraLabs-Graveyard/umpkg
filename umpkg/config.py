import os
import toml

from .log import get_logger

logger = get_logger(__name__)
logger.debug("cwd: %s", os.getcwd())
logger.debug("home: %s", home := os.path.expanduser('~'))
PATH = './umpkg.toml'
GLOBAL_PATH = '~/.config/umpkg.toml'

## DEFAULTS ##
dft_gbl = {
    "editor": "",
    "build_method": "mock"
}
dft_cfg: dict[str, str] = {
    "build_method": "mock",
    "spec": ""
}

def read_cfg() -> dict[str, str]:
    try:
        return toml.load(PATH)
    except Exception:
        logger.error(f'failed to load toml {PATH}; falling back')
        return dft_cfg

def read_globalcfg() -> dict[str, str]:
    path = GLOBAL_PATH.replace('~', home)
    try:
        return toml.load(path)
    except FileNotFoundError or toml.decoder.TomlDecodeError:  # includes file doesn't exist and failure to parse
        os.makedirs(os.path.dirname(path), exist_ok=True)
        toml.dump(dft_gbl, open(path, 'w+'))
        logger.warn("Created global config file at " + path)
        return dft_gbl
