import React, { useState, useRef, useEffect } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { useVoiceInput } from "../hooks/useVoiceInput";
import VoiceInputButton from "./VoiceInputButton";

const QUICK_CROP_KEYS = ["Rice", "Cotton", "Tomato", "Potato", "Maize", "Chilli", "Groundnut"];

export default function OrganicFarmingForm() {
  const [cropName, setCropName] = useState("");
  const [location, setLocation] = useState("Telangana, India");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [audioGenerating, setAudioGenerating] = useState(false);
  const [audioReady, setAudioReady] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioProgress, setAudioProgress] = useState(0);
  const [audioDuration, setAudioDuration] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const audioRef = useRef();
  const audioToastIdRef = useRef(null);
  const { currentLanguage, t } = useLanguage();
  const { isListening: isListeningCrop, startVoiceInput: startCropVoice } = useVoiceInput(currentLanguage);
  const { isListening: isListeningLocation, startVoiceInput: startLocationVoice } = useVoiceInput(currentLanguage);

  const handleSubmit = async () => {
    if (!cropName.trim()) {
      toast.error(t("Organic crop required"));
      return;
    }

    setLoading(true);
    setAudioReady(false);
    setAudioGenerating(false);
    const toastId = toast.loading(t("Generating organic guide"));

    try {
      const res = await fetch("http://127.0.0.1:8000/organic-farming/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          crop_name: cropName.trim(),
          location: location.trim() || "Telangana, India",
          language: currentLanguage,
        }),
      });

      if (!res.ok) throw new Error("Request failed");

      const data = await res.json();
      setResponse(data);
      toast.success(t("Organic guide ready"), { id: toastId });
    } catch (e) {
      console.error(e);
      toast.error(t("API Error"), { id: toastId });
    } finally {
      setLoading(false);
    }
  };

  // Stream audio in real-time (plays while generating + allows replay)
  useEffect(() => {
    if (!response?.text || audioGenerating || audioReady) return;
    
    setAudioGenerating(true);
    audioToastIdRef.current = toast.loading(t('Streaming audio - starts playing as it generates...'));
    
    const streamAudio = async () => {
      try {
        const query_id = response.query_id;
        if (!query_id) {
          toast.error(t('Query ID missing'), { id: audioToastIdRef.current });
          setAudioGenerating(false);
          return;
        }

        // Stream audio (will start playing while generating)
        const streamRes = await fetch(`http://127.0.0.1:8000/stream-audio/${query_id}`);
        
        if (streamRes.status === 202) {
          // File not ready yet, wait a bit and retry
          await new Promise(r => setTimeout(r, 1000));
          return streamAudio();
        }
        
        if (!streamRes.ok) {
          throw new Error(`Streaming failed: ${streamRes.status}`);
        }
        
        // Set up audio element to stream directly from response
        const reader = streamRes.body.getReader();
        const chunks = [];
        let receivedLength = 0;
        
        toast.loading(t('Playing audio...'), { id: audioToastIdRef.current });
        
        // Download chunks while reading (for replay cache)
        while (true) {
          const {done, value} = await reader.read();
          if (done) break;
          chunks.push(value);
          receivedLength += value.length;
        }
        
        // Create blob for replay capability
        const chunksArray = new Uint8Array(receivedLength);
        let position = 0;
        for(const chunk of chunks) {
          chunksArray.set(chunk, position);
          position += chunk.length;
        }
        
        const audioBlob = new Blob([chunksArray], { type: 'audio/mpeg' });
        const audioUrl = URL.createObjectURL(audioBlob);
        
        if (audioRef.current) {
          audioRef.current.src = audioUrl;
          setAudioReady(true);
          toast.success(t('✨ Audio ready! Click play to listen'), { id: audioToastIdRef.current });
        }
        
        setAudioGenerating(false);
      } catch (error) {
        console.error('Audio streaming error:', error);
        toast.error(t('Audio stream failed'), { id: audioToastIdRef.current });
        setAudioGenerating(false);
      }
    };
    
    // Start streaming immediately
    streamAudio();
  }, [response, currentLanguage, audioGenerating, audioReady, t]);

  // Audio playback event listeners
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    const handleEnded = () => {
      setIsPlaying(false);
      setAudioProgress(0);
    };
    const handleLoadedMetadata = () => {
      setAudioDuration(audio.duration);
    };
    const handleTimeUpdate = () => {
      setAudioProgress(audio.currentTime);
    };

    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('timeupdate', handleTimeUpdate);

    return () => {
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('timeupdate', handleTimeUpdate);
    };
  }, []);

  // Format time for display
  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Play/Pause handler
  const handlePlayAudio = () => {
    if (!audioRef.current?.src) {
      if (audioGenerating) {
        toast.loading(t('Audio is being generated...'));
      } else {
        toast.error(t('Audio not ready yet'));
      }
      return;
    }
    
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
  };

  // Change playback speed
  const handleSpeedChange = (speed) => {
    setPlaybackSpeed(speed);
    if (audioRef.current) {
      audioRef.current.playbackRate = speed;
    }
  };

  return (
    <motion.div
      className="bg-white rounded-2xl shadow-xl overflow-hidden border border-emerald-100/80"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
    >
      <div className="bg-gradient-to-r from-emerald-600 via-green-600 to-teal-700 text-white p-6">
        <div className="flex items-start gap-4">
          <span className="text-4xl drop-shadow-sm" aria-hidden>
            🌿
          </span>
          <div className="flex-1 min-w-0">
            <h2 className="text-2xl font-bold tracking-tight">{t("Organic Farming")}</h2>
            <p className="text-emerald-50/95 text-sm mt-1 leading-relaxed">
              {t("Organic Farming subtitle")}
            </p>
          </div>
        </div>
      </div>

      <div className="p-6 md:p-8 space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t("Crop Name")}
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={cropName}
              onChange={(e) => setCropName(e.target.value)}
              placeholder={t("Enter crop name")}
              className="flex-1 px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-shadow bg-gray-50/80"
            />
            <VoiceInputButton
              isListening={isListeningCrop}
              onVoiceClick={() => startCropVoice((text) => setCropName(text))}
              size="md"
            />
          </div>
          <div className="flex flex-wrap gap-2 mt-3">
            {QUICK_CROP_KEYS.map((cropKey) => (
              <button
                key={cropKey}
                type="button"
                onClick={() => setCropName(cropKey)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                  cropName === cropKey
                    ? "bg-emerald-600 text-white shadow-md"
                    : "bg-emerald-50 text-emerald-800 hover:bg-emerald-100 border border-emerald-200/80"
                }`}
              >
                {t(cropKey)}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t("Location")}
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Telangana, India"
              className="flex-1 px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent bg-gray-50/80"
            />
            <VoiceInputButton
              isListening={isListeningLocation}
              onVoiceClick={() => startLocationVoice((text) => setLocation(text))}
              size="md"
            />
          </div>
          <p className="text-xs text-gray-500 mt-1.5">{t("Organic location hint")}</p>
        </div>

        <motion.button
          type="button"
          onClick={handleSubmit}
          disabled={loading || !cropName.trim()}
          className={`w-full py-4 rounded-xl font-semibold text-lg transition-all duration-200 ${
            loading || !cropName.trim()
              ? "bg-gray-200 text-gray-500 cursor-not-allowed"
              : "bg-gradient-to-r from-emerald-600 to-green-700 text-white shadow-lg hover:shadow-xl hover:from-emerald-700 hover:to-green-800"
          }`}
          whileHover={!loading && cropName.trim() ? { scale: 1.01 } : {}}
          whileTap={!loading && cropName.trim() ? { scale: 0.99 } : {}}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              {t("Generating organic guide")}
            </span>
          ) : (
            <span className="flex items-center justify-center gap-2">
              <span>🌱</span>
              {t("Get Organic Guide")}
            </span>
          )}
        </motion.button>

        {response?.text && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="rounded-2xl border border-emerald-100 bg-gradient-to-br from-emerald-50/90 via-white to-green-50/50 shadow-inner overflow-hidden"
          >
            <div className="px-5 py-4 border-b border-emerald-100/80 flex items-center justify-between bg-white/60">
              <div>
                <h3 className="text-sm font-semibold text-emerald-900 uppercase tracking-wide">
                  {t("Organic techniques")}
                </h3>
                <p className="text-xs text-gray-600 mt-0.5">
                  {response.crop_name}
                  {response.location ? ` · ${response.location}` : ""}
                </p>
              </div>
            </div>
            <div className="p-5 md:p-6 max-h-[min(70vh,560px)] overflow-y-auto">
              <pre className="whitespace-pre-wrap font-sans text-sm text-gray-800 leading-relaxed m-0">
                {response.text}
              </pre>
            </div>

            {/* Google-Style Media Player */}
            {audioReady && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                transition={{ duration: 0.3 }}
                className="border-t border-gray-200 bg-white px-6 py-8"
              >
                {/* Play/Pause Button - Large & Centered */}
                <div className="flex justify-center mb-6">
                  <button
                    onClick={handlePlayAudio}
                    disabled={!audioReady && audioGenerating}
                    className="w-16 h-16 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-600 text-white shadow-lg hover:shadow-xl hover:from-emerald-600 hover:to-emerald-700 transition-all active:scale-95 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                    title={isPlaying ? t('Pause') : t('Play Audio')}
                  >
                    <span className="text-3xl" aria-hidden>
                      {isPlaying ? '⏸️' : '▶️'}
                    </span>
                  </button>
                </div>

                {/* Progress Bar */}
                <div className="space-y-3">
                  <div
                    className="w-full h-1 bg-gray-200 rounded-full overflow-hidden cursor-pointer hover:h-1.5 transition-all group"
                    onClick={(e) => {
                      if (audioRef.current) {
                        const rect = e.currentTarget.getBoundingClientRect();
                        const percent = (e.clientX - rect.left) / rect.width;
                        audioRef.current.currentTime = percent * audioDuration;
                      }
                    }}
                  >
                    <motion.div
                      className="h-full bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-full"
                      style={{
                        width: `${(audioProgress / (audioDuration || 1)) * 100}%`,
                      }}
                      transition={{ type: 'linear', duration: 0 }}
                    />
                  </div>

                  {/* Time Display */}
                  <div className="flex items-center justify-between text-xs text-gray-600 font-medium">
                    <span>{formatTime(audioProgress)}</span>
                    <span>{formatTime(audioDuration)}</span>
                  </div>
                </div>

                {/* Speed & Controls */}
                <div className="flex items-center justify-center gap-4 mt-6">
                  {/* Speed Button Group */}
                  <div className="inline-flex gap-1 rounded-lg border border-gray-200 bg-gray-50 p-1">
                    {[
                      { value: 0.5, label: '0.5x' },
                      { value: 0.75, label: '0.75x' },
                      { value: 1, label: '1x' },
                      { value: 1.25, label: '1.25x' },
                      { value: 1.5, label: '1.5x' },
                      { value: 2, label: '2x' },
                    ].map((speed) => (
                      <button
                        key={speed.value}
                        onClick={() => handleSpeedChange(speed.value)}
                        className={`px-3 py-1.5 rounded text-xs font-semibold transition-colors ${
                          playbackSpeed === speed.value
                            ? 'bg-emerald-600 text-white shadow-sm'
                            : 'text-gray-700 hover:bg-gray-200'
                        }`}
                        title={`${speed.label} - ${t('Playback Speed')}`}
                      >
                        {speed.label}
                      </button>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        )}

        <audio ref={audioRef} className="hidden" controls />
      </div>
    </motion.div>
  );
}
