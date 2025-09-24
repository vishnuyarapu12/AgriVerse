import React, { createContext, useContext, useState, useEffect } from 'react';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

// Translation data
const translations = {
  en: {
    // Navigation
    'Disease Detection': 'Disease Detection',
    'Crop Advisory': 'Crop Advisory',
    'Query History': 'Query History',
    'Voice Settings': 'Voice Settings',
    
    // Headers
    'AI Farmer Support': 'AI Farmer Support - AgriVerse',
    'Welcome to AgriVerse': 'Welcome to AgriVerse',
    'subtitle': 'Your AI-powered agricultural advisor for crop disease detection, farming guidance, and market insights',
    
    // Disease Detection
    'Upload Image': 'Upload Crop Image',
    'Enter Query': 'Describe your crop problem',
    'Voice Input': '🎤 Voice Input',
    'Submit': 'Analyze',
    'Language': 'Language',
    'Select Language': 'Select Language',
    
    // Advisory Form
    'Crop Name': 'Crop Name',
    'Location': 'Location',
    'Soil Type': 'Soil Type',
    'Additional Query': 'Additional Questions',
    'Get Advice': 'Get Advisory',
    
    // Placeholders
    'Enter crop name': 'Enter crop name (e.g., Tomato, Wheat, Rice)',
    'Enter location': 'Enter your location (e.g., Punjab, Maharashtra)',
    'Select soil type': 'Select your soil type',
    'Enter additional questions': 'Ask about fertilizers, weather, market prices...',
    'Describe crop problem': 'Describe what you observe in your crops...',
    
    // Soil types
    'Alluvial': 'Alluvial',
    'Black': 'Black (Regur)',
    'Red': 'Red',
    'Laterite': 'Laterite',
    'Sandy': 'Sandy',
    'Clay': 'Clay',
    'Loamy': 'Loamy',
    
    // Response Card
    'AI Response': 'AI Advisory Response',
    'Prediction': 'Disease Prediction',
    'Confidence': 'Confidence Level',
    'Advisory': 'Treatment Advisory',
    'Play Audio': '🔊 Play Audio Response',
    'Feedback': 'Was this helpful?',
    'Thumbs Up': '👍 Helpful',
    'Thumbs Down': '👎 Not Helpful',
    
    // History
    'Recent Queries': 'Recent Queries',
    'No History': 'No query history available',
    'Clear History': 'Clear History',
    
    // Voice
    'Voice Capabilities': 'Voice Input/Output Capabilities',
    'Speech Recognition': 'Speech Recognition',
    'Text to Speech': 'Text to Speech',
    'Supported Languages': 'Supported Languages',
    'Available': 'Available',
    'Not Available': 'Not Available',
    
    // Error Messages
    'Error': 'Error',
    'No file selected': 'Please upload an image or enter text',
    'API Error': 'Service temporarily unavailable. Please try again.',
    'Voice not supported': 'Voice input not supported in this browser',
    
    // Header Feature Tags
    'AI Disease Detection': 'AI Disease Detection',
    'Market Intelligence': 'Market Intelligence', 
    'Voice Support': 'Voice Support',
    'Multilingual': 'Multilingual',
    
    // Footer
    'Empowering Farmers with AI-Driven Insights and Guidance': 'Empowering Farmers with AI-Driven Insights and Guidance',
    'Crop Disease Detection': 'Crop Disease Detection',
    'Market Advisory': 'Market Advisory',
    'Multilingual Support': 'Multilingual Support',
  },
  
  hi: {
    // Navigation
    'Disease Detection': 'रोग जांच',
    'Crop Advisory': 'फसल सलाह',
    'Query History': 'प्रश्न इतिहास',
    'Voice Settings': 'आवाज सेटिंग्स',
    
    // Headers  
    'AI Farmer Support': 'AI किसान सहायता - एग्रीवर्स',
    'Welcome to AgriVerse': 'एग्रीवर्स में आपका स्वागत है',
    'subtitle': 'फसल रोग पहचान, खेती मार्गदर्शन और बाजार जानकारी के लिए आपका AI-संचालित कृषि सलाहकार',
    
    // Disease Detection
    'Upload Image': 'फसल की तस्वीर अपलोड करें',
    'Enter Query': 'अपनी फसल की समस्या बताएं',
    'Voice Input': '🎤 आवाज इनपुट',
    'Submit': 'विश्लेषण करें',
    'Language': 'भाषा',
    'Select Language': 'भाषा चुनें',
    
    // Advisory Form
    'Crop Name': 'फसल का नाम',
    'Location': 'स्थान',
    'Soil Type': 'मिट्टी का प्रकार',
    'Additional Query': 'अतिरिक्त प्रश्न',
    'Get Advice': 'सलाह प्राप्त करें',
    
    // Placeholders
    'Enter crop name': 'फसल का नाम दर्ज करें (जैसे टमाटर, गेहूं, चावल)',
    'Enter location': 'अपना स्थान दर्ज करें (जैसे पंजाब, महाराष्ट्र)',
    'Select soil type': 'अपनी मिट्टी का प्रकार चुनें',
    'Enter additional questions': 'उर्वरक, मौसम, बाजार की कीमतों के बारे में पूछें...',
    'Describe crop problem': 'अपनी फसलों में जो देख रहे हैं उसका वर्णन करें...',
    
    // Soil types
    'Alluvial': 'जलोढ़',
    'Black': 'काली (रेगुर)',
    'Red': 'लाल',
    'Laterite': 'लेटराइट',
    'Sandy': 'रेतीली',
    'Clay': 'चिकनी',
    'Loamy': 'दोमट',
    
    // Response Card
    'AI Response': 'AI सलाह उत्तर',
    'Prediction': 'रोग पूर्वानुमान',
    'Confidence': 'विश्वास स्तर',
    'Advisory': 'उपचार सलाह',
    'Play Audio': '🔊 ऑडियो उत्तर सुनें',
    'Feedback': 'क्या यह सहायक था?',
    'Thumbs Up': '👍 सहायक',
    'Thumbs Down': '👎 सहायक नहीं',
    
    // History
    'Recent Queries': 'हाल की क्वेरीज़',
    'No History': 'कोई क्वेरी इतिहास उपलब्ध नहीं',
    'Clear History': 'इतिहास साफ़ करें',
    
    // Voice
    'Voice Capabilities': 'आवाज इनपुट/आउटपुट क्षमताएं',
    'Speech Recognition': 'भाषण पहचान',
    'Text to Speech': 'टेक्स्ट टू स्पीच',
    'Supported Languages': 'समर्थित भाषाएं',
    'Available': 'उपलब्ध',
    'Not Available': 'उपलब्ध नहीं',
    
    // Error Messages
    'Error': 'त्रुटि',
    'No file selected': 'कृपया एक तस्वीर अपलोड करें या टेक्स्ट दर्ज करें',
    'API Error': 'सेवा अस्थायी रूप से अनुपलब्ध है। कृपया पुनः प्रयास करें।',
    'Voice not supported': 'इस ब्राउज़र में आवाज इनपुट समर्थित नहीं है',
    
    // Header Feature Tags
    'AI Disease Detection': 'AI रोग पहचान',
    'Market Intelligence': 'बाजार बुद्धिमत्ता',
    'Voice Support': 'आवाज समर्थन',
    'Multilingual': 'बहुभाषी',
    
    // Footer
    'Empowering Farmers with AI-Driven Insights and Guidance': 'AI-संचालित अंतर्दृष्टि और मार्गदर्शन के साथ किसानों को सशक्त बनाना',
    'Crop Disease Detection': 'फसल रोग पहचान',
    'Market Advisory': 'बाजार सलाह',
    'Multilingual Support': 'बहुभाषी समर्थन',
  },
  
  ml: {
    // Navigation
    'Disease Detection': 'രോഗ നിർണ്ണയം',
    'Crop Advisory': 'വിള ഉപദേശം',
    'Query History': 'ചോദ്യ ചരിത്രം',
    'Voice Settings': 'വോയ്സ് സെറ്റിംഗുകൾ',
    
    // Headers
    'AI Farmer Support': 'AI കർഷക പിന്തുണ - അഗ്രിവേഴ്സ്',
    'Welcome to AgriVerse': 'അഗ്രിവേഴ്സിലേക്ക് സ്വാഗതം',
    'subtitle': 'വിള രോഗ നിർണ്ണയം, കാർഷിക മാർഗദർശനം, മാർക്കറ്റ് അന്തർദൃഷ്ടികൾ എന്നിവയ്ക്കായി നിങ്ങളുടെ AI-നിയന്ത്രിത കാർഷിക ഉപദേഷ്ടാവ്',
    
    // Disease Detection
    'Upload Image': 'വിള ചിത്രം അപ്‌ലോഡ് ചെയ്യുക',
    'Enter Query': 'നിങ്ങളുടെ വിള പ്രശ്നം വിവരിക്കുക',
    'Voice Input': '🎤 വോയ്സ് ഇൻപുട്ട്',
    'Submit': 'വിശകലനം ചെയ്യുക',
    'Language': 'ഭാഷ',
    'Select Language': 'ഭാഷ തിരഞ്ഞെടുക്കുക',
    
    // Advisory Form
    'Crop Name': 'വിളയുടെ പേര്',
    'Location': 'സ്ഥലം',
    'Soil Type': 'മണ്ണിന്റെ തരം',
    'Additional Query': 'അധിക ചോദ്യങ്ങൾ',
    'Get Advice': 'ഉപദേശം നേടുക',
    
    // Placeholders
    'Enter crop name': 'വിളയുടെ പേര് നൽകുക (ഉദാ: ടൊമാറ്റോ, ഗോതമ്പ്, അരി)',
    'Enter location': 'നിങ്ങളുടെ സ്ഥലം നൽകുക (ഉദാ: പഞ്ചാബ്, മഹാരാഷ്ട്ര)',
    'Select soil type': 'നിങ്ങളുടെ മണ്ണിന്റെ തരം തിരഞ്ഞെടുക്കുക',
    'Enter additional questions': 'വളങ്ങൾ, കാലാവസ്ഥ, മാർക്കറ്റ് വിലകൾ എന്നിവയെക്കുറിച്ച് ചോദിക്കുക...',
    'Describe crop problem': 'നിങ്ങളുടെ വിളകളിൽ നിങ്ങൾ നിരീക്ഷിക്കുന്നത് വിവരിക്കുക...',
    
    // Soil types
    'Alluvial': 'അലൂവിയൽ',
    'Black': 'കറുത്ത (റെഗർ)',
    'Red': 'ചുവപ്പ്',
    'Laterite': 'ലാറ്ററൈറ്റ്',
    'Sandy': 'മണൽ',
    'Clay': 'കളിമണ്ണ്',
    'Loamy': 'ചെളി',
    
    // Response Card
    'AI Response': 'AI ഉപദേശ പ്രതികരണം',
    'Prediction': 'രോഗ പ്രവചനം',
    'Confidence': 'ആത്മവിശ്വാസ നില',
    'Advisory': 'ചികിത്സാ ഉപദേശം',
    'Play Audio': '🔊 ഓഡിയോ പ്രതികരണം കേൾക്കുക',
    'Feedback': 'ഇത് സഹായകരമായിരുന്നുവോ?',
    'Thumbs Up': '👍 സഹായകരം',
    'Thumbs Down': '👎 സഹായകരമല്ല',
    
    // History
    'Recent Queries': 'സമീപകാല ചോദ്യങ്ങൾ',
    'No History': 'ചോദ്യ ചരിത്രം ലഭ്യമല്ല',
    'Clear History': 'ചരിത്രം മായ്ക്കുക',
    
    // Voice
    'Voice Capabilities': 'വോയ്സ് ഇൻപുട്ട്/ഔട്ട്പുട്ട് കഴിവുകൾ',
    'Speech Recognition': 'സ്പീച്ച് റെക്കഗ്നിഷൻ',
    'Text to Speech': 'ടെക്സ്റ്റ് ടു സ്പീച്ച്',
    'Supported Languages': 'പിന്തുണയുള്ള ഭാഷകൾ',
    'Available': 'ലഭ്യമാണ്',
    'Not Available': 'ലഭ്യമല്ല',
    
    // Error Messages
    'Error': 'പിശക്',
    'No file selected': 'ദയവായി ഒരു ചിത്രം അപ്‌ലോഡ് ചെയ്യുക അല്ലെങ്കിൽ ടെക്സ്റ്റ് നൽകുക',
    'API Error': 'സേവനം താൽക്കാലികമായി ലഭ്യമല്ല. ദയവായി വീണ്ടും ശ്രമിക്കുക.',
    'Voice not supported': 'ഈ ബ്രൗസറിൽ വോയ്സ് ഇൻപുട്ട് പിന്തുണയില്ല',
    
    // Header Feature Tags
    'AI Disease Detection': 'AI രോഗ നിർണ്ണയം',
    'Market Intelligence': 'മാർക്കറ്റ് ബുദ്ധി',
    'Voice Support': 'വോയ്സ് പിന്തുണ',
    'Multilingual': 'ബഹുഭാഷാ',
    
    // Footer
    'Empowering Farmers with AI-Driven Insights and Guidance': 'AI-നിയന്ത്രിത അന്തർദൃഷ്ടികളും മാർഗദർശനവും ഉപയോഗിച്ച് കർഷകരെ ശാക്തീകരിക്കുന്നു',
    'Crop Disease Detection': 'വിള രോഗ നിർണ്ണയം',
    'Market Advisory': 'മാർക്കറ്റ് ഉപദേശം',
    'Multilingual Support': 'ബഹുഭാഷാ പിന്തുണ',
  },
  
  te: {
    // Navigation
    'Disease Detection': 'వ్యాధి గుర్తింపు',
    'Crop Advisory': 'పంట సలహా',
    'Query History': 'ప్రశ్న చరిత్ర',
    'Voice Settings': 'వాయిస్ సెట్టింగ్లు',
    
    // Headers
    'AI Farmer Support': 'AI రైతు మద్దతు - అగ్రివర్స్',
    'Welcome to AgriVerse': 'అగ్రివర్స్‌కు స్వాగతం',
    'subtitle': 'పంట వ్యాధుల గుర్తింపు, వ్యవసాయ మార్గదర్శకత్వం మరియు మార్కెట్ అంతర్దృష్టుల కోసం మీ AI-శక్తితో కూడిన వ్యవసాయ సలహాదారు',
    
    // Disease Detection
    'Upload Image': 'పంట చిత్రాన్ని అప్‌లోడ్ చేయండి',
    'Enter Query': 'మీ పంట సమస్యను వివరించండి',
    'Voice Input': '🎤 వాయిస్ ఇన్‌పుట్',
    'Submit': 'విశ్లేషణ చేయండి',
    'Language': 'భాష',
    'Select Language': 'భాష ఎంచుకోండి',
    
    // Advisory Form
    'Crop Name': 'పంట పేరు',
    'Location': 'స్థానం',
    'Soil Type': 'నేల రకం',
    'Additional Query': 'అదనపు ప్రశ్నలు',
    'Get Advice': 'సలహా పొందండి',
    
    // Placeholders
    'Enter crop name': 'పంట పేరు ఎంటర్ చేయండి (ఉదా: టమాటో, గోధుమలు, వరి)',
    'Enter location': 'మీ స్థానాన్ని ఎంటర్ చేయండి (ఉదా: పంజాబ్, మహారాష్ట్ర)',
    'Select soil type': 'మీ నేల రకాన్ని ఎంచుకోండి',
    'Enter additional questions': 'ఎరువులు, వాతావరణం, మార్కెట్ ధరల గురించి అడగండి...',
    'Describe crop problem': 'మీ పంటలలో మీరు గమనించిన వాటిని వివరించండి...',
    
    // Soil types
    'Alluvial': 'అలూవియల్',
    'Black': 'నల్ల (రేగుర్)',
    'Red': 'ఎరుపు',
    'Laterite': 'లాటరైట్',
    'Sandy': 'ఇసుక',
    'Clay': 'మట్టి',
    'Loamy': 'లోమీ',
    
    // Response Card
    'AI Response': 'AI సలహా సమాధానం',
    'Prediction': 'వ్యాధి అంచనా',
    'Confidence': 'విశ్వాస స్థాయి',
    'Advisory': 'చికిత్స సలహా',
    'Play Audio': '🔊 ఆడియో సమాధానం వినండి',
    'Feedback': 'ఇది సహాయకరమైందా?',
    'Thumbs Up': '👍 సహాయకరం',
    'Thumbs Down': '👎 సహాయకరం కాదు',
    
    // History
    'Recent Queries': 'ఇటీవలి ప్రశ్నలు',
    'No History': 'ప్రశ్న చరిత్ర అందుబాటులో లేదు',
    'Clear History': 'చరిత్రను తుడిచివేయండి',
    
    // Voice
    'Voice Capabilities': 'వాయిస్ ఇన్‌పుట్/అవుట్‌పుట్ సామర్థ్యాలు',
    'Speech Recognition': 'స్పీచ్ రికగ్నిషన్',
    'Text to Speech': 'టెక్స్ట్ టు స్పీచ్',
    'Supported Languages': 'మద్దతు ఉన్న భాషలు',
    'Available': 'అందుబాటులో ఉంది',
    'Not Available': 'అందుబాటులో లేదు',
    
    // Error Messages
    'Error': 'లోపం',
    'No file selected': 'దయచేసి ఒక చిత్రాన్ని అప్‌లోడ్ చేయండి లేదా టెక్స్ట్‌ను నమోదు చేయండి',
    'API Error': 'సేవ తాత్కాలికంగా అందుబాటులో లేదు. దయచేసి మళ్లీ ప్రయత్నించండి.',
    'Voice not supported': 'ఈ బ్రౌజర్‌లో వాయిస్ ఇన్‌పుట్ మద్దతు లేదు',
    
    // Header Feature Tags
    'AI Disease Detection': 'AI వ్యాధి గుర్తింపు',
    'Market Intelligence': 'మార్కెట్ బుద్ధిమత్త',
    'Voice Support': 'వాయిస్ మద్దతు',
    'Multilingual': 'బహుభాషా',
    
    // Footer
    'Empowering Farmers with AI-Driven Insights and Guidance': 'AI-లతో అంతర్దృష్టిలు మరియు మార్గదర్శనత్వంతో రైతులను సశక్తీకరణ',
    'Crop Disease Detection': 'పంట వ్యాధి గుర్తింపు',
    'Market Advisory': 'మార్కెట్ సలహా',
    'Multilingual Support': 'బహుభాషా మద్దతు',
  }
};

