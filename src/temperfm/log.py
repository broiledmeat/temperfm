import os
import logging


class Logger:
    def __init__(self, path: str):
        from logging.handlers import RotatingFileHandler

        root = os.path.dirname(path)
        if not os.path.isdir(root):
            os.makedirs(root)

        self._logger = logging.getLogger('temperfm')
        self._logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

        file_handler = RotatingFileHandler(path, 'a', 5 * 1024 * 1024, 5)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

    def log(self, level: int, message: str):
        self._logger.log(level, message)

    def info(self, message: str):
        self.log(logging.INFO, message)

    def debug(self, message: str):
        self.log(logging.DEBUG, message)

    def warning(self, message: str):
        self.log(logging.WARNING, message)

    def error(self, message: str):
        self.log(logging.ERROR, message)
