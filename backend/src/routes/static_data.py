from fastapi import APIRouter
from routes.models.schemas import config_types
from services.external_api_caller import CryptoFetcher

crypto_fetcher = CryptoFetcher()

static_router = APIRouter(prefix="/static")


@static_router.get("/config/{config_type}")
def get_config(config_type: str) -> dict:
    return config_types.get(config_type)


@static_router.get("/pairs-exchanges")
async def get_pairs_exchanges_dict() -> dict:
    return await crypto_fetcher.get_arbitrable_pairs()
