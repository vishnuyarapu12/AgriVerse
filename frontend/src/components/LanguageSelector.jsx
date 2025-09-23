import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { motion } from 'framer-motion';

const LanguageSelector = () => {
  const { currentLanguage, availableLanguages, changeLanguage, t } = useLanguage();

  return (
    <motion.div 
      className="flex justify-end py-4"
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.3 }}
    >
      <div className="flex items-center space-x-3 bg-white rounded-lg shadow-md px-4 py-2">
        <span className="text-sm font-medium text-gray-700">
          {t('Language')}:
        </span>
        <select
          value={currentLanguage}
          onChange={(e) => changeLanguage(e.target.value)}
          className="text-sm border-0 bg-transparent focus:ring-2 focus:ring-green-500 rounded-md font-medium text-green-700 cursor-pointer"
        >
          {availableLanguages.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
        <div className="text-lg">🌍</div>
      </div>
    </motion.div>
  );
};

export default LanguageSelector;