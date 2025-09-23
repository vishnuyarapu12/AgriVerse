import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { motion } from 'framer-motion';

const Header = () => {
  const { t } = useLanguage();

  return (
    <motion.header 
      className="bg-gradient-to-r from-green-600 via-green-700 to-green-800 text-white shadow-2xl"
      initial={{ opacity: 0, y: -50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            className="mb-4"
          >
            <div className="inline-flex items-center justify-center w-20 h-20 bg-white bg-opacity-20 rounded-full mb-4">
              <span className="text-4xl">🌾</span>
            </div>
          </motion.div>
          
          <motion.h1 
            className="text-4xl md:text-5xl font-bold mb-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            {t('AI Farmer Query Support')}
          </motion.h1>
          
          <motion.p 
            className="text-lg md:text-xl text-green-100 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            {t('subtitle')}
          </motion.p>
          
          <motion.div 
            className="mt-6 flex flex-wrap justify-center gap-4 text-sm"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <div className="bg-white bg-opacity-15  px-4 py-2 rounded-full flex items-center">
              <span className="mr-2">🔬</span>
              <span className="text-black font-medium">{t('AI Disease Detection')}</span>
            </div>
            <div className="bg-white bg-opacity-15 px-4 py-2 rounded-full flex items-center">
              <span className="mr-2">📊</span>
              <span className="text-black font-medium">{t('Market Intelligence')}</span>
            </div>
            <div className="bg-white bg-opacity-15 px-4 py-2 rounded-full flex items-center">
              <span className="mr-2">🎙️</span>
              <span className="text-black font-medium">{t('Voice Support')}</span>
            </div>
            <div className="bg-white bg-opacity-15 px-4 py-2 rounded-full flex items-center">
              <span className="mr-2">🌍</span>
              <span className="text-black font-medium">{t('Multilingual')}</span>
            </div>
          </motion.div>
        </div>
      </div>
      
      {/* Decorative wave at bottom */}
      <div className="relative">
        <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="relative block w-full h-8">
          <path d="M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V0H0V27.35A600.21,600.21,0,0,0,321.39,56.44Z" 
                className="fill-green-50"></path>
        </svg>
      </div>
    </motion.header>
  );
};

export default Header;