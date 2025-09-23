import React, { useState, useEffect } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

const QueryHistory = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedItems, setExpandedItems] = useState(new Set());
  const { t } = useLanguage();

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/history?limit=20');
      if (res.ok) {
        const data = await res.json();
        setHistory(data.history || []);
      } else {
        throw new Error('Failed to fetch history');
      }
    } catch (error) {
      console.error('History fetch error:', error);
      toast.error('Failed to load query history');
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = async () => {
    if (window.confirm('Are you sure you want to clear all history?')) {
      // Note: This would require a backend endpoint to clear history
      // For now, we'll just clear the local state
      setHistory([]);
      toast.success('History cleared');
    }
  };

  const toggleExpand = (itemId) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId);
    } else {
      newExpanded.add(itemId);
    }
    setExpandedItems(newExpanded);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateText = (text, maxLength = 150) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex items-center space-x-3">
          <div className="w-6 h-6 border-2 border-green-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-gray-600">Loading history...</span>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white rounded-2xl shadow-xl overflow-hidden"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 text-white p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-3xl">📊</span>
            <div>
              <h2 className="text-2xl font-bold">{t('Recent Queries')}</h2>
              <p className="text-purple-100 text-sm">View your recent disease detections and advisory queries</p>
            </div>
          </div>
          {history.length > 0 && (
            <motion.button
              onClick={clearHistory}
              className="bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {t('Clear History')}
            </motion.button>
          )}
        </div>
      </div>

      <div className="p-6">
        {history.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              {t('No History')}
            </h3>
            <p className="text-gray-600">
              Your query history will appear here once you start using the disease detection or advisory features.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {history.map((item, index) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow duration-200"
              >
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      {/* Query Type Badge */}
                      <div className="flex items-center space-x-3 mb-3">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                          item.type === 'disease_detection' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          {item.type === 'disease_detection' ? '🔬 Disease Detection' : '🌾 Advisory'}
                        </span>
                        <span className="text-sm text-gray-500">
                          {formatDate(item.timestamp)}
                        </span>
                      </div>

                      {/* Content Preview */}
                      <div className="space-y-2">
                        {item.type === 'disease_detection' && (
                          <>
                            {item.filename && (
                              <div className="text-sm text-gray-600">
                                <span className="font-medium">Image:</span> {item.filename}
                              </div>
                            )}
                            {item.prediction && (
                              <div className="text-sm">
                                <span className="font-medium text-gray-700">Prediction:</span>{' '}
                                <span className="text-green-600 font-medium">
                                  {item.prediction.replace(/___/g, ' - ')}
                                </span>
                                {item.confidence && (
                                  <span className="ml-2 text-xs text-gray-500">
                                    ({(item.confidence * 100).toFixed(1)}% confidence)
                                  </span>
                                )}
                              </div>
                            )}
                          </>
                        )}
                        
                        {item.type === 'advisory' && (
                          <div className="text-sm space-y-1">
                            <div>
                              <span className="font-medium text-gray-700">Crop:</span> {item.crop_name}
                            </div>
                            <div>
                              <span className="font-medium text-gray-700">Location:</span> {item.location}
                            </div>
                            <div>
                              <span className="font-medium text-gray-700">Query:</span> {truncateText(item.query)}
                            </div>
                          </div>
                        )}

                        {/* Advisory Preview */}
                        {item.advisory && (
                          <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                            <div className="text-sm text-gray-700">
                              {expandedItems.has(item.id) 
                                ? item.advisory 
                                : truncateText(item.advisory, 200)
                              }
                            </div>
                            {item.advisory.length > 200 && (
                              <button
                                onClick={() => toggleExpand(item.id)}
                                className="mt-2 text-xs text-blue-600 hover:text-blue-800 font-medium"
                              >
                                {expandedItems.has(item.id) ? 'Show Less' : 'Read More'}
                              </button>
                            )}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Language Badge */}
                    <div className="ml-4 flex-shrink-0">
                      <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
                        {item.language?.toUpperCase() || 'EN'}
                      </span>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default QueryHistory;