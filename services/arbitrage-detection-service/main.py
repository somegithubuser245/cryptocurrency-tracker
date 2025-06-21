#!/usr/bin/env python3
"""
Arbitrage Detection Service

Real-time arbitrage opportunity detection using advanced algorithms:
- Cross-exchange spread analysis
- Dynamic fee fetching from exchanges
- Risk-adjusted profit calculations
- Real market data only (no mock data)
"""

import asyncio
import json
import logging
import aiohttp
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis.asyncio as redis

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
REDIS_URL = "redis://redis:6379"
EXCHANGE_INTEGRATION_URL = "http://arbitrage-exchange-integration:8003"
MIN_PROFIT_THRESHOLD = 0.0001  # 0.01% minimum profit (realistic for crypto arbitrage)
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

class DynamicFeeCalculator:
    """Dynamic fee calculator that fetches real-time fees from exchanges"""
    
    def __init__(self, session: aiohttp.ClientSession, redis_client: redis.Redis):
        self.session = session
        self.redis_client = redis_client
        self.fee_cache: Dict[str, Dict] = {}
        
        # Fallback fees if API calls fail
        self.fallback_fees = {
            'binance': {'maker': 0.001, 'taker': 0.001},
            'coinbase': {'maker': 0.005, 'taker': 0.005},
            'kraken': {'maker': 0.0016, 'taker': 0.0026},
            'bitfinex': {'maker': 0.001, 'taker': 0.002},
            'okx': {'maker': 0.0008, 'taker': 0.001},
            'kucoin': {'maker': 0.001, 'taker': 0.001},
        }
    
    async def get_exchange_fees(self, exchange: str, symbol: str = None) -> Dict[str, float]:
        """Fetch real-time trading fees from exchange integration service"""
        try:
            # Try to get from Redis cache first
            cache_key = f"fees:{exchange}"
            if symbol:
                cache_key += f":{symbol}"
            
            cached_fees = await self.redis_client.get(cache_key)
            if cached_fees:
                try:
                    return json.loads(cached_fees)
                except json.JSONDecodeError:
                    pass
            
            # Fetch from exchange integration service
            url = f"{EXCHANGE_INTEGRATION_URL}/exchanges/{exchange}/fees"
            if symbol:
                url += f"/{symbol}"
            
            async with self.session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    fees = data.get('fees', {})
                    
                    # Cache the result
                    await self.redis_client.setex(cache_key, 3600, json.dumps(fees))
                    return fees
                    
        except Exception as e:
            logger.warning(f"Failed to fetch fees for {exchange}: {e}")
        
        # Return fallback fees
        return {
            'trading': {
                'maker': self.fallback_fees.get(exchange, {}).get('maker', 0.002),
                'taker': self.fallback_fees.get(exchange, {}).get('taker', 0.002),
                'percentage': True
            }
        }
    
    async def calculate_total_fees(self, buy_exchange: str, sell_exchange: str, 
                                 symbol: str, trade_amount: Decimal) -> Decimal:
        """Calculate total trading fees for arbitrage opportunity"""
        try:
            # Get fees for both exchanges
            buy_fees = await self.get_exchange_fees(buy_exchange, symbol)
            sell_fees = await self.get_exchange_fees(sell_exchange, symbol)
            
            # Extract trading fees
            buy_taker_fee = buy_fees.get('trading', {}).get('taker', 0.002)
            sell_taker_fee = sell_fees.get('trading', {}).get('taker', 0.002)
            
            # Calculate total trading fees (assuming taker fees for market orders)
            total_fee_pct = buy_taker_fee + sell_taker_fee
            
            # Add estimated withdrawal fee (simplified)
            withdrawal_fee_pct = 0.0005  # 0.05% estimated withdrawal fee
            
            return Decimal(str(total_fee_pct + withdrawal_fee_pct))
            
        except Exception as e:
            logger.error(f"Error calculating fees: {e}")
            # Return conservative estimate
            return Decimal('0.005')  # 0.5%

