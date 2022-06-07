import logging
import sys
import traceback


LEVEL = logging.DEBUG


class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        record.message = record.getMessage()
        match record.levelno:
            case logging.WARN:
                colour = "\33[93m"
            case logging.ERROR:
                colour = "\33[91m"
            case logging.CRITICAL:
                colour = "\33[95m"
            case logging.DEBUG:
                colour = "\33[90m"
            case _:
                colour = ""
        if record.exc_info:
            tb = "\n" + "".join(traceback.format_exception(*record.exc_info[:]))
        else:
            tb = ""
        lvlname = record.levelname.replace("WARNING", "WARN").replace(
            "CRITICAL", "FATAL"
        )
        return f"{lvlname}\t{record.name} - {colour}{record.message}{tb}\33[0m"


cfmt = ConsoleFormatter()
ffmt = logging.Formatter(
    "%(asctime)s %(levelname)s\t%(name)s: %(message)s", datefmt="%T"
)
chdl = logging.StreamHandler(sys.stdout)
chdl.setFormatter(cfmt)
fhdl = logging.FileHandler("/tmp/umpkg.log", "a", "utf-8")
fhdl.setFormatter(ffmt)


def get_logger(name: str):
    logger = logging.getLogger(name.replace("__", ""))
    logger.setLevel(LEVEL)
    logger.addHandler(chdl)
    logger.addHandler(fhdl)
    return logger
