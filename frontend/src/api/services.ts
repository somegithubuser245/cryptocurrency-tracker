import { apiClient } from './client';
import { buildConfigUrl, buildOhlcCompareUrl, buildLineCompareUrl, API_CONFIG } from './config';
import type { ConfigResponse, ChartDataResponse, BackendLineDataResponse, CompareParams, PairsExchangesResponse } from '../types';

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
