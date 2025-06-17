// API Response Types
export interface ConfigResponse {
  [key: string]: string;
}

export interface ChartDataResponse {
  [exchangeName: string]: KlineData[];
}

export interface KlineData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

// UI Types
export interface SelectOption {
  id: string;
  name: string;
}

export interface CompareParams {
  exchange1: string;
  exchange2: string;
  interval: string;
  crypto_id: string;
}

// Component Props
export interface ChartCardProps {
  title: string;
  data: KlineData[];
  api_provider: string;
}

// Hook Return Types
export interface UseConfigData {
  exchanges: SelectOption[];
  timeRanges: SelectOption[];
  pairs: SelectOption[];
  loading: boolean;
  error: string | null;
}

export interface UseChartData {
  data: ChartDataResponse | null;
  loading: boolean;
  error: string | null;
  fetchData: (params: CompareParams) => Promise<void>;
}

// State Types
export interface AppState {
  selectedExchange1: string;
  selectedExchange2: string;
  selectedTimeRange: string;
  selectedPair: string;
}
