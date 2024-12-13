
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Crypto Analytics API",
    description="API for cryptocurrency data analytics",
    version="0.1.0"
)

class Currency(BaseModel):
    name: str
    price: float

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Service is running"}

@app.put("/currencies/{currency_id}")
def update_currency(currency_id: int, currency: Currency):
    return {"currency_name": currency.name, "currency_price": currency.price}

@app.get("/")
def read_root():
    return {"Hello": "World"}

