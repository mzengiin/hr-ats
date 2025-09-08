/**
 * Loading Spinner Component
 */
import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = ({ 
  size = 'medium', 
  message = 'Loading...', 
  overlay = false 
}) => {
  const sizeClass = `spinner-${size}`;
  
  if (overlay) {
    return (
      <div className="loading-overlay">
        <div className="loading-content">
          <div className={`spinner ${sizeClass}`}></div>
          {message && <p className="loading-message">{message}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="loading-container">
      <div className={`spinner ${sizeClass}`}></div>
      {message && <p className="loading-message">{message}</p>}
    </div>
  );
};

export default LoadingSpinner;








