import { useState, useCallback } from 'react';
import toast from 'react-hot-toast';

/**
 * Custom hook for voice input functionality
 * Handles speech recognition across the app
 */
export const useVoiceInput = (currentLanguage) => {
  const [isListening, setIsListening] = useState(false);

  const langMap = {
    'en': 'en-US',
    'hi': 'hi-IN',
    'te': 'te-IN',
    'ml': 'ml-IN',
    'ta': 'ta-IN',
    'kn': 'kn-IN',
    'ma': 'mr-IN'
  };

  const startVoiceInput = useCallback((onResult) => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error('Voice input not supported in this browser');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.lang = langMap[currentLanguage] || 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    setIsListening(true);
    toast.success('🎤 Listening... Please speak now');
    
    recognition.start();
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (onResult) {
        onResult(transcript);
      }
      setIsListening(false);
      toast.success('✓ Voice captured successfully!');
    };
    
    recognition.onerror = (event) => {
      setIsListening(false);
      let errorMsg = 'Voice recognition error';
      if (event.error === 'no-speech') {
        errorMsg = 'No speech detected. Please try again.';
      } else if (event.error === 'network') {
        errorMsg = 'Network error. Please check your internet.';
      }
      toast.error(errorMsg);
    };
    
    recognition.onend = () => {
      setIsListening(false);
    };
  }, [currentLanguage]);

  return {
    isListening,
    startVoiceInput
  };
};

export default useVoiceInput;
