from subprocess import Popen, STDOUT
from logging import Logger


def run(cmd: list[str] | str):
    return Popen(cmd, stderr=STDOUT, shell=True, universal_newlines=True)

def err(title: str, proc: Popen[str], log: Logger, **kws: str):
    out = f"### {title} ###\n"
    for k, w in kws.items():
        out += f"{k}={w}\t"
    out += f"rc={proc.returncode}\toutput:\n"
    out += '\n'.join('\t' + l for l in proc.stdout or '')
    out += f'\n### END OF {title}'
    log.error(out)

async def run_bs(spec: str, bs: str, log: Logger):
    log.info(f"Running build script: {bs}")
    proc = run(bs)
    proc.communicate()
    if proc.returncode:
        err('BUILD SCRIPT ERROR', proc, log, spec=spec, bs=bs)
