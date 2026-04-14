import React, { useState, useEffect } from "react";
import DiseaseForm from "./components/DiseaseForm";
import AdvisoryForm from "./components/AdvisoryForm";
import OrganicFarmingForm from "./components/OrganicFarmingForm";
import FarmerTools from "./components/FarmerTools";
import LanguageSelector from "./components/LanguageSelector";
import Header from "./components/Header";
import NavigationTabs from "./components/NavigationTabs";
import QueryHistory from "./components/QueryHistory";
import VoiceCapabilities from "./components/VoiceCapabilities";
import LanguageWrapper from "./components/LanguageWrapper";
import { Toaster } from "react-hot-toast";
import { LanguageProvider, useLanguage } from "./contexts/LanguageContext";
import { motion, AnimatePresence } from "framer-motion";

const FooterComponent = () => {
  const { t } = useLanguage();
  return (
    <footer className="bg-green-800 text-white py-8 mt-16">
      <div className="max-w-6xl mx-auto px-6 text-center">
        <h3 className="text-xl font-semibold mb-2">AgriVerse AI</h3>
        <p className="text-green-200">
          {t('Empowering Farmers with AI-Driven Insights and Guidance')}
        </p>
        <div className="mt-4 flex flex-wrap justify-center gap-x-4 gap-y-2 text-sm">
          <span>🌱 {t('Crop Disease Detection')}</span>
          <span>🌿 {t('Organic Farming')}</span>
          <span>📈 {t('Market Advisory')}</span>
          <span>🗣️ {t('Multilingual Support')}</span>
        </div>
      </div>
    </footer>
  );
};

export default function App() {
  const [activeTab, setActiveTab] = useState('disease');
  const [voiceCapabilities, setVoiceCapabilities] = useState(null);

  // Check voice capabilities on app load
  useEffect(() => {
    fetch('http://127.0.0.1:8000/languages')
      .then(res => res.json())
      .then(data => setVoiceCapabilities(data))
      .catch(err => console.error('Failed to load voice capabilities:', err));
  }, []);

  const tabs = [
    { id: 'disease', label: 'Disease Detection', icon: '🔬' },
    { id: 'advisory', label: 'Crop Advisory', icon: '🌾' },
    { id: 'organic', label: 'Organic Farming', icon: '🌿' },
    { id: 'tools', label: 'Farmer Tools', icon: '🛠️' },
    { id: 'history', label: 'Query History', icon: '📊' },
    { id: 'voice', label: 'Voice Settings', icon: '🎤' }
  ];

  return (
    <LanguageProvider>
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-indigo-50">
        <Toaster position="top-right" />
        
        <LanguageWrapper>
          {/* Header */}
          <Header />
          
          {/* Language Selector */}
          <div className="max-w-6xl mx-auto px-6">
            <LanguageSelector />
          </div>

          {/* Navigation Tabs */}
          <NavigationTabs 
            tabs={tabs} 
            activeTab={activeTab} 
            onTabChange={setActiveTab} 
          />

          {/* Main Content */}
          <div className="max-w-6xl mx-auto px-6 py-8">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0.8, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0.8, y: -10 }}
                transition={{ duration: 0.2, ease: "easeInOut" }}
                className="space-y-8"
              >
                {activeTab === 'disease' && <DiseaseForm />}
                {activeTab === 'advisory' && <AdvisoryForm />}
                {activeTab === 'organic' && <OrganicFarmingForm />}
                {activeTab === 'tools' && <FarmerTools />}
                {activeTab === 'history' && <QueryHistory />}
                {activeTab === 'voice' && (
                  <VoiceCapabilities capabilities={voiceCapabilities} />
                )}
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Footer */}
          <FooterComponent />
        </LanguageWrapper>
      </div>
    </LanguageProvider>
  );
}
