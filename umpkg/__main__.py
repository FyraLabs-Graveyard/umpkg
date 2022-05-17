import asyncio
import sys
import typer

from umpkg.build import build_rpm, build_src_from_spec

from .config import read_cfg
from . import log

sys.argv = [val if val != '-h' else '--help' for val in sys.argv]
logger = log.get_logger(__name__)
app = typer.Typer()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

@app.command()
def build(path: str = typer.Argument(None, help="The path to the package.")):
    """Builds a package from source."""
    cfg = read_cfg()
    if path:
        return build_rpm(path, cfg)
    specs = cfg['spec'].split()
    #TODO somehow there's a DeprecationWarning
    num = sum(loop.run_until_complete(asyncio.gather(*(build_rpm(spec, cfg) for spec in specs))))
    return logger.info(f"Built {num} packages specified in config.")

@app.command()
def buildsrc(path: str = typer.Argument(None, help="The path to the package.")):
    """Builds source RPM from a spec file."""
    cfg = read_cfg()
    if path:
        return build_src_from_spec(path, cfg)
    specs = loop.run_until_complete(asyncio.gather(*(build_src_from_spec(spec, cfg) for spec in cfg['spec'].split())))
    specs = [s for s in specs if s]
    return logger.info(f'Built {len(specs)} sources specified in config.')


@app.command()
def version():
    """Shows the version and exit."""
    import setup
    return print(setup.__version__)


def main():
    # run help if no arguments are passed
    if len(sys.argv) == 1:
        logger.debug('no args detected; calling --help')
        return app(args=["--help"])
    app()


if __name__ == "__main__":
    main()
