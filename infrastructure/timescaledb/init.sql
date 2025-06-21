-- TimescaleDB initialization script for Cryptocurrency Arbitrage Detection System
-- Creates optimized time-series tables for high-frequency trading data

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Price data table optimized for arbitrage detection
CREATE TABLE price_data (
  time TIMESTAMPTZ NOT NULL,
  exchange VARCHAR(50) NOT NULL,
  symbol VARCHAR(20) NOT NULL,
  price DECIMAL(18,8) NOT NULL,
  bid DECIMAL(18,8),
  ask DECIMAL(18,8),
  volume DECIMAL(18,8),
  spread DECIMAL(18,8) GENERATED ALWAYS AS (ask - bid) STORED,
  spread_pct DECIMAL(8,4) GENERATED ALWAYS AS 
    (CASE WHEN bid > 0 THEN ((ask - bid) / bid) * 100 ELSE NULL END) STORED
);

-- Create hypertable with time partitioning and space partitioning by exchange
SELECT create_hypertable('price_data', 'time', 'exchange', 4);

-- Create indexes for fast arbitrage queries
CREATE INDEX idx_price_symbol_time ON price_data (symbol, time DESC);
CREATE INDEX idx_price_exchange_symbol ON price_data (exchange, symbol, time DESC);
CREATE INDEX idx_price_spread ON price_data (symbol, spread_pct DESC) WHERE spread_pct IS NOT NULL;

-- Arbitrage opportunities table
CREATE TABLE arbitrage_opportunities (
  id SERIAL PRIMARY KEY,
  detected_at TIMESTAMPTZ NOT NULL,
  symbol VARCHAR(20) NOT NULL,
  buy_exchange VARCHAR(50) NOT NULL,
  sell_exchange VARCHAR(50) NOT NULL,
  buy_price DECIMAL(18,8) NOT NULL,
  sell_price DECIMAL(18,8) NOT NULL,
  gross_profit_pct DECIMAL(8,4) NOT NULL,
  estimated_fees DECIMAL(8,4) NOT NULL,
  net_profit_pct DECIMAL(8,4) NOT NULL,
  liquidity_score DECIMAL(4,2),
  confidence_score DECIMAL(4,2),
  estimated_volume DECIMAL(18,8),
  execution_time_estimate INTEGER, -- in seconds
  executed BOOLEAN DEFAULT FALSE,
  executed_at TIMESTAMPTZ,
  actual_profit_pct DECIMAL(8,4),
  notes TEXT
);

-- Create hypertable for arbitrage opportunities
SELECT create_hypertable('arbitrage_opportunities', 'detected_at');

-- Indexes for arbitrage opportunities
CREATE INDEX idx_arb_symbol_time ON arbitrage_opportunities (symbol, detected_at DESC);
CREATE INDEX idx_arb_profit ON arbitrage_opportunities (net_profit_pct DESC);
CREATE INDEX idx_arb_exchanges ON arbitrage_opportunities (buy_exchange, sell_exchange);
CREATE INDEX idx_arb_executed ON arbitrage_opportunities (executed, detected_at DESC);

