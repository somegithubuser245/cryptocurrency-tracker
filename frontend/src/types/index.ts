export interface KlineData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

export interface LineData {
  time: number;
  value: number;
}

export interface ChartDataResponse {
  [exchangeName: string]: KlineData[];
}

export interface LineDataResponse {
  [exchangeName: string]: LineData[];
}

export interface SelectOption {
  id: string;
  name: string;
}

export type ChartType = 'line' | 'ohlc';

export interface ChartCardProps {
  title: string;
  data: KlineData[];
  api_provider: string;
}

// Spreads API types
export interface TaskStatusResponse {
  status: string;
  message: string;
}

export interface BatchStatusSummaryResponse {
  total_pairs: number;
  cached: number;
  spreads_computed: number;
  processing_progress: number;
}

export interface ComputedSpreadResponse {
  crypto_name: string;
  time: string | null;
  spread_percent: number;
  high_exchange: string;
  low_exchange: string;
}
