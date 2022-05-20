from asyncio import Task, create_task
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
        self.spec = join(path, spec)
        self.tasks: list[Task[None]] = []

    async def src(self) -> str | None:
        spec = self.spec
        if not exists(spec):
            return logger.error(f"{spec} not found!")
        if not spec.endswith(".spec"):
            spec += ".spec"

        # we can probably run the script in parallel
        if bs := self.cfg.get("build_script", ""):
            # insert the run_bs task before the build task
            self.tasks.insert(0, create_task(run_bs(spec, bs, logger)))
            #self.tasks.append(create_task(run_bs(spec, bs, logger)))

        buildMethod = self.cfg.get("build_method", "") or read_globalcfg().get(
            "build_method", ""
        )

        match buildMethod:
            case "rpmbuild":
                logger.info(f"{spec[:-5]}: rpmbuild")
                return await RPMBuild(self.cfg).buildsrc(spec, self.path)
            case "mock":
                logger.info(f"{spec[:-5]}: mock")
                return await Mock(self.cfg).buildsrc(spec, self.path)
            case _:
                logger.error(
                    f"{spec[:-5]}: No build method supplied! (rpmbuild or mock?)"
                )

    async def rpm(self) -> int:
        spec = self.spec
        srpm = await self.src()
        if not srpm:
            logger.warn(f"{spec[:-5]}: Skipping RPM build due to buildsrc error")
            return 0

        rpm = await Mock(self.cfg).buildRPM(srpm)
        if rpm:
            logger.info(f"{spec[:-5]}: Built RPM at {rpm}")
            return 1
        return 0
