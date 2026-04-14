import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { useLanguage } from "../contexts/LanguageContext";
import useTranslation from "../hooks/useTranslation";
import { useVoiceInput } from "../hooks/useVoiceInput";
import VoiceInputButton from "./VoiceInputButton";

const API = "http://127.0.0.1:8000";

// Crop name to key mapping for consistent translation
const cropNameToKey = {
  'rice': 'rice',
  'wheat': 'wheat',
  'cotton': 'cotton',
  'tomato': 'tomato',
  'potato': 'potato',
  'onion': 'onion',
  'chilli': 'chilli',
  'chili': 'chilli', // Alternative spelling
  'turmeric': 'turmeric',
  'sugarcane': 'sugarcane',
  'groundnut': 'groundnut',
  'soyabean': 'soyabean',
  'soybean': 'soybean',
  'maize': 'maize',
  'gram': 'gram',
  'pulses': 'pulses',
  'gur': 'gur'
};

// District name translations
const districtTranslations = {
  'Hyderabad': { hi: 'हैदराबाद', te: 'హైదరాబాద్', ml: 'ഹൈദരാബാദ്' },
  'Rangareddy': { hi: 'रंगारेड्डी', te: 'రంగారెడ్డి', ml: 'രംഗാരെഡ്ഡി' },
  'Medchal-Malkajgiri': { hi: 'मेडचल-मल्काजगिरी', te: 'మెడ్చల్-మల్కాజ్‌గిరి', ml: 'മെഡ്‌ചാൽ-മൽകാജ്‌ഗിരി' },
  'Warangal': { hi: 'वारंगल', te: 'వారంగల్', ml: 'വാരംഖോൾ' },
  'Karimnagar': { hi: 'करीमनगर', te: 'కరీమ్‌నగర్', ml: 'കരിമ്നഗർ' },
  'Khammam': { hi: 'खम्मम', te: 'ఖమ్మం', ml: 'ഖമ്മാം' },
  'Nalgonda': { hi: 'नलगोंडा', te: 'నల్గొండ', ml: 'നാൽഗോണ്ട' },
  'Mahabubabad': { hi: 'महाबूबाबाद', te: 'మహాబూబాబాద్', ml: 'മഹാബൂബാബാദ്' },
  'Mancherial': { hi: 'मंचेरियल', te: 'మంచేరియల్', ml: 'മഞ്ചെരിയൽ' },
  'Tandur': { hi: 'तंडूर', te: 'తండూర్', ml: 'തണ്ടൂർ' }
};

