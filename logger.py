import logging
from env import get_env

print(f'{__name__} loaded')


class CustomFormatter(logging.Formatter):
    debug_color = "\x1b[1;32m"      # green text
    info_color = "\x1b[38;20m"      # grey text
    warning_color = "\x1b[33;20m"   # yellow text
    error_color = "\x1b[31;20m"     # red text
    critical_color = "\x1b[41;30m"   # white text, red background
    reset = "\x1b[0m"
    format = "%(asctime)s %(levelname)s %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: debug_color + format + reset,
        logging.INFO: info_color + format + reset,
        logging.WARNING: warning_color + format + reset,
        logging.ERROR: error_color + format + reset,
        logging.CRITICAL: critical_color + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(name):
    logger = logging.getLogger(name)
    ch = logging.StreamHandler()
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)
    logger.setLevel(get_env('AIRPLANE_BUILD_TRACKER_LOGLEVEL', default=logging.DEBUG))
    return logger
