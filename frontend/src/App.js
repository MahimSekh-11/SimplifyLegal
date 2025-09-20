import React, { useState } from 'react';
import DocumentUpload from './components/DocumentUpload';
import DocumentAnalysis from './components/DocumentAnalysis';
import LanguageSelector from './components/LanguageSelector';
import './App.css';

const API_URL = 'https://simplifylegal-9.onrender.com' || 'http://localhost:8000';

function App() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [language, setLanguage] = useState('en');

  // Handle file upload or generic analysis
  const handleAnalysis = async (text) => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("text", text);
      formData.append("language", language);

      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Optional: handle text input specifically
  const handleTextAnalysis = async (text) => {
    await handleAnalysis(text);
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>LegalSimplify</h1>
        <p>Making Legal Documents Simple, Clear & Accessible for Everyone</p>
      </header>

      <div className="app-container">
        <div className="language-selector-container">
          <LanguageSelector 
            selectedLanguage={language} 
            onLanguageChange={setLanguage} 
          />
        </div>

        {!analysis ? (
          <DocumentUpload 
            onAnalysis={handleAnalysis}
            onTextAnalysis={handleTextAnalysis}
            loading={loading}
          />
        ) : (
          <DocumentAnalysis 
            analysis={analysis}
            onReset={() => setAnalysis(null)}
            language={language}
          />
        )}

        {error && (
          <div className="error-message">
            <p>{error}</p>
            <button onClick={() => setError(null)}>Dismiss</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

