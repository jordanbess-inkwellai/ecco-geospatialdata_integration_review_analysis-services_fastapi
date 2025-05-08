import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface BoxIntegrationProps {
  onFileSelect?: (fileInfo: any) => void;
}

const BoxIntegration: React.FC<BoxIntegrationProps> = ({ onFileSelect }) => {
  // State for authentication
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [accessToken, setAccessToken] = useState<string>('');
  const [authError, setAuthError] = useState<string | null>(null);
  
  // State for folder navigation
  const [currentFolder, setCurrentFolder] = useState<any>({ id: '0', name: 'All Files' });
  const [folderContents, setFolderContents] = useState<any[]>([]);
  const [folderPath, setFolderPath] = useState<any[]>([{ id: '0', name: 'All Files' }]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  
  // State for file details
  const [selectedFile, setSelectedFile] = useState<any | null>(null);
  const [fileMetadata, setFileMetadata] = useState<any | null>(null);
  const [fileAnalysis, setFileAnalysis] = useState<any | null>(null);
  
  // State for authentication form
  const [clientId, setClientId] = useState<string>('');
  const [clientSecret, setClientSecret] = useState<string>('');
  const [authCode, setAuthCode] = useState<string>('');
  
  // Mock authentication for demo purposes
  const handleAuthenticate = async () => {
    setAuthError(null);
    
    try {
      // In a real implementation, this would make an API call to Box.com
      // For this demo, we'll use mock authentication
      
      if (!clientId || !clientSecret) {
        setAuthError('Client ID and Client Secret are required');
        return;
      }
      
      // Mock API call
      const response = await axios.post('/api/v1/box/authenticate', {
        client_id: clientId,
        client_secret: clientSecret,
        auth_code: authCode || undefined
      });
      
      setAccessToken(response.data.access_token);
      setIsAuthenticated(true);
      
      // Load root folder
      loadFolder('0');
    } catch (error: any) {
      console.error('Authentication error:', error);
      setAuthError(error.response?.data?.detail || 'Authentication failed');
    }
  };
  
  // Load folder contents
  const loadFolder = async (folderId: string) => {
    if (!isAuthenticated || !accessToken) return;
    
    setIsLoading(true);
    setLoadError(null);
    
    try {
      const response = await axios.get(`/api/v1/box/folders/${folderId}`, {
        params: { access_token: accessToken }
      });
      
      setFolderContents(response.data.items || []);
      
      // Update current folder
      const folder = {
        id: response.data.id,
        name: response.data.name
      };
      
      setCurrentFolder(folder);
      
      // Update folder path
      if (folderId === '0') {
        // Root folder
        setFolderPath([folder]);
      } else {
        // Check if folder is already in path (navigating back)
        const existingIndex = folderPath.findIndex(f => f.id === folderId);
        
        if (existingIndex >= 0) {
          // Navigating back, truncate path
          setFolderPath(folderPath.slice(0, existingIndex + 1));
        } else {
          // Navigating forward, add to path
          setFolderPath([...folderPath, folder]);
        }
      }
    } catch (error: any) {
      console.error('Error loading folder:', error);
      setLoadError(error.response?.data?.detail || 'Error loading folder');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Get file details
  const getFileDetails = async (fileId: string) => {
    if (!isAuthenticated || !accessToken) return;
    
    setIsLoading(true);
    setLoadError(null);
    
    try {
      // Get file info
      const fileResponse = await axios.get(`/api/v1/box/files/${fileId}`, {
        params: { access_token: accessToken }
      });
      
      setSelectedFile(fileResponse.data);
      
      // Get file metadata
      const metadataResponse = await axios.get(`/api/v1/box/files/${fileId}/metadata`, {
        params: { access_token: accessToken }
      });
      
      setFileMetadata(metadataResponse.data);
      
      // Scan file metadata
      const scanResponse = await axios.get(`/api/v1/box/files/${fileId}/scan`, {
        params: { access_token: accessToken }
      });
      
      // Analyze file
      const analysisResponse = await axios.post(`/api/v1/box/files/${fileId}/analyze`, null, {
        params: { access_token: accessToken }
      });
      
      setFileAnalysis(analysisResponse.data);
      
      // Notify parent component if callback provided
      if (onFileSelect) {
        onFileSelect({
          file: fileResponse.data,
          metadata: metadataResponse.data,
          analysis: analysisResponse.data
        });
      }
    } catch (error: any) {
      console.error('Error getting file details:', error);
      setLoadError(error.response?.data?.detail || 'Error getting file details');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Import file to DuckDB
  const importToDuckDB = async (fileId: string, dbName: string) => {
    if (!isAuthenticated || !accessToken) return;
    
    setIsLoading(true);
    setLoadError(null);
    
    try {
      const response = await axios.post(`/api/v1/box/files/${fileId}/import-to-duckdb`, 
        { db_name: dbName },
        { params: { access_token: accessToken } }
      );
      
      alert(`File imported to DuckDB successfully: ${response.data.db_name}`);
    } catch (error: any) {
      console.error('Error importing to DuckDB:', error);
      setLoadError(error.response?.data?.detail || 'Error importing to DuckDB');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle folder click
  const handleFolderClick = (folder: any) => {
    loadFolder(folder.id);
  };
  
  // Handle file click
  const handleFileClick = (file: any) => {
    getFileDetails(file.id);
  };
  
  // Handle breadcrumb click
  const handleBreadcrumbClick = (folder: any, index: number) => {
    loadFolder(folder.id);
  };
  
  // Render file icon based on extension
  const renderFileIcon = (file: any) => {
    const extension = file.extension?.toLowerCase() || '';
    
    if (['geojson', 'json', 'shp', 'gpkg', 'kml'].includes(extension)) {
      return <span className="material-icons">map</span>;
    } else if (['tif', 'tiff', 'jpg', 'jpeg', 'png'].includes(extension)) {
      return <span className="material-icons">image</span>;
    } else if (['pdf'].includes(extension)) {
      return <span className="material-icons">picture_as_pdf</span>;
    } else if (['xlsx', 'xls', 'csv'].includes(extension)) {
      return <span className="material-icons">table_chart</span>;
    } else if (['dxf', 'dwg'].includes(extension)) {
      return <span className="material-icons">architecture</span>;
    } else {
      return <span className="material-icons">insert_drive_file</span>;
    }
  };
  
  return (
    <div className="box-integration">
      {!isAuthenticated ? (
        <div className="auth-form">
          <h2>Connect to Box.com</h2>
          <p>Enter your Box.com API credentials to connect to your account.</p>
          
          <div className="form-group">
            <label htmlFor="clientId">Client ID</label>
            <input
              type="text"
              id="clientId"
              value={clientId}
              onChange={(e) => setClientId(e.target.value)}
              placeholder="Enter Box Client ID"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="clientSecret">Client Secret</label>
            <input
              type="password"
              id="clientSecret"
              value={clientSecret}
              onChange={(e) => setClientSecret(e.target.value)}
              placeholder="Enter Box Client Secret"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="authCode">Authorization Code (Optional)</label>
            <input
              type="text"
              id="authCode"
              value={authCode}
              onChange={(e) => setAuthCode(e.target.value)}
              placeholder="Enter Authorization Code"
            />
          </div>
          
          {authError && (
            <div className="error-message">{authError}</div>
          )}
          
          <button
            className="connect-button"
            onClick={handleAuthenticate}
          >
            Connect to Box
          </button>
          
          <div className="auth-note">
            <p>
              <strong>Note:</strong> For this demo, any credentials will work as we're using mock data.
              In a real implementation, you would need to register an app in the Box Developer Console.
            </p>
          </div>
        </div>
      ) : (
        <div className="box-explorer">
          <div className="explorer-header">
            <h2>Box.com Explorer</h2>
            
            <div className="breadcrumbs">
              {folderPath.map((folder, index) => (
                <React.Fragment key={folder.id}>
                  {index > 0 && <span className="breadcrumb-separator">/</span>}
                  <span
                    className="breadcrumb-item"
                    onClick={() => handleBreadcrumbClick(folder, index)}
                  >
                    {folder.name}
                  </span>
                </React.Fragment>
              ))}
            </div>
          </div>
          
          <div className="explorer-content">
            <div className="file-list">
              {isLoading ? (
                <div className="loading">Loading...</div>
              ) : loadError ? (
                <div className="error-message">{loadError}</div>
              ) : folderContents.length === 0 ? (
                <div className="empty-folder">This folder is empty</div>
              ) : (
                <ul>
                  {folderContents.map((item) => (
                    <li
                      key={item.id}
                      className={`file-item ${item.type} ${selectedFile?.id === item.id ? 'selected' : ''}`}
                      onClick={() => item.type === 'folder' ? handleFolderClick(item) : handleFileClick(item)}
                    >
                      {item.type === 'folder' ? (
                        <span className="material-icons">folder</span>
                      ) : (
                        renderFileIcon(item)
                      )}
                      <span className="file-name">{item.name}</span>
                      {item.type === 'file' && (
                        <span className="file-size">
                          {(item.size / 1024 / 1024).toFixed(2)} MB
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
            
            {selectedFile && (
              <div className="file-details">
                <h3>{selectedFile.name}</h3>
                
                <div className="file-info">
                  <div className="info-item">
                    <span className="info-label">Type:</span>
                    <span className="info-value">{selectedFile.extension?.toUpperCase()}</span>
                  </div>
                  
                  <div className="info-item">
                    <span className="info-label">Size:</span>
                    <span className="info-value">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</span>
                  </div>
                  
                  <div className="info-item">
                    <span className="info-label">Modified:</span>
                    <span className="info-value">
                      {new Date(selectedFile.modified_at).toLocaleDateString()}
                    </span>
                  </div>
                  
                  <div className="info-item">
                    <span className="info-label">Created:</span>
                    <span className="info-value">
                      {new Date(selectedFile.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                
                {fileMetadata?.has_metadata && (
                  <div className="metadata-section">
                    <h4>Box Metadata</h4>
                    
                    {Object.entries(fileMetadata.metadata).map(([scope, templates]: [string, any]) => (
                      <div key={scope} className="metadata-scope">
                        <h5>{scope}</h5>
                        
                        {Object.entries(templates).map(([templateKey, fields]: [string, any]) => (
                          <div key={templateKey} className="metadata-template">
                            <h6>{templateKey}</h6>
                            
                            <ul className="metadata-fields">
                              {Object.entries(fields).map(([field, value]: [string, any]) => (
                                <li key={field} className="metadata-field">
                                  <span className="field-name">{field}:</span>
                                  <span className="field-value">
                                    {typeof value === 'object' ? JSON.stringify(value) : value}
                                  </span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                )}
                
                {fileAnalysis && (
                  <div className="analysis-section">
                    <h4>File Analysis</h4>
                    
                    <div className="analysis-info">
                      <div className="info-item">
                        <span className="info-label">File Type:</span>
                        <span className="info-value">{fileAnalysis.file_type}</span>
                      </div>
                      
                      {fileAnalysis.feature_stats && (
                        <div className="info-item">
                          <span className="info-label">Features:</span>
                          <span className="info-value">{fileAnalysis.feature_stats.count}</span>
                        </div>
                      )}
                      
                      {fileAnalysis.spatial_stats && (
                        <div className="info-item">
                          <span className="info-label">Spatial Reference:</span>
                          <span className="info-value">{fileAnalysis.spatial_stats.spatial_reference}</span>
                        </div>
                      )}
                    </div>
                    
                    {fileAnalysis.recommendations && (
                      <div className="recommendations">
                        <h5>Recommendations</h5>
                        
                        <ul>
                          {fileAnalysis.recommendations.map((rec: any, index: number) => (
                            <li key={index} className={rec.needed ? 'needed' : ''}>
                              {rec.description}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
                
                <div className="file-actions">
                  <button
                    className="action-button analyze-button"
                    onClick={() => getFileDetails(selectedFile.id)}
                  >
                    Analyze
                  </button>
                  
                  <button
                    className="action-button import-button"
                    onClick={() => importToDuckDB(selectedFile.id, `box_${selectedFile.name.split('.')[0]}`)}
                  >
                    Import to DuckDB
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      
      <style jsx>{`
        .box-integration {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 1.5rem;
          max-width: 100%;
        }
        
        .auth-form {
          max-width: 500px;
          margin: 0 auto;
        }
        
        .auth-form h2 {
          margin-top: 0;
          margin-bottom: 0.5rem;
          font-size: 1.5rem;
        }
        
        .auth-form p {
          margin-bottom: 1.5rem;
          color: #666;
        }
        
        .form-group {
          margin-bottom: 1rem;
        }
        
        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
        }
        
        .form-group input {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 1rem;
        }
        
        .connect-button {
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          padding: 0.75rem 1.5rem;
          font-size: 1rem;
          cursor: pointer;
          width: 100%;
          margin-top: 1rem;
        }
        
        .connect-button:hover {
          background-color: #0051a8;
        }
        
        .auth-note {
          margin-top: 1.5rem;
          padding: 1rem;
          background-color: #f8f9fa;
          border-radius: 4px;
          font-size: 0.9rem;
        }
        
        .error-message {
          background-color: #f8d7da;
          color: #721c24;
          padding: 0.75rem;
          border-radius: 4px;
          margin: 1rem 0;
        }
        
        .box-explorer {
          display: flex;
          flex-direction: column;
          height: 600px;
        }
        
        .explorer-header {
          padding-bottom: 1rem;
          border-bottom: 1px solid #eee;
          margin-bottom: 1rem;
        }
        
        .explorer-header h2 {
          margin-top: 0;
          margin-bottom: 0.5rem;
          font-size: 1.5rem;
        }
        
        .breadcrumbs {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          font-size: 0.9rem;
        }
        
        .breadcrumb-item {
          cursor: pointer;
          color: #0070f3;
        }
        
        .breadcrumb-item:hover {
          text-decoration: underline;
        }
        
        .breadcrumb-separator {
          margin: 0 0.5rem;
          color: #999;
        }
        
        .explorer-content {
          display: flex;
          flex: 1;
          overflow: hidden;
        }
        
        .file-list {
          flex: 1;
          overflow-y: auto;
          border-right: 1px solid #eee;
          padding-right: 1rem;
        }
        
        .file-list ul {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        
        .file-item {
          display: flex;
          align-items: center;
          padding: 0.75rem;
          border-radius: 4px;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .file-item:hover {
          background-color: #f5f5f5;
        }
        
        .file-item.selected {
          background-color: #e6f7ff;
        }
        
        .file-item .material-icons {
          margin-right: 0.75rem;
          font-size: 1.5rem;
        }
        
        .file-item.folder .material-icons {
          color: #ffc107;
        }
        
        .file-name {
          flex: 1;
        }
        
        .file-size {
          font-size: 0.8rem;
          color: #666;
        }
        
        .loading, .empty-folder {
          padding: 2rem;
          text-align: center;
          color: #666;
        }
        
        .file-details {
          flex: 1;
          padding-left: 1rem;
          overflow-y: auto;
        }
        
        .file-details h3 {
          margin-top: 0;
          margin-bottom: 1rem;
          font-size: 1.2rem;
        }
        
        .file-info {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 0.5rem;
          margin-bottom: 1.5rem;
        }
        
        .info-item {
          display: flex;
          flex-direction: column;
        }
        
        .info-label {
          font-size: 0.8rem;
          color: #666;
        }
        
        .info-value {
          font-weight: 500;
        }
        
        .metadata-section, .analysis-section {
          margin-bottom: 1.5rem;
          padding: 1rem;
          background-color: #f8f9fa;
          border-radius: 4px;
        }
        
        .metadata-section h4, .analysis-section h4 {
          margin-top: 0;
          margin-bottom: 1rem;
          font-size: 1.1rem;
        }
        
        .metadata-scope {
          margin-bottom: 1rem;
        }
        
        .metadata-scope h5 {
          margin-top: 0;
          margin-bottom: 0.5rem;
          font-size: 1rem;
          color: #0070f3;
        }
        
        .metadata-template h6 {
          margin-top: 0;
          margin-bottom: 0.5rem;
          font-size: 0.9rem;
          color: #666;
        }
        
        .metadata-fields {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        
        .metadata-field {
          display: flex;
          margin-bottom: 0.25rem;
          font-size: 0.9rem;
        }
        
        .field-name {
          font-weight: 500;
          margin-right: 0.5rem;
        }
        
        .analysis-info {
          margin-bottom: 1rem;
        }
        
        .recommendations h5 {
          margin-top: 0;
          margin-bottom: 0.5rem;
          font-size: 1rem;
        }
        
        .recommendations ul {
          padding-left: 1.5rem;
          margin: 0;
        }
        
        .recommendations li.needed {
          color: #dc3545;
          font-weight: 500;
        }
        
        .file-actions {
          display: flex;
          gap: 0.5rem;
        }
        
        .action-button {
          flex: 1;
          padding: 0.75rem;
          border: none;
          border-radius: 4px;
          font-size: 0.9rem;
          cursor: pointer;
          font-weight: 500;
        }
        
        .analyze-button {
          background-color: #f8f9fa;
          color: #333;
          border: 1px solid #ddd;
        }
        
        .analyze-button:hover {
          background-color: #e9ecef;
        }
        
        .import-button {
          background-color: #0070f3;
          color: white;
        }
        
        .import-button:hover {
          background-color: #0051a8;
        }
        
        @media (max-width: 768px) {
          .explorer-content {
            flex-direction: column;
          }
          
          .file-list {
            border-right: none;
            border-bottom: 1px solid #eee;
            padding-right: 0;
            padding-bottom: 1rem;
            max-height: 300px;
          }
          
          .file-details {
            padding-left: 0;
            padding-top: 1rem;
          }
        }
      `}</style>
    </div>
  );
};

export default BoxIntegration;
