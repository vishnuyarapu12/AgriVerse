import React, { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { useLanguage } from "../contexts/LanguageContext";
import useTranslation from "../hooks/useTranslation";
import MarketPrices from "./MarketPrices";

const API = "http://127.0.0.1:8000";

// Disease name translations for One-Tap Solution
const diseaseTranslations = {
  'Tomato Early Blight': { hi: 'टमाटर अर्ली ब्लाइट', te: 'టమోటా ఎర్లీ బ్లైట్', ml: 'തക്കാളി ആദ്യ ബ്ലൈറ്റ്' },
  'Tomato Late Blight': { hi: 'टमाटर लेट ब्लाइट', te: 'టమోటా లేట్ బ్లైట్', ml: 'തക്കാളി വൈകി ബ്ലൈറ്റ്' },
  'Tomato Septoria Leaf Spot': { hi: 'टमाटर सेप्टोरिया पत्ती दाग', te: 'టమోటా సెప్టోరియా ఆకు మచ్చ', ml: 'തക്കാളി സെപ്റ്റോരിയ ഇലയിലെ കളങ്ങൾ' },
  'Tomato Leaf Mold': { hi: 'टमाटर पत्ती मोल्ड', te: 'టమోటా ఆకు మోల్డ్', ml: 'തക്കാളി ഇലയിലെ കിളിർ' },
  'Tomato Mosaic Virus': { hi: 'टमाटर मोजेक वायरस', te: 'టమోటా మోజాయిక్ వైరస్', ml: 'തക്കാളി മോസൈക് വൈറസ്' },
  'Tomato YellowLeaf Curl Virus': { hi: 'टमाटर यलो लीफ कर्ल', te: 'టమోటా పసుపు ఆకు కర్ల్', ml: 'തക്കാളി മഞ്ഞ ഇലയിലെ കോതുകൾ' },
  'Tomato Spider Mites': { hi: 'टमाटर स्पाइडर माइट्स', te: 'టమోటా స్పైడర్ చిలుక', ml: 'തക്കാളി അരിശ സ്പൈഡർ' },
  'Tomato Bacterial Spot': { hi: 'टमाटर बैक्टीरियल दाग', te: 'టమోటా బాక్టీరియల్ మచ్చ', ml: 'തക്കാളി ബാക്ടീരിയൽ കളങ്ങൾ' },
  'Tomato Target Spot': { hi: 'टमाटर टार्गेट दाग', te: 'టమోటా టార్గెట్ మచ్చ', ml: 'തക്കാളി ലക്ഷ്യ കളങ്ങൾ' },
  'Potato Early Blight': { hi: 'आलू अर्ली ब्लाइट', te: 'ఆలూ ఎర్లీ బ్లైట్', ml: 'ഉരുളക്കിഴങ്ങ് ആദ്യ ബ്ലൈറ്റ്' },
  'Potato Late Blight': { hi: 'आलू लेट ब्लाइट', te: 'ఆలూ లేట్ బ్లైట్', ml: 'ഉരുളക്കിഴങ്ങ് വൈകി ബ്ലൈറ്റ്' },
  'Pepper Bacterial Spot': { hi: 'मिर्च बैक्टीरियल दाग', te: 'మిరిచి బాక్టీరియల్ మచ్చ', ml: 'കുരുമുളക് ബാക്ടീരിയൽ കളങ്ങൾ' },
  'Corn Common Rust': { hi: 'मक्का आम जंग', te: 'మక్క సాధారణ తుప్పు', ml: 'ഉരുളയ് പൊതുവായ തുരുമ്പ്' },
  'Corn Northern Leaf Blight': { hi: 'मक्का उत्तरी पत्ती ब्लाइट', te: 'మక్క ఉత్తర ఆకు బ్లైట్', ml: 'ഉരുളയ് വടക്കേ ഇലയിലെ ബ്ലൈറ്റ്' },
  'Rice Blast': { hi: 'चावल ब्लास्ट', te: 'బియ్యం బ్లాస్ట్', ml: 'അരി സ്ഫോടനം' },
  'Rice Brown Spot': { hi: 'चावल भूरा दाग', te: 'బియ్యం గోధుమ కూరలో ', ml: 'അരി ബ്രൗൺ കളങ്ങൾ' },
};

// Weather advice translations
const weatherAdviceTranslations = {
  'safe': { hi: 'सुरक्षित है', te: 'సురక్షితం', ml: 'സുരക്ഷിതം' },
  'not safe': { hi: 'सुरक्षित नहीं', te: 'సురక్షితం కాదు', ml: 'സുരക്ഷിതമല്ല' },
  'high wind': { hi: 'तेज हवा', te: 'అధిక గాలి', ml: 'ശക്തമായ കാറ്റ്' },
  'rain': { hi: 'बारिश', te: 'వర్ష', ml: 'മഴ' },
};

// Enhanced weather recommendations translations
const sprayingAlertTranslations = {
  'Ideal spraying window': { hi: 'आदर्श छिड़काव की खिड़की', te: 'ఆదర్శ స్ప్రేయింగ్ విండో', ml: 'അനുയോജ്യമായ സ്പ്രേയിംഗ് കാലയളവ്' },
  'Spray now - perfect conditions': { hi: 'अभी छिड़कें - सही परिस्थितियाँ', te: 'ఇപుడు స్ప్రే చేయండి - సరిపడిన పరిస్థితులు', ml: 'ഇപ്പോൾ സ്പ്രേ ചെയ്യുക - തികഞ്ഞ സാഹചര്യങ്ങൾ' },
  'Good window': { hi: 'अच्छी खिड়की', te: 'మంచి విండో', ml: 'നല്ല കാലയളവ്' },
  'Heavy rain expected': { hi: 'तेज बारिश की उम्मीद', te: 'భారీ వర్ష ఆశించారు', ml: 'വലിയ മഴ പ്രതീക്ഷിക്കപ്പെടുന്നു' },
  'Do NOT spray today': { hi: 'आज छिड़कें नहीं', te: 'ఈ రోజు స్ప్రే చేయవద్దు', ml: 'ഇന്ന് സ്പ്രേ ചെയ്യരുത്' },
  'Rain stops at': { hi: 'बारिश रुकती है', te: 'వర్ష ఆగుతుంది', ml: 'മഴ നിലയ്ക്കുന്നത്' },
  'Wind speed at ideal time': { hi: 'आदर्श समय पर हवा की गति', te: 'ఆదర్శ సమయంలో గాలి వేగం', ml: 'അനുയോജ്യമായ സമയത്ത് കാറ്റിന്റെ വേഗത' },
  'Temperature': { hi: 'तापमान', te: 'ఉష్ణోగ్రత', ml: 'ഉഷ്ണാവസ്ഥ' },
  'Postpone spraying': { hi: 'छिड़काव को स्थगित करें', te: 'స్ప్రేయింగ్‌ను వాయిదా వేయండి', ml: 'സ്പ്രേയിംഗ് മാറ്റിവെയ്ക്കുക' },
};

/**
 * FarmerTools Component
 * Provides weather information, disease solutions, and market prices
 * Fully multilingual with dynamic language switching
 */
export default function FarmerTools() {
  const { t, currentLanguage } = useLanguage();
  const { getAllDistricts, getAllCrops, getCropName, getAllSeasons } = useTranslation();

  // Weather state
  const [geoStatus, setGeoStatus] = useState("idle");
  const [weather, setWeather] = useState(null);
  const [wLoading, setWLoading] = useState(false);
  const [usedDefault, setUsedDefault] = useState(false);

  // Solution state
  const [diseaseOptions, setDiseaseOptions] = useState([]);
  const [diseasePick, setDiseasePick] = useState("");
  const [solution, setSolution] = useState(null);
  const [sLoading, setSLoading] = useState(false);
  const [originalSolution, setOriginalSolution] = useState(null);
  const [solutionSourceLanguage, setSolutionSourceLanguage] = useState("en");

  // Load disease options from backend
  useEffect(() => {
    fetch(`${API}/solutions`)
      .then((r) => (r.ok ? r.json() : { diseases: [] }))
      .then((d) => {
        if (Array.isArray(d.diseases) && d.diseases.length) {
          setDiseaseOptions(d.diseases);
          if (!diseasePick) {
            setDiseasePick(d.diseases[0]);
          }
        }
      })
      .catch(() => {});
  }, []);

  /** Open-Meteo farm weather: { temperature, wind_speed, advice } */
  const fetchWeather = async (lat, lon) => {
    setWLoading(true);
    setWeather(null);
    setUsedDefault(lat == null && lon == null);
    try {
      let url = `${API}/weather`;
      if (lat != null && lon != null) {
        url += `?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`;
      }
      const res = await fetch(url);
      const data = await res.json().catch(() => ({}));
      if (!res.ok)
        throw new Error(
          typeof data.detail === "string" ? data.detail : "Weather failed"
        );
      setWeather(data);
      toast.success(t("Weather loaded"));
    } catch (e) {
      toast.error(e.message || t("API Error"));
    } finally {
      setWLoading(false);
    }
  };

  const requestLocationAndWeather = useCallback(() => {
    if (!navigator.geolocation) {
      toast.error(t("Geolocation not supported"));
      fetchWeather(null, null);
      return;
    }
    setGeoStatus("loading");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setGeoStatus("granted");
        fetchWeather(pos.coords.latitude, pos.coords.longitude);
      },
      () => {
        setGeoStatus("denied");
        fetchWeather(null, null);
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 60000 }
    );
  }, []);

  useEffect(() => {
    if (!originalSolution) return;

    const doTranslateSolution = async () => {
      try {
        // Translate solution fields
        const translateField = async (field) => {
          if (!field) return "";
          const res = await fetch(`${API}/translate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              text: field,
              target_language: currentLanguage,
              source_language: "en",
            }),
          });
          if (!res.ok) return field;
          const json = await res.json();
          return json.translated_text || field;
        };

        const translated = {
          disease: await translateField(originalSolution.disease || ""),
          medicine: await translateField(originalSolution.medicine || ""),
          dosage: await translateField(originalSolution.dosage || ""),
          time: await translateField(originalSolution.time || ""),
          note: await translateField(originalSolution.note || ""),
        };
        setSolution(translated);
      } catch (err) {
        console.error("Failed to translate solution:", err);
      }
    };

    doTranslateSolution();
  }, [currentLanguage, originalSolution]);

  const fetchSolution = async () => {
    setSLoading(true);
    setSolution(null);
    try {
      const slug = diseasePick.replace(/\s+/g, " ");
      const res = await fetch(
        `${API}/solution/${encodeURIComponent(slug)}`
      );
      const data = await res.json();
      if (!res.ok)
        throw new Error(
          typeof data.detail === "string" ? data.detail : "Failed"
        );
      setSolution(data);
      setOriginalSolution(data);
      setSolutionSourceLanguage("en");
      toast.success(t("Solution loaded"));
    } catch (e) {
      toast.error(e.message || t("API Error"));
    } finally {
      setSLoading(false);
    }
  };

  const sprayOk =
    weather &&
    weather.advice &&
    weather.advice.toLowerCase().includes("safe");

  // Translate disease name
  const translateDiseaseName = (diseaseName) => {
    if (currentLanguage === 'en') return diseaseName;
    return diseaseTranslations[diseaseName]?.[currentLanguage] || diseaseName;
  };

  // Translate weather advice
  const translateWeatherAdvice = (advice) => {
    if (!advice || currentLanguage === 'en') return advice;
    
    const lowerAdvice = advice.toLowerCase();
    if (lowerAdvice.includes('safe')) {
      return weatherAdviceTranslations['safe'][currentLanguage] + ' - ' + advice;
    } else if (lowerAdvice.includes('high wind') || lowerAdvice.includes('wind > 20')) {
      return weatherAdviceTranslations['high wind'][currentLanguage] + ' - ' + advice;
    } else if (lowerAdvice.includes('rain')) {
      return weatherAdviceTranslations['rain'][currentLanguage] + ' - ' + advice;
    }
    return advice;
  };

  // Translate spraying alert text
  const translate = (key) => {
    return sprayingAlertTranslations[key]?.[currentLanguage] || key;
  };

  return (
    <div className="space-y-8">
      {/* Open-Meteo weather — GPS or Hyderabad default */}
      <motion.section
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-2xl shadow-xl border border-sky-100 overflow-hidden"
      >
        <div className="bg-gradient-to-r from-sky-600 via-blue-600 to-indigo-700 text-white px-6 py-5">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h2 className="text-xl font-bold flex items-center gap-2">
                <span>🌤️</span> {t("Weather & spray")}
              </h2>
              <p className="text-sky-100 text-sm mt-1">{t("Weather openmeteo hint")}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={requestLocationAndWeather}
                disabled={wLoading || geoStatus === "loading"}
                className="px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 text-sm font-medium backdrop-blur transition-colors"
              >
                {t("Refresh location weather")}
              </button>
              <button
                type="button"
                onClick={() => fetchWeather(null, null)}
                disabled={wLoading}
                className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm"
              >
                {t("Hyderabad default weather")}
              </button>
            </div>
          </div>
          {geoStatus === "denied" && (
            <p className="text-amber-100 text-sm mt-3">{t("Location denied banner")}</p>
          )}
        </div>

        <div className="p-6 space-y-6">
          {wLoading && (
            <div className="flex items-center gap-3 text-slate-600">
              <span className="w-6 h-6 border-2 border-sky-500 border-t-transparent rounded-full animate-spin" />
              {t("Loading weather")}
            </div>
          )}

          {weather && !wLoading && (
            <>
              {usedDefault && (
                <p className="text-sm text-slate-500 bg-slate-50 rounded-lg px-3 py-2 border border-slate-100">
                  {t("Using Hyderabad default")}
                </p>
              )}
              <div className="flex flex-col lg:flex-row gap-6 items-stretch">
                <div className="flex-1 rounded-2xl bg-gradient-to-br from-sky-500 to-blue-700 text-white p-6 shadow-inner">
                  <p className="text-sky-100 text-sm font-medium uppercase tracking-wide">
                    {t("Current conditions")}
                  </p>
                  <p className="text-5xl sm:text-6xl font-light mt-2">
                    {weather.temperature}°C
                  </p>
                  <p className="text-sky-100 mt-4 text-sm">
                    {t("Wind speed")}:{" "}
                    <span className="text-white font-semibold">
                      {weather.wind_speed} km/h
                    </span>
                  </p>
                  <p className="text-xs text-sky-200 mt-2">
                    {t("OpenMeteo wind note")}
                  </p>
                </div>
                <div
                  className={`lg:w-80 rounded-2xl p-5 border-2 ${
                    sprayOk
                      ? "bg-emerald-50 border-emerald-200"
                      : "bg-amber-50 border-amber-200"
                  }`}
                >
                  <p className="text-xs uppercase font-semibold text-slate-600">
                    {t("Spray advice")}
                  </p>
                  <p className="text-lg font-semibold text-slate-900 mt-2 leading-snug">
                    {weather && weather.advice ? translateWeatherAdvice(weather.advice) : 'N/A'}
                  </p>
                </div>
              </div>

              {/* Enhanced Spraying Window Recommendations - HIDDEN FOR LATER */}
              {false && weather.spray_window && (
                <div className={`rounded-2xl p-6 border-2 ${
                  sprayOk && weather.spray_window.ideal_hour_display
                    ? "bg-green-50 border-green-300"
                    : "bg-red-50 border-red-300"
                }`}>
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">
                      {sprayOk && weather.spray_window.ideal_hour_display ? "✅" : "⚠️"}
                    </span>
                    <div className="flex-1">
                      <h3 className="font-bold text-slate-900 mb-3">
                        {translate("Ideal spraying window")}
                      </h3>
                      
                      {weather.spray_window.ideal_hour_display ? (
                        <div className="space-y-2">
                          <p className="text-sm font-semibold text-slate-800">
                            {translate("Spray now - perfect conditions")} <span className="text-lg">🎯</span>
                          </p>
                          <div className="grid grid-cols-2 gap-3 mt-3">
                            <div className="bg-white rounded-lg p-3 border border-green-200">
                              <p className="text-xs text-slate-600">{translate("Ideal spraying window")}</p>
                              <p className="text-lg font-bold text-green-700">
                                {weather.spray_window.ideal_hour_display}
                              </p>
                            </div>
                            <div className="bg-white rounded-lg p-3 border border-green-200">
                              <p className="text-xs text-slate-600">{translate("Wind speed at ideal time")}</p>
                              <p className="text-lg font-bold text-green-700">
                                {weather.spray_window.wind_at_ideal?.toFixed(1) || 'N/A'} km/h
                              </p>
                            </div>
                            <div className="bg-white rounded-lg p-3 border border-green-200 col-span-2">
                              <p className="text-xs text-slate-600">{translate("Temperature")}</p>
                              <p className="text-lg font-bold text-green-700">
                                {weather.spray_window.temp_at_ideal?.toFixed(1) || 'N/A'}°C - {currentLanguage === 'en' ? 'Perfect for spraying' : currentLanguage === 'hi' ? 'छिड़काव के लिए उत्तम' : currentLanguage === 'te' ? 'స్ప్రేయింగ్‌కు సరిపడినది' : 'സ്പ്രേയിംഗ്‌ന് അനുയോജ്യം'}
                              </p>
                            </div>
                          </div>
                          <div className="mt-4 p-3 bg-green-100 rounded-lg border border-green-400">
                            <p className="text-sm text-green-900 font-semibold">
                              💡 {currentLanguage === 'en' ? 'Tips:' : currentLanguage === 'hi' ? 'सुझाव:' : currentLanguage === 'te' ? 'చిట్కాలు:' : 'നുറുങ്ങുകൾ:'}
                            </p>
                            <ul className="text-xs text-green-800 mt-2 space-y-1">
                              <li>• {currentLanguage === 'en' ? 'Spray early morning for best results' : currentLanguage === 'hi' ? 'सर्वोत्तम परिणामों के लिए सुबह जल्दी छिड़कें' : currentLanguage === 'te' ? 'ఉత్తమ ఫలితాల కోసం తెల్లవారుజామున స్ప్రేయింగ్ చేయండి' : 'മികച്ച ഫലങ്ങൾക്കായി പുലർ കാലത്ത് സ്പ്രേ ചെയ്യുക'}</li>
                              <li>• {currentLanguage === 'en' ? 'Low wind means better spray coverage' : currentLanguage === 'hi' ? 'कम हवा का मतलब बेहतर छिड़काव कवरेज' : currentLanguage === 'te' ? 'తక్క గాలి అంటే మెరుగైన స్ప్రే కవరేజ్' : 'കുറഞ്ഞ കാറ്റ് നല്ല സ്പ്രേ കവറേജ്'}</li>
                              <li>• {currentLanguage === 'en' ? 'Prevents input waste and costs' : currentLanguage === 'hi' ? 'निविष्ट अपशिष्ट और लागत को रोकता है' : currentLanguage === 'te' ? 'ఇన్‌పుట్ వ్యర్థాలను మరియు ఖర్చులను నిరోధిస్తుంది' : 'ഇൻപുട്ട് കാലвійськ നഷ്ടവും ചിലവും തടയുന്നു'}</li>
                            </ul>
                          </div>
                        </div>
                      ) : (
                        <div className="space-y-2">
                          <p className="text-sm font-semibold text-red-800">
                            {translate("Postpone spraying")} 📅
                          </p>
                          <p className="text-sm text-slate-700 mt-2">
                            <strong>{translate("Heavy rain expected")}</strong> - {weather.spray_window.warning_message}
                          </p>
                          {weather.spray_window.rain_end_hour && (
                            <p className="text-sm text-slate-600 mt-2">
                              ⏰ {translate("Rain stops at")}: <strong>Hour {weather.spray_window.rain_end_hour}</strong>
                            </p>
                          )}
                          <div className="mt-3 p-3 bg-red-100 rounded-lg border border-red-400">
                            <p className="text-sm text-red-900 font-semibold">
                              💡 {currentLanguage === 'en' ? 'Recommendation:' : currentLanguage === 'hi' ? 'अनुशंसा:' : currentLanguage === 'te' ? 'సిఫారిష్:' : 'సిఫారిష్:'}
                            </p>
                            <p className="text-xs text-red-800 mt-2">
                              {currentLanguage === 'en' ? 'Wait for better weather conditions. Spraying during rain or high wind causes spray drift and reduced effectiveness, wasting your inputs and money.' : 
                               currentLanguage === 'hi' ? 'बेहतर मौसम की प्रतीक्षा करें। बारिश या तेज हवा के दौरान छिड़काव से ड्रिफ्ट होता है और प्रभावशीलता कम होती है।' : 
                               currentLanguage === 'te' ? 'మంచి వాతావరణ పరిస్థితుల కోసం వేచిరండి. వర్ష లేదా అధిక గాలులో స్ప్రేయింగ్ చేయడం చెదరిపోవటానికి కారణమవుతుంది.' : 
                               'നല്ല കാലാവസ്ഥാ സാഹചര്യങ്ങൾക്കായി കാത്തിരിക്കുക.'}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </motion.section>

      <motion.section
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="bg-white rounded-2xl shadow-xl border border-violet-100 overflow-hidden"
      >
        <div className="bg-gradient-to-r from-violet-600 to-purple-700 text-white px-6 py-5">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <span>💊</span> {t("One-tap solution")}
          </h2>
          <p className="text-violet-100 text-sm mt-1">{t("Solution hint")}</p>
        </div>
        <div className="p-6 space-y-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <select
              value={diseasePick}
              onChange={(e) => setDiseasePick(e.target.value)}
              className="flex-1 px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-violet-500 bg-white"
            >
              <option value="">
                {currentLanguage === 'en' ? 'Select a disease...' : 
                 currentLanguage === 'hi' ? 'रोग चुनें...' :
                 currentLanguage === 'te' ? 'వ్యాధిని ఎంచుకోండి...' :
                 'രോഗം തിരഞ്ഞെടുക്കുക...'}
              </option>
              {diseaseOptions.map((d) => (
                <option key={d} value={d}>
                  {translateDiseaseName(d)}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={fetchSolution}
              disabled={sLoading || !diseasePick}
              className="px-6 py-3 rounded-xl bg-violet-600 text-white font-semibold hover:bg-violet-700 disabled:opacity-50"
            >
              {sLoading ? "…" : t("Get solution")}
            </button>
          </div>
          {solution && (
            <dl className="grid gap-3 rounded-xl bg-violet-50/80 border border-violet-100 p-5 text-sm">
              <div className="flex justify-between gap-4 border-b border-violet-100 pb-2">
                <dt className="text-violet-700 font-medium">{t("Disease")}</dt>
                <dd className="text-slate-800 font-semibold">{translateDiseaseName(solution.disease)}</dd>
              </div>
              <div className="flex justify-between gap-4 border-b border-violet-100 pb-2">
                <dt className="text-violet-700 font-medium">{t("Medicine")}</dt>
                <dd className="text-slate-800">{solution.medicine}</dd>
              </div>
              <div className="flex justify-between gap-4 border-b border-violet-100 pb-2">
                <dt className="text-violet-700 font-medium">{t("Dosage")}</dt>
                <dd className="text-slate-800">{solution.dosage}</dd>
              </div>
              <div className="flex justify-between gap-4 border-b border-violet-100 pb-2">
                <dt className="text-violet-700 font-medium">{t("Time")}</dt>
                <dd className="text-slate-800">{solution.time}</dd>
              </div>
              <div>
                <dt className="text-violet-700 font-medium mb-1">{t("Note")}</dt>
                <dd className="text-slate-700">{solution.note}</dd>
              </div>
            </dl>
          )}
        </div>
      </motion.section>

      {/* Market Prices Section */}
      <MarketPrices />
    </div>
  );
}
