import sys
from .config import get_logger
import gitlab as gl
import github as gh
import pygit2 as pg
# from urllib.parse import urlparse


logger = get_logger(__name__)

def clone(url: str, path: str) -> pg.Repository:
    repo = pg.clone_repository(url, path)
    if not repo:
        logger.error(f"Can't clone {url} to {path}")
        sys.exit(1)
    return repo
