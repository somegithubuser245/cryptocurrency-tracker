import { apiClient } from './client';
import type { 
  TaskStatusResponse, 
  BatchStatusSummaryResponse, 
  ComputedSpreadResponse 
} from '../types';

// Spreads API Services

/**
 * Initialize crypto pairs and supported exchanges in the database.
 * This must be called first before computing spreads.
 * Returns true if successful.
 */
export const initPairs = async (): Promise<boolean> => {
  return apiClient.post<boolean>('/spreads/init-pairs', {});
};

/**
 * Trigger background task to download all OHLC data for arbitrable pairs.
 * Should only be called after initPairs completes successfully.
 */
export const computeAllSpreads = async (): Promise<TaskStatusResponse> => {
  return apiClient.post<TaskStatusResponse>('/spreads/compute-all', {});
};

/**
 * Get aggregate batch processing status summary.
 */
export const getBatchStatus = async (): Promise<BatchStatusSummaryResponse> => {
  return apiClient.get<BatchStatusSummaryResponse>('/spreads/batch-status');
};

/**
 * Get all computed spreads with exchange names resolved.
 * Results are ordered by spread_percent in descending order.
 */
export const getComputedSpreads = async (): Promise<ComputedSpreadResponse[]> => {
  return apiClient.get<ComputedSpreadResponse[]>('/spreads/computed');
};

/**
 * Initialize the entire spreads computation workflow.
 * This function:
 * 1. Initializes crypto pairs in the database
 * 2. Waits for initialization to complete
 * 3. Triggers the compute-all background task
 * 
 * @throws Error if any step fails
 */
export const initializeAndComputeSpreads = async (): Promise<void> => {
  // Step 1: Initialize pairs
  const initSuccess = await initPairs();
  
  if (!initSuccess) {
    throw new Error('Failed to initialize pairs');
  }
  
  // Step 2: Wait for a moment to ensure DB operations complete
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Step 3: Trigger compute-all
  const computeResponse = await computeAllSpreads();
  
  if (computeResponse.status !== 'success') {
    throw new Error(`Failed to start spread computation: ${computeResponse.message}`);
  }
};

