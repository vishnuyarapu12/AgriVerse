/**
 * Translation Service
 * Handles text translation with caching and fallback support
 * Uses backend API for translation, with local fallback support
 */

const API = "http://127.0.0.1:8000";
const TRANSLATION_CACHE = {};

/**
 * Translate text to target language
 * @param {string} text - Text to translate
 * @param {string} targetLanguage - Target language code (en, te, hi, ml)
 * @param {string} sourceLanguage - Source language (default: en)
 * @returns {Promise<string>} - Translated text
 */
export const translateText = async (text, targetLanguage, sourceLanguage = "en") => {
  // Skip if target language is same as source
  if (targetLanguage === sourceLanguage) {
    return text;
  }

  // Check cache first
  const cacheKey = `${text}_${sourceLanguage}_${targetLanguage}`;
  if (TRANSLATION_CACHE[cacheKey]) {
    return TRANSLATION_CACHE[cacheKey];
  }

  try {
    // Call backend translation API
    const response = await fetch(`${API}/translate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        source_language: sourceLanguage,
        target_language: targetLanguage,
      }),
    });

    if (!response.ok) {
      console.warn(`Translation failed for "${text}"`);
      return text; // Fallback to original text
    }

    const data = await response.json();
    const translatedText = data.translated_text || text;

    // Cache the result
    TRANSLATION_CACHE[cacheKey] = translatedText;
    return translatedText;
  } catch (error) {
    console.error("Translation API error:", error);
    return text; // Fallback to original text
  }
};

/**
 * Batch translate multiple texts
 * @param {Array<string>} texts - Array of texts to translate
 * @param {string} targetLanguage - Target language code
 * @returns {Promise<Array<string>>} - Array of translated texts
 */
export const translateBatch = async (texts, targetLanguage) => {
  if (targetLanguage === "en") {
    return texts; // Skip translation for English
  }

  try {
    const response = await fetch(`${API}/translate-batch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        texts,
        target_language: targetLanguage,
      }),
    });

    if (!response.ok) {
      return texts; // Fallback
    }

    const data = await response.json();
    return data.translated_texts || texts;
  } catch (error) {
    console.error("Batch translation error:", error);
    return texts;
  }
};

/**
 * Clear translation cache (useful for testing or manual refresh)
 */
export const clearTranslationCache = () => {
  Object.keys(TRANSLATION_CACHE).forEach((key) => delete TRANSLATION_CACHE[key]);
};

/**
 * Get translation status
 */
export const getTranslationCacheSize = () => {
  return Object.keys(TRANSLATION_CACHE).length;
};
