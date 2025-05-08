import React, { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

interface TileUploaderProps {
  onUploadComplete?: (result: any) => void;
}

const TileUploader: React.FC<TileUploaderProps> = ({ onUploadComplete }) => {
  // State for file upload
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<any | null>(null);
  
  // State for tile sources
  const [tileSources, setTileSources] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  
  // Fetch tile sources on component mount
  useEffect(() => {
    fetchTileSources();
  }, []);
  
  // Dropzone configuration
  const { getRootProps, getInputProps } = useDropzone({
    accept: {
      'application/octet-stream': ['.mbtiles', '.pmtiles'],
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setUploadedFile(acceptedFiles[0]);
      }
    },
  });
  
  // Fetch available tile sources
  const fetchTileSources = async () => {
    setIsLoading(true);
    setLoadError(null);
    
    try {
      const response = await axios.get('/api/v1/tiles/sources');
      setTileSources(response.data);
    } catch (error: any) {
      console.error('Error fetching tile sources:', error);
      setLoadError(error.response?.data?.detail || 'Error fetching tile sources');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle file upload
  const handleUpload = async () => {
    if (!uploadedFile) {
      setUploadError('Please select a file to upload');
      return;
    }
    
    setIsUploading(true);
    setUploadError(null);
    setUploadSuccess(null);
    
    const formData = new FormData();
    formData.append('file', uploadedFile);
    formData.append('tile_type', uploadedFile.name.endsWith('.pmtiles') ? 'pmtiles' : 'mbtiles');
    formData.append('name', uploadedFile.name.split('.')[0]);
    
    try {
      const response = await axios.post('/api/v1/tiles/upload', formData);
      setUploadSuccess(response.data);
      
      if (onUploadComplete) {
        onUploadComplete(response.data);
      }
      
      // Refresh the list of tile sources
      fetchTileSources();
    } catch (error: any) {
      console.error('Error uploading file:', error);
      setUploadError(error.response?.data?.detail || 'Error uploading file');
    } finally {
      setIsUploading(false);
    }
  };
  
  // Handle tile source deletion
  const handleDelete = async (name: string) => {
    if (!confirm(`Are you sure you want to delete the tile source "${name}"?`)) {
      return;
    }
    
    try {
      await axios.delete(`/api/v1/tiles/sources/${name}`);
      
      // Refresh the list of tile sources
      fetchTileSources();
    } catch (error: any) {
      console.error('Error deleting tile source:', error);
      alert(error.response?.data?.detail || 'Error deleting tile source');
    }
  };
  
  // Handle conversion to GeoPackage
  const handleConvertToGpkg = async (source: any) => {
    try {
      const formData = new FormData();
      formData.append('source_path', source.file_path);
      formData.append('source_type', source.tile_type);
      formData.append('output_name', source.name);
      
      // Add all zoom levels
      if (source.metadata && source.metadata.minzoom !== undefined && source.metadata.maxzoom !== undefined) {
        for (let z = source.metadata.minzoom; z <= source.metadata.maxzoom; z++) {
          formData.append('zoom_levels', z.toString());
        }
      }
      
      const response = await axios.post('/api/v1/tippecanoe/convert-to-gpkg', formData);
      
      // Open download link
      window.open(`/api/v1/tippecanoe/download-gpkg/${response.data.name}`, '_blank');
    } catch (error: any) {
      console.error('Error converting to GeoPackage:', error);
      alert(error.response?.data?.detail || 'Error converting to GeoPackage');
    }
  };
  
  return (
    <div className="tile-uploader">
      <div className="uploader-section">
        <h2>Upload Tile File</h2>
        
        <div {...getRootProps({ className: 'dropzone' })}>
          <input {...getInputProps()} />
          <p>Drag & drop a PMTiles or MBTiles file here, or click to select a file</p>
          {uploadedFile && (
            <div className="file-info">
              <p><strong>Selected file:</strong> {uploadedFile.name}</p>
              <p><strong>Size:</strong> {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          )}
        </div>
        
        <button 
          className="upload-button" 
          onClick={handleUpload}
          disabled={!uploadedFile || isUploading}
        >
          {isUploading ? 'Uploading...' : 'Upload File'}
        </button>
        
        {uploadError && (
          <div className="error-message">{uploadError}</div>
        )}
        
        {uploadSuccess && (
          <div className="success-message">
            <p>File uploaded successfully!</p>
            <p><strong>Name:</strong> {uploadSuccess.name}</p>
            <p><strong>Type:</strong> {uploadSuccess.tile_type}</p>
            <p><strong>Size:</strong> {(uploadSuccess.size_bytes / 1024 / 1024).toFixed(2)} MB</p>
          </div>
        )}
      </div>
      
      <div className="sources-section">
        <h2>Available Tile Sources</h2>
        
        {isLoading && <div className="loading">Loading tile sources...</div>}
        
        {loadError && (
          <div className="error-message">{loadError}</div>
        )}
        
        {tileSources.length === 0 && !isLoading ? (
          <div className="no-sources">No tile sources available</div>
        ) : (
          <div className="sources-list">
            {tileSources.map((source, index) => (
              <div key={index} className="source-item">
                <div className="source-info">
                  <h3>{source.name}</h3>
                  <p><strong>Type:</strong> {source.tile_type}</p>
                  <p><strong>Size:</strong> {(source.size_bytes / 1024 / 1024).toFixed(2)} MB</p>
                  {source.metadata && (
                    <>
                      <p><strong>Format:</strong> {source.metadata.format || 'Unknown'}</p>
                      <p><strong>Zoom Levels:</strong> {source.metadata.minzoom || 0} - {source.metadata.maxzoom || 0}</p>
                    </>
                  )}
                </div>
                
                <div className="source-actions">
                  <button 
                    className="action-button view-button"
                    onClick={() => window.open(source.url.replace('{z}/{x}/{y}', '0/0/0'), '_blank')}
                  >
                    View Tile
                  </button>
                  
                  <button 
                    className="action-button convert-button"
                    onClick={() => handleConvertToGpkg(source)}
                  >
                    Convert to GPKG
                  </button>
                  
                  <button 
                    className="action-button delete-button"
                    onClick={() => handleDelete(source.name)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <style jsx>{`
        .tile-uploader {
          max-width: 800px;
          margin: 0 auto;
        }
        
        .uploader-section, .sources-section {
          margin-bottom: 2rem;
          padding: 1.5rem;
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        h2 {
          margin-top: 0;
          margin-bottom: 1.5rem;
          font-size: 1.5rem;
        }
        
        .dropzone {
          border: 2px dashed #ccc;
          border-radius: 4px;
          padding: 2rem;
          text-align: center;
          cursor: pointer;
          margin-bottom: 1.5rem;
          transition: border-color 0.3s;
        }
        
        .dropzone:hover {
          border-color: #0070f3;
        }
        
        .file-info {
          margin-top: 1rem;
          padding: 1rem;
          background-color: #f8f9fa;
          border-radius: 4px;
        }
        
        .file-info p {
          margin: 0.25rem 0;
        }
        
        .upload-button {
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          padding: 0.75rem 1.5rem;
          font-size: 1rem;
          cursor: pointer;
          transition: background-color 0.3s;
          width: 100%;
        }
        
        .upload-button:hover {
          background-color: #0051a8;
        }
        
        .upload-button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
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
        
        .no-sources {
          text-align: center;
          padding: 2rem;
          color: #666;
          background-color: #f8f9fa;
          border-radius: 4px;
        }
        
        .sources-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        
        .source-item {
          border: 1px solid #eee;
          border-radius: 4px;
          padding: 1rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        
        @media (min-width: 768px) {
          .source-item {
            flex-direction: row;
            justify-content: space-between;
            align-items: center;
          }
        }
        
        .source-info {
          flex: 1;
        }
        
        .source-info h3 {
          margin-top: 0;
          margin-bottom: 0.5rem;
          font-size: 1.2rem;
        }
        
        .source-info p {
          margin: 0.25rem 0;
          font-size: 0.9rem;
        }
        
        .source-actions {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }
        
        @media (min-width: 768px) {
          .source-actions {
            flex-direction: column;
          }
        }
        
        .action-button {
          padding: 0.5rem 1rem;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.9rem;
          white-space: nowrap;
        }
        
        .view-button {
          background-color: #e9ecef;
          color: #495057;
        }
        
        .convert-button {
          background-color: #28a745;
          color: white;
        }
        
        .delete-button {
          background-color: #dc3545;
          color: white;
        }
      `}</style>
    </div>
  );
};

export default TileUploader;
