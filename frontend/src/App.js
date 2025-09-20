import React, { useState } from 'react';
import DocumentUpload from './components/DocumentUpload';
import DocumentAnalysis from './components/DocumentAnalysis';
import LanguageSelector from './components/LanguageSelector';
import './App.css';

// ✅ Fix: don't use `||` for API URL. Use env var fallback for Render
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [language, setLanguage] = useState('en');

  // ✅ Handles file OR text input based on type
  const handleAnalysis = async ({ file, text }) => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();

      if (file) {
        // Upload actual file
        formData.append("file", file);
      } else if (text) {
        // Send plain text
        formData.append("text", text);
      }

      formData.append("language", language);

      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Analysis failed: ${response.status} - ${errText}`);
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ✅ Wrapper for text analysis
  const handleTextAnalysis = async (text) => {
    await handleAnalysis({ text });
  };

  // ✅ Wrapper for file analysis
  const handleFileAnalysis = async (file) => {
    await handleAnalysis({ file });
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
            onFileAnalysis={handleFileAnalysis}
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
