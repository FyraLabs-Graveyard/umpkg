"""monogatari: Interface for koji"""
from typing import Any, Literal
from .log import get_logger
import sys
import koji
from koji_cli import lib as kojilib

from .config import read_cfg, read_globalcfg

logger = get_logger(__name__)


class Session:
    cfg: dict[str, Any]
    server: str
    session: koji.ClientSession

    def __init__(self, profile: str = "ultramarine"):
        self.prof = koji.get_profile_module(profile)
        self.session = self.prof.ClientSession(self.prof.config.server)
        self.cfg = self.prof.config
        self.session.gssapi_login()

    def build(self, src: str, target: str, opts: dict[str, Any]) -> Literal[0, 1]:
        # ? https://github.com/koji-project/koji/blob/master/cli/koji_cli/commands.py#L570
        #! opts are hard to parse, to be implemented
        # meantime, assume not dealing with complex stuff
        if not self.session.logged_in:
            logger.error("Please login to koji first.")
            sys.exit(1)
        id: int = self.session.build(src, target, opts)
        logger.info(f"Task info at {self.prof.config.weburl}/taskinfo?taskID={id}")
        self.session.logout()
        return kojilib.watch_tasks(self.session, [id], poll_interval=1)

    def add(self, tag: str, pkg: str) -> Literal[0, 1]:
        dtag: dict[str, Any] = (sess := self.session).getTag(tag)
        if not dtag:
            logger.error("Tag not found.")
            sys.exit(1)
        if pkg in [p["package_name"] for p in sess.listPackages(tagID=dtag["id"])]:
            logger.error("Package already exists.")
            sys.exit(1)
        logger.debug(read_cfg())
        owner = read_cfg()[pkg].get("owner", "") or read_globalcfg().get("owner", "")
        if not owner:
            logger.error("Please specify 'owner' in umpkg.toml")
            sys.exit(1)
        sess.packageListAdd(tag, pkg, owner)  #! owner
        sess.logout()
        #return kojilib.watch_tasks(self.session, [id], poll_interval=1)
