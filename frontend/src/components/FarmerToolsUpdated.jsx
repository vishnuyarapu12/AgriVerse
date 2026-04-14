import React, { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { useLanguage } from "../contexts/LanguageContext";
import useTranslation from "../hooks/useTranslation";
import MarketPrices from "./MarketPrices";

const API = "http://127.0.0.1:8000";

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

  // Handle location and fetch weather
  const requestLocationAndWeather = useCallback(async () => {
    setGeoStatus("loading");
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setGeoStatus("granted");
          fetchWeather(pos.coords.latitude, pos.coords.longitude);
        },
        () => {
          setGeoStatus("denied");
          fetchWeather(null, null);
        }
      );
    } else {
      setGeoStatus("denied");
      fetch(`${API}/weather`)
        .then((r) => r.json())
        .then(setWeather)
        .catch(() => {
          toast.error(t("Error"));
        });
    }
  }, []);

  /**
   * Fetch weather for given coordinates
   */
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

      if (res.ok && data.temperature !== undefined) {
        setWeather(data);
        toast.success(t("Weather loaded"));
      } else {
        throw new Error("Invalid response");
      }
    } catch (error) {
      console.error("Weather fetch failed:", error);
      toast.error(t("API Error"));
    } finally {
      setWLoading(false);
    }
  };

  // Translate solution when language changes
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

  /**
   * Fetch disease solution
   */
  const fetchSolution = async () => {
    setSLoading(true);
    setSolution(null);
    try {
      const slug = diseasePick.replace(/\s+/g, " ");
      const res = await fetch(`${API}/solution/${encodeURIComponent(slug)}`);
      const data = await res.json();
      if (!res.ok)
        throw new Error(
          typeof data.detail === "string" ? data.detail : t("Failed")
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

  return (
    <div className="space-y-8">
      {/* ==================== WEATHER SECTION ==================== */}
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
              <p className="text-sky-100 text-sm mt-1">
                {t("Weather openmeteo hint")}
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={requestLocationAndWeather}
                disabled={wLoading || geoStatus === "loading"}
                className="px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 text-sm font-medium backdrop-blur transition-colors disabled:opacity-50"
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
              <div className="w-5 h-5 border-2 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
              <span>{t("Loading weather")}</span>
            </div>
          )}

          {weather && (
            <>
              <div>
                {usedDefault && (
                  <p className="mb-3 text-sm text-sky-600">
                    {t("Using Hyderabad default")}
                  </p>
                )}
              </div>

              <div className="grid sm:grid-cols-2 gap-4">
                <div className="bg-sky-50 border border-sky-200 rounded-xl p-4">
                  <p className="text-sm text-sky-700 font-semibold mb-2">
                    {t("Current conditions")}
                  </p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold text-sky-900">
                      {Math.round(weather.temperature)}°C
                    </span>
                    <span className="text-sm text-sky-600">
                      {t("Feels like")} {Math.round(weather.feels_like)}°C
                    </span>
                  </div>
                  <p className="text-xs text-sky-600 mt-2">
                    {t("Humidity")}: {Math.round(weather.humidity)}%
                  </p>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                  <p className="text-sm text-blue-700 font-semibold mb-2">
                    {t("Wind speed")}
                  </p>
                  <p className="text-2xl font-bold text-blue-900">
                    {Math.round(weather.wind_speed)} km/h
                  </p>
                  <p
                    className={`text-xs mt-2 font-semibold ${
                      sprayOk ? "text-green-600" : "text-orange-600"
                    }`}
                  >
                    {weather.advice || "N/A"}
                  </p>
                </div>
              </div>

              {weather.forecast && Array.isArray(weather.forecast) && (
                <div>
                  <p className="text-sm font-semibold text-slate-700 mb-3">
                    {t("Five day forecast")}
                  </p>
                  <div className="grid grid-cols-5 gap-2">
                    {weather.forecast.slice(0, 5).map((day, idx) => (
                      <div key={idx} className="bg-slate-50 rounded-lg p-2 text-center text-xs">
                        <p className="font-semibold text-slate-900">
                          {Math.round(day.max_temp)}°
                        </p>
                        <p className="text-slate-600">{Math.round(day.min_temp)}°</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {!weather.forecast && (
                <p className="text-xs text-slate-500">{t("City mode no forecast")}</p>
              )}
            </>
          )}
        </div>
      </motion.section>

      {/* ==================== ONE-TAP SOLUTION SECTION ==================== */}
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
              className="flex-1 px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-violet-500 bg-white text-gray-900"
            >
              <option value="">{t("Select Language")}</option>
              {diseaseOptions.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={fetchSolution}
              disabled={sLoading || !diseasePick}
              className="px-6 py-3 rounded-xl bg-violet-600 text-white font-semibold hover:bg-violet-700 disabled:opacity-50 transition-colors"
            >
              {sLoading ? "…" : t("Get solution")}
            </button>
          </div>
          {solution && (
            <dl className="grid gap-3 rounded-xl bg-violet-50/80 border border-violet-100 p-5 text-sm">
              <div className="flex justify-between gap-4 border-b border-violet-100 pb-2">
                <dt className="text-violet-700 font-medium">{t("Disease")}</dt>
                <dd className="text-slate-800 font-semibold">{solution.disease}</dd>
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

      {/* ==================== MARKET PRICES SECTION ==================== */}
      <MarketPrices />
    </div>
  );
}
