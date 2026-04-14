import React from 'react';
import { motion } from 'framer-motion';

/**
 * Reusable VoiceInputButton component
 * Can be placed next to any text input field
 */
const VoiceInputButton = ({ 
  isListening, 
  onVoiceClick, 
  disabled = false,
  size = 'md',
  showLabel = true
}) => {
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-3 text-base'
  };

  const buttonClasses = disabled
    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
    : isListening 
      ? 'bg-red-500 text-white animate-pulse'
      : 'bg-green-600 text-white hover:bg-green-700';

  return (
    <motion.button
      type="button"
      onClick={onVoiceClick}
      disabled={disabled || isListening}
      className={`${sizeClasses[size]} rounded-lg font-medium transition-all duration-200 flex items-center gap-2 whitespace-nowrap ${buttonClasses}`}
      whileHover={!disabled && !isListening ? { scale: 1.05 } : {}}
      whileTap={!disabled && !isListening ? { scale: 0.95 } : {}}
      title={isListening ? 'Listening...' : 'Click to use voice input'}
    >
      <span className="text-lg">
        {isListening ? '🎙️' : '🎤'}
      </span>
      {showLabel && (
        <span className="hidden sm:inline">
          {isListening ? 'Listening' : 'Voice'}
        </span>
      )}
    </motion.button>
  );
};

export default VoiceInputButton;
