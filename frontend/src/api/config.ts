// API Configuration
export const API_CONFIG = {
  BASE_URL: 'http://127.0.0.1:8000',
  ENDPOINTS: {
    CONFIG: '/static/config',
    OHLC_COMPARE: '/crypto/ohlc',
    LINE_COMPARE: '/crypto/line-compare',
  },
  TIMEOUT: 10000,
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
