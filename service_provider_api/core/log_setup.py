"""Module used to configure the application logging.

Creates a basic structlog logging configuration that can be used
by the application.
"""

import logging

import structlog
from structlog.stdlib import LoggerFactory
from structlog.processors import JSONRenderer

from service_provider_api.core.config import settings


def setup_logging() -> None:
    """Setup the application logging.

    Global configuration for application logging

    Returns:
        None
    """

    logging.basicConfig(level=settings.LOG_LEVEL.upper())
    structlog.configure(
        logger_factory=LoggerFactory(),
        processors=[JSONRenderer()],
    )
