import React, { createContext, useState, useCallback } from 'react';

export const FormStateContext = createContext();

export const FormStateProvider = ({ children }) => {
  const [formStates, setFormStates] = useState({
    disease: {
      images: [],
      imagePreviews: [],
      response: null,
      originalResponse: null,
      originalAdvisory: "",
      sourceLanguage: "en",
      text: "",
      audioReady: false,
      audioData: null,
      cropModel: ""
    },
    advisory: {
      cropName: "",
      location: "",
      soilType: "",
      query: "",
      season: "kharif",
      response: null,
      audioReady: false,
      audioData: null
    },
    organic: {
      cropName: "",
      location: "Telangana, India",
      response: null,
      audioReady: false,
      audioData: null
    }
  });

  const saveFormState = useCallback((formType, state) => {
    setFormStates(prev => ({
      ...prev,
      [formType]: {
        ...prev[formType],
        ...state
      }
    }));
  }, []);

  const getFormState = useCallback((formType) => {
    return formStates[formType] || {};
  }, [formStates]);

  const clearFormState = useCallback((formType) => {
    setFormStates(prev => ({
      ...prev,
      [formType]: formType === 'disease' 
        ? {
            images: [],
            imagePreviews: [],
            response: null,
            originalResponse: null,
            originalAdvisory: "",
            sourceLanguage: "en",
            text: "",
            audioReady: false,
            audioData: null,
            cropModel: ""
          }
        : formType === 'advisory'
        ? {
            cropName: "",
            location: "",
            soilType: "",
            query: "",
            season: "kharif",
            response: null,
            audioReady: false,
            audioData: null
          }
        : {
            cropName: "",
            location: "Telangana, India",
            response: null,
            audioReady: false,
            audioData: null
          }
    }));
  }, []);

  return (
    <FormStateContext.Provider value={{
      formStates,
      saveFormState,
      getFormState,
      clearFormState
    }}>
      {children}
    </FormStateContext.Provider>
  );
};

export const useFormState = (formType) => {
  const context = React.useContext(FormStateContext);
  if (!context) {
    throw new Error('useFormState must be used within FormStateProvider');
  }
  return {
    state: context.getFormState(formType),
    saveState: (newState) => context.saveFormState(formType, newState),
    clearState: () => context.clearFormState(formType)
  };
};
