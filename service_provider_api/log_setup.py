import logging

import structlog
from structlog.stdlib import LoggerFactory
from structlog.processors import JSONRenderer

logging.basicConfig(level=logging.INFO)


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO)
    structlog.configure(
        logger_factory=LoggerFactory(),
        processors=[JSONRenderer()],
    )
