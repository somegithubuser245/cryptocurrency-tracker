import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Activity, Clock, Database, Wifi, WifiOff } from 'lucide-react';

interface DataMetadata {
  response_time_ms: number;
  timestamp: number;
  crypto_pair: string;
  interval: string;
  exchanges: {
    [key: string]: {
      source: string;
      cache_age_seconds: number;
      last_external_fetch: number;
    };
  };
  data_points: {
    [key: string]: number;
  };
  cache_ttl_seconds: number;
  is_real_time: boolean;
}

interface DataSourceStatusProps {
  metadata?: DataMetadata | null;
  onRefreshRequest?: () => void;
  autoRefreshInterval?: number; // seconds
}

// Progress Bar Component with smooth animation
const ProgressBar: React.FC<{ value: number; className?: string }> = ({ 
  value, 
  className = "" 
}) => (
  <div className={`w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1 ${className}`}>
    <motion.div
      className="bg-gradient-to-r from-blue-500 to-purple-600 h-1 rounded-full"
      style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
      transition={{ duration: 0.1, ease: "easeOut" }}
    />
  </div>
);

// Border Beam Effect Component (Magic UI inspired)
const BorderBeam: React.FC<{ className?: string }> = ({ className = "" }) => (
  <div className={`absolute inset-0 rounded-lg overflow-hidden ${className}`}>
    <motion.div
      className="absolute inset-0 rounded-lg border-2 border-transparent"
      style={{
        background: "linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.5), transparent)",
        backgroundSize: "200% 100%",
      }}
      animate={{
        backgroundPosition: ["200% 0%", "-200% 0%"],
      }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: "linear",
      }}
    />
  </div>
);

