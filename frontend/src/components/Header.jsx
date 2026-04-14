import React, { useState, useEffect } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { motion, AnimatePresence } from 'framer-motion';

const Header = () => {
  const { t } = useLanguage();
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  
  // Array of background images from public folder
  const backgroundImages = [
    '/images/360_F_123709836_yl1Njg7BoOxOMCrINsseOWZvitaqfvjU.jpg',
    '/images/ai-generated-indian-female-farmer-working-in-her-field-bokeh-style-background-with-generative-ai-photo.jpeg',
    '/images/shutterstock_394940713.jpg',
    '/images/happyfarmer.jpg',
  ];

  // Auto-slide images every 2 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prevIndex) => (prevIndex + 1) % backgroundImages.length);
    }, 2000);

    return () => clearInterval(interval);
  }, [backgroundImages.length]);

  return (
    <motion.header 
      className="relative overflow-hidden text-white shadow-2xl h-96"
      initial={{ opacity: 0, y: -50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      {/* Background Images with Slideshow */}
      <div className="absolute inset-0 w-full h-full">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentImageIndex}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
            className="absolute inset-0 w-full h-full"
            style={{
              backgroundImage: `url(${backgroundImages[currentImageIndex]})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              backgroundRepeat: 'no-repeat',
            }}
          />
        </AnimatePresence>

        {/* Dark Overlay for Text Readability */}
        <div className="absolute inset-0 bg-black/50"></div>

        {/* Gradient Overlay for Better Text Contrast */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-black/30 to-black/50"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 h-full flex items-center max-w-6xl mx-auto px-6 w-full">
        <div className="text-center w-full">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            className="mb-4"
          >
            <div className="inline-flex items-center justify-center w-20 h-20 bg-white bg-opacity-20 rounded-full mb-4 backdrop-blur-sm border border-white/20">
              <span className="text-4xl">🌾</span>
            </div>
          </motion.div>
          
          <motion.h1 
            className="text-3xl md:text-4xl font-bold mb-2 drop-shadow-lg text-white"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            {t('AI Farmer Support')}
          </motion.h1>
          
          <motion.p 
            className="text-base md:text-lg text-white max-w-2xl mx-auto leading-relaxed drop-shadow-md mb-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            {t('subtitle')}
          </motion.p>
          
          <motion.div 
            className="flex flex-wrap justify-center gap-2 text-xs md:text-sm"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <div className="bg-white bg-opacity-90 backdrop-blur-sm px-3 py-1 rounded-full flex items-center border border-white/20 hover:bg-opacity-100 transition-all">
              <span className="mr-1">🔬</span>
              <span className="text-black font-medium">{t('AI Disease Detection')}</span>
            </div>
            <div className="bg-white bg-opacity-90 backdrop-blur-sm px-3 py-1 rounded-full flex items-center border border-white/20 hover:bg-opacity-100 transition-all">
              <span className="mr-1">📊</span>
              <span className="text-black font-medium">{t('Market Intelligence')}</span>
            </div>
            <div className="bg-white bg-opacity-90 backdrop-blur-sm px-3 py-1 rounded-full flex items-center border border-white/20 hover:bg-opacity-100 transition-all">
              <span className="mr-1">🎙️</span>
              <span className="text-black font-medium">{t('Voice Support')}</span>
            </div>
            <div className="bg-white bg-opacity-90 backdrop-blur-sm px-3 py-1 rounded-full flex items-center border border-white/20 hover:bg-opacity-100 transition-all">
              <span className="mr-1">🌍</span>
              <span className="text-black font-medium">{t('Multilingual')}</span>
            </div>
          </motion.div>

          {/* Image Indicators */}
          <motion.div 
            className="mt-4 flex justify-center gap-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
          >
            {backgroundImages.map((_, index) => (
              <motion.button
                key={index}
                onClick={() => setCurrentImageIndex(index)}
                className={`w-2 h-2 rounded-full transition-all duration-300 ${
                  index === currentImageIndex 
                    ? 'bg-white w-6' 
                    : 'bg-white/40 hover:bg-white/60'
                }`}
                whileHover={{ scale: 1.2 }}
                whileTap={{ scale: 0.9 }}
              />
            ))}
          </motion.div>
        </div>
      </div>
      
      {/* Decorative wave at bottom */}
      <div className="absolute bottom-0 left-0 right-0 z-10">
        <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="relative block w-full h-6 md:h-8">
          <path d="M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V0H0V27.35A600.21,600.21,0,0,0,321.39,56.44Z" 
                className="fill-green-50"></path>
        </svg>
      </div>
    </motion.header>
  );
};

export default Header;