import React, { useState } from 'react';

const DocumentUpload = ({ onAnalysis, onTextAnalysis, loading }) => {
  const [activeTab, setActiveTab] = useState('upload');
  const [textInput, setTextInput] = useState('');

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    onAnalysis(formData);
  };

  const handleTextSubmit = () => {
    if (textInput.trim()) {
      onTextAnalysis(textInput);
    }
  };

  return (
    <div className="document-upload">
      <div className="upload-tabs">
        <button 
          className={activeTab === 'upload' ? 'active' : ''}
          onClick={() => setActiveTab('upload')}
        >
          Upload Document
        </button>
        <button 
          className={activeTab === 'text' ? 'active' : ''}
          onClick={() => setActiveTab('text')}
        >
          Paste Text
        </button>
      </div>
      
      <div className="upload-content">
        {activeTab === 'upload' ? (
          <div className="file-upload">
            <div className="upload-area">
              <input
                type="file"
                id="file-upload"
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleFileUpload}
                disabled={loading}
              />
              <label htmlFor="file-upload" className="upload-label">
                {loading ? 'Processing...' : 'Choose a file or drag it here'}
              </label>
              <p className="upload-hint">Supported formats: PDF, DOC, DOCX, TXT</p>
            </div>
          </div>
        ) : (
          <div className="text-upload">
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Paste your legal document text here..."
              disabled={loading}
            />
            <button 
              onClick={handleTextSubmit}
              disabled={loading || !textInput.trim()}
            >
              {loading ? 'Analyzing...' : 'Analyze Text'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentUpload;