/**
 * useTranslation Hook
 * Custom hook for managing translations in components
 * Integrates with LanguageContext and translationService
 */

import { useState, useEffect, useCallback } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import { translateText, translateBatch } from "../services/translationService";
import cropsData from "../constants/crops.json";
import districtsData from "../constants/districts.json";
import seasonsData from "../constants/seasons.json";

/**
 * Custom hook for translations
 * Provides methods to translate text and manages language-aware dropdown options
 */
export const useTranslation = () => {
  const { t, currentLanguage } = useLanguage();
  const [translations, setTranslations] = useState({});
  const [isLoadingTranslations, setIsLoading] = useState(false);

  /**
   * Translate a single text
   */
  const translate = useCallback(async (text) => {
    if (!text) return "";
    if (currentLanguage === "en") return text;

    const translatedText = await translateText(text, currentLanguage, "en");
    return translatedText;
  }, [currentLanguage]);

  /**
   * Get crop name in selected language with fallback
   */
  const getCropName = useCallback((cropKey) => {
    const crop = cropsData[cropKey];
    if (!crop) return cropKey; // Fallback to key if not found

    return crop[currentLanguage] || crop.en;
  }, [currentLanguage]);

  /**
   * Get all crops list with names in selected language
   */
  const getAllCrops = useCallback(() => {
    return Object.entries(cropsData).map(([key, translations]) => ({
      key,
      label: translations[currentLanguage] || translations.en,
      en: translations.en,
    }));
  }, [currentLanguage]);

  /**
   * Get district name in selected language with fallback
   */
  const getDistrictName = useCallback((districtIndex, state = "telangana_districts") => {
    const stateDistricts = districtsData[state];
    if (!stateDistricts || !stateDistricts[districtIndex]) {
      return `District ${districtIndex}`;
    }

    const district = stateDistricts[districtIndex];
    return district[currentLanguage] || district.en;
  }, [currentLanguage]);

  /**
   * Get all districts for a state with names in selected language
   */
  const getAllDistricts = useCallback((state = "telangana_districts") => {
    const stateDistricts = districtsData[state] || [];
    return stateDistricts.map((district, idx) => ({
      index: idx,
      label: district[currentLanguage] || district.en,
      en: district.en,
    }));
  }, [currentLanguage]);

  /**
   * Get season name in selected language
   */
  const getSeasonName = useCallback((seasonKey) => {
    const season = seasonsData.seasons.find((s) => s.key === seasonKey);
    if (!season) return seasonKey;

    return season[currentLanguage] || season.en;
  }, [currentLanguage]);

  /**
   * Get all seasons with names in selected language
   */
  const getAllSeasons = useCallback(() => {
    return seasonsData.seasons.map((season) => ({
      key: season.key,
      label: season[currentLanguage] || season.en,
      en: season.en,
    }));
  }, [currentLanguage]);

  /**
   * Translate multiple texts at once
   */
  const translateMultiple = useCallback(async (texts) => {
    if (currentLanguage === "en") {
      return texts;
    }

    setIsLoading(true);
    const translated = await translateBatch(texts, currentLanguage);
    setIsLoading(false);

    return translated;
  }, [currentLanguage]);

  /**
   * Get UI translations (for common UI elements)
   */
  const getUITranslation = useCallback((key) => {
    return t(key) || key;
  }, [t]);

  return {
    // Core translation methods
    translate,
    translateMultiple,
    getUITranslation,

    // Crop utilities
    getCropName,
    getAllCrops,

    // District utilities
    getDistrictName,
    getAllDistricts,

    // Season utilities
    getSeasonName,
    getAllSeasons,

    // State
    currentLanguage,
    isLoadingTranslations,
  };
};

export default useTranslation;
