from fastapi import APIRouter

from routes.models.schemas import PriceTicketRequest
from services.dependencies import spreads_calculator_dependency

spreads_router = APIRouter(prefix="/spreads")

@spreads_router.get("/test")
async def get_spreads(
    spreads_calculator: spreads_calculator_dependency
):
    return await spreads_calculator.calculate(
        PriceTicketRequest(
            crypto_id='BTC/USDT',
            interval="4h",
            api_provider="binance"
        )
    )