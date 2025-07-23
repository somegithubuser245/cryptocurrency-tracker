// API Configuration with environment detection
const getBaseUrl = (): string => {
  // Check if running in Docker (frontend service can reach backend via service name)
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    // Local development - backend running on localhost
    return 'http://localhost:8000';
  } else if (typeof window !== 'undefined') {
    // Docker or other containerized environment
    return `http://${window.location.hostname}:8000`;
  } else {
    // SSR or Node.js environment
    return 'http://backend:8000';
  }
};

export const API_CONFIG = {
  BASE_URL: getBaseUrl(),
  ENDPOINTS: {
    CONFIG: '/static/config',
    OHLC_COMPARE: '/crypto/ohlc',
    LINE_COMPARE: '/crypto/line-compare',
  },
  TIMEOUT: 30000, // Reasonable timeout for real cryptocurrency APIs
} as const;

// API endpoint builders
export const buildConfigUrl = (configType: string): string => 
  `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CONFIG}/${configType}`;

export const buildOhlcCompareUrl = (params: {
  exchange1: string;
  exchange2: string;
  interval: string;
  crypto_id: string;
}): string => {
  const searchParams = new URLSearchParams(params);
  return `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.OHLC_COMPARE}?${searchParams.toString()}`;
};

export const buildLineCompareUrl = (params: {
  exchange1: string;
  exchange2: string;
  interval: string;
  crypto_id: string;
}): string => {
  const searchParams = new URLSearchParams(params);
  return `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.LINE_COMPARE}?${searchParams.toString()}`;
};

// Log the configuration for debugging
console.log('[API Config] Base URL:', API_CONFIG.BASE_URL);
