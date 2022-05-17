from asyncio import create_task
from os.path import exists

from umpkg.utils import run_bs

from .rpm_util import Mock, RPMBuild
from .log import get_logger
from .config import read_globalcfg

logger = get_logger(__name__)


async def build_src_from_spec(spec: str, cfg: dict[str, str]) -> str|None:
    if not exists(spec):
        logger.error(f"{spec} not found!")
        return
    if not spec.endswith('.spec'):
        spec += ".spec"

    # we can probably run the script in parallel
    if bs := cfg.get('build_script', ''):
        create_task(run_bs(spec, bs, logger))  #! if bs takes too long, program might exit


    gcfg = read_globalcfg()
    buildMethod = cfg.get('build_method', gcfg.get('build_method', ''))

    match buildMethod:
        case 'rpmbuild':  #? return
            logger.info(f"{spec[:-5]}: rpmbuild")
            return await RPMBuild.buildsrc(spec)
        case 'mock':
            logger.info(f"{spec[:-5]}: mock")
            return await Mock.buildsrc(spec)
        case _:
            logger.error(f"{spec[:-5]}: No build method supplied! (rpmbuild or mock?)")


async def build_rpm(spec: str, cfg: dict[str, str]) -> int:
    srpm = await build_src_from_spec(spec, cfg)
    if not srpm:
        logger.warn(f"{spec[:-5]}: Skipping RPM build due to buildsrc error")
        return 0
    
    await Mock.buildRPM(srpm)
    return 1
