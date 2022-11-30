from fastapi import FastAPI
from fastapi_versioning import VersionedFastAPI, version

from service_provider_api.api.endpoints import (
    service_provider,
    service_provider_aggregations,
)
from service_provider_api.database.database import Base, engine
from service_provider_api.core.log_setup import setup_logging

# bind the models to the DB engine
Base.metadata.create_all(bind=engine)
setup_logging()


app = FastAPI(title="Service Provider API")
app.include_router(service_provider.router)
app.include_router(service_provider_aggregations.router)


@app.get("/health")
@version(1, 0)
async def health() -> dict:
    return {"status": "ok"}


app = VersionedFastAPI(app, version_format="{major}.{minor}")
