import React, { useState } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import { motion } from "framer-motion";
import toast from "react-hot-toast";

export default function ResponseCard({ response, audioRef, onPlayAudio, language, type = "disease" }) {
  const [feedback, setFeedback] = useState(null);
  const [showFullResponse, setShowFullResponse] = useState(false);
  const { t } = useLanguage();

  const submitFeedback = async (feedbackType) => {
    try {
      const feedbackData = {
        query_id: response.query_id,
        feedback: feedbackType,
        comments: null
      };

      const res = await fetch("http://127.0.0.1:8000/feedback/", {
        method: "POST",
        body: JSON.stringify(feedbackData),
        headers: { "Content-Type": "application/json" },
      });

      if (res.ok) {
        setFeedback(feedbackType);
        toast.success('Thank you for your feedback!');
      }
    } catch (error) {
      toast.error('Failed to submit feedback');
    }
  };

  const sanitizeText = (text) => {
    if (!text) return "";
    return text.replace(/\*/g, "").trim();
  };

  const renderAdvisoryParagraphs = (text) => {
    if (!text) return null;

    const lines = sanitizeText(text)
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    return lines.map((line, idx) => {
      if (/^\d+[.)]/.test(line) || /^[A-Z][).]/.test(line)) {
        return (
          <h5 key={idx} className="font-semibold mt-3 text-gray-800">
            {line}
          </h5>
        );
      }
      if (/^-\s+/.test(line) || /^•\s+/.test(line) || /^[*\-\u2022]\s+/.test(line)) {
        return (
          <li key={idx} className="ml-5 list-disc text-gray-700">
            {line.replace(/^[-*\u2022]\s+/, "")}
          </li>
        );
      }
      return (
        <p key={idx} className="text-gray-700 leading-relaxed">
          {line}
        </p>
      );
    });
  };

  const truncateText = (text, maxLength = 200) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  return (
    <motion.div 
      className="bg-gradient-to-br from-white to-gray-50 rounded-xl shadow-lg overflow-hidden border border-gray-200"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className={`px-6 py-4 ${type === 'disease' ? 'bg-green-600' : 'bg-blue-600'} text-white`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">
              {type === 'disease' ? '🔬' : '🌱'}
            </span>
            <h3 className="text-lg font-semibold">
              {t('AI Response')}
            </h3>
          </div>
          {onPlayAudio && (
            <motion.button
              onClick={onPlayAudio}
              className="bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span>🔊</span>
              <span>{t('Play Audio')}</span>
            </motion.button>
          )}
        </div>
      </div>

      <div className="p-6">
        {/* Disease Detection Specific Info */}
        {type === 'disease' && response.prediction && (
          <div className="mb-6">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-800 mb-2">{t('Prediction')}</h4>
              <p className="text-lg font-medium text-green-700">
                {sanitizeText(response.prediction).replace(/___/g, ' - ')}
              </p>
            </div>
          </div>
        )}

        {/* Advisory Content */}
        <div className="mb-6">
          <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
            <span className="mr-2">📋</span>
            {type === 'disease' ? t('Advisory') : 'Advisory Response'}
          </h4>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed">
              {showFullResponse ? 
                renderAdvisoryParagraphs(response.text || response.advisory || response.answer) :
                renderAdvisoryParagraphs(truncateText(response.text || response.advisory || response.answer || 'No advisory available', 300))
              }
            </div>
            {(response.text || response.advisory || response.answer) && (response.text || response.advisory || response.answer).length > 300 && (
              <button
                onClick={() => setShowFullResponse(!showFullResponse)}
                className="mt-3 text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors"
              >
                {showFullResponse ? t('Show Less') : t('Read More')}
              </button>
            )}
          </div>
        </div>

        {/* Audio Player */}
        {audioRef && (
          <div className="mb-6">
            <audio 
              ref={audioRef} 
              controls 
              className="w-full h-10 rounded-lg"
              style={{ filter: 'hue-rotate(120deg)' }}
            />
          </div>
        )}

        {/* Feedback Section */}
        <div className="border-t border-gray-200 pt-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">
              {t('Feedback')}
            </span>
            {!feedback ? (
              <div className="flex space-x-3">
                <motion.button
                  onClick={() => submitFeedback('positive')}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors duration-200"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <span>👍</span>
                  <span className="text-sm">{t('Thumbs Up')}</span>
                </motion.button>
                <motion.button
                  onClick={() => submitFeedback('negative')}
                  className="flex items-center space-x-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors duration-200"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <span>👎</span>
                  <span className="text-sm">{t('Thumbs Down')}</span>
                </motion.button>
              </div>
            ) : (
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <span>{feedback === 'positive' ? '👍' : '👎'}</span>
                <span>{t('Thank you for your feedback!')}</span>
              </div>
            )}
          </div>
        </div>

        {/* Query ID (for debugging) */}
        {response.query_id && (
          <div className="mt-4 text-xs text-gray-400">
            Query ID: {response.query_id}
          </div>
        )}
      </div>
    </motion.div>
  );
}
