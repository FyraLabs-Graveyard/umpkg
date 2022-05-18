"""monogatari: Interface for koji"""
from configparser import ConfigParser
from typing import Any, Literal
from .log import get_logger
import sys
import koji
from koji_cli import lib as kojilib


logger = get_logger(__name__)


class Session:
    cfg: dict [str,Any]
    server: str
    session: koji.ClientSession
    def __init__(self, profile: str = 'ultramarine'):
        self.prof = koji.get_profile_module(profile)
        self.session: koji.ClientSession = self.prof.ClientSession(self.prof.config.server)
        self.cfg = self.prof.config
        self.session.gssapi_login()

    def build(self, src: str, target: str, opts: dict[str, Any]) -> Literal[0]|Literal[1]:
        #? https://github.com/koji-project/koji/blob/master/cli/koji_cli/commands.py#L570
        #! opts are hard to parse, to be implemented
        # meantime, assume not dealing with complex stuff
        if not self.session.logged_in:
            logger.error("Please login to koji first.")
            sys.exit(1)
        id: int = self.session.build(src, target, opts)
        self.session.logout()
        return kojilib.watch_tasks(self.session, [id], poll_interval=1)
