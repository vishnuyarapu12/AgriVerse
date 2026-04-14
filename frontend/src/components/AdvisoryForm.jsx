import React, { useState, useRef, useEffect } from "react";
import ResponseCard from "./ResponseCard";
import { useLanguage } from "../contexts/LanguageContext";
import useTranslation from "../hooks/useTranslation";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { useVoiceInput } from "../hooks/useVoiceInput";
import VoiceInputButton from "./VoiceInputButton";

export default function AdvisoryForm() {
  const [cropName, setCropName] = useState("");
  const [location, setLocation] = useState("");
  const [soilType, setSoilType] = useState("");
  const [season, setSeason] = useState("");
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [audioGenerating, setAudioGenerating] = useState(false);
  const [audioReady, setAudioReady] = useState(false);
  const audioRef = useRef();
  const audioToastIdRef = useRef(null);
  const { currentLanguage, t } = useLanguage();
  const { getAllSeasons } = useTranslation();
  
  const { isListening: isListeningCrop, startVoiceInput: startCropVoice } = useVoiceInput(currentLanguage);
  const { isListening: isListeningLocation, startVoiceInput: startLocationVoice } = useVoiceInput(currentLanguage);
  const { isListening: isListeningQuery, startVoiceInput: startQueryVoice } = useVoiceInput(currentLanguage);

  const soilTypes = [
    { value: "alluvial", label: "Alluvial" },
    { value: "black", label: "Black" },
    { value: "red", label: "Red" },
    { value: "laterite", label: "Laterite" },
    { value: "sandy", label: "Sandy" },
    { value: "clay", label: "Clay" },
    { value: "loamy", label: "Loamy" }
  ];

  const seasons = [
    { value: "kharif", label: "Kharif (Monsoon)" },
    { value: "rabi", label: "Rabi (Winter)" },
    { value: "summer", label: "Summer" },
    { value: "spring", label: "Spring" }
  ];

  // The voice input hooks are now used directly in the JSX via the VoiceInputButton component
  // No need for a separate handleVoiceInput function

  // Auto-generate audio when response is received
  useEffect(() => {
    if (!response?.text || audioGenerating || audioReady) return;
    
    setAudioGenerating(true);
    audioToastIdRef.current = toast.loading(t('Generating audio in background...'));
    
    const generateAudio = async () => {
      try {
        const ttsRes = await fetch("http://127.0.0.1:8000/text-to-speech/", {
          method: "POST",
          body: JSON.stringify({ 
            text: response.text, 
            language: currentLanguage 
          }),
          headers: { "Content-Type": "application/json" },
        });
        
        if (ttsRes.ok) {
          const audioBlob = await ttsRes.blob();
          const audioUrl = URL.createObjectURL(audioBlob);
          audioRef.current.src = audioUrl;
          setAudioReady(true);
          toast.success(t('Audio ready! Click play button to listen'), { id: audioToastIdRef.current });
        } else {
          throw new Error('TTS failed');
        }
      } catch (error) {
        console.error('Auto audio generation failed:', error);
        toast.error(t('Audio generation failed'), { id: audioToastIdRef.current });
      } finally {
        setAudioGenerating(false);
      }
    };
    
    generateAudio();
  }, [response, currentLanguage, audioGenerating, audioReady, t]);

  const handleSubmit = async () => {
    if (!cropName.trim() || !location.trim() || !soilType) {
      toast.error(t('Please fill in crop name, location, and soil type'));
      return;
    }

    setLoading(true);
    setAudioReady(false);
    setAudioGenerating(false);
    const toastId = toast.loading(t('Getting agricultural advisory...'));

    try {
      const requestData = {
        crop_name: cropName,
        location: location,
        soil_type: soilType,
        season: season || "kharif",
        query: query || "General farming advice",
        language: currentLanguage
      };

      const res = await fetch("http://127.0.0.1:8000/advisory/", {
        method: "POST",
        body: JSON.stringify(requestData),
        headers: { "Content-Type": "application/json" },
      });
      
      if (!res.ok) {
        throw new Error(t('API Error'));
      }
      
      const data = await res.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      setResponse(data);
      toast.success(t('Advisory generated successfully!'), { id: toastId });

    } catch (error) {
      console.error('Advisory error:', error);
      toast.error(t('API Error'), { id: toastId });
    } finally {
      setLoading(false);
    }
  };

  // Play audio (auto-generated in background)
  const handlePlayAudio = () => {
    if (!audioRef.current?.src) {
      if (audioGenerating) {
        toast.loading(t('Audio is being generated...'));
      } else {
        toast.error(t('Audio not ready yet'));
      }
      return;
    }
    
    audioRef.current.play();
    toast.success(t('Playing audio advisory'));
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
            <p className="text-blue-100 text-sm">{t('Crop Advisory subtitle')}</p>
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
              <div className="flex gap-2">
                <input
                  type="text"
                  value={cropName}
                  onChange={(e) => setCropName(e.target.value)}
                  placeholder={t('Enter crop name')}
                  className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                />
                <VoiceInputButton
                  isListening={isListeningCrop}
                  onVoiceClick={() => startCropVoice((text) => setCropName(text))}
                  size="md"
                />
              </div>
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('Location')} *
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder={t('Enter location')}
                  className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                />
                <VoiceInputButton
                  isListening={isListeningLocation}
                  onVoiceClick={() => startLocationVoice((text) => setLocation(text))}
                  size="md"
                />
              </div>
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

            {/* Season */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('Farming Season')} (Optional)
              </label>
              <select
                value={season}
                onChange={(e) => setSeason(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              >
                <option value="">{t('Select current season')}</option>
                {seasons.map((s) => (
                  <option key={s.value} value={s.value}>
                    {t(s.label)}
                  </option>
                ))}
              </select>
              <p className="text-xs text-gray-500 mt-1">{t('Choose your current farming season for better recommendations')}</p>
            </div>
          </div>

          {/* Right Column */}
          <div>
            {/* Query */}
            <div className="h-full flex flex-col">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('Additional Query')} *
              </label>
              <div className="flex-1 flex flex-col gap-2">
                <div className="flex gap-2">
                  <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={t('Enter additional questions')}
                    className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all duration-200"
                    rows={6}
                  />
                  <div className="flex flex-col gap-2">
                    <VoiceInputButton
                      isListening={isListeningQuery}
                      onVoiceClick={() => startQueryVoice((text) => setQuery(text))}
                      size="md"
                      showLabel={false}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <motion.button
          onClick={handleSubmit}
          disabled={loading || !cropName.trim() || !location.trim() || !soilType}
          className={`w-full mt-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200 ${
            loading || !cropName.trim() || !location.trim() || !soilType
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 shadow-lg hover:shadow-xl'
          }`}
          whileHover={!loading && cropName.trim() && location.trim() && soilType ? { scale: 1.02 } : {}}
          whileTap={!loading && cropName.trim() && location.trim() && soilType ? { scale: 0.98 } : {}}
        >
          {loading ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>{t('Getting Advisory...')}</span>
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
            className="mt-8 space-y-6"
          >
            {/* Advisory Response */}
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border-2 border-blue-300">
              <h3 className="text-lg font-bold text-blue-900 mb-3">🌾 {t('Farming Advisory')}</h3>
              <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">{response.text}</p>
            </div>

            {/* Farming Options Section */}
            {response.farming_options && response.farming_options.options && response.farming_options.options.length > 0 && (
              <div className="space-y-4">
                <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-6 rounded-xl">
                  <h3 className="text-xl font-bold flex items-center gap-2">
                    <span>🌱</span> {t('Recommended Crop Options')}
                  </h3>
                  <p className="text-green-100 text-sm mt-2">
                    {t('Based on')} {response.farming_options.season}, {response.farming_options.soil_type} {t('soil')}, {t('and')} {response.farming_options.location}
                  </p>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  {response.farming_options.options.map((option, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      className="bg-white border-2 border-green-200 rounded-xl p-5 hover:shadow-lg transition-shadow"
                    >
                      <h4 className="text-lg font-bold text-green-800 mb-3">{option.crop}</h4>
                      <p className="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap">{option.details}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Audio Playback for Advisory */}
            {response.advisory && (
              <motion.button
                onClick={handlePlayAudio}
                className="w-full py-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold flex items-center justify-center gap-2 transition-colors"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <span>🔊</span>
                <span>{t('Play Audio Advisory')}</span>
              </motion.button>
            )}
          </motion.div>
        )}

        {/* Hidden audio element */}
        <audio ref={audioRef} className="hidden" controls />
      </div>
    </motion.div>
  );
}