export const LanguageProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const [availableLanguages, setAvailableLanguages] = useState([]);

  // Load available languages from backend
  useEffect(() => {
    fetch('http://127.0.0.1:8000/languages')
      .then(res => res.json())
      .then(data => {
        if (data.languages) {
          setAvailableLanguages(data.languages);
        }
      })
      .catch(err => {
        console.error('Failed to load languages:', err);
        // Fallback to default languages
        setAvailableLanguages([
          { code: 'en', name: 'English' },
          { code: 'hi', name: 'हिंदी (Hindi)' },
          { code: 'ml', name: 'മലയാളം (Malayalam)' },
          { code: 'te', name: 'తెలుగు (Telugu)' }
        ]);
      });
  }, []);

  const translate = (key) => {
    const translation = translations[currentLanguage]?.[key] || translations['en'][key] || key;
    // Uncomment for debugging:
    // console.log(`Translating '${key}' to '${translation}' in language '${currentLanguage}'`);
    return translation;
  };

  const changeLanguage = (languageCode) => {
    console.log(`Changing language from ${currentLanguage} to ${languageCode}`);
    setCurrentLanguage(languageCode);
    // Save preference to localStorage
    localStorage.setItem('agriverse_language', languageCode);
    
    // Force a small delay to ensure state updates
    setTimeout(() => {
      console.log(`Language changed to: ${languageCode}`);
    }, 100);
  };

  // Load saved language preference on component mount
  useEffect(() => {
    const savedLanguage = localStorage.getItem('agriverse_language');
    if (savedLanguage && translations[savedLanguage]) {
      setCurrentLanguage(savedLanguage);
    }
  }, []);

  const value = {
    currentLanguage,
    availableLanguages,
    translate,
    changeLanguage,
    t: translate // Shorthand for translate
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};