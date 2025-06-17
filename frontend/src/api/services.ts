import { apiClient } from './client';
import { buildConfigUrl, buildCompareUrl } from './config';
import type { ConfigResponse, ChartDataResponse, CompareParams } from '../types';

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
};

export const chartApi = {
  async getCompareData(params: CompareParams): Promise<ChartDataResponse> {
    const url = buildCompareUrl(params);
    return apiClient.get<ChartDataResponse>(url);
  },
};