const DataSourceStatusToast: React.FC<DataSourceStatusProps> = ({
  metadata,
  onRefreshRequest,
  autoRefreshInterval = 300, // 5 minutes default
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [timeProgress, setTimeProgress] = useState(100);
  const [timeUntilRefresh, setTimeUntilRefresh] = useState<number | null>(null);
  const timerRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(0);
  const pausedTimeRef = useRef<number>(0);

  // Auto-show toast when metadata changes
  useEffect(() => {
    if (metadata) {
      setIsVisible(true);
      startTimeRef.current = Date.now();
      setTimeProgress(100);
      pausedTimeRef.current = 0;
      
      // Auto-hide after 8 seconds if not hovered
      const hideTimer = setTimeout(() => {
        if (!isHovered) {
          setIsVisible(false);
        }
      }, 8000);

      return () => clearTimeout(hideTimer);
    }
  }, [metadata, isHovered]);

  // Progress bar timer with hover pause
  useEffect(() => {
    if (isVisible && !isHovered) {
      const duration = 8000; // 8 seconds
      const interval = 50; // Update every 50ms
      
      timerRef.current = window.setInterval(() => {
        const elapsed = Date.now() - startTimeRef.current - pausedTimeRef.current;
        const progress = Math.max(0, 100 - (elapsed / duration) * 100);
        setTimeProgress(progress);
        
        if (progress <= 0) {
          setIsVisible(false);
        }
      }, interval);
    } else if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [isVisible, isHovered]);

  // Handle hover pause/resume
  const handleMouseEnter = () => {
    setIsHovered(true);
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    const currentTime = Date.now();
    pausedTimeRef.current += currentTime - startTimeRef.current;
    startTimeRef.current = currentTime;
  };

  // Auto-refresh countdown
  useEffect(() => {
    if (!metadata) return;

    const interval = setInterval(() => {
      const now = Date.now() / 1000;
      const dataAge = now - metadata.timestamp;
      const nextRefresh = autoRefreshInterval - dataAge;
      
      if (nextRefresh <= 0 && onRefreshRequest) {
        onRefreshRequest();
        setTimeUntilRefresh(null);
      } else {
        setTimeUntilRefresh(Math.max(0, nextRefresh));
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [metadata, autoRefreshInterval, onRefreshRequest]);

  if (!metadata) return null;

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  };

  const formatTimestamp = (timestamp: number): string => {
    return new Date(timestamp * 1000).toLocaleTimeString();
  };

  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'memory_cache': return <Database className="w-3 h-3 text-green-500" />;
      case 'redis_cache': return <Activity className="w-3 h-3 text-blue-500" />;
      case 'external_api': return <Wifi className="w-3 h-3 text-purple-500" />;
      case 'external_api_fallback': return <WifiOff className="w-3 h-3 text-orange-500" />;
      default: return <Clock className="w-3 h-3 text-gray-500" />;
    }
  };

  const getSourceLabel = (source: string): string => {
    switch (source) {
      case 'memory_cache': return 'Instant';
      case 'redis_cache': return 'Cached';
      case 'external_api': return 'Live';
      case 'external_api_fallback': return 'Fallback';
      default: return 'Unknown';
    }
  };

  const totalDataPoints = Object.values(metadata.data_points).reduce((a, b) => a + b, 0);

  return (
    <>
      <AnimatePresence>
        {isVisible && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 50, x: 50 }}
            animate={{ opacity: 1, scale: 1, y: 0, x: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: -50, x: 50 }}
            transition={{ 
              type: "spring", 
              stiffness: 300, 
              damping: 30,
              opacity: { duration: 0.2 }
            }}
            className="fixed top-4 right-4 z-50 max-w-sm"
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            style={{
              position: 'fixed',
              top: '1rem',
              right: '1rem',
              zIndex: 9999,
              maxWidth: '20rem',
            }}
          >
            <div className="relative">
              {/* Border Beam Effect */}
              <BorderBeam />
              
              {/* Main Card */}
              <motion.div
                className="relative bg-white dark:bg-gray-900 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden backdrop-blur-sm"
                whileHover={{ scale: 1.02 }}
                transition={{ type: "spring", stiffness: 400, damping: 25 }}
                style={{
                  backgroundColor: 'white',
                  borderRadius: '8px',
                  boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                  border: '1px solid #e5e7eb',
                  overflow: 'hidden',
                }}
              >
                {/* Progress Bar */}
                <div style={{ position: 'absolute', top: 0, left: 0, right: 0 }}>
                  <ProgressBar value={timeProgress} />
                </div>

                {/* Content */}
                <div style={{ padding: '1rem', paddingTop: '1.25rem' }}>
                  {/* Header */}
                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <motion.div
                        style={{
                          width: '12px',
                          height: '12px',
                          backgroundColor: '#10b981',
                          borderRadius: '50%',
                        }}
                        animate={{ 
                          scale: [1, 1.2, 1],
                          opacity: [1, 0.7, 1]
                        }}
                        transition={{ 
                          duration: 2, 
                          repeat: Infinity,
                          ease: "easeInOut"
                        }}
                      />
                      <h3 style={{ 
                        fontWeight: '600', 
                        color: '#111827', 
                        fontSize: '14px',
                        margin: 0
                      }}>
                        📈 Real-time Crypto Data
                      </h3>
                    </div>
                    <motion.button
                      onClick={() => setIsVisible(false)}
                      style={{
                        color: '#9ca3af',
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        padding: '2px',
                      }}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                    >
                      <X size={16} />
                    </motion.button>
                  </div>

                  {/* Main Info */}
                  <div style={{ fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ color: '#6b7280' }}>Pair:</span>
                      <span style={{ fontWeight: '500', color: '#111827' }}>
                        {metadata.crypto_pair} ({metadata.interval})
                      </span>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ color: '#6b7280' }}>Response:</span>
                      <span style={{ fontWeight: '500', color: '#111827' }}>
                        {metadata.response_time_ms}ms
                      </span>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ color: '#6b7280' }}>Updated:</span>
                      <span style={{ fontWeight: '500', color: '#111827' }}>
                        {formatTimestamp(metadata.timestamp)}
                      </span>
                    </div>
                  </div>

                  {/* Exchange Sources */}
                  <div style={{ 
                    marginTop: '0.75rem', 
                    paddingTop: '0.75rem', 
                    borderTop: '1px solid #e5e7eb' 
                  }}>
                    <div style={{ 
                      fontSize: '12px', 
                      fontWeight: '500', 
                      color: '#374151', 
                      marginBottom: '0.5rem' 
                    }}>
                      Data Sources:
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {Object.entries(metadata.exchanges).map(([exchange, info]) => (
                        <motion.div 
                          key={exchange}
                          style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.1 }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            {getSourceIcon(info.source)}
                            <span style={{ fontSize: '12px', fontWeight: '500', color: '#374151' }}>
                              {exchange}
                            </span>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span style={{
                              fontSize: '12px',
                              padding: '0.25rem 0.5rem',
                              borderRadius: '9999px',
                              fontWeight: '500',
                              backgroundColor: info.source === 'memory_cache' ? '#dcfce7' : 
                                             info.source === 'redis_cache' ? '#dbeafe' :
                                             info.source === 'external_api' ? '#f3e8ff' : '#fed7aa',
                              color: info.source === 'memory_cache' ? '#166534' : 
                                     info.source === 'redis_cache' ? '#1e40af' :
                                     info.source === 'external_api' ? '#7c3aed' : '#c2410c',
                            }}>
                              {getSourceLabel(info.source)}
                            </span>
                            <span style={{ fontSize: '12px', color: '#6b7280' }}>
                              {info.cache_age_seconds > 0 ? formatTime(info.cache_age_seconds) : 'fresh'}
                            </span>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>

                  {/* Data Points */}
                  <div style={{ 
                    marginTop: '0.75rem', 
                    paddingTop: '0.75rem', 
                    borderTop: '1px solid #e5e7eb' 
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                      <span style={{ color: '#6b7280' }}>Data points:</span>
                      <span style={{ color: '#111827', fontWeight: '500' }}>
                        {Object.values(metadata.data_points).join(' + ')} = {totalDataPoints}
                      </span>
                    </div>
                  </div>

                  {/* Auto-refresh info */}
                  {timeUntilRefresh !== null && timeUntilRefresh > 0 && (
                    <motion.div 
                      style={{ 
                        marginTop: '0.75rem', 
                        paddingTop: '0.75rem', 
                        borderTop: '1px solid #e5e7eb' 
                      }}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px' }}>
                        <span style={{ color: '#6b7280' }}>Next refresh:</span>
                        <span style={{ color: '#111827', fontWeight: '500' }}>
                          {formatTime(timeUntilRefresh)}
                        </span>
                      </div>
                    </motion.div>
                  )}

                  {/* Action Button */}
                  <motion.button
                    onClick={() => {
                      onRefreshRequest?.();
                      setIsVisible(false);
                    }}
                    style={{
                      width: '100%',
                      marginTop: '0.75rem',
                      fontSize: '12px',
                      padding: '0.5rem 0.75rem',
                      background: 'linear-gradient(to right, #3b82f6, #8b5cf6)',
                      color: 'white',
                      borderRadius: '6px',
                      border: 'none',
                      fontWeight: '500',
                      cursor: 'pointer',
                    }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    🔄 Refresh Now
                  </motion.button>
                </div>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Persistent status indicator */}
      <AnimatePresence>
        {!isVisible && metadata && (
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0 }}
            style={{
              position: 'fixed',
              bottom: '1rem',
              right: '1rem',
              zIndex: 9999,
            }}
          >
            <motion.button
              onClick={() => setIsVisible(true)}
              style={{
                background: 'linear-gradient(to right, #10b981, #3b82f6)',
                color: 'white',
                padding: '0.75rem',
                borderRadius: '50%',
                border: 'none',
                cursor: 'pointer',
                boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.25)',
              }}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              title="Show Data Source Status"
            >
              <motion.div
                style={{
                  width: '12px',
                  height: '12px',
                  backgroundColor: 'white',
                  borderRadius: '50%',
                }}
                animate={{ 
                  scale: [1, 1.3, 1],
                  opacity: [1, 0.6, 1]
                }}
                transition={{ 
                  duration: 2, 
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default DataSourceStatusToast;