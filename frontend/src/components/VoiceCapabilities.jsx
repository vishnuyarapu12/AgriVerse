import React, { useState, useRef } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

const VoiceCapabilities = ({ capabilities }) => {
  const [isTestingVoice, setIsTestingVoice] = useState(false);
  const [testText, setTestText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const audioRef = useRef();
  const { currentLanguage, availableLanguages, t } = useLanguage();

  const testVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error(t('Voice not supported'));
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    const langMap = {
      'en': 'en-US',
      'hi': 'hi-IN',
      'te': 'te-IN',
      'ta': 'ta-IN',
      'kn': 'kn-IN'
    };
    
    recognition.lang = langMap[currentLanguage] || 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    setIsRecording(true);
    toast.success('Listening... Please speak now');
    
    recognition.start();
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setTestText(transcript);
      setIsRecording(false);
      toast.success('Voice captured successfully!');
    };
    
    recognition.onerror = (event) => {
      setIsRecording(false);
      toast.error('Voice recognition error. Please try again.');
    };
    
    recognition.onend = () => {
      setIsRecording(false);
    };
  };

  const testVoiceOutput = async () => {
    if (!testText.trim()) {
      toast.error('Please enter some text to test voice output');
      return;
    }

    setIsTestingVoice(true);
    const toastId = toast.loading('Generating test audio...');

    try {
      const ttsRes = await fetch("http://127.0.0.1:8000/text-to-speech/", {
        method: "POST",
        body: JSON.stringify({ 
          text: testText, 
          language: currentLanguage 
        }),
        headers: { "Content-Type": "application/json" },
      });
      
      if (ttsRes.ok) {
        const audioBlob = await ttsRes.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        audioRef.current.src = audioUrl;
        audioRef.current.play();
        toast.success('Playing test audio', { id: toastId });
      } else {
        throw new Error('TTS failed');
      }
    } catch (error) {
      toast.error('Audio generation failed', { id: toastId });
    } finally {
      setIsTestingVoice(false);
    }
  };

  const getStatusBadge = (available) => {
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
        available 
          ? 'bg-green-100 text-green-800' 
          : 'bg-red-100 text-red-800'
      }`}>
        {available ? t('Available') : t('Not Available')}
      </span>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white rounded-2xl shadow-xl overflow-hidden"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 text-white p-6">
        <div className="flex items-center space-x-3">
          <span className="text-3xl">🎤</span>
          <div>
            <h2 className="text-2xl font-bold">{t('Voice Capabilities')}</h2>
            <p className="text-indigo-100 text-sm">Test and configure voice input/output features</p>
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* Capabilities Status */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Speech Recognition */}
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800">
                {t('Speech Recognition')}
              </h3>
              {getStatusBadge('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)}
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Convert your voice into text for queries and commands.
            </p>
            <div className="space-y-2">
              <div className="text-sm">
                <span className="font-medium text-gray-700">Browser Support:</span>{' '}
                <span className={`${
                  'webkitSpeechRecognition' in window || 'SpeechRecognition' in window 
                    ? 'text-green-600' : 'text-red-600'
                }`}>
                  {('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) 
                    ? 'Supported' : 'Not Supported'}
                </span>
              </div>
            </div>
          </div>

          {/* Text to Speech */}
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800">
                {t('Text to Speech')}
              </h3>
              {getStatusBadge(true)}
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Listen to AI responses in your preferred language.
            </p>
            <div className="space-y-2">
              <div className="text-sm">
                <span className="font-medium text-gray-700">Service:</span>{' '}
                <span className="text-green-600">Google TTS</span>
              </div>
            </div>
          </div>
        </div>

        {/* Supported Languages */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            {t('Supported Languages')}
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
            {availableLanguages.map((lang) => (
              <div 
                key={lang.code} 
                className={`p-3 rounded-lg border text-center transition-all duration-200 ${
                  currentLanguage === lang.code 
                    ? 'bg-indigo-100 border-indigo-300 text-indigo-800' 
                    : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
                }`}
              >
                <div className="font-medium text-sm">{lang.name}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {lang.code.toUpperCase()}
                </div>
                {currentLanguage === lang.code && (
                  <div className="text-xs text-indigo-600 mt-1">
                    Currently Active
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Voice Testing Section */}
        <div className="border-t border-gray-200 pt-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Test Voice Features
          </h3>
          
          <div className="space-y-6">
            {/* Voice Input Test */}
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Voice Input Test</h4>
              <div className="flex items-center space-x-3">
                <motion.button
                  onClick={testVoiceInput}
                  disabled={isRecording}
                  className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                    isRecording 
                      ? 'bg-red-500 text-white animate-pulse'
                      : 'bg-indigo-600 text-white hover:bg-indigo-700'
                  }`}
                  whileHover={!isRecording ? { scale: 1.05 } : {}}
                  whileTap={!isRecording ? { scale: 0.95 } : {}}
                >
                  <span>{isRecording ? '🎙️' : '🎤'}</span>
                  <span>{isRecording ? 'Listening...' : 'Test Voice Input'}</span>
                </motion.button>
                {testText && (
                  <span className="text-sm text-gray-600 italic">
                    Captured: "{testText}"
                  </span>
                )}
              </div>
            </div>

            {/* Voice Output Test */}
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Voice Output Test</h4>
              <div className="space-y-3">
                <textarea
                  value={testText}
                  onChange={(e) => setTestText(e.target.value)}
                  placeholder="Enter text to convert to speech or use voice input above..."
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none h-20"
                />
                <motion.button
                  onClick={testVoiceOutput}
                  disabled={isTestingVoice || !testText.trim()}
                  className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                    isTestingVoice || !testText.trim()
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-green-600 text-white hover:bg-green-700'
                  }`}
                  whileHover={!isTestingVoice && testText.trim() ? { scale: 1.05 } : {}}
                  whileTap={!isTestingVoice && testText.trim() ? { scale: 0.95 } : {}}
                >
                  {isTestingVoice ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Generating...</span>
                    </>
                  ) : (
                    <>
                      <span>🔊</span>
                      <span>Test Voice Output</span>
                    </>
                  )}
                </motion.button>
              </div>
            </div>

            {/* Audio Player */}
            <audio ref={audioRef} controls className="w-full rounded-lg" />
          </div>
        </div>

        {/* Tips and Information */}
        <div className="mt-8 bg-blue-50 rounded-lg p-4">
          <h4 className="font-semibold text-blue-800 mb-2">💡 Tips for Better Voice Experience</h4>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Speak clearly and at a normal pace</li>
            <li>• Ensure you're in a quiet environment for better recognition</li>
            <li>• Allow microphone access when prompted by your browser</li>
            <li>• Voice input works best in Chrome, Edge, and Safari browsers</li>
            <li>• Audio output supports all major languages for farming guidance</li>
          </ul>
        </div>
      </div>
    </motion.div>
  );
};

export default VoiceCapabilities;