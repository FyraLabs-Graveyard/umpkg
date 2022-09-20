from functools import cache
import os
import sys
import toml

from .log import get_logger

logger = get_logger(__name__)
#logger.debug("cwd: %s", os.getcwd())
home = os.path.expanduser("~")
#logger.debug("home: %s", home := os.path.expanduser("~"))
PATH = "./umpkg.toml"
GLOBAL_PATH = "~/.config/umpkg.toml"
LINK = "https://github.com/ultramarine-linux/"

## DEFAULTS ##
dft_gbl = {"build_method": "mock", "repo": LINK}
dft_cfg: dict[str, str] = {"build_method": "mock", "spec": ""}


@cache
def read_cfg(path: str = PATH) -> dict[str, dict[str, str]]:
    path = os.path.abspath(path)
    try:
        obj: dict[str, dict[str, str]] = toml.load(path)
        for v in obj.values():
            new = dft_cfg.copy()
            new.update(v)
            v = new
        return obj
    except Exception:
        logger.error(f"failed to load toml {path}")
        logger.debug("", exc_info=True)
        sys.exit(1)


@cache
def read_globalcfg() -> dict[str, str]:
    path = GLOBAL_PATH.replace("~", home)
    try:
        obj = dft_gbl.copy()
        obj.update(toml.load(path))
        return obj
    except FileNotFoundError or toml.decoder.TomlDecodeError:  # includes file doesn't exist and failure to parse
        os.makedirs(os.path.dirname(path), exist_ok=True)
        toml.dump(dft_gbl, open(path, "w+"))
        logger.warn("Created global config file at " + path)
        return dft_gbl
