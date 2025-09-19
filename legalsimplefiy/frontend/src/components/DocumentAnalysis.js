import React from 'react';
import RiskIndicator from './RiskIndicator';

const DocumentAnalysis = ({ analysis, onReset, language }) => {
  const getRiskLevel = (score) => {
    if (score < 0.4) return 'Low Risk';
    if (score < 0.7) return 'Medium Risk';
    return 'High Risk';
  };

  return (
    <div className="document-analysis">
      <div className="analysis-header">
        <h2>Document Analysis</h2>
        <button onClick={onReset}>Analyze Another Document</button>
      </div>
      
      <div className="risk-summary">
        <h3>Risk Assessment</h3>
        <div className="risk-display">
          <RiskIndicator score={analysis.risk_score} />
          <div className="risk-details">
            <p className="risk-level">{getRiskLevel(analysis.risk_score)}</p>
            <p className="risk-score">Score: {(analysis.risk_score * 100).toFixed(0)}/100</p>
          </div>
        </div>
      </div>
      
      <div className="analysis-section">
        <h3>Summary</h3>
        <p>{analysis.summary}</p>
      </div>
      
      <div className="analysis-section">
        <h3>Plain Language Explanation</h3>
        <p>{analysis.plain_language}</p>
      </div>
      
      {analysis.clauses && analysis.clauses.length > 0 && (
        <div className="analysis-section">
          <h3>Key Clauses</h3>
          <div className="clauses-list">
            {analysis.clauses.map((clause, index) => (
              <div key={index} className={`clause ${clause.risk_level}`}>
                <h4>{clause.type.replace(/_/g, ' ').toUpperCase()}</h4>
                <p className="clause-description">{clause.description}</p>
                <p className="clause-explanation">{clause.explanation}</p>
                <span className={`risk-badge ${clause.risk_level}`}>
                  {clause.risk_level.toUpperCase()} RISK
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="analysis-section">
        <h3>Recommended Actions</h3>
        <ul className="recommended-actions">
          {analysis.recommended_actions.map((action, index) => (
            <li key={index}>{action}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default DocumentAnalysis;