import { apiClient } from './client';
import { buildConfigUrl, buildOhlcCompareUrl, buildLineCompareUrl, API_CONFIG } from './config';
import type { 
  ConfigResponse, 
  ChartDataResponse, 
  BackendLineDataResponse, 
  CompareParams, 
  PairsExchangesResponse,
  MaxSpreadResponse,
  AllSpreadsResponse,
  SpreadRequest
} from '../types';

export const configApi = {
  async getExchanges(): Promise<ConfigResponse> {
    return apiClient.get<ConfigResponse>(buildConfigUrl('exchanges'));
  },

  async getTimeRanges(): Promise<ConfigResponse> {
    return apiClient.get<ConfigResponse>(buildConfigUrl('timeranges'));
  },

  async getPairs(): Promise<ConfigResponse> {
    return apiClient.get<ConfigResponse>(buildConfigUrl('pairs'));
  },

  async getPairsExchanges(): Promise<PairsExchangesResponse> {
    return apiClient.get<PairsExchangesResponse>(`${API_CONFIG.BASE_URL}/static/pairs-exchanges`);
  },
};

export const chartApi = {
  async getCompareData(params: CompareParams): Promise<ChartDataResponse> {
    const url = buildOhlcCompareUrl(params);
    return apiClient.get<ChartDataResponse>(url);
  },
  async getLineCompareData(params: CompareParams): Promise<BackendLineDataResponse> {
    const url = buildLineCompareUrl(params);
    return apiClient.get<BackendLineDataResponse>(url);
  },
};

export const spreadApi = {
  async getMaxSpread(params: SpreadRequest): Promise<MaxSpreadResponse> {
    return apiClient.post<MaxSpreadResponse>(`${API_CONFIG.BASE_URL}/spreads/per-ticker/max`, params);
  },
  
  async getAllSpreads(params: SpreadRequest): Promise<AllSpreadsResponse> {
    return apiClient.post<AllSpreadsResponse>(`${API_CONFIG.BASE_URL}/spreads/per-ticker/all`, params);
  },
};
