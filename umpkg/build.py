from os.path import exists, join

from umpkg.utils import run_bs

from .rpm_util import Mock, RPMBuild
from .log import get_logger
from .config import read_globalcfg

logger = get_logger(__name__)


class Build:
    def __init__(self, path: str, cfg: dict[str, str], spec: str):
        self.path = path
        self.cfg = cfg
        self.spec = join(path, cfg['spec'])
        self.name = spec

    def src(self) -> str | None:
        spec = self.spec
        if not exists(spec):
            return logger.error(f"{spec} not found!")
        if not spec.endswith(".spec"):
            spec += ".spec"

        if bs := self.cfg.get("build_script", ""):
            # insert the run_bs task before the build task
            run_bs(spec, bs, logger)

        buildMethod = self.cfg.get("build_method", "") or read_globalcfg().get(
            "build_method", ""
        )

        logger.debug(f'{spec=}\t{buildMethod=}')
        match buildMethod:
            case "rpmbuild":
                logger.info(f"{self.name}: rpmbuild")
                return RPMBuild(self.cfg).buildsrc(spec, self.path)
            case "mock":
                logger.info(f"{self.name}: mock")
                return Mock(self.cfg).buildsrc(spec, self.path)
            case _:
                logger.error(
                    f"{self.name}: No build method supplied! (rpmbuild or mock?)"
                )

    def rpm(self) -> int:
        spec = self.spec
        srpm = self.src()
        if not srpm:
            logger.warn(f"{self.name}: Skipping RPM build due to buildsrc error")
            return 0
        buildMethod = self.cfg.get("build_method", "") or read_globalcfg().get(
            "build_method", ""
        )
        
        logger.debug(f'{spec=}\t{buildMethod=}')
        match buildMethod:
            case "rpmbuild":
                rpm = RPMBuild(self.cfg).buildRPM(srpm)
            case "mock":
                rpm = Mock(self.cfg).buildRPM(srpm)
            case _:
                logger.error(
                    f"{self.name}: No build method supplied! (rpmbuild or mock?)"
                )
                return 0
        if rpm:
            logger.info(f"{self.name}: Built RPM at {rpm}")
            return 1
        return 0
