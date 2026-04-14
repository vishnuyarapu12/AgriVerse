import React, { useEffect, useState } from 'react';
import { useLanguage } from '../contexts/LanguageContext';

const LanguageWrapper = ({ children }) => {
  // Use context for language-driven translation labels, but do not remount every time.
  return <div>{children}</div>;
};

export default LanguageWrapper;