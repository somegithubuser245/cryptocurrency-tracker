from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models.schemas import CompareRequest, KlinesRequest
from app.routes.static_data import static_api
from app.services.api_call_manager import ApiCallManager

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
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/crypto/klines/{crypto_id}")
async def get_data(request: KlinesRequest) -> list[dict]:
    request = request
    return api_call_manager.get_price_stats(request)


@app.get("/compare")
async def get_klines_data(
    request: CompareRequest = Query(),  # noqa: B008
) -> dict[str, list[dict[str, float | int]]]:
    return api_call_manager.get_timeframe_aligned(request)
