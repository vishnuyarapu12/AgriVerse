import React from 'react';
import { motion } from 'framer-motion';
import { useLanguage } from '../contexts/LanguageContext';

const NavigationTabs = ({ tabs, activeTab, onTabChange }) => {
  const { t } = useLanguage();

  return (
    <div className="max-w-6xl mx-auto px-6 py-4">
      <div className="flex flex-wrap justify-center gap-2 bg-white rounded-xl shadow-lg p-2">
        {tabs.map((tab) => (
          <motion.button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`relative px-6 py-3 rounded-lg font-medium text-sm transition-all duration-200 flex items-center space-x-2 ${
              activeTab === tab.id
                ? 'text-white bg-gradient-to-r from-green-600 to-green-700 shadow-md'
                : 'text-gray-600 hover:text-green-600 hover:bg-green-50'
            }`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <span className="text-lg">{tab.icon}</span>
            <span>{t(tab.label)}</span>
            {activeTab === tab.id && (
              <motion.div
                layoutId="activeTab"
                className="absolute inset-0 bg-gradient-to-r from-green-600 to-green-700 rounded-lg -z-10"
                initial={false}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
              />
            )}
          </motion.button>
        ))}
      </div>
    </div>
  );
};

export default NavigationTabs;