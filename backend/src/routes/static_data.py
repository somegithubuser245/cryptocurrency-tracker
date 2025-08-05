from fastapi import APIRouter
from routes.models.schemas import config_types
from utlis.dependencies.dependencies import call_manager_dependency

static_router = APIRouter(prefix="/static")


@static_router.get("/config/{config_type}")
def get_config(config_type: str) -> dict:
    return config_types.get(config_type)


@static_router.get("/pairs-exchanges")
async def get_pairs_exchanges_dict(call_manager: call_manager_dependency) -> dict:
    return await call_manager.get_arbitrable_pairs()
