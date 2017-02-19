import logging


_logger = None
""":type: logging.Logger | None"""


def _get_logger():
    """
    :rtype: logging.Logger
    """
    global _logger

    if _logger is None:
        from logging.handlers import RotatingFileHandler
        from temperfm.config import log_path

        _logger = logging.getLogger('temperfm')
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        handler = RotatingFileHandler(log_path, 'a', 5 * 1024 * 1024, 5)

        handler.setFormatter(formatter)
        _logger.addHandler(handler)
        _logger.setLevel(logging.DEBUG)

    return _logger


def log(level, message):
    """
    :type level: int
    :type message: str
    """
    _get_logger().log(level, message)


def info(message):
    """
    :type message: str
    """
    log(logging.INFO, message)


def debug(message):
    """
    :type message: str
    """
    log(logging.DEBUG, message)


def warning(message):
    """
    :type message: str
    """
    log(logging.WARNING, message)


def error(message):
    """
    :type message: str
    """
    log(logging.ERROR, message)