-- Exchange metadata table
CREATE TABLE exchanges (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL,
  display_name VARCHAR(100) NOT NULL,
  api_url VARCHAR(255),
  websocket_url VARCHAR(255),
  maker_fee DECIMAL(6,4) NOT NULL DEFAULT 0.001,
  taker_fee DECIMAL(6,4) NOT NULL DEFAULT 0.001,
  withdrawal_fee DECIMAL(18,8) DEFAULT 0.0005,
  min_trade_amount DECIMAL(18,8) DEFAULT 0.001,
  max_trade_amount DECIMAL(18,8),
  daily_volume_24h DECIMAL(20,2),
  reliability_score DECIMAL(3,2) DEFAULT 0.85,
  avg_response_time_ms INTEGER DEFAULT 100,
  uptime_pct DECIMAL(5,2) DEFAULT 99.00,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert initial exchange data
INSERT INTO exchanges (name, display_name, maker_fee, taker_fee, withdrawal_fee, reliability_score) VALUES
('binance', 'Binance', 0.0010, 0.0010, 0.0005, 0.95),
('coinbase', 'Coinbase Pro', 0.0050, 0.0050, 0.0005, 0.90),
('kraken', 'Kraken', 0.0016, 0.0026, 0.0005, 0.85),
('bitfinex', 'Bitfinex', 0.0010, 0.0020, 0.0004, 0.80),
('okx', 'OKX', 0.0008, 0.0010, 0.0005, 0.85),
('kucoin', 'KuCoin', 0.0010, 0.0010, 0.0005, 0.80),
('huobi', 'Huobi', 0.0020, 0.0020, 0.0005, 0.75),
('gate', 'Gate.io', 0.0020, 0.0020, 0.0005, 0.75),
('bybit', 'Bybit', 0.0010, 0.0010, 0.0005, 0.80),
('mexc', 'MEXC', 0.0020, 0.0020, 0.0005, 0.70),
('lbank', 'LBank', 0.0010, 0.0010, 0.0005, 0.70),
('cryptocom', 'Crypto.com', 0.0010, 0.0010, 0.0005, 0.75),
('bitget', 'Bitget', 0.0010, 0.0010, 0.0005, 0.75),
('poloniex', 'Poloniex', 0.0015, 0.0025, 0.0005, 0.70),
('bingx', 'BingX', 0.0010, 0.0010, 0.0005, 0.70);

-- Trading pairs table
CREATE TABLE trading_pairs (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(20) NOT NULL,
  base_currency VARCHAR(10) NOT NULL,
  quote_currency VARCHAR(10) NOT NULL,
  min_trade_amount DECIMAL(18,8),
  max_trade_amount DECIMAL(18,8),
  price_precision INTEGER DEFAULT 8,
  amount_precision INTEGER DEFAULT 8,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert major trading pairs
INSERT INTO trading_pairs (symbol, base_currency, quote_currency) VALUES
('BTC/USDT', 'BTC', 'USDT'),
('ETH/USDT', 'ETH', 'USDT'),
('BNB/USDT', 'BNB', 'USDT'),
('ADA/USDT', 'ADA', 'USDT'),
('SOL/USDT', 'SOL', 'USDT'),
('XRP/USDT', 'XRP', 'USDT'),
('DOT/USDT', 'DOT', 'USDT'),
('AVAX/USDT', 'AVAX', 'USDT'),
('MATIC/USDT', 'MATIC', 'USDT'),
('LINK/USDT', 'LINK', 'USDT'),
('LTC/USDT', 'LTC', 'USDT'),
('BCH/USDT', 'BCH', 'USDT'),
('UNI/USDT', 'UNI', 'USDT'),
('ATOM/USDT', 'ATOM', 'USDT'),
('FIL/USDT', 'FIL', 'USDT');

-- Exchange pair relationships (which exchanges support which pairs)
CREATE TABLE exchange_pairs (
  id SERIAL PRIMARY KEY,
  exchange_id INTEGER REFERENCES exchanges(id),
  pair_id INTEGER REFERENCES trading_pairs(id),
  exchange_symbol VARCHAR(20), -- Exchange-specific symbol format
  min_order_size DECIMAL(18,8),
  max_order_size DECIMAL(18,8),
  is_active BOOLEAN DEFAULT TRUE,
  last_updated TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(exchange_id, pair_id)
);

-- Portfolio tracking table
CREATE TABLE portfolio_positions (
  id SERIAL PRIMARY KEY,
  exchange VARCHAR(50) NOT NULL,
  symbol VARCHAR(20) NOT NULL,
  amount DECIMAL(18,8) NOT NULL DEFAULT 0,
  average_price DECIMAL(18,8),
  unrealized_pnl DECIMAL(18,8) DEFAULT 0,
  last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Trade execution log
CREATE TABLE trade_executions (
  id SERIAL PRIMARY KEY,
  opportunity_id INTEGER REFERENCES arbitrage_opportunities(id),
  trade_type VARCHAR(10) NOT NULL, -- 'BUY' or 'SELL'
  exchange VARCHAR(50) NOT NULL,
  symbol VARCHAR(20) NOT NULL,
  amount DECIMAL(18,8) NOT NULL,
  price DECIMAL(18,8) NOT NULL,
  fee DECIMAL(18,8) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING, FILLED, CANCELLED, FAILED
  external_order_id VARCHAR(100),
  executed_at TIMESTAMPTZ DEFAULT NOW(),
  filled_at TIMESTAMPTZ,
  error_message TEXT
);

-- Performance metrics table
CREATE TABLE performance_metrics (
  id SERIAL PRIMARY KEY,
  date DATE NOT NULL,
  total_opportunities_detected INTEGER DEFAULT 0,
  opportunities_executed INTEGER DEFAULT 0,
  total_gross_profit DECIMAL(18,8) DEFAULT 0,
  total_fees DECIMAL(18,8) DEFAULT 0,
  total_net_profit DECIMAL(18,8) DEFAULT 0,
  success_rate DECIMAL(5,2) DEFAULT 0,
  avg_profit_per_trade DECIMAL(18,8) DEFAULT 0,
  max_drawdown DECIMAL(8,4) DEFAULT 0,
  sharpe_ratio DECIMAL(6,4) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(date)
);

-- Continuous aggregates for fast analytics queries

-- 1-minute price aggregates
CREATE MATERIALIZED VIEW price_1min AS
SELECT 
  time_bucket('1 minute', time) AS bucket,
  exchange,
  symbol,
  first(price, time) AS open,
  max(price) AS high,
  min(price) AS low,
  last(price, time) AS close,
  avg(volume) AS avg_volume,
  avg(spread_pct) AS avg_spread_pct
FROM price_data
GROUP BY bucket, exchange, symbol
WITH NO DATA;

SELECT add_continuous_aggregate_policy('price_1min',
  start_offset => INTERVAL '7 days',
  end_offset => INTERVAL '1 minute',
  schedule_interval => INTERVAL '1 minute');

-- 5-minute arbitrage opportunity aggregates
CREATE MATERIALIZED VIEW arbitrage_5min AS
SELECT 
  time_bucket('5 minutes', detected_at) AS bucket,
  symbol,
  count(*) AS opportunity_count,
  avg(net_profit_pct) AS avg_profit_pct,
  max(net_profit_pct) AS max_profit_pct,
  avg(confidence_score) AS avg_confidence,
  count(*) FILTER (WHERE executed = true) AS executed_count
FROM arbitrage_opportunities
GROUP BY bucket, symbol
WITH NO DATA;

SELECT add_continuous_aggregate_policy('arbitrage_5min',
  start_offset => INTERVAL '7 days',
  end_offset => INTERVAL '5 minutes',
  schedule_interval => INTERVAL '5 minutes');

-- Data retention policies

-- Keep raw price data for 30 days
SELECT add_retention_policy('price_data', INTERVAL '30 days');

-- Keep arbitrage opportunities for 90 days
SELECT add_retention_policy('arbitrage_opportunities', INTERVAL '90 days');

-- Functions for common queries

-- Function to get current spreads across exchanges
CREATE OR REPLACE FUNCTION get_current_spreads(p_symbol VARCHAR)
RETURNS TABLE (
  exchange VARCHAR,
  price DECIMAL,
  bid DECIMAL,
  ask DECIMAL,
  spread_pct DECIMAL,
  last_update TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT DISTINCT ON (pd.exchange)
    pd.exchange,
    pd.price,
    pd.bid,
    pd.ask,
    pd.spread_pct,
    pd.time AS last_update
  FROM price_data pd
  WHERE pd.symbol = p_symbol
    AND pd.time > NOW() - INTERVAL '5 minutes'
  ORDER BY pd.exchange, pd.time DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate arbitrage opportunities
CREATE OR REPLACE FUNCTION calculate_arbitrage_opportunities(p_symbol VARCHAR)
RETURNS TABLE (
  buy_exchange VARCHAR,
  sell_exchange VARCHAR,
  buy_price DECIMAL,
  sell_price DECIMAL,
  profit_pct DECIMAL
) AS $$
BEGIN
  RETURN QUERY
  WITH latest_prices AS (
    SELECT DISTINCT ON (exchange)
      exchange,
      ask,
      bid
    FROM price_data
    WHERE symbol = p_symbol
      AND time > NOW() - INTERVAL '1 minute'
      AND ask IS NOT NULL
      AND bid IS NOT NULL
    ORDER BY exchange, time DESC
  )
  SELECT 
    buy.exchange AS buy_exchange,
    sell.exchange AS sell_exchange,
    buy.ask AS buy_price,
    sell.bid AS sell_price,
    ((sell.bid - buy.ask) / buy.ask * 100) AS profit_pct
  FROM latest_prices buy
  CROSS JOIN latest_prices sell
  WHERE buy.exchange != sell.exchange
    AND sell.bid > buy.ask
    AND ((sell.bid - buy.ask) / buy.ask * 100) > 0.5  -- Minimum 0.5% profit
  ORDER BY profit_pct DESC;
END;
$$ LANGUAGE plpgsql;

-- Indexes for performance
CREATE INDEX idx_portfolio_exchange_symbol ON portfolio_positions (exchange, symbol);
CREATE INDEX idx_trades_opportunity ON trade_executions (opportunity_id);
CREATE INDEX idx_trades_status ON trade_executions (status, executed_at);
CREATE INDEX idx_metrics_date ON performance_metrics (date DESC);

-- Create user for application
CREATE USER arbitrage_app WITH PASSWORD 'arbitrage_secure_password_2025';
GRANT USAGE ON SCHEMA public TO arbitrage_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO arbitrage_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO arbitrage_app;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO arbitrage_app;

COMMIT;
