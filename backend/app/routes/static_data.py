from fastapi import APIRouter
from app.models.schemas import config_types

static_api = APIRouter(prefix="/static")

@static_api.get("/config/{config_type}")
def get_config(config_type: str) -> dict:
    return config_types.get(config_type)