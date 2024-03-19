import logging


logger = logging.getLogger(__name__)


class DebugLogger:
    def __init__(self):
        self.debug = False

    def log(self, level, message):
        if not self.debug:
            return
        message = f"\033[31m:Debug:{message}\033[0m"
        if level == "info":
            logger.info(message)
        elif level == "warning":
            logger.warning(message)
        elif level == "error":
            logger.error(message)
        elif level == "debug":
            if self.debug:
                logger.debug(message)
        else:
            logger.info(message)


debugger = DebugLogger()
