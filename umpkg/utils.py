import subprocess as sp
from logging import Logger


def run(cmd: list[str] | str, show_cmd: bool = False):
    if show_cmd == True:
        if isinstance(cmd, str):
            print(cmd)
        else:
            print(*cmd)

    return sp.run(cmd, universal_newlines=True)

def err(title: str, proc: sp.CompletedProcess[str]|str, log: Logger, **kws: str):
    out = f"\n### {title} ###\n"
    for k, w in kws.items():
        out += f"{k}={w}\t"
    if isinstance(proc, sp.CompletedProcess):
        out += f"rc={proc.returncode}\toutput:\n"
        out += ''.join('\t' + l for l in proc.stdout or '')
    else:
        out += "output:\n"
        out += '\n'.join('\t' + l for l in proc or '')
    out += f'\n### END OF {title} ###'
    log.error(out)

def run_bs(spec: str, bs: str, log: Logger):
    log.info(f"Running build script: {bs}")
    proc = run(bs)
    if proc.returncode:
        err('BUILD SCRIPT ERROR', proc, log, spec=spec, bs=bs)