export default function MarketPrices() {
  const { t, currentLanguage } = useLanguage();
  const { getCropName } = useTranslation();
  const [allPrices, setAllPrices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const { isListening, startVoiceInput } = useVoiceInput(currentLanguage);

  // Fetch ALL market prices on component mount
  useEffect(() => {
    fetchAllMarketPrices();
  }, []);

  const fetchAllMarketPrices = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/market-prices/top-districts`);
      if (!res.ok) {
        throw new Error(`API returned status ${res.status}`);
      }
      const data = await res.json();
      
      console.log("API Response:", data);
      console.log("Data entries:", data.data?.length || 0);
      
      const priceData = Array.isArray(data.data) ? data.data : [];
      setAllPrices(priceData);
      
      if (priceData.length === 0) {
        toast.warning("No market prices available");
      } else {
        toast.success(t("Market prices loaded"));
      }
    } catch (error) {
      console.error("Error fetching market prices:", error);
      toast.error(t("Failed to load market prices"));
    } finally {
      setLoading(false);
    }
  };

  // Get translated district name
  const getTranslatedDistrict = (districtName) => {
    if (currentLanguage === 'en') return districtName;
    return districtTranslations[districtName]?.[currentLanguage] || districtName;
  };

  // Get translated commodity name - improved logic
  const getTranslatedCommodity = (commodityName) => {
    if (!commodityName) return commodityName;
    
    // Convert to lowercase for lookup
    const lowerCommodity = commodityName.toLowerCase().trim();
    
    // Try direct lookup in mapping
    const cropKey = cropNameToKey[lowerCommodity] || lowerCommodity;
    
    // Get translation from crops.json via getCropName
    const translated = getCropName(cropKey);
    
    return translated || commodityName;
  };

  // Group data by district and get top 5 crops per district
  const groupedByDistrict = React.useMemo(() => {
    const grouped = {};
    
    allPrices.forEach(item => {
      const district = item.district;
      if (!grouped[district]) {
        grouped[district] = [];
      }
      grouped[district].push(item);
    });

    // Filter and sort: get top 5 commodities per district by modal price
    const result = [];
    Object.entries(grouped).forEach(([district, items]) => {
      const filtered = items.filter(item =>
        district.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.commodity.toLowerCase().includes(searchTerm.toLowerCase())
      );
      
      // Sort by modal price descending and take top 5
      filtered.sort((a, b) => b.modalPrice - a.modalPrice);
      result.push({
        district,
        crops: filtered.slice(0, 5)
      });
    });

    return result;
  }, [allPrices, searchTerm]);


  const getSortIndicator = (key) => {
    if (sortConfig.key !== key) return " ⇅";
    return sortConfig.direction === "asc" ? " ↑" : " ↓";
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-600 to-red-700 text-white p-6 rounded-2xl shadow-lg">
        <h2 className="text-3xl font-bold flex items-center gap-3 mb-2">
          <span>📊</span> {t("Market Prices")}
        </h2>
        <p className="text-orange-100">
          {t("Current commodity prices across all Telangana districts")}
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <button
            onClick={fetchAllMarketPrices}
            disabled={loading}
            className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
          >
            {loading ? `🔄 ${t("Loading")}...` : `🔄 ${t("Refresh Prices")}`}
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="flex gap-3">
        <input
          type="text"
          placeholder={`${t("Search")} ${t("district")} ${t("or")} ${t("commodity")}...`}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 px-4 py-2 border-2 border-orange-300 rounded-lg focus:outline-none focus:border-orange-600"
        />
        <VoiceInputButton
          isListening={isListening}
          onVoiceClick={() => startVoiceInput((text) => setSearchTerm(text))}
          size="md"
        />
      </div>

      {/* Loading State */}
      {loading && !allPrices.length ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="ml-3 text-gray-600">{t("Loading market prices...")}</span>
        </div>
      ) : groupedByDistrict.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          {t("No results found")}
        </div>
      ) : (
        // Cards Grid - Each district as a card with 5 crops
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {groupedByDistrict.map((districtData, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="border-2 border-orange-200 rounded-2xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow bg-white"
            >
              {/* District Card Header */}
              <div className="bg-gradient-to-r from-orange-500 to-red-600 text-white p-4">
                <h3 className="text-xl font-bold">
                  {getTranslatedDistrict(districtData.district)}
                </h3>
                <p className="text-sm text-orange-100">
                  {districtData.crops.length} {t("commodities available")}
                </p>
              </div>

              {/* Crops Grid (5 crops) */}
              <div className="p-4">
                <div className="grid grid-cols-1 gap-3">
                  {districtData.crops.map((crop, cropIdx) => (
                    <motion.div
                      key={cropIdx}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: cropIdx * 0.1 }}
                      className="bg-orange-50 border-l-4 border-orange-500 p-3 rounded hover:bg-orange-100 transition-colors"
                    >
                      <div className="flex justify-between items-start gap-2">
                        <div className="flex-1">
                          <p className="font-bold text-gray-900">
                            {getTranslatedCommodity(crop.commodity)}
                          </p>
                          <p className="text-xs text-gray-600 mt-1">
                            {t("Market")}: {crop.market}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-bold text-orange-700">
                            ₹{crop.modalPrice}
                          </p>
                          <p className="text-xs text-gray-600">
                            ₹{crop.minPrice} - ₹{crop.maxPrice}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Info Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4"
      >
        <p className="text-sm text-blue-900">
          <span className="font-semibold">💡 {t("Price Info")}:</span> Displaying top 5 commodities with highest modal prices per district. Prices updated from Agricultural Market Data.
        </p>
      </motion.div>
    </motion.div>
  );
}

