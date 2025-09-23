import React, { useState, useRef } from "react";
import ResponseCard from "./ResponseCard";
import { useLanguage } from "../contexts/LanguageContext";
import { motion } from "framer-motion";
import toast from "react-hot-toast";

export default function AdvisoryForm() {
  const [cropName, setCropName] = useState("");
  const [location, setLocation] = useState("");
  const [soilType, setSoilType] = useState("");
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const audioRef = useRef();
  const { currentLanguage, t } = useLanguage();

  const soilTypes = [
    { value: "alluvial", label: "Alluvial" },
    { value: "black", label: "Black" },
    { value: "red", label: "Red" },
    { value: "laterite", label: "Laterite" },
    { value: "sandy", label: "Sandy" },
    { value: "clay", label: "Clay" },
    { value: "loamy", label: "Loamy" }
  ];

  // Voice input for query
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
    toast.success('Listening for your farming question...');
    
    recognition.start();
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setQuery(transcript);
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

  const handleSubmit = async () => {
    if (!cropName.trim() || !location.trim() || !soilType || !query.trim()) {
      toast.error('Please fill in all fields');
      return;
    }

    setLoading(true);
    const toastId = toast.loading('Getting agricultural advisory...');

    try {
      const requestData = {
        crop_name: cropName,
        location: location,
        soil_type: soilType,
        query: query,
        language: currentLanguage
      };

      const res = await fetch("http://127.0.0.1:8000/advisory/", {
        method: "POST",
        body: JSON.stringify(requestData),
        headers: { "Content-Type": "application/json" },
      });
      
      if (!res.ok) {
        throw new Error('API request failed');
      }
      
      const data = await res.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      setResponse(data);
      toast.success('Advisory generated successfully!', { id: toastId });

    } catch (error) {
      console.error('Advisory error:', error);
      toast.error(t('API Error'), { id: toastId });
    } finally {
      setLoading(false);
    }
  };

  // Generate voice output
  const handlePlayAudio = async () => {
    if (!response?.advisory) return;
    
    const audioToastId = toast.loading('Generating audio advisory...');
    
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
        toast.success('Playing audio advisory', { id: audioToastId });
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
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6">
        <div className="flex items-center space-x-3">
          <span className="text-3xl">🌾</span>
          <div>
            <h2 className="text-2xl font-bold">{t('Crop Advisory')}</h2>
            <p className="text-blue-100 text-sm">Get comprehensive farming guidance and market insights</p>
          </div>
        </div>
      </div>

      <div className="p-6">
        <div className="grid md:grid-cols-2 gap-6">
          {/* Left Column */}
          <div className="space-y-6">
            {/* Crop Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('Crop Name')} *
              </label>
              <input
                type="text"
                value={cropName}
                onChange={(e) => setCropName(e.target.value)}
                placeholder={t('Enter crop name')}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              />
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('Location')} *
              </label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder={t('Enter location')}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              />
            </div>

            {/* Soil Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('Soil Type')} *
              </label>
              <select
                value={soilType}
                onChange={(e) => setSoilType(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              >
                <option value="">{t('Select soil type')}</option>
                {soilTypes.map((soil) => (
                  <option key={soil.value} value={soil.value}>
                    {t(soil.label)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Right Column */}
          <div>
            {/* Query */}
            <div className="h-full flex flex-col">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('Additional Query')} *
              </label>
              <div className="flex-1 flex flex-col">
                <div className="flex space-x-3 mb-3">
                  <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={t('Enter additional questions')}
                    className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all duration-200"
                    rows={6}
                  />
                </div>
                <motion.button
                  onClick={handleVoiceInput}
                  disabled={isListening || loading}
                  className={`self-start px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                    isListening 
                      ? 'bg-red-500 text-white animate-pulse'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <span>{isListening ? '🎙️' : '🎤'}</span>
                  <span className="text-sm">
                    {isListening ? 'Listening...' : t('Voice Input')}
                  </span>
                </motion.button>
              </div>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <motion.button
          onClick={handleSubmit}
          disabled={loading || !cropName.trim() || !location.trim() || !soilType || !query.trim()}
          className={`w-full mt-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200 ${
            loading || !cropName.trim() || !location.trim() || !soilType || !query.trim()
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 shadow-lg hover:shadow-xl'
          }`}
          whileHover={!loading && cropName.trim() && location.trim() && soilType && query.trim() ? { scale: 1.02 } : {}}
          whileTap={!loading && cropName.trim() && location.trim() && soilType && query.trim() ? { scale: 0.98 } : {}}
        >
          {loading ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Getting Advisory...</span>
            </div>
          ) : (
            <div className="flex items-center justify-center space-x-2">
              <span>🌱</span>
              <span>{t('Get Advice')}</span>
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
              type="advisory"
            />
          </motion.div>
        )}

        {/* Hidden audio element */}
        <audio ref={audioRef} className="hidden" controls />
      </div>
    </motion.div>
  );
}
