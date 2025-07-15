"""
Data processing helpers for API call manager to eliminate code duplication
"""
import time
import logging
from typing import Dict, List, Any, Tuple

from ..config.config import TickerType
from ..routes.models.schemas import CompareRequest
from ..utils.timeframes_equalizer import Equalizer

logger = logging.getLogger(__name__)


class DataProcessor:
    """Helper class to process and equalize timeframe data"""
    
    def __init__(self, equalizer: Equalizer):
        self.equalizer = equalizer
    
    def process_chart_data(
        self, 
        data_sets_raw: List[List], 
        ticker_type: TickerType, 
        request: CompareRequest,
        start_time: float
    ) -> Tuple[List[Dict], List[Dict], float]:
        """
        Process raw data sets and return equalized data with response time
        
        Args:
            data_sets_raw: Raw data from exchanges
            ticker_type: Type of ticker (OHLC or CHART_LINE)
            request: Original request with exchange info
            start_time: Request start time for calculating response time
        
        Returns:
            Tuple of (exchange1_data, exchange2_data, response_time)
        """
        # Process data based on type
        column_names = list(self.equalizer.cnames)
        columns_to_drop = column_names[-1] if ticker_type == TickerType.OHLC else column_names[2:]
        
        eq_data_exchange1, eq_data_exchange2 = self.equalizer.equalize_timeframes(
            data_sets_raw[0], data_sets_raw[1], columns_to_drop
        )
        
        response_time = time.time() - start_time
        logger.info(f"Chart data served in {response_time:.2f}s for {request.crypto_id}")
        
        return eq_data_exchange1, eq_data_exchange2, response_time
    
    def create_error_response(
        self, 
        request: CompareRequest, 
        start_time: float, 
        error: Exception
    ) -> Dict[str, Any]:
        """
        Create standardized error response structure
        
        Args:
            request: Original request with exchange info
            start_time: Request start time
            error: Exception that occurred
        
        Returns:
            Error response dictionary
        """
        response_time = time.time() - start_time
        logger.error(f"Error getting chart data after {response_time:.2f}s: {error}")
        
        return {
            request.exchange1.value: [],
            request.exchange2.value: [],
        }
    
    def create_success_response(
        self, 
        eq_data_exchange1: List[Dict], 
        eq_data_exchange2: List[Dict], 
        request: CompareRequest
    ) -> Dict[str, List[Dict]]:
        """
        Create standardized success response structure
        
        Args:
            eq_data_exchange1: Processed data for first exchange
            eq_data_exchange2: Processed data for second exchange  
            request: Original request with exchange info
        
        Returns:
            Success response dictionary
        """
        return {
            request.exchange1.value: eq_data_exchange1,
            request.exchange2.value: eq_data_exchange2,
        }
    
    def create_metadata_response(
        self,
        eq_data_exchange1: List[Dict],
        eq_data_exchange2: List[Dict], 
        request: CompareRequest,
        response_time: float,
        cache_info: Dict[str, Dict],
        cache_ttl_seconds: int
    ) -> Dict[str, Any]:
        """
        Create response with metadata about data freshness and source
        
        Args:
            eq_data_exchange1: Processed data for first exchange
            eq_data_exchange2: Processed data for second exchange
            request: Original request
            response_time: Time taken to process request
            cache_info: Information about cache usage
            cache_ttl_seconds: Cache TTL for this request type
        
        Returns:
            Response with data and metadata
        """
        return {
            "data": {
                request.exchange1.value: eq_data_exchange1,
                request.exchange2.value: eq_data_exchange2,
            },
            "metadata": {
                "response_time_ms": round(response_time * 1000, 2),
                "timestamp": time.time(),
                "crypto_pair": request.crypto_id,
                "interval": request.interval,
                "exchanges": {
                    request.exchange1.value: cache_info.get(request.exchange1.value, {}),
                    request.exchange2.value: cache_info.get(request.exchange2.value, {}),
                },
                "data_points": {
                    request.exchange1.value: len(eq_data_exchange1),
                    request.exchange2.value: len(eq_data_exchange2),
                },
                "cache_ttl_seconds": cache_ttl_seconds,
                "is_real_time": True,  # Always true since we use real cryptocurrency APIs
            }
        }
    
    def create_metadata_error_response(
        self,
        request: CompareRequest,
        response_time: float,
        error: Exception
    ) -> Dict[str, Any]:
        """
        Create error response with metadata
        
        Args:
            request: Original request
            response_time: Time taken before error
            error: Exception that occurred
        
        Returns:
            Error response with metadata
        """
        return {
            "data": {
                request.exchange1.value: [],
                request.exchange2.value: [],
            },
            "metadata": {
                "response_time_ms": round(response_time * 1000, 2),
                "timestamp": time.time(),
                "error": str(error),
                "crypto_pair": request.crypto_id,
                "interval": request.interval,
                "is_real_time": True,
            }
        }