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
