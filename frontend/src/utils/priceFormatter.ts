/**
 * Dynamically formats cryptocurrency prices based on their magnitude
 * - For prices >= $1: Shows 2-4 decimal places
 * - For prices < $1: Shows enough significant digits to be meaningful
 * - For very small prices: Uses scientific notation when appropriate
 */
export const formatCryptoPrice = (price: number, maxSignificantDigits = 6): string => {
  if (price === 0) return "0.00";
  if (!isFinite(price)) return "N/A";

  const absolutePrice = Math.abs(price);
  
  // For prices >= $1, use standard decimal formatting
  if (absolutePrice >= 1) {
    if (absolutePrice >= 1000) {
      // For large prices, show fewer decimals
      return price.toFixed(2);
    } else if (absolutePrice >= 100) {
      return price.toFixed(3);
    } else {
      return price.toFixed(4);
    }
  }
  
  // For prices < $1, calculate dynamic precision
  if (absolutePrice >= 0.01) {
    // Between $0.01 and $1, show 4-6 decimals
    return price.toFixed(6);
  }
  
  if (absolutePrice >= 0.0001) {
    // Between $0.0001 and $0.01, show up to 8 decimals
    return price.toFixed(8);
  }
  
  // For very small prices, use significant digits approach
  if (absolutePrice >= 1e-12) {
    // Find the number of leading zeros after decimal point
    const leadingZeros = Math.floor(-Math.log10(absolutePrice));
    const decimals = Math.min(leadingZeros + maxSignificantDigits, 12);
    const formatted = price.toFixed(decimals);
    
    // Remove trailing zeros
    return formatted.replace(/\.?0+$/, '');
  }
  
  // For extremely small prices, use scientific notation
  return price.toExponential(3);
};

/**
 * Smart price formatter that adapts based on the price range in a dataset
 * Analyzes the price range and chooses optimal formatting
 */
export const createSmartPriceFormatter = (prices: number[]) => {
  if (!prices.length) return formatCryptoPrice;
  
  const validPrices = prices.filter(p => isFinite(p) && p > 0);
  if (!validPrices.length) return formatCryptoPrice;
  
  const minPrice = Math.min(...validPrices);
  const maxPrice = Math.max(...validPrices);
  
  // If all prices are in similar range, optimize for that range
  if (minPrice >= 1 && maxPrice < 10000) {
    // Standard range: 2-4 decimals
    return (price: number) => price.toFixed(4);
  }
  
  if (maxPrice < 0.01) {
    // All micro-prices: use more precision
    return (price: number) => formatCryptoPrice(price, 8);
  }
  
  if (minPrice < 0.001 && maxPrice > 1) {
    // Wide range: use dynamic formatting
    return formatCryptoPrice;
  }
  
  // Default to dynamic formatting
  return formatCryptoPrice;
};

/**
 * Format price with currency symbol if needed
 */
export const formatCryptoPriceWithSymbol = (
  price: number,
  symbol: string = "$",
  maxSignificantDigits = 6
): string => {
  const formattedPrice = formatCryptoPrice(price, maxSignificantDigits);
  return `${symbol}${formattedPrice}`;
};
