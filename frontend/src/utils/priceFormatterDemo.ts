// Example usage of the dynamic price formatter
import { formatCryptoPrice, createSmartPriceFormatter } from './priceFormatter';

console.log('=== Dynamic Price Formatting Examples ===');

// High-value cryptocurrencies
console.log('BTC-like prices:');
console.log(`$65,432.12 → ${formatCryptoPrice(65432.12)}`);
console.log(`$43,891.00 → ${formatCryptoPrice(43891.00)}`);

// Mid-range cryptocurrencies  
console.log('\nETH/SOL-like prices:');
console.log(`$234.56 → ${formatCryptoPrice(234.56)}`);
console.log(`$12.3456 → ${formatCryptoPrice(12.3456)}`);

// Lower value cryptocurrencies
console.log('\nAltcoin prices:');
console.log(`$0.5678 → ${formatCryptoPrice(0.5678)}`);
console.log(`$0.01234 → ${formatCryptoPrice(0.01234)}`);

// Micro-cap/meme coin prices
console.log('\nMicro-cap prices (SHIB/PEPE-like):');
console.log(`$0.00001234 → ${formatCryptoPrice(0.00001234)}`);
console.log(`$0.000000456 → ${formatCryptoPrice(0.000000456)}`);
console.log(`$0.000000001 → ${formatCryptoPrice(0.000000001)}`);

// Extremely small prices
console.log('\nExtremely small prices:');
console.log(`$0.000000000123 → ${formatCryptoPrice(0.000000000123)}`);
console.log(`$1.23e-15 → ${formatCryptoPrice(1.23e-15)}`);

// Edge cases
console.log('\nEdge cases:');
console.log(`$0 → ${formatCryptoPrice(0)}`);
console.log(`Infinity → ${formatCryptoPrice(Infinity)}`);
console.log(`NaN → ${formatCryptoPrice(NaN)}`);

// Smart formatter for different datasets
console.log('\n=== Smart Formatter Examples ===');

const btcPrices = [65000, 64500, 65200, 64800];
const btcFormatter = createSmartPriceFormatter(btcPrices);
console.log(`BTC range formatter: $65,123.45 → ${btcFormatter(65123.45)}`);

const shibPrices = [0.00001234, 0.00001156, 0.00001298];
const shibFormatter = createSmartPriceFormatter(shibPrices);
console.log(`SHIB range formatter: $0.00001234 → ${shibFormatter(0.00001234)}`);

const mixedPrices = [65000, 0.00001234, 234.56];
const mixedFormatter = createSmartPriceFormatter(mixedPrices);
console.log(`Mixed range formatter: $0.00001234 → ${mixedFormatter(0.00001234)}`);
console.log(`Mixed range formatter: $65,000 → ${mixedFormatter(65000)}`);
