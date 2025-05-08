import React, { useState, useEffect } from 'react';
import axios from 'axios';
import StyleEditor from './StyleEditor';

interface StyleWizardProps {
  layer: any;
  onStyleChange: (style: any) => void;
}

const StyleWizard: React.FC<StyleWizardProps> = ({ layer, onStyleChange }) => {
  // State for style format
  const [styleFormat, setStyleFormat] = useState<'mapbox' | 'sld' | 'openlayers'>('mapbox');
  
  // State for current style
  const [currentStyle, setCurrentStyle] = useState<any>(null);
  
  // State for saved styles
  const [savedStyles, setSavedStyles] = useState<any[]>([]);
  
  // State for style name
  const [styleName, setStyleName] = useState<string>('');
  
  // State for loading
  const [isLoading, setIsLoading] = useState<boolean>(false);
  
  // State for error
  const [error, setError] = useState<string | null>(null);
  
  // State for success message
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  // Load saved styles on component mount
  useEffect(() => {
    if (layer) {
      loadSavedStyles();
    }
  }, [layer]);
  
  // Load saved styles
  const loadSavedStyles = async () => {
    if (!layer) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // In a real application, you would fetch styles from an API
      // For this demo, we'll use mock data
      const mockStyles = [
        {
          id: 1,
          name: 'Default Style',
          format: 'mapbox',
          style: {
            type: 'circle',
            paint: {
              'circle-radius': 5,
              'circle-color': '#3388ff',
              'circle-opacity': 0.7,
              'circle-stroke-width': 1,
              'circle-stroke-color': '#000000'
            }
          }
        },
        {
          id: 2,
          name: 'Red Style',
          format: 'mapbox',
          style: {
            type: 'circle',
            paint: {
              'circle-radius': 6,
              'circle-color': '#ff3333',
              'circle-opacity': 0.8,
              'circle-stroke-width': 1,
              'circle-stroke-color': '#000000'
            }
          }
        }
      ];
      
      setSavedStyles(mockStyles);
    } catch (error) {
      console.error('Error loading saved styles:', error);
      setError('Failed to load saved styles');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle style change
  const handleStyleChange = (style: any) => {
    setCurrentStyle(style);
    onStyleChange(style);
  };
  
  // Handle style format change
  const handleStyleFormatChange = (format: 'mapbox' | 'sld' | 'openlayers') => {
    setStyleFormat(format);
  };
  
  // Handle style save
  const handleSaveStyle = async () => {
    if (!currentStyle || !styleName) return;
    
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);
    
    try {
      // In a real application, you would save the style to an API
      // For this demo, we'll just add it to the local state
      const newStyle = {
        id: Date.now(),
        name: styleName,
        format: styleFormat,
        style: currentStyle
      };
      
      setSavedStyles(prev => [...prev, newStyle]);
      setStyleName('');
      setSuccessMessage('Style saved successfully!');
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (error) {
      console.error('Error saving style:', error);
      setError('Failed to save style');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle style load
  const handleLoadStyle = (style: any) => {
    setCurrentStyle(style.style);
    onStyleChange(style.style);
    setStyleFormat(style.format);
  };
  
  // Handle style delete
  const handleDeleteStyle = async (id: number) => {
    if (!confirm('Are you sure you want to delete this style?')) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // In a real application, you would delete the style from an API
      // For this demo, we'll just remove it from the local state
      setSavedStyles(prev => prev.filter(style => style.id !== id));
      setSuccessMessage('Style deleted successfully!');
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (error) {
      console.error('Error deleting style:', error);
      setError('Failed to delete style');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle style export
  const handleExportStyle = (format: 'sld' | 'mapbox' | 'openlayers') => {
    if (!currentStyle) return;
    
    // In a real application, you would convert the style to the requested format
    // For this demo, we'll just download the current style as JSON
    
    const styleData = JSON.stringify(currentStyle, null, 2);
    const blob = new Blob([styleData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `${layer.name || 'style'}.${format === 'sld' ? 'sld' : 'json'}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  
  return (
    <div className="style-wizard">
      <div className="wizard-header">
        <h2>Style Wizard</h2>
        <div className="format-selector">
          <label>Format:</label>
          <select
            value={styleFormat}
            onChange={(e) => handleStyleFormatChange(e.target.value as any)}
          >
            <option value="mapbox">MapBox GL</option>
            <option value="sld">SLD</option>
            <option value="openlayers">OpenLayers</option>
          </select>
        </div>
      </div>
      
      <div className="wizard-content">
        <StyleEditor
          layer={layer}
          onStyleChange={handleStyleChange}
          outputFormat={styleFormat}
        />
      </div>
      
      <div className="wizard-actions">
        <div className="save-style">
          <input
            type="text"
            placeholder="Style name"
            value={styleName}
            onChange={(e) => setStyleName(e.target.value)}
          />
          <button
            className="save-button"
            onClick={handleSaveStyle}
            disabled={!currentStyle || !styleName || isLoading}
          >
            {isLoading ? 'Saving...' : 'Save Style'}
          </button>
        </div>
        
        <div className="export-style">
          <button
            className="export-button"
            onClick={() => handleExportStyle('mapbox')}
            disabled={!currentStyle || isLoading}
          >
            Export MapBox
          </button>
          <button
            className="export-button"
            onClick={() => handleExportStyle('sld')}
            disabled={!currentStyle || isLoading}
          >
            Export SLD
          </button>
          <button
            className="export-button"
            onClick={() => handleExportStyle('openlayers')}
            disabled={!currentStyle || isLoading}
          >
            Export OpenLayers
          </button>
        </div>
      </div>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      {successMessage && (
        <div className="success-message">
          {successMessage}
        </div>
      )}
      
      <div className="saved-styles">
        <h3>Saved Styles</h3>
        
        {savedStyles.length === 0 ? (
          <div className="no-styles">No saved styles</div>
        ) : (
          <ul className="styles-list">
            {savedStyles.map(style => (
              <li key={style.id} className="style-item">
                <div className="style-info">
                  <div className="style-name">{style.name}</div>
                  <div className="style-format">{style.format}</div>
                </div>
                <div className="style-actions">
                  <button
                    className="load-button"
                    onClick={() => handleLoadStyle(style)}
                  >
                    Load
                  </button>
                  <button
                    className="delete-button"
                    onClick={() => handleDeleteStyle(style.id)}
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
      
      <style jsx>{`
        .style-wizard {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 1.5rem;
          max-width: 100%;
        }
        
        .wizard-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }
        
        .wizard-header h2 {
          margin: 0;
          font-size: 1.5rem;
        }
        
        .format-selector {
          display: flex;
          align-items: center;
        }
        
        .format-selector label {
          margin-right: 0.5rem;
          font-weight: 500;
        }
        
        .format-selector select {
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.9rem;
        }
        
        .wizard-content {
          margin-bottom: 1.5rem;
        }
        
        .wizard-actions {
          display: flex;
          justify-content: space-between;
          margin-bottom: 1.5rem;
        }
        
        .save-style {
          display: flex;
          gap: 0.5rem;
          flex: 1;
          max-width: 400px;
        }
        
        .save-style input {
          flex: 1;
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.9rem;
        }
        
        .save-button {
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          padding: 0.5rem 1rem;
          font-size: 0.9rem;
          cursor: pointer;
        }
        
        .save-button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }
        
        .export-style {
          display: flex;
          gap: 0.5rem;
        }
        
        .export-button {
          background-color: #f0f0f0;
          color: #333;
          border: 1px solid #ddd;
          border-radius: 4px;
          padding: 0.5rem 1rem;
          font-size: 0.9rem;
          cursor: pointer;
        }
        
        .export-button:hover {
          background-color: #e0e0e0;
        }
        
        .export-button:disabled {
          background-color: #f0f0f0;
          color: #999;
          cursor: not-allowed;
        }
        
        .error-message {
          background-color: #f8d7da;
          color: #721c24;
          padding: 0.75rem;
          border-radius: 4px;
          margin-bottom: 1.5rem;
        }
        
        .success-message {
          background-color: #d4edda;
          color: #155724;
          padding: 0.75rem;
          border-radius: 4px;
          margin-bottom: 1.5rem;
        }
        
        .saved-styles {
          border-top: 1px solid #eee;
          padding-top: 1.5rem;
        }
        
        .saved-styles h3 {
          margin-top: 0;
          margin-bottom: 1rem;
          font-size: 1.2rem;
        }
        
        .no-styles {
          color: #666;
          font-style: italic;
        }
        
        .styles-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        
        .style-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem;
          border: 1px solid #eee;
          border-radius: 4px;
          margin-bottom: 0.5rem;
        }
        
        .style-info {
          flex: 1;
        }
        
        .style-name {
          font-weight: 500;
          margin-bottom: 0.25rem;
        }
        
        .style-format {
          font-size: 0.8rem;
          color: #666;
          text-transform: uppercase;
        }
        
        .style-actions {
          display: flex;
          gap: 0.5rem;
        }
        
        .load-button {
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          padding: 0.25rem 0.5rem;
          font-size: 0.8rem;
          cursor: pointer;
        }
        
        .delete-button {
          background-color: #dc3545;
          color: white;
          border: none;
          border-radius: 4px;
          padding: 0.25rem 0.5rem;
          font-size: 0.8rem;
          cursor: pointer;
        }
      `}</style>
    </div>
  );
};

export default StyleWizard;
