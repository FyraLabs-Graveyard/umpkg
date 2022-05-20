import asyncio
from subprocess import Popen, STDOUT, PIPE
from logging import Logger

SLEEP = 0.2  # sleep interval


def run(cmd: list[str] | str, show_cmd: bool = False):
    if show_cmd == True:
        print(f"- {cmd.join(' ')}")
    return Popen(cmd, stderr=STDOUT, shell=True, universal_newlines=True)

def err(title: str, proc: Popen[str]|str, log: Logger, **kws: str):
    out = f"\n### {title} ###\n"
    for k, w in kws.items():
        out += f"{k}={w}\t"
    if isinstance(proc, Popen):
        out += f"rc={proc.returncode}\toutput:\n"
        out += ''.join('\t' + l for l in proc.stdout or '')
    else:
        out += "output:\n"
        out += '\n'.join('\t' + l for l in proc or '')
    out += f'\n### END OF {title} ###'
    log.error(out)

async def run_bs(spec: str, bs: str, log: Logger):
    log.info(f"Running build script: {bs}")
    proc = run(bs)
    while proc.poll() is None:
        await asyncio.sleep(SLEEP)
    if proc.returncode:
        err('BUILD SCRIPT ERROR', proc, log, spec=spec, bs=bs)
