import json
from fastapi import APIRouter
from app.models.schemas import KlinesRequest, config_types
from app.services.external_api_caller import CryptoFetcher
from app.services.timeframes_equalizer import Equalizer

static_api = APIRouter(prefix="/static")
equalizer = Equalizer()


@static_api.get("/config/{config_type}")
def get_config(config_type: str) -> dict:
    return config_types.get(config_type)
