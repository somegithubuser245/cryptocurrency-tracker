import ccxt
import sqlalchemy
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes.scan_spreads import spreads_router

# Setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(spreads_router)


@app.get("/db-version")
def get_db_version() -> str:
    return sqlalchemy.__version__


@app.exception_handler(ValueError)
async def validation_exception_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"Some Value Error:": str(exc)})

@app.exception_handler(ccxt.BaseError)
async def ccxt_error(request: Request, exc: ccxt.BaseError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"CCXT error:": str(exc)})
