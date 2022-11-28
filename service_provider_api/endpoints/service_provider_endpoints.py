from fastapi import APIRouter

router = APIRouter("/service-provider")


@router.post("")
async def create_service_provider() -> dict:
    pass


@router.put("/{service_provider_id}")
async def update_service_provider(service_provider_id: str) -> dict:
    pass


@router.delete("/{service_provider_id}")
async def delete_service_provider(service_provider_id: str) -> dict:
    pass
