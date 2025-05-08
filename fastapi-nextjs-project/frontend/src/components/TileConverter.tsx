import React, { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

interface TileConverterProps {
  onConversionComplete?: (result: any) => void;
}

const TileConverter: React.FC<TileConverterProps> = ({ onConversionComplete }) => {
  // State for file upload
  const [geojsonFiles, setGeojsonFiles] = useState<any[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  
  // State for tile generation
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [tileOptions, setTileOptions] = useState({
    outputFormat: 'pmtiles',
    outputName: '',
    minZoom: 0,
    maxZoom: 14,
    layerName: '',
    simplification: 1,
    dropRate: 2.5,
    bufferSize: 5
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [generatedTiles, setGeneratedTiles] = useState<any | null>(null);
  
  // State for GeoPackage conversion
  const [isConverting, setIsConverting] = useState(false);
  const [conversionError, setConversionError] = useState<string | null>(null);
  const [convertedGpkg, setConvertedGpkg] = useState<any | null>(null);
  const [zoomLevels, setZoomLevels] = useState<number[]>([]);
  
  // Fetch existing GeoJSON files on component mount
  useEffect(() => {
    fetchGeojsonFiles();
  }, []);
  
  // Dropzone configuration for GeoJSON upload
  const { getRootProps, getInputProps } = useDropzone({
    accept: {
      'application/json': ['.json', '.geojson'],
    },
    onDrop: (acceptedFiles) => {
      handleFileUpload(acceptedFiles);
    },
  });
  
  // Fetch existing GeoJSON files
  const fetchGeojsonFiles = async () => {
    try {
      const response = await axios.get('/api/v1/tippecanoe/list-geojson');
      setGeojsonFiles(response.data);
    } catch (error) {
      console.error('Error fetching GeoJSON files:', error);
    }
  };
  
  // Handle file upload
  const handleFileUpload = async (files: File[]) => {
    setIsUploading(true);
    setUploadError(null);
    
    try {
      const uploadedFiles = [];
      
      for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('name', file.name.split('.')[0]);
        
        const response = await axios.post('/api/v1/tippecanoe/upload-geojson', formData);
        uploadedFiles.push(response.data);
      }
      
      setUploadedFiles(uploadedFiles);
      fetchGeojsonFiles();  // Refresh the list
    } catch (error: any) {
      console.error('Error uploading files:', error);
      setUploadError(error.response?.data?.detail || 'Error uploading files');
    } finally {
      setIsUploading(false);
    }
  };
  
  // Handle file selection for tile generation
  const handleFileSelection = (filePath: string) => {
    setSelectedFiles((prev) => {
      if (prev.includes(filePath)) {
        return prev.filter(f => f !== filePath);
      } else {
        return [...prev, filePath];
      }
    });
  };
  
  // Handle tile option changes
  const handleOptionChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target as HTMLInputElement;
    
    setTileOptions(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value
    }));
  };
  
  // Generate tiles
  const handleGenerateTiles = async () => {
    if (selectedFiles.length === 0) {
      setGenerationError('Please select at least one GeoJSON file');
      return;
    }
    
    if (!tileOptions.outputName) {
      setGenerationError('Please provide an output name');
      return;
    }
    
    setIsGenerating(true);
    setGenerationError(null);
    setGeneratedTiles(null);
    
    try {
      const formData = new FormData();
      
      // Add selected files
      selectedFiles.forEach(file => {
        formData.append('input_files', file);
      });
      
      // Add options
      formData.append('output_format', tileOptions.outputFormat);
      formData.append('output_name', tileOptions.outputName);
      
      if (tileOptions.minZoom !== undefined) {
        formData.append('min_zoom', tileOptions.minZoom.toString());
      }
      
      if (tileOptions.maxZoom !== undefined) {
        formData.append('max_zoom', tileOptions.maxZoom.toString());
      }
      
      if (tileOptions.layerName) {
        formData.append('layer_name', tileOptions.layerName);
      }
      
      if (tileOptions.simplification !== undefined) {
        formData.append('simplification', tileOptions.simplification.toString());
      }
      
      if (tileOptions.dropRate !== undefined) {
        formData.append('drop_rate', tileOptions.dropRate.toString());
      }
      
      if (tileOptions.bufferSize !== undefined) {
        formData.append('buffer_size', tileOptions.bufferSize.toString());
      }
      
      const response = await axios.post('/api/v1/tippecanoe/generate-tiles', formData);
      setGeneratedTiles(response.data);
      
      // Set zoom levels for GeoPackage conversion
      const minZoom = response.data.metadata.minzoom || 0;
      const maxZoom = response.data.metadata.maxzoom || 14;
      const levels = [];
      
      for (let z = minZoom; z <= maxZoom; z++) {
        levels.push(z);
      }
      
      setZoomLevels(levels);
    } catch (error: any) {
      console.error('Error generating tiles:', error);
      setGenerationError(error.response?.data?.detail || 'Error generating tiles');
    } finally {
      setIsGenerating(false);
    }
  };
  
  // Convert to GeoPackage
  const handleConvertToGpkg = async () => {
    if (!generatedTiles) {
      setConversionError('Please generate tiles first');
      return;
    }
    
    setIsConverting(true);
    setConversionError(null);
    setConvertedGpkg(null);
    
    try {
      const formData = new FormData();
      
      formData.append('source_path', generatedTiles.output_path);
      formData.append('source_type', generatedTiles.output_format);
      formData.append('output_name', generatedTiles.name);
      
      // Add selected zoom levels
      const selectedZoomLevels = zoomLevels.filter(z => document.getElementById(`zoom-${z}`)?.checked);
      
      if (selectedZoomLevels.length > 0) {
        selectedZoomLevels.forEach(z => {
          formData.append('zoom_levels', z.toString());
        });
      }
      
      const response = await axios.post('/api/v1/tippecanoe/convert-to-gpkg', formData);
      setConvertedGpkg(response.data);
      
      if (onConversionComplete) {
        onConversionComplete(response.data);
      }
    } catch (error: any) {
      console.error('Error converting to GeoPackage:', error);
      setConversionError(error.response?.data?.detail || 'Error converting to GeoPackage');
    } finally {
      setIsConverting(false);
    }
  };
  
  // Download GeoPackage
  const handleDownloadGpkg = () => {
    if (!convertedGpkg) return;
    
    window.open(`/api/v1/tippecanoe/download-gpkg/${convertedGpkg.name}`, '_blank');
  };
  
  return (
    <div className="tile-converter">
      <div className="converter-section">
        <h2>1. Upload GeoJSON Files</h2>
        
        <div {...getRootProps({ className: 'dropzone' })}>
          <input {...getInputProps()} />
          <p>Drag & drop GeoJSON files here, or click to select files</p>
        </div>
        
        {isUploading && <div className="loading">Uploading files...</div>}
        
        {uploadError && (
          <div className="error-message">{uploadError}</div>
        )}
        
        {uploadedFiles.length > 0 && (
          <div className="success-message">
            <p>Successfully uploaded {uploadedFiles.length} file(s)</p>
          </div>
        )}
        
        <div className="file-list">
          <h3>Available GeoJSON Files</h3>
          
          {geojsonFiles.length === 0 ? (
            <p>No GeoJSON files available</p>
          ) : (
            <ul>
              {geojsonFiles.map((file, index) => (
                <li key={index} className={selectedFiles.includes(file.file_path) ? 'selected' : ''}>
                  <label>
                    <input
                      type="checkbox"
                      checked={selectedFiles.includes(file.file_path)}
                      onChange={() => handleFileSelection(file.file_path)}
                    />
                    <span className="file-name">{file.name}</span>
                    <span className="file-size">({(file.size_bytes / 1024 / 1024).toFixed(2)} MB)</span>
                  </label>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
      
      <div className="converter-section">
        <h2>2. Generate Vector Tiles</h2>
        
        <div className="options-form">
          <div className="form-group">
            <label htmlFor="outputFormat">Output Format</label>
            <select
              id="outputFormat"
              name="outputFormat"
              value={tileOptions.outputFormat}
              onChange={handleOptionChange}
            >
              <option value="pmtiles">PMTiles</option>
              <option value="mbtiles">MBTiles</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="outputName">Output Name</label>
            <input
              type="text"
              id="outputName"
              name="outputName"
              value={tileOptions.outputName}
              onChange={handleOptionChange}
              placeholder="e.g., my_vector_tiles"
            />
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="minZoom">Min Zoom</label>
              <input
                type="number"
                id="minZoom"
                name="minZoom"
                value={tileOptions.minZoom}
                onChange={handleOptionChange}
                min="0"
                max="22"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="maxZoom">Max Zoom</label>
              <input
                type="number"
                id="maxZoom"
                name="maxZoom"
                value={tileOptions.maxZoom}
                onChange={handleOptionChange}
                min="0"
                max="22"
              />
            </div>
          </div>
          
          <div className="form-group">
            <label htmlFor="layerName">Layer Name (optional)</label>
            <input
              type="text"
              id="layerName"
              name="layerName"
              value={tileOptions.layerName}
              onChange={handleOptionChange}
              placeholder="e.g., my_layer"
            />
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="simplification">Simplification</label>
              <input
                type="number"
                id="simplification"
                name="simplification"
                value={tileOptions.simplification}
                onChange={handleOptionChange}
                min="0"
                step="0.1"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="dropRate">Drop Rate</label>
              <input
                type="number"
                id="dropRate"
                name="dropRate"
                value={tileOptions.dropRate}
                onChange={handleOptionChange}
                min="0"
                step="0.1"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="bufferSize">Buffer Size</label>
              <input
                type="number"
                id="bufferSize"
                name="bufferSize"
                value={tileOptions.bufferSize}
                onChange={handleOptionChange}
                min="0"
              />
            </div>
          </div>
          
          <button
            className="generate-button"
            onClick={handleGenerateTiles}
            disabled={isGenerating || selectedFiles.length === 0}
          >
            {isGenerating ? 'Generating...' : 'Generate Tiles'}
          </button>
        </div>
        
        {generationError && (
          <div className="error-message">{generationError}</div>
        )}
        
        {generatedTiles && (
          <div className="success-message">
            <h3>Tiles Generated Successfully</h3>
            <p>
              <strong>Name:</strong> {generatedTiles.name}
            </p>
            <p>
              <strong>Format:</strong> {generatedTiles.output_format}
            </p>
            <p>
              <strong>Size:</strong> {(generatedTiles.size_bytes / 1024 / 1024).toFixed(2)} MB
            </p>
            <p>
              <strong>Zoom Levels:</strong> {generatedTiles.metadata.minzoom} - {generatedTiles.metadata.maxzoom}
            </p>
          </div>
        )}
      </div>
      
      {generatedTiles && (
        <div className="converter-section">
          <h2>3. Convert to GeoPackage</h2>
          
          <div className="zoom-levels">
            <h3>Select Zoom Levels to Include</h3>
            
            <div className="zoom-checkboxes">
              {zoomLevels.map(z => (
                <label key={z} className="zoom-checkbox">
                  <input
                    type="checkbox"
                    id={`zoom-${z}`}
                    defaultChecked
                  />
                  {z}
                </label>
              ))}
            </div>
          </div>
          
          <button
            className="convert-button"
            onClick={handleConvertToGpkg}
            disabled={isConverting}
          >
            {isConverting ? 'Converting...' : 'Convert to GeoPackage'}
          </button>
          
          {conversionError && (
            <div className="error-message">{conversionError}</div>
          )}
          
          {convertedGpkg && (
            <div className="success-message">
              <h3>GeoPackage Created Successfully</h3>
              <p>
                <strong>Name:</strong> {convertedGpkg.name}
              </p>
              <p>
                <strong>Size:</strong> {(convertedGpkg.size_bytes / 1024 / 1024).toFixed(2)} MB
              </p>
              
              <button
                className="download-button"
                onClick={handleDownloadGpkg}
              >
                Download GeoPackage
              </button>
            </div>
          )}
        </div>
      )}
      
      <style jsx>{`
        .tile-converter {
          max-width: 800px;
          margin: 0 auto;
        }
        
        .converter-section {
          margin-bottom: 2rem;
          padding: 1.5rem;
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .converter-section h2 {
          margin-top: 0;
          margin-bottom: 1rem;
          font-size: 1.5rem;
          color: #333;
        }
        
        .dropzone {
          border: 2px dashed #ccc;
          border-radius: 4px;
          padding: 2rem;
          text-align: center;
          cursor: pointer;
          margin-bottom: 1rem;
          transition: border-color 0.3s;
        }
        
        .dropzone:hover {
          border-color: #0070f3;
        }
        
        .loading {
          text-align: center;
          margin: 1rem 0;
          color: #666;
        }
        
        .error-message {
          background-color: #f8d7da;
          color: #721c24;
          padding: 0.75rem;
          border-radius: 4px;
          margin: 1rem 0;
        }
        
        .success-message {
          background-color: #d4edda;
          color: #155724;
          padding: 0.75rem;
          border-radius: 4px;
          margin: 1rem 0;
        }
        
        .file-list {
          margin-top: 1.5rem;
        }
        
        .file-list h3 {
          margin-top: 0;
          margin-bottom: 0.5rem;
          font-size: 1.2rem;
        }
        
        .file-list ul {
          list-style: none;
          padding: 0;
          margin: 0;
          max-height: 200px;
          overflow-y: auto;
          border: 1px solid #eee;
          border-radius: 4px;
        }
        
        .file-list li {
          padding: 0.5rem;
          border-bottom: 1px solid #eee;
        }
        
        .file-list li:last-child {
          border-bottom: none;
        }
        
        .file-list li.selected {
          background-color: #e6f7ff;
        }
        
        .file-list label {
          display: flex;
          align-items: center;
          cursor: pointer;
        }
        
        .file-name {
          margin-left: 0.5rem;
          flex: 1;
        }
        
        .file-size {
          color: #666;
          font-size: 0.875rem;
        }
        
        .options-form {
          margin-top: 1rem;
        }
        
        .form-group {
          margin-bottom: 1rem;
        }
        
        .form-row {
          display: flex;
          gap: 1rem;
          margin-bottom: 1rem;
        }
        
        .form-row .form-group {
          flex: 1;
          margin-bottom: 0;
        }
        
        label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
        }
        
        input, select {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 1rem;
        }
        
        .generate-button, .convert-button, .download-button {
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          padding: 0.75rem 1.5rem;
          font-size: 1rem;
          cursor: pointer;
          transition: background-color 0.3s;
        }
        
        .generate-button:hover, .convert-button:hover, .download-button:hover {
          background-color: #0051a8;
        }
        
        .generate-button:disabled, .convert-button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }
        
        .download-button {
          margin-top: 1rem;
        }
        
        .zoom-levels {
          margin-bottom: 1.5rem;
        }
        
        .zoom-levels h3 {
          margin-top: 0;
          margin-bottom: 0.5rem;
          font-size: 1.2rem;
        }
        
        .zoom-checkboxes {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-top: 0.5rem;
        }
        
        .zoom-checkbox {
          display: flex;
          align-items: center;
          background-color: #f0f0f0;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          cursor: pointer;
        }
        
        .zoom-checkbox input {
          width: auto;
          margin-right: 0.25rem;
        }
      `}</style>
    </div>
  );
};

export default TileConverter;
