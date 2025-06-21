#!/usr/bin/env python3
"""
Exchange Integration Service

Unified API management for multiple cryptocurrency exchanges:
- Rate limit management
- Authentication handling
- Order execution
- Balance tracking
- Error handling and retry logic
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis.asyncio as redis
from kafka import KafkaProducer
import ccxt.async_support as ccxt
import hashlib
import hmac
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Exchange Integration Service", version="1.0.0")

# Configuration
KAFKA_BOOTSTRAP_SERVERS = ['kafka:9092']
REDIS_URL = "redis://redis:6379"

class ExchangeCredentials(BaseModel):
    api_key: str
    secret: str
    passphrase: Optional[str] = None
    sandbox: bool = True

class OrderRequest(BaseModel):
    exchange: str
    symbol: str
    side: str  # 'buy' or 'sell'
    amount: float
    price: Optional[float] = None
    order_type: str = "market"  # 'market' or 'limit'

class BalanceResponse(BaseModel):
    exchange: str
    currency: str
    free: Decimal
    used: Decimal
    total: Decimal

class OrderResponse(BaseModel):
    order_id: str
    exchange: str
    symbol: str
    side: str
    amount: float
    price: float
    status: str
    timestamp: datetime

class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def can_make_request(self) -> bool:
        now = time.time()
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False
    
    async def wait_for_slot(self):
        while not await self.can_make_request():
            await asyncio.sleep(0.1)

class ExchangeManager:
    def __init__(self):
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.credentials: Dict[str, ExchangeCredentials] = {}
        self.rate_limiters: Dict[str, RateLimiter] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.kafka_producer: Optional[KafkaProducer] = None
        
        # Rate limits per exchange (requests per minute)
        self.rate_limits = {
            'binance': 1200,  # 1200 requests per minute
            'coinbase': 10,   # 10 requests per second = 600 per minute
            'kraken': 60,     # 1 request per second = 60 per minute
            'bitfinex': 90,   # 90 requests per minute
            'okx': 600,       # 600 requests per minute
            'kucoin': 300,    # 300 requests per minute
        }
        
    async def initialize(self):
        """Initialize connections and rate limiters"""
        logger.info("Initializing Exchange Integration Service...")
        
        # Initialize Redis
        self.redis_client = redis.from_url(REDIS_URL)
        
        # Initialize Kafka
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8')
        )
        
        # Initialize rate limiters
        for exchange, limit in self.rate_limits.items():
            self.rate_limiters[exchange] = RateLimiter(limit, 60)  # 60 seconds window
        
        logger.info("Exchange Integration Service initialized")
    
    async def add_exchange(self, exchange_name: str, credentials: ExchangeCredentials):
        """Add exchange with credentials"""
        try:
            exchange_class = getattr(ccxt, exchange_name)
            
            config = {
                'apiKey': credentials.api_key,
                'secret': credentials.secret,
                'sandbox': credentials.sandbox,
                'rateLimit': True,
                'enableRateLimit': True,
            }
            
            if credentials.passphrase:
                config['passphrase'] = credentials.passphrase
            
            exchange = exchange_class(config)
            await exchange.load_markets()
            
            self.exchanges[exchange_name] = exchange
            self.credentials[exchange_name] = credentials
            
            logger.info(f"Added exchange: {exchange_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add exchange {exchange_name}: {e}")
            return False
    
    async def get_balance(self, exchange_name: str, currency: Optional[str] = None) -> List[BalanceResponse]:
        """Get account balance from exchange"""
        if exchange_name not in self.exchanges:
            raise HTTPException(status_code=404, detail=f"Exchange {exchange_name} not configured")
        
        try:
            # Apply rate limiting
            if exchange_name in self.rate_limiters:
                await self.rate_limiters[exchange_name].wait_for_slot()
            
            exchange = self.exchanges[exchange_name]
            balance = await exchange.fetch_balance()
            
            balances = []
            for curr, amounts in balance.items():
                if curr == 'info':  # Skip raw response info
                    continue
                
                if currency and curr != currency:
                    continue
                    
                if isinstance(amounts, dict) and 'free' in amounts:
                    balances.append(BalanceResponse(
                        exchange=exchange_name,
                        currency=curr,
                        free=Decimal(str(amounts.get('free', 0))),
                        used=Decimal(str(amounts.get('used', 0))),
                        total=Decimal(str(amounts.get('total', 0)))
                    ))
            
            return balances
            
        except Exception as e:
            logger.error(f"Error fetching balance from {exchange_name}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def place_order(self, order_request: OrderRequest) -> OrderResponse:
        """Place order on exchange"""
        exchange_name = order_request.exchange
        
        if exchange_name not in self.exchanges:
            raise HTTPException(status_code=404, detail=f"Exchange {exchange_name} not configured")
        
        try:
            # Apply rate limiting
            if exchange_name in self.rate_limiters:
                await self.rate_limiters[exchange_name].wait_for_slot()
            
            exchange = self.exchanges[exchange_name]
            
            # Place order based on type
            if order_request.order_type == "market":
                if order_request.side == "buy":
                    order = await exchange.create_market_buy_order(
                        order_request.symbol, 
                        order_request.amount
                    )
                else:
                    order = await exchange.create_market_sell_order(
                        order_request.symbol, 
                        order_request.amount
                    )
            else:  # limit order
                if not order_request.price:
                    raise HTTPException(status_code=400, detail="Price required for limit orders")
                    
                order = await exchange.create_limit_order(
                    order_request.symbol,
                    order_request.side,
                    order_request.amount,
                    order_request.price
                )
            
            # Create response
            order_response = OrderResponse(
                order_id=order['id'],
                exchange=exchange_name,
                symbol=order_request.symbol,
                side=order_request.side,
                amount=order_request.amount,
                price=float(order.get('price', order_request.price or 0)),
                status=order.get('status', 'unknown'),
                timestamp=datetime.utcnow()
            )
            
            # Publish to Kafka for tracking
            await self._publish_trade_execution(order_response)
            
            return order_response
            
        except Exception as e:
            logger.error(f"Error placing order on {exchange_name}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_order_status(self, exchange_name: str, order_id: str, symbol: str) -> OrderResponse:
        """Get order status from exchange"""
        if exchange_name not in self.exchanges:
            raise HTTPException(status_code=404, detail=f"Exchange {exchange_name} not configured")
        
        try:
            # Apply rate limiting
            if exchange_name in self.rate_limiters:
                await self.rate_limiters[exchange_name].wait_for_slot()
            
            exchange = self.exchanges[exchange_name]
            order = await exchange.fetch_order(order_id, symbol)
            
            return OrderResponse(
                order_id=order['id'],
                exchange=exchange_name,
                symbol=order['symbol'],
                side=order['side'],
                amount=float(order['amount']),
                price=float(order.get('price', 0)),
                status=order.get('status', 'unknown'),
                timestamp=datetime.fromisoformat(order['datetime'].replace('Z', '+00:00')) if order.get('datetime') else datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error fetching order status from {exchange_name}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def cancel_order(self, exchange_name: str, order_id: str, symbol: str) -> bool:
        """Cancel order on exchange"""
        if exchange_name not in self.exchanges:
            raise HTTPException(status_code=404, detail=f"Exchange {exchange_name} not configured")
        
        try:
            # Apply rate limiting
            if exchange_name in self.rate_limiters:
                await self.rate_limiters[exchange_name].wait_for_slot()
            
            exchange = self.exchanges[exchange_name]
            result = await exchange.cancel_order(order_id, symbol)
            
            return result.get('status') == 'canceled'
            
        except Exception as e:
            logger.error(f"Error canceling order on {exchange_name}: {e}")
            return False
    
    async def _publish_trade_execution(self, order: OrderResponse):
        """Publish trade execution to Kafka"""
        try:
            message = {
                'order_id': order.order_id,
                'exchange': order.exchange,
                'symbol': order.symbol,
                'side': order.side,
                'amount': order.amount,
                'price': order.price,
                'status': order.status,
                'timestamp': order.timestamp.isoformat()
            }
            
            self.kafka_producer.send('trade-executions', message)
            
        except Exception as e:
            logger.error(f"Error publishing trade execution: {e}")

# Global exchange manager
exchange_manager = ExchangeManager()

@app.on_event("startup")
async def startup_event():
    await exchange_manager.initialize()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "exchange-integration", "timestamp": datetime.utcnow()}

@app.post("/exchanges/{exchange_name}/configure")
async def configure_exchange(exchange_name: str, credentials: ExchangeCredentials):
    """Configure exchange with API credentials"""
    success = await exchange_manager.add_exchange(exchange_name, credentials)
    if success:
        return {"message": f"Exchange {exchange_name} configured successfully"}
    raise HTTPException(status_code=400, detail=f"Failed to configure {exchange_name}")

@app.get("/exchanges")
async def list_exchanges():
    """List configured exchanges"""
    return {"exchanges": list(exchange_manager.exchanges.keys())}

@app.get("/exchanges/{exchange_name}/balance")
async def get_balance(exchange_name: str, currency: Optional[str] = None):
    """Get account balance"""
    balances = await exchange_manager.get_balance(exchange_name, currency)
    return {"balances": [balance.dict() for balance in balances]}

@app.post("/orders")
async def place_order(order_request: OrderRequest):
    """Place order on exchange"""
    order_response = await exchange_manager.place_order(order_request)
    return order_response.dict()

@app.get("/orders/{exchange_name}/{order_id}")
async def get_order_status(exchange_name: str, order_id: str, symbol: str):
    """Get order status"""
    order_response = await exchange_manager.get_order_status(exchange_name, order_id, symbol)
    return order_response.dict()

@app.delete("/orders/{exchange_name}/{order_id}")
async def cancel_order(exchange_name: str, order_id: str, symbol: str):
    """Cancel order"""
    success = await exchange_manager.cancel_order(exchange_name, order_id, symbol)
    return {"canceled": success}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