class ArbitrageDetector:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.http_session: Optional[aiohttp.ClientSession] = None
        self.fee_calculator: Optional[DynamicFeeCalculator] = None
        self.price_cache: Dict[str, Dict[str, dict]] = {}
        self.opportunities: List[ArbitrageOpportunity] = []
        self.min_profit = MIN_PROFIT_THRESHOLD
        
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
        
        # Initialize HTTP session
        self.http_session = aiohttp.ClientSession()
        
        # Initialize dynamic fee calculator
        if self.redis_client and self.http_session:
            self.fee_calculator = DynamicFeeCalculator(self.http_session, self.redis_client)
        
        logger.info("Arbitrage Detection Service initialized")
    
    async def cleanup(self):
        """Clean up connections"""
        if self.http_session:
            await self.http_session.close()
    
    async def get_opportunities_from_cache(self) -> List[dict]:
        """Get cached arbitrage opportunities from Redis (exclude mock data)"""
        try:
            if not self.redis_client:
                return []
                
            # Get all opportunity keys from Redis (exclude mock)
            keys = await self.redis_client.keys("opportunity:*")
            opportunities = []
            
            for key in keys:
                # Skip mock opportunities
                if b"mock" in key:
                    continue
                    
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
        """Detect arbitrage opportunities from Redis cached prices with dynamic fees"""
        try:
            if not self.redis_client or not self.fee_calculator:
                return []
            
            # Get price data from Redis
            price_keys = await self.redis_client.keys("price:*")
            if not price_keys:
                logger.info("No price data available in Redis")
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
            
            logger.info(f"Analyzing {len(symbol_prices)} symbols for arbitrage opportunities")
            
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
                        
                        # Calculate gross profit
                        gross_profit_pct = (sell_bid - buy_ask) / buy_ask
                        
                        if gross_profit_pct < self.min_profit:
                            continue
                        
                        # Estimate volume (conservative)
                        buy_volume = buy_data.get('volume', 0) or 0
                        sell_volume = sell_data.get('volume', 0) or 0
                        estimated_volume = min(buy_volume, sell_volume) * MAX_POSITION_SIZE
                        
                        if estimated_volume <= 0:
                            estimated_volume = 1.0  # Default minimum
                        
                        # Calculate real-time fees
                        estimated_fees_pct = await self.fee_calculator.calculate_total_fees(
                            buy_exchange, sell_exchange, symbol, Decimal(str(estimated_volume))
                        )
                        
                        # Net profit after fees
                        net_profit_pct = gross_profit_pct - float(estimated_fees_pct)
                        
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
                                'estimated_fees': float(estimated_fees_pct),
                                'net_profit_pct': net_profit_pct,
                                'liquidity_score': liquidity_score,
                                'confidence_score': confidence_score,
                                'timestamp': datetime.utcnow().isoformat(),
                                'estimated_volume': estimated_volume,
                                'execution_time_estimate': 300  # 5 minutes default
                            }
                            
                            opportunities.append(opportunity)
            
            logger.info(f"Found {len(opportunities)} real arbitrage opportunities")
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
            # Clear any old mock opportunities from Redis
            if arbitrage_detector.redis_client:
                mock_keys = await arbitrage_detector.redis_client.keys("opportunity:mock_*")
                if mock_keys:
                    await arbitrage_detector.redis_client.delete(*mock_keys)
                    logger.info(f"Cleared {len(mock_keys)} mock opportunities")
            
            # Detect real opportunities from current price data
            opportunities = await arbitrage_detector.detect_arbitrage_from_redis_prices()
            
            # Cache real opportunities in Redis
            if opportunities and arbitrage_detector.redis_client:
                for i, opportunity in enumerate(opportunities[:10]):  # Store top 10
                    cache_key = f"opportunity:{i}"
                    await arbitrage_detector.redis_client.setex(
                        cache_key, 300, json.dumps(opportunity)  # 5 minute TTL
                    )
                logger.info(f"Cached {len(opportunities)} real opportunities")
            
            # Real arbitrage opportunities are rare in efficient markets
            if len(opportunities) == 0:
                logger.info("No arbitrage opportunities detected (normal in efficient markets)")
            else:
                logger.info(f"Detected {len(opportunities)} real arbitrage opportunities")
            
            # Wait 30 seconds before next detection cycle
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Error in arbitrage detection task: {e}")
            await asyncio.sleep(30)

@app.on_event("startup")
async def startup_event():
    await arbitrage_detector.initialize()
    # Start background arbitrage detection
    asyncio.create_task(arbitrage_detection_background_task())

@app.on_event("shutdown")
async def shutdown_event():
    await arbitrage_detector.cleanup()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "arbitrage-detection", "timestamp": datetime.utcnow()}

@app.get("/opportunities")
async def get_current_opportunities():
    """Get current real arbitrage opportunities (no mock data)"""
    try:
        # Get real opportunities only
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
            "market_efficiency_note": "Low opportunity count indicates efficient markets"
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return {
            "active_symbols": 0,
            "min_profit_threshold": MIN_PROFIT_THRESHOLD,
            "max_position_size": MAX_POSITION_SIZE,
            "total_opportunities_detected": 0,
            "market_efficiency_note": "Error retrieving statistics"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)