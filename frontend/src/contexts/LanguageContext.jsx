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
    'Organic Farming': 'Organic Farming',
    'Organic Farming subtitle': 'Sustainable, chemical-free methods tailored for Telangana',
    'Get Organic Guide': 'Get Organic Guide',
    'Generating organic guide': 'Generating guide...',
    'Organic guide ready': 'Guide ready',
    'Organic crop required': 'Please enter a crop name',
    'Organic location hint': 'Defaults to Telangana; add your district if needed',
    'Organic techniques': 'Organic farming techniques',
    
    // Quick Crops for Organic Farming
    'Rice': 'Rice',
    'Cotton': 'Cotton',
    'Tomato': 'Tomato',
    'Potato': 'Potato',
    'Maize': 'Maize',
    'Chilli': 'Chilli',
    'Groundnut': 'Groundnut',
    
    'Farmer Tools': 'Farmer Tools',
    'Weather & spray': 'Weather & spray safety',
    'Weather spray hint': 'Live weather for your area — know if it is safe to spray',
    'Enter city': 'Enter a city name',
    'Get weather': 'Get weather',
    'Weather loaded': 'Weather loaded',
    'Spray advice': 'Spray advice',
    'One-tap solution': 'One-tap solution card',
    'Solution hint': 'Quick medicine, dosage, and timing (demo data)',
    'Get solution': 'Get solution',
    'Solution loaded': 'Solution loaded',
    'Disease': 'Disease',
    'Medicine': 'Medicine',
    'Dosage': 'Dosage',
    'Time': 'Time',
    'Note': 'Note',
    'Field reminder': 'Field reminder',
    'Reminder hint': 'Server will log REMINDER after the delay (check backend console)',
    'Reminder placeholder': 'e.g. Check drip irrigation in plot B',
    'Delay seconds': 'Delay (seconds)',
    'Schedule reminder': 'Schedule reminder',
    'Scheduled': 'Scheduled',
    'Reminder message required': 'Enter a reminder message',
    'Reminder scheduled': 'Reminder scheduled',
    'Weather GPS hint': 'Uses your phone location automatically — 5-day outlook like the weather app',
    'Refresh location weather': 'Update weather',
    'Use GPS instead': 'Use my location',
    'Search city instead': 'Search by city',
    'Location denied banner': 'Location access is off. Enable it in the browser or search by city.',
    'Geolocation not supported': 'Geolocation is not available in this browser',
    'Location denied hint': 'Allow location access for automatic weather, or use city search.',
    'Loading weather': 'Loading weather…',
    'Feels like': 'Feels like',
    'Humidity': 'Humidity',
    'Wind': 'Wind',
    'Five day forecast': '5-day forecast',
    'City mode no forecast': 'Search mode shows today only. Use “Use my location” for the full 5-day outlook.',
    'Telangana brands title': 'Popular brands in Telangana',
    'Telangana brands subtitle': 'Common crop inputs — always follow label & dealer advice',
    'Brands loading': 'Loading brand list…',
    'Weather openmeteo hint': 'Open-Meteo (free) — GPS or Hyderabad if location is off',
    'Hyderabad default weather': 'Hyderabad (default)',
    'Using Hyderabad default': 'Showing weather for Hyderabad (Telangana) — allow location for your area.',
    'Current conditions': 'Current conditions',
    'Wind speed': 'Wind speed',
    'OpenMeteo wind note': 'Wind in km/h (10 m). Advice: rain code → no spray; wind > 20 → high wind.',
    
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
    'Select soil type': 'Select soil type',
    
    // Farming Seasons
    'Farming Season': 'Farming Season',
    'Kharif (Monsoon)': 'Kharif (Monsoon)',
    'Rabi (Winter)': 'Rabi (Winter)',
    'Summer': 'Summer',
    'Spring': 'Spring',
    'Select current season': 'Select current season',
    
    // Response Card
    'AI Response': 'AI Advisory Response',
    'Prediction': 'Disease Prediction',
    'Confidence': 'Confidence Level',
    'Advisory': 'Treatment Advisory',
    'Play Audio': '🔊 Play Audio Response',
    'Feedback': 'Was this helpful?',
    'Thumbs Up': '👍 Helpful',
    'Thumbs Down': '👎 Not Helpful',
    
    // Advisory Form Additional
    'Crop Advisory subtitle': 'Get comprehensive farming guidance and market insights',
    'Farming Advisory': 'Farming Advisory',
    'Recommended Crop Options': 'Recommended Crop Options',
    'Based on': 'Based on',
    'soil': 'soil',
    'and': 'and',
    'Choose your current farming season for better recommendations': 'Choose your current farming season for better recommendations',
    'Generating audio in background...': 'Generating audio in background...',
    'Audio ready! Click play button to listen': 'Audio ready! Click play button to listen',
    'Streaming audio - starts playing as it generates...': 'Streaming audio - starts playing as it generates...',
    '✨ Audio ready! Click play to listen': '✨ Audio ready! Click play to listen',
    'Playing audio...': 'Playing audio...',
    
    // Playback Speed Controls
    'Playback Speed': 'Playback Speed',
    '0.5x': '0.5x (Slow)',
    '0.75x': '0.75x',
    '1x': '1x (Normal)',
    '1.25x': '1.25x',
    '1.5x': '1.5x (Fast)',
    '2x': '2x (Very Fast)',
    
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
    
    // Messages and Alerts
    'Listening... Please speak now': 'Listening... Please speak now',
    'Analyzing crop disease...': 'Analyzing crop disease...',
    'Voice captured successfully!': 'Voice captured successfully!',
    'Generating audio...': 'Generating audio...',
    'Playing audio response': 'Playing audio response',
    'Disease analysis completed!': 'Disease analysis completed!',
    'Listening...': 'Listening...',
    'Analyzing...': 'Analyzing...',
    'Please fill in all fields': 'Please fill in all fields',
    'Getting agricultural advisory...': 'Getting agricultural advisory...',
    'Advisory generated successfully!': 'Advisory generated successfully!',
    'Generating guide...': 'Generating guide...',
    'Show Less': 'Show Less',
    'Read More': 'Read More',
    'Thank you for your feedback!': 'Thank you for your feedback!',
    'Failed to submit feedback': 'Failed to submit feedback',
    'Audio generation failed': 'Audio generation failed',
    'Playing audio advisory': 'Playing audio advisory',
    'TTS failed': 'TTS failed',
    'Generating test audio...': 'Generating test audio...',
    'Test Voice Input': 'Test Voice Input',
    'Test Voice Output': 'Test Voice Output',
    'No advisory available': 'No advisory available',
    'Voice recognition error. Please try again.': 'Voice recognition error. Please try again.',
    'Please enter some text to test voice output': 'Please enter some text to test voice output',
    'Browser Support:': 'Browser Support:',
    'Google TTS': 'Google TTS',
    'Currently Active': 'Currently Active',
    'Test Voice Features': 'Test Voice Features',
    'Voice Input Test': 'Voice Input Test',
    'Voice Output Test': 'Voice Output Test',
    'Convert your voice into text for queries and commands.': 'Convert your voice into text for queries and commands.',
    'Listen to AI responses in your preferred language.': 'Listen to AI responses in your preferred language.',
    'Service:': 'Service:',
    'Captured': 'Captured',
    'Tips for Better Voice Experience': 'Tips for Better Voice Experience',
    'Speak clearly and at a normal pace': 'Speak clearly and at a normal pace',
    'Ensure you are in a quiet environment for better recognition': 'Ensure you are in a quiet environment for better recognition',
    'Allow microphone access when prompted by your browser': 'Allow microphone access when prompted by your browser',
    'Voice input works best in Chrome, Edge, and Safari browsers': 'Voice input works best in Chrome, Edge, and Safari browsers',
    'Audio output supports all major languages for farming guidance': 'Audio output supports all major languages for farming guidance',
    'View query history': 'View your recent disease detections and advisory queries',
    'History empty message': 'Your query history will appear here once you start using the disease detection or advisory features.',
    
    // Market Prices
    'Market Prices': 'Market Prices',
    'Current commodity prices across top 10 Telangana districts': 'Current commodity prices across all Telangana districts',
    'Current commodity prices across all Telangana districts': 'Current commodity prices across all Telangana districts',
    'Loading market prices...': 'Loading market prices...',
    'All Commodity Prices': 'All Commodity Prices',
    'District Summary': 'District Summary',
    'Average prices across commodities': 'Average prices across commodities',
    'District': 'District',
    'Avg Modal ₹': 'Avg Modal ₹',
    'Commodities': 'Commodities',
    'Action': 'Action',
    'View': 'View',
    'commodities available': 'commodities available',
    'Commodity': 'Commodity',
    'Modal ₹': 'Modal ₹',
    'Range': 'Range',
    'Market': 'Market',
    'Min ₹': 'Min ₹',
    'Max ₹': 'Max ₹',
    'Select a district to view commodities': 'Select a district to view commodities',
    'Price Info': 'Price Info',
    'Prices updated from Agriculture Market Data (data.gov.in). Click on column headers to sort. Use search to filter by district or commodity.': 'Prices updated from Agriculture Market Data (data.gov.in). Click on column headers to sort. Use search to filter by district or commodity.',
    'Prices updated from Agriculture Market Data (data.gov.in). Click on any district to view detailed commodity prices including min, max, and modal prices.': 'Prices updated from Agriculture Market Data (data.gov.in). Click on any district to view detailed commodity prices including min, max, and modal prices.',
    'Min Avg': 'Min Avg',
    'Max Avg': 'Max Avg',
    'Min Price': 'Min Price',
    'Max Price': 'Max Price',
    'Failed to load details for': 'Failed to load details for',
    'Search': 'Search',
    'or': 'or',
    'entries': 'entries',
    'No results found': 'No results found',
    
    // Additional Market Prices & Buttons
    'Refresh': 'Refresh',
    'Refresh Prices': 'Refresh Prices',
    'Loading': 'Loading',
    'Select District': 'Select District',
    'Select by Voice': 'Select by Voice',
    'District Name': 'District Name',
    'Selected': 'Selected',
    
    // District Names
    'Hyderabad': 'Hyderabad',
    'Rangareddy': 'Rangareddy',
    'Medchal-Malkajgiri': 'Medchal-Malkajgiri',
    'Warangal': 'Warangal',
    'Karimnagar': 'Karimnagar',
    'Khammam': 'Khammam',
    'Nalgonda': 'Nalgonda',
    'Mahabubabad': 'Mahabubabad',
    'Mancherial': 'Mancherial',
    'Tandur': 'Tandur',
    
    // Market Names
    'APMC Hyderabad': 'APMC Hyderabad',
    'APMC Rangareddy': 'APMC Rangareddy',
    'APMC Warangal': 'APMC Warangal',
    'APMC Karimnagar': 'APMC Karimnagar',
    'APMC Khammam': 'APMC Khammam',
    'APMC Nalgonda': 'APMC Nalgonda',
    'APMC Medchal': 'APMC Medchal',
    'APMC Mahabubabad': 'APMC Mahabubabad',
    'APMC Mancherial': 'APMC Mancherial',
    'APMC Tandur': 'APMC Tandur',
    
    'District not found': 'District not found'
  },
  
  hi: {
    // Navigation
    'Disease Detection': 'रोग जांच',
    'Crop Advisory': 'फसल सलाह',
    'Query History': 'प्रश्न इतिहास',
    'Voice Settings': 'आवाज सेटिंग्स',
    'Organic Farming': 'जैविक खेती',
    'Organic Farming subtitle': 'तेलंगाना के लिए टिकाऊ, रासायनिक-मुक्त तरीके',
    'Get Organic Guide': 'जैविक गाइड प्राप्त करें',
    'Generating organic guide': 'गाइड तैयार हो रही है...',
    'Organic guide ready': 'गाइड तैयार',
    'Organic crop required': 'फसल का नाम दर्ज करें',
    'Organic location hint': 'डिफॉल्ट तेलंगाना; जिला जोड़ सकते हैं',
    'Organic techniques': 'जैविक खेती तकनीक',
    
    // Quick Crops for Organic Farming
    'Rice': 'चावल',
    'Cotton': 'कपास',
    'Tomato': 'टमाटर',
    'Potato': 'आलू',
    'Maize': 'मकई',
    'Chilli': 'मिर्च',
    'Groundnut': 'मूंगफली',
    
    'Farmer Tools': 'किसान उपकरण',
    'Weather & spray': 'मौसम और स्प्रे सुरक्षा',
    'Weather spray hint': 'अपने क्षेत्र का लाइव मौसम देखें',
    'Enter city': 'शहर का नाम लिखें',
    'Get weather': 'मौसम लाएं',
    'Weather loaded': 'मौसम लोड हो गया',
    'Spray advice': 'स्प्रे सलाह',
    'One-tap solution': 'एक टैप समाधान कार्ड',
    'Solution hint': 'दवा, खुराक, समय (डेमो डेटा)',
    'Get solution': 'समाधान लाएं',
    'Solution loaded': 'समाधान लोड हो गया',
    'Disease': 'रोग',
    'Medicine': 'दवा',
    'Dosage': 'खुराक',
    'Time': 'समय',
    'Note': 'नोट',
    'Field reminder': 'खेत अनुस्मारक',
    'Reminder hint': 'देरी के बाद सर्वर लॉग करेगा (कंसोल देखें)',
    'Reminder placeholder': 'उदा. खेत B में ड्रिप चेक करें',
    'Delay seconds': 'विलंब (सेकंड)',
    'Schedule reminder': 'अनुस्मारक निर्धारित करें',
    'Scheduled': 'निर्धारित',
    'Reminder message required': 'संदेश लिखें',
    'Reminder scheduled': 'अनुस्मारक निर्धारित',
    'Weather GPS hint': 'स्वचालित स्थान — 5 दिन का पूर्वानुमान',
    'Refresh location weather': 'मौसम अपडेट',
    'Use GPS instead': 'मेरा स्थान',
    'Search city instead': 'शहर से खोजें',
    'Location denied banner': 'स्थान बंद है। ब्राउज़र में अनुमति दें या शहर लिखें।',
    'Geolocation not supported': 'जियोलोकेशन उपलब्ध नहीं',
    'Location denied hint': 'स्थान की अनुमति दें या शहर खोजें',
    'Loading weather': 'लोड हो रहा है…',
    'Feels like': 'महसूस',
    'Humidity': 'नमी',
    'Wind': 'हवा',
    'Five day forecast': '5 दिन पूर्वानुमान',
    'City mode no forecast': 'शहर मोड में केवल आज। पूरा पूर्वानुमान के लिए स्थान चालू करें।',
    'Telangana brands title': 'तेलंगाना में लोकप्रिय ब्रांड',
    'Telangana brands subtitle': 'सामान्य इनपुट — लेबल व डीलर सलाह मानें',
    'Brands loading': 'लोड हो रहा है…',
    'Weather openmeteo hint': 'ओपन-मेटियो (मुफ़्त) — जीपीएस या हैदराबाद यदि स्थान बंद',
    'Hyderabad default weather': 'हैदराबाद (डिफ़ॉल्ट)',
    'Using Hyderabad default': 'हैदराबाद (तेलंगाना) का मौसम — अपने क्षेत्र के लिए स्थान चालू करें।',
    'Current conditions': 'वर्तमान स्थिति',
    'Wind speed': 'हवा की गति',
    'OpenMeteo wind note': 'हवा km/h (10 m)। सलाह: बारिश कोड → स्प्रे नहीं; 20 से अधिक हवा → तेज़।',
    
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
    'Select soil type': 'मिट्टी का प्रकार चुनें',
    
    // Farming Seasons
    'Farming Season': 'खेती का मौसम',
    'Kharif (Monsoon)': 'खरीफ (मानसून)',
    'Rabi (Winter)': 'रबी (सर्दी)',
    'Summer': 'गर्मी',
    'Spring': 'वसंत',
    'Select current season': 'वर्तमान मौसम चुनें',
    
    // Response Card
    'AI Response': 'AI सलाह उत्तर',
    'Prediction': 'रोग पूर्वानुमान',
    'Confidence': 'विश्वास स्तर',
    'Advisory': 'उपचार सलाह',
    'Play Audio': '🔊 ऑडियो उत्तर सुनें',
    'Feedback': 'क्या यह सहायक था?',
    'Thumbs Up': '👍 सहायक',
    'Thumbs Down': '👎 सहायक नहीं',
    
    // Advisory Form Additional
    'Crop Advisory subtitle': 'व्यापक खेती मार्गदर्शन और बाजार अंतर्दृष्टि प्राप्त करें',
    'Farming Advisory': 'कृषि सलाह',
    'Recommended Crop Options': 'अनुशंसित फसल विकल्प',
    'Based on': 'के आधार पर',
    'soil': 'मिट्टी',
    'and': 'और',
    'Choose your current farming season for better recommendations': 'बेहतर सिफारिशों के लिए अपने वर्तमान खेती के मौसम को चुनें',
    'Generating audio in background...': 'पृष्ठभूमि में ऑडियो तैयार किया जा रहा है...',
    'Audio ready! Click play button to listen': 'ऑडियो तैयार! सुनने के लिए प्ले बटन पर क्लिक करें',
    'Streaming audio - starts playing as it generates...': 'ऑडियो स्ट्रीमिंग - जनरेट होते ही प्ले होने लगेगा...',
    '✨ Audio ready! Click play to listen': '✨ ऑडियो तैयार! सुनने के लिए प्ले करें',
    'Playing audio...': 'ऑडियो चल रहा है...',
    
    // Playback Speed Controls
    'Playback Speed': 'प्लेबैक गति',
    '0.5x': '0.5x (धीमा)',
    '0.75x': '0.75x',
    '1x': '1x (सामान्य)',
    '1.25x': '1.25x',
    '1.5x': '1.5x (तेज)',
    '2x': '2x (बहुत तेज)',
    
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
    
    // Messages and Alerts
    'Listening... Please speak now': 'अभी बोलें...',
    'Analyzing crop disease...': 'फसल रोग का विश्लेषण जारी है...',
    'Voice captured successfully!': 'आवाज सफलतापूर्वक कैप्चर की गई!',
    'Generating audio...': 'ऑडियो तैयार हो रही है...',
    'Playing audio response': 'ऑडियो चल रही है',
    'Disease analysis completed!': 'रोग विश्लेषण पूरा हो गया!',
    'Listening...': 'सुन रहे हैं...',
    'Analyzing...': 'विश्लेषण जारी है...',
    'Please fill in all fields': 'कृपया सभी फील्ड भरें',
    'Getting agricultural advisory...': 'कृषि सलाह प्राप्त जारी है...',
    'Advisory generated successfully!': 'सलाह सफलतापूर्वक बनाई गई!',
    'Generating guide...': 'गाइड तैयार हो रही है...',
    'Show Less': 'कम दिखाएं',
    'Read More': 'अधिक पढ़ें',
    'Thank you for your feedback!': 'आपकी प्रतिक्रिया के लिए धन्यवाद!',
    'Failed to submit feedback': 'प्रतिक्रिया सबमिट करने में विफल',
    'Audio generation failed': 'ऑडियो जनरेशन विफल',
    'Playing audio advisory': 'ऑडियो सलाह चल रही है',
    'TTS failed': 'टेक्स्ट-टू-स्पीच विफल',
    'Generating test audio...': 'परीक्षण ऑडियो तैयार हो रही है...',
    'Test Voice Input': 'आवाज परीक्षण इनपुट',
    'Test Voice Output': 'आवाज परीक्षण आउटपुट',
    'No advisory available': 'कोई सलाह उपलब्ध नहीं',
    'Voice recognition error. Please try again.': 'आवाज पहचान त्रुटि। कृपया पुनः प्रयास करें।',
    'Please enter some text to test voice output': 'कृपया आवाज परीक्षण के लिए कुछ पाठ दर्ज करें',
    'Browser Support:': 'ब्राउज़र समर्थन:',
    'Google TTS': 'Google टेक्स्ट-टू-स्पीच',
    'Currently Active': 'वर्तमान में सक्रिय',
    'Test Voice Features': 'आवाज सुविधाएं परीक्षण करें',
    'Voice Input Test': 'आवाज इनपुट परीक्षण',
    'Voice Output Test': 'आवाज आउटपुट परीक्षण',
    'Convert your voice into text for queries and commands.': 'अपनी आवाज को क्वेरी और कमांड के लिए टेक्स्ट में बदलें।',
    'Listen to AI responses in your preferred language.': 'अपनी पसंद की भाषा में AI प्रतিक्रिया सुनें।',
    'Service:': 'सेवा:',
    'Captured': 'कैप्चर किया गया',
    'Tips for Better Voice Experience': 'बेहतर आवाज अनुभव के लिए सुझाव',
    'Speak clearly and at a normal pace': 'स्पष्ट और सामान्य गति से बोलें',
    'Ensure you are in a quiet environment for better recognition': 'बेहतर पहचान के लिए शांत पर्यावरण में हों',
    'Allow microphone access when prompted by your browser': 'ब्राउज़र द्वारा संकेत दिए जाने पर माइक्रोफ़ोन एक्सेस की अनुमति दें',
    'Voice input works best in Chrome, Edge, and Safari browsers': 'आवाज इनपुट Chrome, Edge और Safari ब्राउज़र में सर्वश्रेष्ठ काम करता है',
    'Audio output supports all major languages for farming guidance': 'ऑडियो आउटपुट कृषि मार्गदर्शन के लिए सभी प्रमुख भाषाओं का समर्थन करता है',
    'View query history': 'अपने हाल के रोग पहचान और सलाह प्रश्न देखें',
    'History empty message': 'एक बार जब आप रोग पहचान या सलाह सुविधाओं का उपयोग करना शुरू करते हैं, तो आपका प्रश्न इतिहास यहाँ दिखाई देगा।',
    
    // Market Prices
    'Market Prices': 'बाजार कीमतें',
    'Current commodity prices across top 10 Telangana districts': 'तेलंगाना के सभी जिलों में वर्तमान कमोडिटी कीमतें',
    'Current commodity prices across all Telangana districts': 'तेलंगाना के सभी जिलों में वर्तमान कमोडिटी कीमतें',
    'Loading market prices...': 'बाजार कीमतें लोड हो रही हैं...',
    'All Commodity Prices': 'सभी कमोडिटी कीमतें',
    'District Summary': 'जिला सारांश',
    'Average prices across commodities': 'कमोडिटीज में औसत कीमतें',
    'District': 'जिला',
    'Avg Modal ₹': 'औसत मोडल ₹',
    'Commodities': 'कमोडिटीज',
    'Action': 'कार्रवाई',
    'View': 'देखें',
    'commodities available': 'कमोडिटीज उपलब्ध',
    'Commodity': 'कमोडिटी',
    'Modal ₹': 'मोडल ₹',
    'Range': 'श्रेणी',
    'Market': 'बाजार',
    'Min ₹': 'न्यूनतम ₹',
    'Max ₹': 'अधिकतम ₹',
    'Select a district to view commodities': 'कमोडिटीज देखने के लिए एक जिला चुनें',
    'Price Info': 'कीमत जानकारी',
    'Prices updated from Agriculture Market Data (data.gov.in). Click on column headers to sort. Use search to filter by district or commodity.': 'कीमतें कृषि बाजार डेटा (data.gov.in) से अपडेट की गई हैं। सॉर्ट करने के लिए कॉलम हेडर पर क्लिक करें। जिले या कमोडिटी द्वारा फ़िल्टर करने के लिए खोज का उपयोग करें।',
    'Prices updated from Agriculture Market Data (data.gov.in). Click on any district to view detailed commodity prices including min, max, and modal prices.': 'कीमतें कृषि बाजार डेटा (data.gov.in) से अपडेट की गई। विस्तृत कमोडिटी कीमतें देखने के लिए किसी भी जिले पर क्लिक करें।',
    'Min Avg': 'न्यूनतम औसत',
    'Max Avg': 'अधिकतम औसत',
    'Min Price': 'न्यूनतम कीमत',
    'Max Price': 'अधिकतम कीमत',
    'Failed to load details for': 'के लिए विवरण लोड करने में विफल',
    'Search': 'खोज',
    'or': 'या',
    'entries': 'प्रविष्टियां',
    'No results found': 'कोई परिणाम नहीं मिला',
    
    // Additional Market Prices & Buttons
    'Refresh': 'रीफ्रेश करें',
    'Refresh Prices': 'कीमतें रीफ्रेश करें',
    'Loading': 'लोड हो रहा है',
    'Select District': 'जिला चुनें',
    'Select by Voice': 'वॉयस द्वारा चुनें',
    'District Name': 'जिला का नाम',
    'Selected': 'चयनित',
    'District not found': 'जिला नहीं मिला'
  },
  
  ml: {
    // Navigation
    'Disease Detection': 'രോഗ നിർണ്ണയം',
    'Crop Advisory': 'വിള ഉപദേശം',
    'Query History': 'ചോദ്യ ചരിത്രം',
    'Voice Settings': 'വോയ്സ് സെറ്റിംഗുകൾ',
    'Organic Farming': 'ഓർഗാനിക് കൃഷി',
    'Organic Farming subtitle': 'തെലങ്കാനയ്ക്ക് അനുയോജ്യമായ സുസ്ഥിര രീതികൾ',
    'Get Organic Guide': 'ഓർഗാനിക് ഗൈഡ് നേടുക',
    'Generating organic guide': 'ഗൈഡ് തയ്യാറാക്കുന്നു...',
    'Organic guide ready': 'ഗൈഡ് തയ്യാർ',
    'Organic crop required': 'വിളയുടെ പേര് നൽകുക',
    'Organic location hint': 'സ്ഥിരസ്ഥിതി തെലങ്കാന; ജില്ല ചേർക്കാം',
    'Organic techniques': 'ഓർഗാനിക് കൃഷിരീതികൾ',
    
    // Quick Crops for Organic Farming
    'Rice': 'അരി',
    'Cotton': 'പയറ്',
    'Tomato': 'തക്കാളി',
    'Potato': 'ഉരുളകിഴങ്ങ്',
    'Maize': 'കോൺ',
    'Chilli': 'മുളകു',
    'Groundnut': 'കടലച്ചീര',
    
    'Farmer Tools': 'കർഷക ഉപകരണങ്ങൾ',
    'Weather & spray': 'കാലാവസ്ഥയും സ്പ്രേയും',
    'Weather spray hint': 'നിങ്ങളുടെ പ്രദേശത്തെ കാലാവസ്ഥ',
    'Enter city': 'നഗരത്തിന്റെ പേര്',
    'Get weather': 'കാലാവസ്ഥ കാണുക',
    'Weather loaded': 'ലോഡ് ചെയ്തു',
    'Spray advice': 'സ്പ്രേ ഉപദേശം',
    'One-tap solution': 'ഒറ്റ ടാപ്പ് പരിഹാരം',
    'Solution hint': 'ഡോസേജ്, സമയം (ഡെമോ)',
    'Get solution': 'പരിഹാരം കാണുക',
    'Solution loaded': 'ലോഡ് ചെയ്തു',
    'Disease': 'രോഗം',
    'Medicine': 'മരുന്ന്',
    'Dosage': 'ഡോസേജ്',
    'Time': 'സമയം',
    'Note': 'കുറിപ്പ്',
    'Field reminder': 'ഫീൽഡ് ഓർമ്മപ്പെടുത്തൽ',
    'Reminder hint': 'സെർവർ ലോഗ് (കൺസോൾ)',
    'Reminder placeholder': 'ഉദാ. ഫീൽഡ് B പരിശോധിക്കുക',
    'Delay seconds': 'കാലതാമസം (സെക്കൻഡ്)',
    'Schedule reminder': 'ഷെഡ്യൂൾ ചെയ്യുക',
    'Scheduled': 'ഷെഡ്യൂൾ ചെയ്തു',
    'Reminder message required': 'സന്ദേശം നൽകുക',
    'Reminder scheduled': 'ഷെഡ്യൂൾ ചെയ്തു',
    'Weather GPS hint': 'സ്വയം സ്ഥാനം — 5 ദിവസത്തെ പ്രവചനം',
    'Refresh location weather': 'കാലാവസ്ഥ അപ്ഡേറ്റ്',
    'Use GPS instead': 'എന്റെ സ്ഥാനം',
    'Search city instead': 'നഗരം തിരയുക',
    'Location denied banner': 'ലൊക്കേഷൻ ഓഫാണ്. അനുവദിക്കുക അല്ലെങ്കിൽ നഗരം നൽകുക.',
    'Geolocation not supported': 'ജിയോലൊക്കേഷൻ ഇല്ല',
    'Location denied hint': 'ലൊക്കേഷൻ അനുവദിക്കുക അല്ലെങ്കിൽ നഗരം',
    'Loading weather': 'ലോഡ് ചെയ്യുന്നു…',
    'Feels like': 'അനുഭവം',
    'Humidity': 'ആർദ്രത',
    'Wind': 'കാറ്റ്',
    'Five day forecast': '5 ദിവസ പ്രവചനം',
    'City mode no forecast': 'നഗര മോഡിൽ ഇന്ന് മാത്രം. പൂർണ്ണ പ്രവചനത്തിന് ലൊക്കേഷൻ.',
    'Telangana brands title': 'തെലങ്കാനയിലെ ബ്രാൻഡുകൾ',
    'Telangana brands subtitle': 'പൊതു ഇൻപുട്ടുകൾ — ലേബൽ പാലിക്കുക',
    'Brands loading': 'ലോഡ് ചെയ്യുന്നു…',
    'Weather openmeteo hint': 'ഓപ്പൺ-മെറ്റിയോ (സൗജന്യം) — ജിപിഎസ് അല്ലെങ്കിൽ ലൊക്കേഷൻ ഓഫ് ആയാൽ ഹൈദരാബാദ്',
    'Hyderabad default weather': 'ഹൈദരാബാദ് (ഡിഫോൾട്ട്)',
    'Using Hyderabad default': 'ഹൈദരാബാദ് (തെലങ്കാന) കാലാവസ്ഥ — നിങ്ങളുടെ പ്രദേശത്തിന് ലൊക്കേഷൻ അനുവദിക്കുക.',
    'Current conditions': 'നിലവിലെ അവസ്ഥ',
    'Wind speed': 'കാറ്റിന്റെ വേഗം',
    'OpenMeteo wind note': 'കാറ്റ് km/h (10 m). ഉപദേശം: മഴ കോഡ് → സ്പ്രേ വേണ്ട; കാറ്റ് > 20 → ഉയർന്ന കാറ്റ്.',
    
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
    'Select soil type': 'മണ്ണ് തരം തിരഞ്ഞെടുക്കുക',
    
    // Farming Seasons
    'Farming Season': 'കൃഷി സീസൺ',
    'Kharif (Monsoon)': 'ഖരീഫ് (മൺസൂൺ)',
    'Rabi (Winter)': 'രബി (ശീതകാലം)',
    'Summer': 'വേനൽ',
    'Spring': 'വസന്തം',
    'Select current season': 'നിലവിലെ സീസൺ തിരഞ്ഞെടുക്കുക',
    
    // Response Card
    'AI Response': 'AI ഉപദേശ പ്രതികരണം',
    'Prediction': 'രോഗ പ്രവചനം',
    'Confidence': 'ആത്മവിശ്വാസ നില',
    'Advisory': 'ചികിത്സാ ഉപദേശം',
    'Play Audio': '🔊 ഓഡിയോ പ്രതികരണം കേൾക്കുക',
    'Feedback': 'ഇത് സഹായകരമായിരുന്നുവോ?',
    'Thumbs Up': '👍 സഹായകരം',
    'Thumbs Down': '👎 സഹായകരമല്ല',
    
    // Advisory Form Additional
    'Crop Advisory subtitle': 'ব്যাপক കൃഷി മാർഗ്ഗനിർദ്ദേശം നേടുക',
    'Farming Advisory': 'കൃഷി ഉപദേശം',
    'Recommended Crop Options': 'ശുപാർശ ചെയ്ത വിള ഓപ്ഷനുകൾ',
    'Based on': 'ഇതിനെ അടിസ്ഥാനമാക്കി',
    'soil': 'മണ്ണ്',
    'and': 'കൂടാതെ',
    'Choose your current farming season for better recommendations': 'ഉത്തമമായ ശുപാർശകൾക്കായി നിങ്ങളുടെ നിലവിലെ കൃഷി സീസൺ തിരഞ്ഞെടുക്കുക',
    'Generating audio in background...': 'പശ്ചാത്തലത്തിൽ ഓഡിയോ തയ്യാറാണ്...',
    'Audio ready! Click play button to listen': 'ഓഡിയോ തയ്യാർ! കേൾക്കാൻ പ്ലേ ബട്ടൺ ക്ലിക്ക് ചെയ്യുക',
    'Streaming audio - starts playing as it generates...': 'ഓഡിയോ സ്ട്രീമിംഗ് - സൃഷ്ടിയാകുമ്പോൾ പ്ലേ ആരംഭിക്കും...',
    '✨ Audio ready! Click play to listen': '✨ ഓഡിയോ തയ്യാർ! കേൾക്കാൻ പ്ലേ കളിക്കുക',
    'Playing audio...': 'ഓഡിയോ പ്ലേ ചെയ്യുന്നു...',
    
    // Playback Speed Controls
    'Playback Speed': 'പ്ലേബാക്ക് വേഗത',
    '0.5x': '0.5x (സാവധാനം)',
    '0.75x': '0.75x',
    '1x': '1x (സാധാരണ)',
    '1.25x': '1.25x',
    '1.5x': '1.5x (വേഗത്തിൽ)',
    '2x': '2x (വളരെ വേഗം)',
    
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
    
    // Messages and Alerts
    'Listening... Please speak now': 'കേൾക്കുന്നു... ഇപ്പോൾ സംസാരിക്കുക',
    'Analyzing crop disease...': 'വിള രോഗ വിശ്ലേഷണം നടക്കുന്നു...',
    'Voice captured successfully!': 'വോയ്സ് വിജയകരമായി ക്യാപ്ചര് ചെയ്തു!',
    'Generating audio...': 'ഓഡിയോ തയ്യാറാണ്...',
    'Playing audio response': 'ഓഡിയോ പ്ലേ ചെയ്യുന്നു',
    'Disease analysis completed!': 'രോഗ വിശ്ലേഷണം പൂർത്തിയായി!',
    'Listening...': 'കേൾക്കുന്നു...',
    'Analyzing...': 'വിശ്ലേഷണം നടക്കുന്നു...',
    'Please fill in all fields': 'ദയവായി എല്ലാ ഫീൽഡിലും പൂരിപ്പിക്കുക',
    'Getting agricultural advisory...': 'കൃഷി ഉപദേശം ലഭിക്കുന്നു...',
    'Advisory generated successfully!': 'ഉപദേശം വിജയകരമായി സർജ്ജിച്ചു!',
    'Generating guide...': 'ഗൈഡ് തയ്യാറാണ്...',
    'Show Less': 'കുറവ് കാണിക്കുക',
    'Read More': 'കൂടുതൽ വായിക്കുക',
    'Thank you for your feedback!': 'നിങ്ങളുടെ മതിപ്പ് പങ്കിട്ടതിനു നന്ദി!',
    'Failed to submit feedback': 'മതിപ്പ് സമർപ്പിക്കത് പരാജയപ്പെട്ടു',
    'Audio generation failed': 'ഓഡിയോ തൈരി പരാജയപ്പെട്ടു',
    'Playing audio advisory': 'ഓഡിയോ ഉപദേശം പ്ലേ ചെയ്യുന്നു',
    'TTS failed': 'ടെക്സ്ट് ടു സ്പീച് പരാജയപ്പെട്ടു',
    'Generating test audio...': 'പരീക്ഷാ ഓഡിയോ തയ്യാറാണ്...',
    'Test Voice Input': 'പരീക്ഷാ വോയ്സ് ഇൻപുട്ട്',
    'Test Voice Output': 'പരീക്ഷാ വോയ്സ് ഔട്ട്പുട്ട്',
    'No advisory available': 'ഉപദേശം ലഭ്യമല്ല',
    'Voice recognition error. Please try again.': 'വോയ്സ് തിരിച്ചറിയൽ പിശക്. വീണ്ടും ശ്രമിക്കുക.',
    'Please enter some text to test voice output': 'വോയ്സ് ഔട്ട്പുട്ട് പരീക്ഷിക്കാൻ വാചകം നൽകുക',
    'Browser Support:': 'ബ്രൗസർ സപ്പോർട്ട്:',
    'Google TTS': 'Google ടെക്സ്ട് ടു സ്പീച്ച്',
    'Currently Active': 'നിലവിൽ സജീവം',
    'Test Voice Features': 'വോയ്സ് ഫീച്ചറുകൾ പരീക്ഷിക്കുക',
    'Voice Input Test': 'വോയ്സ് ഇൻപുട്ട് പരീക്ഷണം',
    'Voice Output Test': 'വോയ്സ് ഔട്ട്പുട്ട് പരീക്ഷണം',
    'Convert your voice into text for queries and commands.': 'നിങ്ങളുടെ വോയ്സിനെ ചോദ്യങ്ങൾക്കും കമാൻഡുകൾക്കുമായി വാചകമാക്കുക.',
    'Listen to AI responses in your preferred language.': 'നിങ്ങളുടെ ഇഷ്ടപ്പെട്ട ഭാഷയിൽ AI പ്രതികരണം കേൾക്കുക.',
    'Service:': 'സേവനം:',
    'Captured': 'ക്യാപ്ചർ ചെയ്ത',
    'Tips for Better Voice Experience': 'കൂടുതൽ നല്ല വോയ്സ് അനുഭവത്തിനുള്ള നുറുങ്ങുകൾ',
    'Speak clearly and at a normal pace': 'പ്രതിഷ്ഠിതമായും സാധാരണ വേഗതയിലും സംസാരിക്കുക',
    'Ensure you are in a quiet environment for better recognition': 'കൂടുതൽ നല്ല തിരിച്ചറിയലിനായി നിശ്ശബ്ദ പരിതസ്ഥിതിയിൽ ഉണ്ടായിരിക്കുക',
    'Allow microphone access when prompted by your browser': 'ബ്രൗസർ സൂചിപ്പിക്കുമ്പോൾ മൈക്രോഫോൺ ആക്സെസ് അനുവദിക്കുക',
    'Voice input works best in Chrome, Edge, and Safari browsers': 'വോയ്സ് ഇൻപുട്ട് Chrome, Edge, Safari ബ്രൗസറുകളിൽ ഏറ്റവും നല്ലതായി പ്രവർത്തിക്കുന്നു',
    'Audio output supports all major languages for farming guidance': 'ഓഡിയോ ഔട്ട്പുട്ട് കാർഷിക മാർഗ്ഗദർശനത്തിനൊരു പ്രധാന ഭാഷകളെ പിന്തുണയ്ക്കുന്നു',
    'View query history': 'നിങ്ങളുടെ സമീപകാല രോഗ കണ്ടെത്തലുകളും ഉപദേശ ചോദ്യങ്ങളും കാണുക',
    'History empty message': 'നിങ്ങൾ രോഗ കണ്ടെത്തൽ അല്ലെങ്കിൽ ഉപദേശ സൌകര്യങ്ങൾ ഉപയോഗിക്കാൻ തുടങ്ങിയാൽ നിങ്ങളുടെ ചോദ്യ ചരിത്രം ഇവിടെ ദൃശ്യമാകും.',
    
    // Market Prices
    'Market Prices': 'വിപണി വിലകൾ',
    'Current commodity prices across top 10 Telangana districts': 'തെലങ്കാനയിലെ എല്ലാ ജില്ലകളിലെ വിലകൾ',
    'Current commodity prices across all Telangana districts': 'തെലങ്കാനയിലെ എല്ലാ ജില്ലകളിലെ വിലകൾ',
    'Loading market prices...': 'വിപണി വിലകൾ ലോഡ് ചെയ്യുന്നു...',
    'All Commodity Prices': 'എല്ലാ വില വിലകൾ',
    'District Summary': 'ജില്ല സംഗ്രഹം',
    'Average prices across commodities': 'ഉൽപത്തികളിലെ ശരാശരി വിലകൾ',
    'District': 'ജില്ല',
    'Avg Modal ₹': 'ശരാശരി മോഡൽ ₹',
    'Commodities': 'ഉൽപത്തികൾ',
    'Action': 'പ്രവർത്തനം',
    'View': 'കാണുക',
    'commodities available': 'ഉൽപത്തികൾ ലഭ്യമാണ്',
    'Commodity': 'ഉൽപത്തി',
    'Modal ₹': 'മോഡൽ ₹',
    'Range': 'ശ്രേണി',
    'Market': 'വിപണി',
    'Min ₹': 'കുറഞ്ഞ ₹',
    'Max ₹': 'കൂടിയ ₹',
    'Select a district to view commodities': 'ഉൽപത്തികൾ കാണാൻ ഒരു ജില്ല തിരഞ്ഞെടുക്കുക',
    'Price Info': 'വില വിവരം',
    'Prices updated from Agriculture Market Data (data.gov.in). Click on column headers to sort. Use search to filter by district or commodity.': 'വിലകൾ കൃഷി വിപണി ഡാറ്റയിൽ നിന്ന് അപ്ഡേറ്റ് ചെയ്തു (data.gov.in). സോർട്ട് ചെയ്യാൻ കോളം ഹെഡറുകളിൽ ക്ലിക്ക് ചെയ്യുക। ജില്ല അല്ലെങ്കിൽ ഉൽപത്തി അനുസരിച്ച് ഫിൽട്ടർ ചെയ്യാൻ തിരയൽ ഉപയോഗിക്കുക।',
    'Prices updated from Agriculture Market Data (data.gov.in). Click on any district to view detailed commodity prices including min, max, and modal prices.': 'വിലകൾ കൃഷി വിപണി ഡാറ്റയിൽ നിന്ന് അപ്ഡേറ്റ് ചെയ്തു (data.gov.in). വിശദമായ ഉൽപത്തി വിലകൾ കാണാൻ ഏതെങ്കിലും ജില്ലയിൽ ക്ലിക്ക് ചെയ്യുക.',
    'Min Avg': 'കുറഞ്ഞ ശരാശരി',
    'Max Avg': 'കൂടിയ ശരാശരി',
    'Min Price': 'കുറഞ്ഞ വില',
    'Max Price': 'കൂടിയ വില',
    'Failed to load details for': 'ന്റെ വിവരങ്ങൾ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല',
    'Search': 'തിരയൽ',
    'or': 'അല്ലെങ്കിൽ',
    'entries': 'എൻട്രികൾ',
    'No results found': 'ഫലങ്ങൾ കണ്ടെത്തിയില്ല',
    
    // Additional Market Prices & Buttons
    'Refresh': 'പുതുക്കുക',
    'Refresh Prices': 'വില പുതുക്കുക',
    'Loading': 'ലോഡ് ചെയ്യുന്നു',
    'Select District': 'ജില്ല തിരഞ്ഞെടുക്കുക',
    'Select by Voice': 'വോയ്സ് ഉപയോഗിച്ച് തിരഞ്ഞെടുക്കുക',
    'District Name': 'ജില്ല പേര്',
    'Selected': 'തിരഞ്ഞെടുത്തത്',
    'District not found': 'ജില്ല കണ്ടെത്തിയില്ല'
  },
  
  te: {
    // Navigation
    'Disease Detection': 'వ్యాధి గుర్తింపు',
    'Crop Advisory': 'పంట సలహా',
    'Query History': 'ప్రశ్న చరిత్ర',
    'Voice Settings': 'వాయిస్ సెట్టింగ్లు',
    'Organic Farming': 'సేంద్రీయ వ్యవసాయం',
    'Organic Farming subtitle': 'తెలంగాణకు అనువైన సుస్థిర, రసాయనరహిత పద్ధతులు',
    'Get Organic Guide': 'సేంద్రీయ గైడ్ పొందండి',
    'Generating organic guide': 'గైడ్ తయారవుతోంది...',
    'Organic guide ready': 'గైడ్ సిద్ధం',
    'Organic crop required': 'పంట పేరు ఇవ్వండి',
    'Organic location hint': 'డిఫాల్ట్ తెలంగాణ; జిల్లా చేర్చవచ్చు',
    'Organic techniques': 'సేంద్రీయ వ్యవసాయ పద్ధతులు',
    
    // Quick Crops for Organic Farming
    'Rice': 'వరి',
    'Cotton': 'పట్టు',
    'Tomato': 'టమోటో',
    'Potato': 'బంగాళాదుంప',
    'Maize': 'మక్కజోళ్ళు',
    'Chilli': 'మిర్చి',
    'Groundnut': 'వేరుశనగ',
    
    'Farmer Tools': 'రైతు సాధనాలు',
    'Weather & spray': 'వాతావరణం & స్ప్రే సురక్ష',
    'Weather spray hint': 'మీ ప్రాంతపు వాతావరణం',
    'Enter city': 'నగరం పేరు',
    'Get weather': 'వాతావరణం తెలుసుకోండి',
    'Weather loaded': 'లోడ్ అయింది',
    'Spray advice': 'స్ప్రే సలహా',
    'One-tap solution': 'ఒక ట్యాప్ పరిష్కారం',
    'Solution hint': 'మోతాదు, సమయం (డెమో)',
    'Get solution': 'పరిష్కారం',
    'Solution loaded': 'లోడ్ అయింది',
    'Disease': 'వ్యాధి',
    'Medicine': 'మందు',
    'Dosage': 'మోతాదు',
    'Time': 'సమయం',
    'Note': 'గమనిక',
    'Field reminder': 'ఫీల్డ్ రిమైండర్',
    'Reminder hint': 'సర్వర్ లాగ్ (కన్సోల్ చూడండి)',
    'Reminder placeholder': 'ఉదా. ఫీల్డ్ B తనిఖీ',
    'Delay seconds': 'ఆలస్యం (సెకన్లు)',
    'Schedule reminder': 'షెడ్యూల్ చేయండి',
    'Scheduled': 'షెడ్యూల్ అయింది',
    'Reminder message required': 'సందేశం ఇవ్వండి',
    'Reminder scheduled': 'రిమైండర్ షెడ్యూల్',
    'Weather GPS hint': 'స్వయంచాలక స్థానం — 5 రోజుల అంచనా',
    'Refresh location weather': 'వాతావరణం రిఫ్రెష్',
    'Use GPS instead': 'నా స్థానం',
    'Search city instead': 'నగరంతో వెతకండి',
    'Location denied banner': 'లొకేషన్ ఆఫ్. బ్రౌజర్‌లో అనుమతి ఇవ్వండి లేదా నగరం.',
    'Geolocation not supported': 'జియోలొకేషన్ లేదు',
    'Location denied hint': 'లొకేషన్ అనుమతించండి లేదా నగరం వాడండి',
    'Loading weather': 'లోడ్ అవుతోంది…',
    'Feels like': 'అనుభవం',
    'Humidity': 'తేమ',
    'Wind': 'గాలి',
    'Five day forecast': '5 రోజుల అంచనా',
    'City mode no forecast': 'నగర మోడ్‌లో ఈరోజు మాత్రమే. పూర్తి అంచనాకు స్థానం.',
    'Telangana brands title': 'తెలంగాణలో ప్రజాదరణ పొందిన బ్రాండ్లు',
    'Telangana brands subtitle': 'సాధారణ ఇన్‌పుట్లు — లేబుల్ & డీలర్ సలహా',
    'Brands loading': 'లోడ్ అవుతోంది…',
    'Weather openmeteo hint': 'ఓపెన్-మెటియో (ఉచితం) — GPS లేదా లొకేషన్ ఆఫ్ అయితే హైదరాబాద్',
    'Hyderabad default weather': 'హైదరాబాద్ (డిఫాల్ట్)',
    'Using Hyderabad default': 'హైదరాబాద్ (తెలంగాణ) వాతావరణం — మీ ప్రాంతానికి లొకేషన్ అనుమతించండి.',
    'Current conditions': 'ప్రస్తుత పరిస్థితులు',
    'Wind speed': 'గాలి వేగం',
    'OpenMeteo wind note': 'గాలి km/h (10 m). సలహా: వర్షం కోడ్ → స్ప్రే వద్దు; గాలి > 20 → ఎక్కువ గాలి.',
    
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
    'Select soil type': 'మట్టి రకాన్ని ఎంచుకోండి',
    
    // Farming Seasons
    'Farming Season': 'వ్యవసాయ సీజన్',
    'Kharif (Monsoon)': 'ఖరీఫ్ (మానసూన్)',
    'Rabi (Winter)': 'రబీ (శీతకాలం)',
    'Summer': 'వేసవి',
    'Spring': 'వసంతకాలం',
    'Select current season': 'ప్రస్తుత సీజన్‌ను ఎంచుకోండి',
    
    // Response Card
    'AI Response': 'AI సలహా సమాధానం',
    'Prediction': 'వ్యాధి అంచనా',
    'Confidence': 'విశ్వాస స్థాయి',
    'Advisory': 'చికిత్స సలహా',
    'Play Audio': '🔊 ఆడియో సమాధానం వినండి',
    'Feedback': 'ఇది సహాయకరమైందా?',
    'Thumbs Up': '👍 సహాయకరం',
    'Thumbs Down': '👎 సహాయకరం కాదు',
    
    // Advisory Form Additional
    'Crop Advisory subtitle': 'సమగ్ర వ్యవసాయ మార్గదర్శకత్వం మరియు మార్కెట్ అంతర్దృష్టులను పొందండి',
    'Farming Advisory': 'వ్యవసాయ సలహా',
    'Recommended Crop Options': 'సిఫారసు చేయబడిన పంట ఎంపికలు',
    'Based on': 'ఆధారపడి',
    'soil': 'నేల',
    'and': 'మరియు',
    'Choose your current farming season for better recommendations': 'మెరుగైన సిఫారసుల కోసం మీ ప్రస్తుత వ్యవసాయ సీజన్‌ను ఎంచుకోండి',
    'Generating audio in background...': 'నేపథ్యంలో ఆడియో ఉత్పత్తి చేస్తోంది...',
    'Audio ready! Click play button to listen': 'ఆడియో సిద్ధమైంది! వింటే ప్లే బటన్‌ను క్లిక్ చేయండి',
    'Streaming audio - starts playing as it generates...': 'ఆడియో స్ట్రీమింగ్ - ఉత్పత్తి అయిన వెంటనే ప్లే ఆరంభమవుతుంది...',
    '✨ Audio ready! Click play to listen': '✨ ఆడియో సిద్ధమైంది! వినడానికి ప్లే చేయండి',
    'Playing audio...': 'ఆడియో చేస్తోంది...',
    
    // Playback Speed Controls
    'Playback Speed': 'ప్లేబ్యాక్ వేగం',
    '0.5x': '0.5x (నెమ్ము)',
    '0.75x': '0.75x',
    '1x': '1x (సాధారణ)',
    '1.25x': '1.25x',
    '1.5x': '1.5x (వేగం)',
    '2x': '2x (చాలా వేగం)',
    
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
    
    // Messages and Alerts
    'Listening... Please speak now': 'విని ఉన్నాను... ఇప్పుడు మాట్లాడండి',
    'Analyzing crop disease...': 'పంట వ్యాధు విశ్లేషణ నుండుంది...',
    'Voice captured successfully!': 'వాయిస్ విజయవంతంగా క్యాప్చర్ చేయబడింది!',
    'Generating audio...': 'ఆడియో తయారువుతోంది...',
    'Playing audio response': 'ఆడియో ప్లే చేస్తోంది',
    'Disease analysis completed!': 'వ్యాధు విశ్లేషణ పూర్తయింది!',
    'Listening...': 'విని ఉన్నాను...',
    'Analyzing...': 'విశ్లేషణ జరుగుతోంది...',
    'Please fill in all fields': 'దయచేసి అన్ని ఫీల్డులను పూరించండి',
    'Getting agricultural advisory...': 'వ్యవసాయ సలహా పొందటం జరుగుతోంది...',
    'Advisory generated successfully!': 'సలహా విజయవంతంగా డిజిటల్ నిర్మితమైంది!',
    'Generating guide...': 'గైడ్ తయారువుతోంది...',
    'Show Less': 'తక్కువ చూపించు',
    'Read More': 'మరిన్ని చదవండి',
    'Thank you for your feedback!': 'మీ వ్యాఖ్యకు ధన్యవాదాలు!',
    'Failed to submit feedback': 'ప్రతిస్పందన సమర్పించడం విఫలమైంది',
    'Audio generation failed': 'ఆడియో జనరేషన్ విఫలమైంది',
    'Playing audio advisory': 'ఆడియో సలహా ప్లే చేస్తోంది',
    'TTS failed': 'టెక్స్ట్ టు స్పీచ్ విఫలమైంది',
    'Generating test audio...': 'టెస్ట్ ఆడియో తయారువుతోంది...',
    'Test Voice Input': 'టెస్ట్ వాయిస్ ఇంపుట్',
    'Test Voice Output': 'పరీక్ష వాయిస్ అవుట్‌పుట్',
    'No advisory available': 'సలహా పొందుబాటులో లేదు',
    'Voice recognition error. Please try again.': 'వాయిస్ గుర్తింపు లోపం. దయచేసి మళ్లీ ప్రయత్నించండి.',
    'Please enter some text to test voice output': 'వాయిస్ అవుట్‌పుట్ పరీక్ష చేయడానికి వచనాన్ని నమోదు చేయండి',
    'Browser Support:': 'బ్రౌజర్ మద్దతు:',
    'Google TTS': 'Google టెక్స్ట్ టు స్పీచ్',
    'Currently Active': 'ప్రస్తుతం సక్రియమైనది',
    'Test Voice Features': 'వాయిస్ ఫీచర్‌లను పరీక్షించండి',
    'Voice Input Test': 'వాయిస్ ఇంపుట్ పరీక్ష',
    'Voice Output Test': 'వాయిస్ అవుట్‌పుట్ పరీక్ష',
    'Convert your voice into text for queries and commands.': 'ప్రశ్నలు మరియు ఆదేశాల కోసం మీ వాయిస్‌ను వచనంగా మార్చండి.',
    'Listen to AI responses in your preferred language.': 'మీ ఇష్టపడిన భాషలో AI ప్రతిస్పందనలను వినండి.',
    'Service:': 'సేవ:',
    'Captured': 'క్యాప్చర్ చేయబడింది',
    'Tips for Better Voice Experience': 'ఉత్తమ వాయిస్ అనుభవం కోసం చిట్కాలు',
    'Speak clearly and at a normal pace': 'స్పష్టంగా మరియు సాధారణ గతిలో మాట్లాడండి',
    'Ensure you are in a quiet environment for better recognition': 'ఉత్తమ గుర్తింపు కోసం నిశ్శబ్ద వాతావరణంలో ఉండండి',
    'Allow microphone access when prompted by your browser': 'బ్రౌజర్ ద్వారా సూచించిన సందర్భంలో మైక్రోఫోన్ ప్రాప్యతను అనుమతించండి',
    'Voice input works best in Chrome, Edge, and Safari browsers': 'వాయిస్ ఇంపుట్ Chrome, Edge మరియు Safari బ్రౌజర్‌లలో ఉత్తమంగా పనిచేస్తుంది',
    'Audio output supports all major languages for farming guidance': 'ఆడియో అవుట్‌పుట్ వ్యవసాయ నిర్దేశకత కోసం అన్ని ప్రధాన భాషలకు మద్దతు ఇస్తుంది',
    'View query history': 'మీ ఇటీవలి వ్యాధి గుర్తింపులు మరియు సలహా ప్రశ్నలను చూడండి',
    'History empty message': 'మీరు వ్యాధి కనుగొనే లేదా సలహా సమర్థనలను ఉపయోగించడం ప్రారంభించిన తర్వాత మీ ప్రశ్న చరిత్ర ఇక్కడ కనిపిస్తుంది.',
    
    // Market Prices
    'Market Prices': 'మార్కెట్ ధరలు',
    'Current commodity prices across top 10 Telangana districts': 'తెలంగాణలోని అన్ని జిల్లల్లో సరుకుల ధరలు',
    'Current commodity prices across all Telangana districts': 'తెలంగాణలోని అన్ని జిల్లల్లో సరుకుల ధరలు',
    'Loading market prices...': 'మార్కెట్ ధరలు లోడ్ చేస్తోంది...',
    'All Commodity Prices': 'సమస్త సరుకుల ధరలు',
    'District Summary': 'జిల్లా సారాంశం',
    'Average prices across commodities': 'సరుకుల్లో సగటు ధరలు',
    'District': 'జిల్లా',
    'Avg Modal ₹': 'సగటు మోడల్ ₹',
    'Commodities': 'సరుకులు',
    'Action': 'చర్య',
    'View': 'చూడండి',
    'commodities available': 'సరుకులు లభ్యమే',
    'Commodity': 'సరుకు',
    'Modal ₹': 'మోడల్ ₹',
    'Range': 'పరిధి',
    'Market': 'మార్కెట్',
    'Min ₹': 'కనిష్ట ₹',
    'Max ₹': 'గరిష్ట ₹',
    'Select a district to view commodities': 'సరుకులను చూడటానికి జిల్లను ఎంచుకోండి',
    'Price Info': 'ధర సమాచారం',
    'Prices updated from Agriculture Market Data (data.gov.in). Click on column headers to sort. Use search to filter by district or commodity.': 'కృషి మార్కెట్ ఢాటా నుండి ధరలు అపడేట్ చేయబడ్డాయి (data.gov.in). సాధించటానికి కాలమ్ హెడర్‌ల్లో క్లిక్ చేయండి. జిల్లా లేదా సరుకు ద్వారా ఫిల్టర్ చేయడానికి శోధనను ఉపయోగించండి.',
    'Prices updated from Agriculture Market Data (data.gov.in). Click on any district to view detailed commodity prices including min, max, and modal prices.': 'కృషి మార్కెట్ ఢాటా నుండి ధరలు అపడేట్ చేయబడ్డాయి (data.gov.in). విస్తృత సరుకు ధరలను చూడటానికి ఏదైనా జిల్లను క్లిక్ చేయండి.',
    'Min Avg': 'కనిష్ట సగటు',
    'Max Avg': 'గరిష్ట సగటు',
    'Min Price': 'కనిష్ట ధర',
    'Max Price': 'గరిష్ట ధర',
    'Failed to load details for': 'కి ఆ వివరాలను లోడ్ చేయడం విఫలమైంది',
    'Search': 'శోధన',
    'or': 'లేదా',
    'entries': 'ఎంట్రీలు',
    'No results found': 'ఫలితాలు కనుగొనబడలేదు',
    
    // Additional Market Prices & Buttons
    'Refresh': 'రీఫ్రెష్ చేయండి',
    'Refresh Prices': 'ధరలను రీఫ్రెష్ చేయండి',
    'Loading': 'లోడ్ చేస్తోంది',
    'Select District': 'జిల్లను ఎంచుకోండి',
    'Select by Voice': 'వాయిస్ ద్వారా ఎంచుకోండి',
    'District Name': 'జిల్లా పేరు',
    'Selected': 'ఎంచుకోబడినది',
    'District not found': 'జిల్లా కనుగొనబడలేదు'
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