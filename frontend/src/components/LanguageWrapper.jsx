import React, { useEffect, useState } from 'react';
import { useLanguage } from '../contexts/LanguageContext';

const LanguageWrapper = ({ children }) => {
  const { currentLanguage } = useLanguage();
  const [forceRender, setForceRender] = useState(0);

  // Force re-render when language changes
  useEffect(() => {
    setForceRender(prev => prev + 1);
  }, [currentLanguage]);

  return (
    <div key={`lang-${currentLanguage}-${forceRender}`}>
      {children}
    </div>
  );
};

export default LanguageWrapper;