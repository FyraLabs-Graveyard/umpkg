from .config import get_logger, read_globalcfg, sys
# import gitlab as gl
# import github as gh
import pygit2 as pg
# from urllib.parse import urlparse


logger = get_logger(__name__)

def clone(url: str, path: str) -> pg.Repository:
    repo = pg.clone_repository(url, path)
    if not repo:
        logger.error(f"Can't clone {url} to {path}")
        sys.exit(1)
    return repo

def initrepo(name: str) -> str:
    url = read_globalcfg()['repo']
    if not url.endswith('/'): url += '/'
    url += name
    pg.init_repository(name, origin_url=url)
    return url
