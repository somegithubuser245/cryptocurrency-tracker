import logging
from contextlib import asynccontextmanager

import ccxt
from config.database import run_alembic_migrations
from config.logs import setup_logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes.scan_spreads import spreads_router
from utils.dependencies.dependencies import get_crypto_fetcher

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201 # unnecessarily complex return type
    run_alembic_migrations()
    setup_logging()
    yield
    fetcher = get_crypto_fetcher()
    await fetcher.close_all()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(spreads_router)


@app.exception_handler(ValueError)
async def validation_exception_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"Some Value Error:": str(exc)})


@app.exception_handler(ccxt.BaseError)
async def ccxt_error(request: Request, exc: ccxt.BaseError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"CCXT error:": str(exc)})
