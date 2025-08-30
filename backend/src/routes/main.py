import ccxt
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes.crypto_data import crypto_router
from routes.scan_spreads import spreads_router
from routes.static_data import static_router

# Setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(static_router)
app.include_router(crypto_router)
app.include_router(spreads_router)


@app.exception_handler(ValueError)
async def validation_exception_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"Some Value Error:": str(exc)})

@app.exception_handler(ccxt.BaseError)
async def ccxt_error(request: Request, exc: ccxt.BaseError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"CCXT error:": str(exc)})
