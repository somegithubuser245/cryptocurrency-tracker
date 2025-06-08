from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models.schemas import KlinesRequest
from app.services.api_call_manager import ApiCallManager

from app.routes.static_data import static_api
from app.config.config import ApiProvider

# Setup
app = FastAPI()
api_call_manager = ApiCallManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(static_api)

@app.exception_handler(ValueError)
async def validation_exception_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.get("/crypto/klines/{crypto_id}")
async def get_data(
    crypto_id: str,
    api_provider: ApiProvider,
    interval: str = '4h',
) -> list[dict]:
    request = KlinesRequest(crypto_id=crypto_id, interval=interval, api_provider=api_provider)
    return await api_call_manager.get_price_stats(request)


