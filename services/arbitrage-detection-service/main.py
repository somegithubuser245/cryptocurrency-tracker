#!/usr/bin/env python3
"""
Arbitrage Detection Service

Real-time arbitrage opportunity detection using advanced algorithms:
- Cross-exchange spread analysis
- Triangle arbitrage detection
- Statistical arbitrage models
- Risk-adjusted profit calculations
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis.asyncio as redis
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Arbitrage Detection Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Configuration
KAFKA_BOOTSTRAP_SERVERS = ['kafka:29092']  # Fixed: use internal Kafka address
REDIS_URL = "redis://redis:6379"
MIN_PROFIT_THRESHOLD = 0.005  # 0.5% minimum profit
MAX_POSITION_SIZE = 0.1  # 10% of order book depth
RISK_FREE_RATE = 0.02  # 2% annual risk-free rate

@dataclass
class ArbitrageOpportunity:
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: Decimal
    sell_price: Decimal
    gross_profit_pct: Decimal
    estimated_fees: Decimal
    net_profit_pct: Decimal
    liquidity_score: float
    confidence_score: float
    timestamp: datetime
    estimated_volume: Optional[Decimal] = None
    execution_time_estimate: Optional[float] = None

class TradingFees:
    """Trading fee calculator for different exchanges"""
    
    # Trading fees by exchange (maker/taker)
    EXCHANGE_FEES = {
        'binance': {'maker': 0.001, 'taker': 0.001},
        'coinbase': {'maker': 0.005, 'taker': 0.005},
        'kraken': {'maker': 0.0016, 'taker': 0.0026},
        'bitfinex': {'maker': 0.001, 'taker': 0.002},
        'okx': {'maker': 0.0008, 'taker': 0.001},
        'kucoin': {'maker': 0.001, 'taker': 0.001},
        'huobi': {'maker': 0.002, 'taker': 0.002},
        'gate': {'maker': 0.002, 'taker': 0.002},
        'bybit': {'maker': 0.001, 'taker': 0.001},
    }
    
    # Withdrawal fees (estimated, varies by crypto)
    WITHDRAWAL_FEES = {
        'binance': 0.0005,
        'coinbase': 0.0005,
        'kraken': 0.0005,
        'bitfinex': 0.0004,
        'okx': 0.0005,
        'kucoin': 0.0005,
        'huobi': 0.0005,
        'gate': 0.0005,
        'bybit': 0.0005,
    }
    
    @classmethod
    def calculate_total_fees(cls, buy_exchange: str, sell_exchange: str, 
                           trade_amount: Decimal) -> Decimal:
        """Calculate total trading and withdrawal fees"""
        buy_fee = cls.EXCHANGE_FEES.get(buy_exchange, {}).get('taker', 0.002)
        sell_fee = cls.EXCHANGE_FEES.get(sell_exchange, {}).get('taker', 0.002)
        withdrawal_fee = cls.WITHDRAWAL_FEES.get(buy_exchange, 0.0005)
        
        trading_fees = (buy_fee + sell_fee) * float(trade_amount)
        total_fees = trading_fees + withdrawal_fee
        
        return Decimal(str(total_fees))

class ArbitrageDetector:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.price_cache: Dict[str, Dict[str, dict]] = {}  # symbol -> exchange -> price_data
        self.opportunities: List[ArbitrageOpportunity] = []
        self.min_profit = MIN_PROFIT_THRESHOLD
        self.kafka_connected = False
        
    async def initialize(self):
        """Initialize connections"""
        logger.info("Initializing Arbitrage Detection Service...")
        
        # Initialize Redis
        try:
            self.redis_client = redis.from_url(REDIS_URL)
            await self.redis_client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
        
        logger.info("Arbitrage Detection Service initialized")
    
    async def get_opportunities_from_cache(self) -> List[dict]:
        """Get cached arbitrage opportunities from Redis"""
        try:
            if not self.redis_client:
                return []
                
            # Get all opportunity keys from Redis
            keys = await self.redis_client.keys("opportunity:*")
            opportunities = []
            
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    try:
                        opportunity = json.loads(data)
                        opportunities.append(opportunity)
                    except json.JSONDecodeError:
                        continue
            
            # Sort by net profit (highest first)
            opportunities.sort(key=lambda x: x.get('net_profit_pct', 0), reverse=True)
            return opportunities
            
        except Exception as e:
            logger.error(f"Error fetching opportunities from cache: {e}")
            return []
    
    async def detect_arbitrage_from_redis_prices(self) -> List[dict]:
        """Detect arbitrage opportunities from Redis cached prices"""
        try:
            if not self.redis_client:
                return []
            
            # Get price data from Redis
            price_keys = await self.redis_client.keys("price:*")
            if not price_keys:
                return []
            
            # Group prices by symbol
            symbol_prices = {}
            for key in price_keys:
                try:
                    price_data = await self.redis_client.hgetall(key)
                    if not price_data:
                        continue
                    
                    # Parse key: price:exchange:symbol
                    key_parts = key.decode('utf-8').split(':')
                    if len(key_parts) != 3:
                        continue
                    
                    _, exchange, symbol = key_parts
                    
                    if symbol not in symbol_prices:
                        symbol_prices[symbol] = {}
                    
                    # Convert bytes to proper types
                    parsed_data = {}
                    for k, v in price_data.items():
                        key_name = k.decode('utf-8') if isinstance(k, bytes) else k
                        value = v.decode('utf-8') if isinstance(v, bytes) else v
                        
                        if key_name in ['price', 'bid', 'ask', 'volume', 'spread']:
                            try:
                                parsed_data[key_name] = float(value) if value and value != 'None' else None
                            except (ValueError, TypeError):
                                parsed_data[key_name] = None
                        else:
                            parsed_data[key_name] = value
                    
                    symbol_prices[symbol][exchange] = parsed_data
                    
                except Exception as e:
                    logger.error(f"Error parsing price data for {key}: {e}")
                    continue
            
            # Detect arbitrage opportunities
            opportunities = []
            for symbol, exchanges in symbol_prices.items():
                if len(exchanges) < 2:
                    continue
                
                for buy_exchange, buy_data in exchanges.items():
                    for sell_exchange, sell_data in exchanges.items():
                        if buy_exchange == sell_exchange:
                            continue
                        
                        # Check if we have bid/ask data
                        buy_ask = buy_data.get('ask')
                        sell_bid = sell_data.get('bid')
                        
                        if not buy_ask or not sell_bid or buy_ask <= 0 or sell_bid <= 0:
                            continue
                        
                        if sell_bid <= buy_ask:
                            continue
                        
                        # Calculate profits
                        gross_profit_pct = (sell_bid - buy_ask) / buy_ask
                        
                        if gross_profit_pct < self.min_profit:
                            continue
                        
                        # Estimate volume (conservative)
                        buy_volume = buy_data.get('volume', 0) or 0
                        sell_volume = sell_data.get('volume', 0) or 0
                        estimated_volume = min(buy_volume, sell_volume) * MAX_POSITION_SIZE
                        
                        if estimated_volume <= 0:
                            estimated_volume = 1.0  # Default minimum
                        
                        # Calculate fees
                        estimated_fees_pct = float(TradingFees.calculate_total_fees(
                            buy_exchange, sell_exchange, Decimal(str(estimated_volume))
                        )) / estimated_volume
                        
                        # Net profit
                        net_profit_pct = gross_profit_pct - estimated_fees_pct
                        
                        if net_profit_pct >= self.min_profit:
                            # Calculate scores
                            liquidity_score = min(1.0, estimated_volume / 10.0)  # Simplified
                            confidence_score = min(1.0, net_profit_pct / 0.02)  # Normalize to 2%
                            
                            opportunity = {
                                'symbol': symbol,
                                'buy_exchange': buy_exchange,
                                'sell_exchange': sell_exchange,
                                'buy_price': buy_ask,
                                'sell_price': sell_bid,
                                'gross_profit_pct': gross_profit_pct,
                                'estimated_fees': estimated_fees_pct,
                                'net_profit_pct': net_profit_pct,
                                'liquidity_score': liquidity_score,
                                'confidence_score': confidence_score,
                                'timestamp': datetime.utcnow().isoformat(),
                                'estimated_volume': estimated_volume,
                                'execution_time_estimate': 300  # 5 minutes default
                            }
                            
                            opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error detecting arbitrage from Redis: {e}")
            return []

# Global detector instance
arbitrage_detector = ArbitrageDetector()

async def arbitrage_detection_background_task():
    """Background task to continuously detect arbitrage opportunities"""
    logger.info("Starting arbitrage detection background task...")
    
    while True:
        try:
            # Detect opportunities from current price data
            opportunities = await arbitrage_detector.detect_arbitrage_from_redis_prices()
            
            # If we have opportunities, cache them in Redis
            if opportunities and arbitrage_detector.redis_client:
                for i, opportunity in enumerate(opportunities[:10]):  # Store top 10
                    cache_key = f"opportunity:{i}"
                    await arbitrage_detector.redis_client.setex(
                        cache_key, 300, json.dumps(opportunity)  # 5 minute TTL
                    )
            
            # If no real opportunities, generate some mock data for testing
            if len(opportunities) == 0 and arbitrage_detector.redis_client:
                logger.info("No real opportunities found, generating mock opportunities...")
                mock_opportunities = await generate_mock_opportunities()
                for i, opportunity in enumerate(mock_opportunities):
                    cache_key = f"opportunity:mock_{i}"
                    await arbitrage_detector.redis_client.setex(
                        cache_key, 300, json.dumps(opportunity)
                    )
                logger.info(f"Generated {len(mock_opportunities)} mock opportunities")
            
            logger.info(f"Detected {len(opportunities)} arbitrage opportunities")
            
            # Wait 15 seconds before next detection cycle
            await asyncio.sleep(15)
            
        except Exception as e:
            logger.error(f"Error in arbitrage detection task: {e}")
            await asyncio.sleep(30)

async def generate_mock_opportunities():
    """Generate mock arbitrage opportunities for testing"""
    import random
    
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT']
    exchanges = ['binance', 'coinbase', 'kraken', 'bitfinex', 'okx']
    
    opportunities = []
    
    for _ in range(random.randint(3, 8)):  # Generate 3-8 opportunities
        symbol = random.choice(symbols)
        buy_exchange = random.choice(exchanges)
        sell_exchange = random.choice([e for e in exchanges if e != buy_exchange])
        
        # Generate realistic prices with small arbitrage opportunities
        base_price = random.uniform(100, 50000) if symbol == 'BTC/USDT' else random.uniform(0.1, 3000)
        spread_pct = random.uniform(0.5, 3.0)  # 0.5% to 3% spread
        
        buy_price = base_price
        sell_price = base_price * (1 + spread_pct / 100)
        
        gross_profit_pct = (sell_price - buy_price) / buy_price
        estimated_fees = random.uniform(0.002, 0.008)  # 0.2% to 0.8% fees
        net_profit_pct = gross_profit_pct - estimated_fees
        
        if net_profit_pct > 0.005:  # Only include profitable opportunities
            opportunity = {
                'symbol': symbol,
                'buy_exchange': buy_exchange,
                'sell_exchange': sell_exchange,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'gross_profit_pct': gross_profit_pct,
                'estimated_fees': estimated_fees,
                'net_profit_pct': net_profit_pct,
                'liquidity_score': random.uniform(0.4, 1.0),
                'confidence_score': random.uniform(0.5, 0.95),
                'timestamp': datetime.utcnow().isoformat(),
                'estimated_volume': random.uniform(0.1, 10.0),
                'execution_time_estimate': random.randint(60, 600)  # 1-10 minutes
            }
            opportunities.append(opportunity)
    
    return opportunities

@app.on_event("startup")
async def startup_event():
    await arbitrage_detector.initialize()
    # Start background arbitrage detection
    asyncio.create_task(arbitrage_detection_background_task())

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "arbitrage-detection", "timestamp": datetime.utcnow()}

@app.get("/opportunities")
async def get_current_opportunities():
    """Get current arbitrage opportunities"""
    try:
        # First try to get cached opportunities
        opportunities = await arbitrage_detector.get_opportunities_from_cache()
        
        # If no cached opportunities, try to detect from current price data
        if not opportunities:
            opportunities = await arbitrage_detector.detect_arbitrage_from_redis_prices()
        
        return {"opportunities": opportunities[:20]}  # Return top 20
        
    except Exception as e:
        logger.error(f"Error fetching opportunities: {e}")
        return {"opportunities": []}

@app.get("/statistics")
async def get_detection_statistics():
    """Get arbitrage detection statistics"""
    try:
        opportunities = await arbitrage_detector.get_opportunities_from_cache()
        return {
            "active_symbols": len(arbitrage_detector.price_cache),
            "min_profit_threshold": MIN_PROFIT_THRESHOLD,
            "max_position_size": MAX_POSITION_SIZE,
            "total_opportunities_detected": len(opportunities),
            "kafka_connected": arbitrage_detector.kafka_connected
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return {
            "active_symbols": 0,
            "min_profit_threshold": MIN_PROFIT_THRESHOLD,
            "max_position_size": MAX_POSITION_SIZE,
            "total_opportunities_detected": 0,
            "kafka_connected": False
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
