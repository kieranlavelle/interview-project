from fastapi import FastAPI

from service_provider_api.endpoints import service_provider_endpoints
from service_provider_api.utils.database import Base, engine
from service_provider_api.log_setup import setup_logging

# bind the models to the DB engine
Base.metadata.create_all(bind=engine)
setup_logging()


app = FastAPI(title="Service Provider API")
app.include_router(service_provider_endpoints.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
