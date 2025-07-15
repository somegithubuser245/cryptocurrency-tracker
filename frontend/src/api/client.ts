import { API_CONFIG } from './config';

interface RetryConfig {
  maxRetries: number;
  retryDelay: number;
  backoffMultiplier: number;
}

interface RequestConfig {
  timeout?: number;
  retries?: Partial<RetryConfig>;
}

// Enhanced API client with timeout handling and retry logic
class ApiClient {
  private defaultTimeout: number;
  private defaultRetryConfig: RetryConfig;

  constructor(_baseURL: string, timeout: number = API_CONFIG.TIMEOUT) {
    this.defaultTimeout = timeout;
    this.defaultRetryConfig = {
      maxRetries: 3,
      retryDelay: 1000,
      backoffMultiplier: 2,
    };
  }

  private async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private isRetryableError(error: Error): boolean {
    // Retry on network errors, timeouts, and 5xx server errors
    return (
      error.name === 'AbortError' ||
      error.message.includes('Failed to fetch') ||
      error.message.includes('Network request failed') ||
      error.message.includes('HTTP 5') ||
      error.message.includes('Request timeout')
    );
  }

  private async requestWithRetry<T>(
    url: string,
    options: RequestInit = {},
    config: RequestConfig = {}
  ): Promise<T> {
    const timeout = config.timeout || this.defaultTimeout;
    const retryConfig = { ...this.defaultRetryConfig, ...config.retries };
    
    let lastError: Error = new Error('Unknown error occurred');

    for (let attempt = 0; attempt <= retryConfig.maxRetries; attempt++) {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      try {
        console.log(`API Request attempt ${attempt + 1}/${retryConfig.maxRetries + 1} to ${url}`);
        
        const response = await fetch(url, {
          ...options,
          signal: controller.signal,
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            ...options.headers,
          },
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorMessage = `HTTP ${response.status}: ${response.statusText}`;
          
          // Don't retry 4xx client errors (except 408 timeout)
          if (response.status >= 400 && response.status < 500 && response.status !== 408) {
            throw new Error(errorMessage);
          }
          
          throw new Error(errorMessage);
        }

        const data = await response.json();
        console.log(`API Request successful to ${url}`);
        return data;
      } catch (error) {
        clearTimeout(timeoutId);
        
        if (error instanceof Error) {
          if (error.name === 'AbortError') {
            lastError = new Error(`Request timeout after ${timeout}ms`);
          } else {
            lastError = error;
          }
        } else {
          lastError = new Error('Unknown error occurred');
        }

        console.warn(`API Request failed (attempt ${attempt + 1}): ${lastError.message}`);

        // Don't retry on last attempt or non-retryable errors
        if (attempt === retryConfig.maxRetries || !this.isRetryableError(lastError)) {
          break;
        }

        // Wait before retrying with exponential backoff
        const delayMs = retryConfig.retryDelay * Math.pow(retryConfig.backoffMultiplier, attempt);
        console.log(`Retrying in ${delayMs}ms...`);
        await this.delay(delayMs);
      }
    }

    throw lastError;
  }

  private async request<T>(
    url: string,
    options: RequestInit = {},
    config: RequestConfig = {}
  ): Promise<T> {
    return this.requestWithRetry<T>(url, options, config);
  }

  async get<T>(url: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(url, { method: 'GET' }, config);
  }

  async post<T>(url: string, data: unknown, config?: RequestConfig): Promise<T> {
    return this.request<T>(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    }, config);
  }

  // Health check method to test connectivity
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(3000), // Short timeout for health check
      });
      return response.ok;
    } catch {
      return false;
    }
  }
}

// Create API client instance
export const apiClient = new ApiClient(API_CONFIG.BASE_URL);
