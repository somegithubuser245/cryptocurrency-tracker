import React, { useState, useMemo } from 'react';
import type { PairsExchangesResponse } from '../types';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

interface PairsTableProps {
  pairsData: PairsExchangesResponse | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}

const PairsTable: React.FC<PairsTableProps> = ({
  pairsData,
  loading,
  error,
  onRetry,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 50;

  // Filter pairs based on search term
  const filteredPairs = useMemo(() => {
    if (!pairsData) return [];
    
    const pairs = Object.keys(pairsData);
    if (!searchTerm) return pairs;
    
    return pairs.filter(pair => 
      pair.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [pairsData, searchTerm]);

  // Paginate filtered pairs
  const paginatedPairs = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredPairs.slice(startIndex, endIndex);
  }, [filteredPairs, currentPage]);

  const totalPages = Math.ceil(filteredPairs.length / itemsPerPage);

  // Get all unique exchanges from the data
  const allExchanges = useMemo(() => {
    if (!pairsData) return [];
    
    const exchangeSet = new Set<string>();
    Object.values(pairsData).forEach(exchangeList => {
      exchangeList.forEach(exchange => exchangeSet.add(exchange));
    });
    
    return Array.from(exchangeSet).sort();
  }, [pairsData]);

  if (loading) {
    return <LoadingSpinner message="Loading pairs data..." />;
  }

  if (error) {
    return <ErrorMessage error={error} onRetry={onRetry} />;
  }

  if (!pairsData) {
    return <div style={{ padding: '20px', textAlign: 'center' }}>No data available</div>;
  }

  return (
    <div style={{ padding: '20px', backgroundColor: '#ffffff', minHeight: '100vh' }}>
      <div style={{ marginBottom: '20px' }}>
        <h2 style={{ margin: '0 0 15px 0', color: '#000000', fontSize: '24px' }}>
          Cryptocurrency Pairs Exchange Support
        </h2>
        
        {/* Search Bar */}
        <div style={{ marginBottom: '15px' }}>
          <input
            type="text"
            placeholder="Search pairs (e.g., BTC, ETH, USDT)..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1); // Reset to first page when searching
            }}
            style={{
              width: '100%',
              maxWidth: '400px',
              padding: '12px',
              fontSize: '16px',
              border: '1px solid #e0e0e0',
              borderRadius: '8px',
              outline: 'none',
              backgroundColor: '#ffffff',
              color: '#000000',
            }}
          />
        </div>

        {/* Stats */}
        <div style={{ 
          display: 'flex', 
          gap: '20px', 
          marginBottom: '20px',
          fontSize: '14px',
          color: '#666666'
        }}>
          <span>Total Pairs: {filteredPairs.length}</span>
          <span>Total Exchanges: {allExchanges.length}</span>
          {searchTerm && <span>Filtered from {Object.keys(pairsData).length} total pairs</span>}
        </div>
      </div>

      {/* Table Container with Horizontal Scroll */}
      <div style={{ 
        overflowX: 'auto',
        border: '1px solid #e0e0e0',
        borderRadius: '8px',
        backgroundColor: '#ffffff'
      }}>
        <table style={{ 
          width: '100%', 
          borderCollapse: 'collapse',
          minWidth: `${Math.max(600, allExchanges.length * 100 + 200)}px`
        }}>
          <thead>
            <tr style={{ backgroundColor: '#f8f9fa' }}>
              <th style={{
                padding: '12px',
                textAlign: 'left',
                fontWeight: 'bold',
                color: '#000000',
                borderBottom: '2px solid #e0e0e0',
                position: 'sticky',
                left: 0,
                backgroundColor: '#f8f9fa',
                zIndex: 10,
                minWidth: '150px'
              }}>
                Pair
              </th>
              {allExchanges.map((exchange) => (
                <th key={exchange} style={{
                  padding: '12px',
                  textAlign: 'center',
                  fontWeight: 'bold',
                  color: '#000000',
                  borderBottom: '2px solid #e0e0e0',
                  borderLeft: '1px solid #e0e0e0',
                  minWidth: '80px',
                  fontSize: '12px'
                }}>
                  {exchange}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedPairs.map((pair, index) => (
              <tr key={pair} style={{ 
                backgroundColor: index % 2 === 0 ? '#ffffff' : '#f8f9fa'
              }}>
                <td style={{
                  padding: '12px',
                  fontWeight: 'bold',
                  color: '#000000',
                  borderBottom: '1px solid #e0e0e0',
                  position: 'sticky',
                  left: 0,
                  backgroundColor: index % 2 === 0 ? '#ffffff' : '#f8f9fa',
                  zIndex: 5
                }}>
                  {pair}
                </td>
                {allExchanges.map((exchange) => {
                  const isSupported = pairsData[pair]?.includes(exchange);
                  return (
                    <td key={exchange} style={{
                      padding: '12px',
                      textAlign: 'center',
                      borderBottom: '1px solid #e0e0e0',
                      borderLeft: '1px solid #e0e0e0'
                    }}>
                      <span style={{
                        display: 'inline-block',
                        width: '20px',
                        height: '20px',
                        borderRadius: '50%',
                        backgroundColor: isSupported ? '#007bff' : '#e0e0e0',
                        color: isSupported ? '#ffffff' : '#999999',
                        fontSize: '12px',
                        lineHeight: '20px',
                        fontWeight: 'bold'
                      }}>
                        {isSupported ? '✓' : '✗'}
                      </span>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ 
          marginTop: '20px', 
          display: 'flex', 
          justifyContent: 'center',
          alignItems: 'center',
          gap: '10px'
        }}>
          <button
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            style={{
              padding: '8px 16px',
              backgroundColor: currentPage === 1 ? '#e0e0e0' : '#007bff',
              color: currentPage === 1 ? '#999999' : '#ffffff',
              border: 'none',
              borderRadius: '4px',
              cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
              fontSize: '14px'
            }}
          >
            Previous
          </button>
          
          <span style={{ color: '#666666', fontSize: '14px' }}>
            Page {currentPage} of {totalPages}
          </span>
          
          <button
            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
            style={{
              padding: '8px 16px',
              backgroundColor: currentPage === totalPages ? '#e0e0e0' : '#007bff',
              color: currentPage === totalPages ? '#999999' : '#ffffff',
              border: 'none',
              borderRadius: '4px',
              cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
              fontSize: '14px'
            }}
          >
            Next
          </button>
        </div>
      )}

      {filteredPairs.length === 0 && searchTerm && (
        <div style={{ 
          textAlign: 'center', 
          padding: '40px', 
          color: '#666666',
          fontSize: '16px'
        }}>
          No pairs found matching "{searchTerm}"
        </div>
      )}
    </div>
  );
};

export default PairsTable;
