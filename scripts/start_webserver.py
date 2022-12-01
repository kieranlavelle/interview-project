"""This module contains code that is used to start the FastAPI server.

It's used by the Dockerfile to start the server.
"""

import uvicorn

from service_provider_api.api.app import app


def start() -> None:
    """Starts the FastAPI server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)
