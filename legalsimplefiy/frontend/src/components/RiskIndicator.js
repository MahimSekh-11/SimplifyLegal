import React from 'react';

const RiskIndicator = ({ score }) => {
  const getColor = (score) => {
    if (score < 0.4) return '#4caf50'; // Green
    if (score < 0.7) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  return (
    <div className="risk-indicator">
      <div className="risk-meter">
        <div 
          className="risk-fill"
          style={{
            width: `${score * 100}%`,
            backgroundColor: getColor(score)
          }}
        ></div>
      </div>
    </div>
  );
};

export default RiskIndicator;