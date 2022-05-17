import logging
import sys


LEVEL = logging.DEBUG

class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        record.message = record.getMessage()
        match record.levelno:
            case logging.INFO:
                colour = ''
            case logging.WARN:
                colour = '\33[93m'
            case logging.ERROR:
                colour = '\33[91m'
            case logging.CRITICAL:
                colour = '\33[95m'
        return f'{record.levelname}\t{record.name} - {colour}{record.message}\33[0m'

cfmt = ConsoleFormatter()
ffmt = logging.Formatter('%(asctime)s %(levelname)s\t%(name)s: %(message)s', datefmt='%T')
chdl = logging.StreamHandler(sys.stdout)
fhdl = logging.FileHandler('/tmp/umpkg.log', 'a', 'utf-8')

def get_logger(name: str):
    logger = logging.getLogger(name.replace('__', ''))
    logger.setLevel(LEVEL)
    logger.addHandler(chdl)
    logger.addHandler(fhdl)
    return logger
