import React, { useState, useRef } from "react";
import ResponseCard from "./ResponseCard";
import { useLanguage } from "../contexts/LanguageContext";
import { motion } from "framer-motion";
import toast from "react-hot-toast";

export default function DiseaseForm() {
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [response, setResponse] = useState(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const audioRef = useRef();
  const { currentLanguage, t } = useLanguage();

  // Image upload handler with preview
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        toast.error("Image size should be less than 10MB");
        return;
      }
      setImage(file);
      const reader = new FileReader();
      reader.onload = (e) => setImagePreview(e.target.result);
      reader.readAsDataURL(file);
    }
  };

  // Enhanced voice input handler
  const handleVoiceInput = () => {
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
    
    setIsListening(true);
    toast.success('Listening... Please speak now');
    
    recognition.start();
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setText(transcript);
      setIsListening(false);
      toast.success('Voice captured successfully!');
    };
    
    recognition.onerror = (event) => {
      setIsListening(false);
      toast.error('Voice recognition error. Please try again.');
    };
    
    recognition.onend = () => {
      setIsListening(false);
    };
  };

  // Enhanced submit handler
  const handleSubmit = async () => {
    if (!image && !text.trim()) {
      toast.error(t('No file selected'));
      return;
    }

    setLoading(true);
    const toastId = toast.loading('Analyzing crop disease...');

    try {
      const formData = new FormData();
      if (image) formData.append("file", image);
      formData.append("language", currentLanguage);

      const res = await fetch("http://127.0.0.1:8000/detect-disease/", {
        method: "POST",
        body: formData,
      });
      
      if (!res.ok) {
        throw new Error('API request failed');
      }
      
      const data = await res.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      setResponse(data);
      toast.success('Disease analysis completed!', { id: toastId });

    } catch (error) {
      console.error('Disease detection error:', error);
      toast.error(t('API Error'), { id: toastId });
    } finally {
      setLoading(false);
    }
  };

  // Generate voice output
  const handlePlayAudio = async () => {
    if (!response?.advisory) return;
    
    const audioToastId = toast.loading('Generating audio...');
    
    try {
      const ttsRes = await fetch("http://127.0.0.1:8000/text-to-speech/", {
        method: "POST",
        body: JSON.stringify({ 
          text: response.advisory, 
          language: currentLanguage 
        }),
        headers: { "Content-Type": "application/json" },
      });
      
      if (ttsRes.ok) {
        const audioBlob = await ttsRes.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        audioRef.current.src = audioUrl;
        audioRef.current.play();
        toast.success('Playing audio response', { id: audioToastId });
      } else {
        throw new Error('TTS failed');
      }
    } catch (error) {
      toast.error('Audio generation failed', { id: audioToastId });
    }
  };

  return (
    <motion.div 
      className="bg-white rounded-2xl shadow-xl overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-6">
        <div className="flex items-center space-x-3">
          <span className="text-3xl">🔬</span>
          <div>
            <h2 className="text-2xl font-bold">{t('Disease Detection')}</h2>
            <p className="text-green-100 text-sm">Upload crop images for AI-powered disease analysis</p>
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* Image Upload Section */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('Upload Image')}
          </label>
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="w-full text-sm text-gray-500 file:mr-4 file:py-3 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100 transition-all duration-200"
              />
            </div>
            {imagePreview && (
              <motion.div 
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="w-20 h-20 rounded-lg overflow-hidden border-2 border-green-200"
              >
                <img 
                  src={imagePreview} 
                  alt="Preview" 
                  className="w-full h-full object-cover"
                />
              </motion.div>
            )}
          </div>
        </div>

        {/* Text Input Section */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('Enter Query')}
          </label>
          <div className="flex space-x-3">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={t('Describe crop problem')}
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none h-24 transition-all duration-200"
            />
            <motion.button
              onClick={handleVoiceInput}
              disabled={isListening || loading}
              className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                isListening 
                  ? 'bg-red-500 text-white animate-pulse'
                  : 'bg-green-600 text-white hover:bg-green-700'
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span>{isListening ? '🎙️' : '🎤'}</span>
              <span className="text-xs hidden sm:block">
                {isListening ? 'Listening...' : t('Voice Input')}
              </span>
            </motion.button>
          </div>
        </div>

        {/* Submit Button */}
        <motion.button
          onClick={handleSubmit}
          disabled={loading || (!image && !text.trim())}
          className={`w-full py-4 rounded-lg font-semibold text-lg transition-all duration-200 ${
            loading || (!image && !text.trim())
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-green-600 to-green-700 text-white hover:from-green-700 hover:to-green-800 shadow-lg hover:shadow-xl'
          }`}
          whileHover={!loading && (image || text.trim()) ? { scale: 1.02 } : {}}
          whileTap={!loading && (image || text.trim()) ? { scale: 0.98 } : {}}
        >
          {loading ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Analyzing...</span>
            </div>
          ) : (
            <div className="flex items-center justify-center space-x-2">
              <span>🔍</span>
              <span>{t('Submit')}</span>
            </div>
          )}
        </motion.button>

        {/* Response Section */}
        {response && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-8"
          >
            <ResponseCard 
              response={response} 
              audioRef={audioRef}
              onPlayAudio={handlePlayAudio}
              language={currentLanguage}
            />
          </motion.div>
        )}

        {/* Hidden audio element */}
        <audio ref={audioRef} className="hidden" controls />
      </div>
    </motion.div>
  );
}
