import sys

from loguru import logger

from backend.config import settings

LOGS_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

logger.remove(0)
if settings.DEBUG:
    logger.add(
        sink=sys.stderr,
        level="DEBUG",
        format=LOGS_FORMAT,
        colorize=True,
    )
else:
    logger.add(
        sink=sys.stderr,
        level="INFO",
        format=LOGS_FORMAT,
        colorize=True,
    )

if settings.LOG_TO_FILE:
    logger.add(
        sink=f"{settings.PROJECT_NAME}.log", level="DEBUG", colorize=False
    )


logger.level(
    name="FAILURE",
    no=25,
    color="<red>",
)


def __log_failure(self, message, *args, **kwargs):
    self.log("FAILURE", message, *args, **kwargs)


logger.failure = __log_failure.__get__(logger, logger.__class__)


def get_logger():
    return logger
