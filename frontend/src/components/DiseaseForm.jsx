import React, { useState, useRef, useEffect } from "react";
import ResponseCard from "./ResponseCard";
import { useLanguage } from "../contexts/LanguageContext";
import { useFormState } from "../contexts/FormStateContext";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { useVoiceInput } from "../hooks/useVoiceInput";
import VoiceInputButton from "./VoiceInputButton";

export default function DiseaseForm() {
  const { state: savedState, saveState } = useFormState('disease');
  
  // Initialize state from saved state or defaults
  const [images, setImages] = useState(savedState.images || []);
  const [imagePreviews, setImagePreviews] = useState(savedState.imagePreviews || []);
  const [response, setResponse] = useState(savedState.response || null);
  const [originalResponse, setOriginalResponse] = useState(savedState.originalResponse || null);
  const [originalAdvisory, setOriginalAdvisory] = useState(savedState.originalAdvisory || "");
  const [sourceLanguage, setSourceLanguage] = useState(savedState.sourceLanguage || "en");
  const [text, setText] = useState(savedState.text || "");
  const [loading, setLoading] = useState(false);
  const [audioGenerating, setAudioGenerating] = useState(false);
  const [audioReady, setAudioReady] = useState(savedState.audioReady || false);
  const [cropModel, setCropModel] = useState(savedState.cropModel || "");
  const [modelOptions, setModelOptions] = useState([]);
  const audioRef = useRef();
  const audioToastIdRef = useRef(null);
  const { currentLanguage, t } = useLanguage();
  const { isListening, startVoiceInput } = useVoiceInput(currentLanguage);

  // Save state to context whenever it changes
  useEffect(() => {
    saveState({
      images,
      imagePreviews,
      response,
      originalResponse,
      originalAdvisory,
      sourceLanguage,
      text,
      audioReady,
      cropModel
    });
  }, [images, imagePreviews, response, originalResponse, originalAdvisory, sourceLanguage, text, audioReady, cropModel, saveState]);

  useEffect(() => {
    let cancelled = false;
    fetch("http://127.0.0.1:8000/disease-models/")
      .then((r) => (r.ok ? r.json() : { models: [] }))
      .then((data) => {
        if (!cancelled && Array.isArray(data.models)) setModelOptions(data.models);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  // Image upload handler with preview - supports multiple images
  const handleImageChange = (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    const validImages = [];
    const previews = [];

    files.forEach((file) => {
      if (file.size > 10 * 1024 * 1024) {
        toast.error(`${file.name} exceeds 10MB limit`);
        return;
      }
      validImages.push(file);
      const reader = new FileReader();
      reader.onload = (event) => {
        previews.push(event.target.result);
        if (previews.length === validImages.length) {
          setImages([...images, ...validImages]);
          setImagePreviews([...imagePreviews, ...previews]);
          toast.success(`${validImages.length} image(s) added`);
        }
      };
      reader.readAsDataURL(file);
    });
  };

  // Remove a specific image
  const removeImage = (index) => {
    setImages(images.filter((_, i) => i !== index));
    setImagePreviews(imagePreviews.filter((_, i) => i !== index));
    toast.success("Image removed");
  };

  // Voice input is now handled via useVoiceInput hook and VoiceInputButton component

  // Enhanced submit handler to handle multiple images
  const handleSubmit = async () => {
    if (images.length === 0 && !text.trim()) {
      toast.error(t('Please upload at least one image or enter a query'));
      return;
    }

    setLoading(true);
    setAudioReady(false);
    setAudioGenerating(false);
    const toastId = toast.loading(t('Analyzing crop diseases...'));

    try {
      const formData = new FormData();
      
      // Add all images
      images.forEach((img) => {
        formData.append("files", img);
      });
      
      if (text.trim()) formData.append("text_query", text.trim());
      formData.append("language", currentLanguage);
      if (cropModel.trim()) formData.append("crop", cropModel.trim());

      const res = await fetch("http://127.0.0.1:8000/detect-disease/", {
        method: "POST",
        body: formData,
      });
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || t('API Error'));
      }
      
      const data = await res.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      // Handle both single and multiple responses
      if (Array.isArray(data)) {
        setResponse(data);
      } else {
        setResponse(data);
      }
      
      setOriginalResponse(data);
      setOriginalAdvisory(
        Array.isArray(data) 
          ? data.map(d => d.text || d.advisory || d.answer || "").join("\n")
          : (data.text || data.advisory || data.answer || "")
      );
      setSourceLanguage(currentLanguage);
      toast.success(t('Disease analysis completed!'), { id: toastId });

    } catch (error) {
      console.error('Disease detection error:', error);
      toast.error(error.message || t('API Error'), { id: toastId });
    } finally {
      setLoading(false);
    }
  };

  // Translate existing response when language changes (without resetting UI)
  useEffect(() => {
    if (!originalResponse || !sourceLanguage) return;
    if (currentLanguage === sourceLanguage) {
      setResponse(originalResponse);
      return;
    }

    const translateField = async (text) => {
      if (!text) return "";
      const res = await fetch("http://127.0.0.1:8000/translate/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, target_language: currentLanguage }),
      });
      if (!res.ok) throw new Error('Translate API failed');
      const body = await res.json();
      return body.text || "";
    };

    const translateAndSet = async () => {
      try {
        if (Array.isArray(originalResponse)) {
          // Handle multiple responses
          const translated = await Promise.all(
            originalResponse.map(async (resp) => ({
              ...resp,
              text: await translateField(resp.text || resp.advisory || resp.answer || ""),
              advisory: await translateField(resp.text || resp.advisory || resp.answer || ""),
              prediction: await translateField(resp.prediction || ""),
              prediction_ml: await translateField(resp.prediction_ml || ""),
            }))
          );
          setResponse(translated);
        } else {
          // Handle single response
          const translatedText = await translateField(originalResponse.text || originalResponse.advisory || originalResponse.answer || "");
          const translatedPrediction = await translateField(originalResponse.prediction || "");
          const translatedPredictionMl = await translateField(originalResponse.prediction_ml || "");

          setResponse({
            ...originalResponse,
            text: translatedText || (originalResponse.text || originalResponse.advisory || originalResponse.answer || ""),
            advisory: translatedText || (originalResponse.advisory || originalResponse.answer || ""),
            answer: translatedText || originalResponse.answer,
            prediction: translatedPrediction || originalResponse.prediction,
            prediction_ml: translatedPredictionMl || originalResponse.prediction_ml,
          });
        }
      } catch (error) {
        console.error('Translate-on-language-change failed:', error);
        setResponse((prev) => prev || originalResponse);
      }
    };

    translateAndSet();
  }, [currentLanguage, originalResponse, originalAdvisory, sourceLanguage]);

  // Auto-generate audio when response is received
  useEffect(() => {
    if (!response?.text || audioGenerating || audioReady) return;
    
    setAudioGenerating(true);
    audioToastIdRef.current = toast.loading(t('Generating audio in background...'));
    
    const generateAudio = async () => {
      try {
        // Handle both single and multiple responses
        const textToSpeak = Array.isArray(response)
          ? response.map(r => r.text || r.advisory || r.answer || "").join(" ")
          : (response.text || response.advisory || response.answer || "");
        
        if (!textToSpeak.trim()) {
          throw new Error('No text to convert');
        }

        const ttsRes = await fetch("http://127.0.0.1:8000/text-to-speech/", {
          method: "POST",
          body: JSON.stringify({ 
            text: textToSpeak, 
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
    toast.success(t('Playing audio response'));
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
            {t('Upload Images')} ({images.length})
          </label>
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <p className="text-xs text-gray-600 mb-2">
                {currentLanguage === 'en' ? '📁 Click button to choose files' :
                 currentLanguage === 'hi' ? '📁 फ़ाइलें चुनने के लिए बटन पर क्लिक करें' :
                 currentLanguage === 'te' ? '📁 ఫైల్‌లను ఎంచుకోవడానికి బటన్‌ను క్లిక్ చేయండి' :
                 '📁 ഫയലുകൾ തിരഞ്ഞെടുക്കാൻ ബട്ടൺ ക്ലിക്ക് ചെയ്യുക'}
              </p>
              <input
                type="file"
                accept="image/*"
                multiple
                onChange={handleImageChange}
                className="w-full text-sm text-gray-500 file:mr-4 file:py-3 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100 transition-all duration-200"
              />
              <p className="text-xs text-gray-500 mt-1">{t('Upload multiple leaf images for disease detection')}</p>
            </div>
          </div>

          {/* Image Previews Grid */}
          {imagePreviews.length > 0 && (
            <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {imagePreviews.map((preview, idx) => (
                <motion.div 
                  key={idx}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="relative w-full aspect-square rounded-lg overflow-hidden border-2 border-green-200 group"
                >
                  <img 
                    src={preview} 
                    alt={`Preview ${idx + 1}`} 
                    className="w-full h-full object-cover"
                  />
                  <button
                    onClick={() => removeImage(idx)}
                    className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    ✕
                  </button>
                  <span className="absolute bottom-1 left-1 bg-black bg-opacity-60 text-white text-xs px-2 py-1 rounded">
                    {idx + 1}
                  </span>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Text Input Section */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('Enter Query')}
          </label>
          <div className="flex gap-2">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={t('Describe crop problem')}
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none h-24 transition-all duration-200"
            />
            <VoiceInputButton
              isListening={isListening}
              onVoiceClick={() => startVoiceInput((transcript) => setText(transcript))}
              size="md"
              showLabel={false}
            />
          </div>
        </div>

        {/* Submit Button */}
        <motion.button
          onClick={handleSubmit}
          disabled={loading || (images.length === 0 && !text.trim())}
          className={`w-full py-4 rounded-lg font-semibold text-lg transition-all duration-200 ${
            loading || (images.length === 0 && !text.trim())
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-green-600 to-green-700 text-white hover:from-green-700 hover:to-green-800 shadow-lg hover:shadow-xl'
          }`}
          whileHover={!loading && (images.length > 0 || text.trim()) ? { scale: 1.02 } : {}}
          whileTap={!loading && (images.length > 0 || text.trim()) ? { scale: 0.98 } : {}}
        >
          {loading ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>{t('Analyzing...')}</span>
            </div>
          ) : (
            <div className="flex items-center justify-center space-x-2">
              <span>🔍</span>
              <span>{t('Analyze Diseases')} ({images.length})</span>
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
            {Array.isArray(response) ? (
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-gray-800">{t('Disease Analysis Results')} ({response.length})</h3>
                {response.map((resp, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className="border-l-4 border-green-500 pl-4 py-2"
                  >
                    <h4 className="font-semibold text-gray-700 mb-2">{t('Image')} {idx + 1}</h4>
                    <ResponseCard 
                      response={resp} 
                      audioRef={audioRef}
                      onPlayAudio={handlePlayAudio}
                      language={currentLanguage}
                    />
                  </motion.div>
                ))}
              </div>
            ) : (
              <ResponseCard 
                response={response} 
                audioRef={audioRef}
                onPlayAudio={handlePlayAudio}
                language={currentLanguage}
              />
            )}
          </motion.div>
        )}

        {/* Hidden audio element */}
        <audio ref={audioRef} className="hidden" controls />
      </div>
    </motion.div>
  );
}
