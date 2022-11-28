from fastapi import FastAPI

from service_provider_api.endpoints import service_provider_endpoints

app = FastAPI("Service Provider API")
app.include_router(service_provider_endpoints.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
