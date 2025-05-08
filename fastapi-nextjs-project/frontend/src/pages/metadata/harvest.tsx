import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import axios from 'axios';
import Layout from '../../components/Layout';

const MetadataHarvestPage: React.FC = () => {
  // State for harvest job
  const [sourceType, setSourceType] = useState<string>('file');
  const [sourcePath, setSourcePath] = useState<string>('');
  const [fileUpload, setFileUpload] = useState<File | null>(null);
  const [isRecursive, setIsRecursive] = useState<boolean>(true);
  const [overwriteExisting, setOverwriteExisting] = useState<boolean>(false);
  const [extractAttributes, setExtractAttributes] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // State for harvest jobs
  const [harvestJobs, setHarvestJobs] = useState<any[]>([]);
  const [jobsLoading, setJobsLoading] = useState<boolean>(true);
  
  // Router
  const router = useRouter();
  
  // Load harvest jobs on component mount
  useEffect(() => {
    loadHarvestJobs();
  }, []);
  
  // Load harvest jobs from API
  const loadHarvestJobs = async () => {
    setJobsLoading(true);
    
    try {
      const response = await axios.get('/api/v1/metadata/harvest/jobs');
      setHarvestJobs(response.data);
    } catch (error: any) {
      console.error('Error loading harvest jobs:', error);
    } finally {
      setJobsLoading(false);
    }
  };
  
  // Handle file change
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFileUpload(e.target.files[0]);
    }
  };
  
  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      let response;
      
      if (sourceType === 'file' && fileUpload) {
        // Create form data for file upload
        const formData = new FormData();
        formData.append('file', fileUpload);
        formData.append('extract_attributes', extractAttributes.toString());
        formData.append('overwrite_existing', overwriteExisting.toString());
        
        response = await axios.post('/api/v1/metadata/harvest/file', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      } else {
        // Create harvest job for directory or service
        response = await axios.post('/api/v1/metadata/harvest/jobs', {
          source_type: sourceType,
          source_path: sourcePath,
          config: {
            recursive: isRecursive,
            extract_attributes: extractAttributes,
            overwrite_existing: overwriteExisting
          }
        });
      }
      
      setSuccess('Metadata harvest job started successfully');
      
      // Reload harvest jobs
      loadHarvestJobs();
      
      // Reset form if it's a file upload
      if (sourceType === 'file') {
        setFileUpload(null);
        const fileInput = document.getElementById('file-upload') as HTMLInputElement;
        if (fileInput) {
          fileInput.value = '';
        }
      }
    } catch (error: any) {
      console.error('Error starting harvest job:', error);
      setError(error.response?.data?.detail || 'Error starting harvest job');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Format date
  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleString();
  };
  
  // Get status badge class
  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'completed':
        return 'status-completed';
      case 'running':
        return 'status-running';
      case 'failed':
        return 'status-failed';
      default:
        return 'status-pending';
    }
  };
  
  // Render source type specific fields
  const renderSourceTypeFields = () => {
    switch (sourceType) {
      case 'file':
        return (
          <div className="form-group">
            <label htmlFor="file-upload">Upload File</label>
            <input
              type="file"
              id="file-upload"
              onChange={handleFileChange}
              className="form-control"
              accept=".shp,.geojson,.json,.gpkg,.gdb,.xml,.tif,.tiff,.kml,.kmz,.csv,.xlsx"
            />
            <div className="form-help">
              Supported formats: Shapefile, GeoJSON, GeoPackage, FileGDB, XML, GeoTIFF, KML, CSV, Excel
            </div>
          </div>
        );
        
      case 'directory':
        return (
          <>
            <div className="form-group">
              <label htmlFor="source-path">Directory Path</label>
              <input
                type="text"
                id="source-path"
                value={sourcePath}
                onChange={(e) => setSourcePath(e.target.value)}
                className="form-control"
                placeholder="Enter directory path"
                required
              />
              <div className="form-help">
                Enter the path to a directory containing geospatial files
              </div>
            </div>
            
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={isRecursive}
                  onChange={(e) => setIsRecursive(e.target.checked)}
                />
                Scan Recursively
              </label>
              <div className="form-help">
                Scan subdirectories for geospatial files
              </div>
            </div>
          </>
        );
        
      case 'service':
        return (
          <div className="form-group">
            <label htmlFor="source-path">Service URL</label>
            <input
              type="url"
              id="source-path"
              value={sourcePath}
              onChange={(e) => setSourcePath(e.target.value)}
              className="form-control"
              placeholder="Enter service URL"
              required
            />
            <div className="form-help">
              Enter the URL of a geospatial service (WMS, WFS, CSW, etc.)
            </div>
          </div>
        );
        
      default:
        return null;
    }
  };
  
  return (
    <Layout>
      <div className="harvest-page">
        <div className="page-header">
          <h1>Harvest Metadata</h1>
          <p>
            Extract metadata from geospatial files, directories, or services.
            Automatically populate metadata records from existing data.
          </p>
        </div>
        
        <div className="harvest-container">
          <div className="harvest-form-container">
            <div className="harvest-form">
              <h2>Start Harvest Job</h2>
              
              {error && (
                <div className="error-message">{error}</div>
              )}
              
              {success && (
                <div className="success-message">{success}</div>
              )}
              
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label htmlFor="source-type">Source Type</label>
                  <select
                    id="source-type"
                    value={sourceType}
                    onChange={(e) => setSourceType(e.target.value)}
                    className="form-control"
                  >
                    <option value="file">File Upload</option>
                    <option value="directory">Directory</option>
                    <option value="service">Service</option>
                  </select>
                </div>
                
                {renderSourceTypeFields()}
                
                <div className="form-options">
                  <div className="form-group checkbox-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={extractAttributes}
                        onChange={(e) => setExtractAttributes(e.target.checked)}
                      />
                      Extract Attributes
                    </label>
                    <div className="form-help">
                      Extract attribute information from datasets
                    </div>
                  </div>
                  
                  <div className="form-group checkbox-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={overwriteExisting}
                        onChange={(e) => setOverwriteExisting(e.target.checked)}
                      />
                      Overwrite Existing
                    </label>
                    <div className="form-help">
                      Overwrite existing metadata records with the same identifier
                    </div>
                  </div>
                </div>
                
                <div className="form-actions">
                  <button
                    type="submit"
                    className="submit-button"
                    disabled={isLoading || (sourceType === 'file' && !fileUpload) || (sourceType !== 'file' && !sourcePath)}
                  >
                    {isLoading ? 'Starting...' : 'Start Harvest'}
                  </button>
                </div>
              </form>
            </div>
          </div>
          
          <div className="harvest-jobs">
            <h2>Recent Harvest Jobs</h2>
            
            {jobsLoading ? (
              <div className="loading">Loading jobs...</div>
            ) : harvestJobs.length === 0 ? (
              <div className="empty-jobs">No harvest jobs found</div>
            ) : (
              <ul className="jobs-list">
                {harvestJobs.map((job) => (
                  <li key={job.id} className="job-item">
                    <div className="job-header">
                      <div className="job-source">
                        <span className="source-type">{job.source_type}</span>
                        <span className="source-path">{job.source_path}</span>
                      </div>
                      
                      <div className="job-status">
                        <span className={`status-badge ${getStatusBadgeClass(job.status)}`}>
                          {job.status}
                        </span>
                      </div>
                    </div>
                    
                    <div className="job-details">
                      <div className="job-stats">
                        <div className="stat-item">
                          <span className="stat-label">Started:</span>
                          <span className="stat-value">{formatDate(job.started_at)}</span>
                        </div>
                        
                        {job.completed_at && (
                          <div className="stat-item">
                            <span className="stat-label">Completed:</span>
                            <span className="stat-value">{formatDate(job.completed_at)}</span>
                          </div>
                        )}
                        
                        <div className="stat-item">
                          <span className="stat-label">Records:</span>
                          <span className="stat-value">
                            {job.success_records} / {job.total_records}
                            {job.failed_records > 0 && ` (${job.failed_records} failed)`}
                          </span>
                        </div>
                      </div>
                      
                      {job.error_message && (
                        <div className="job-error">
                          <span className="error-label">Error:</span>
                          <span className="error-message">{job.error_message}</span>
                        </div>
                      )}
                      
                      {job.status === 'completed' && job.success_records > 0 && (
                        <div className="job-actions">
                          <Link href="/metadata">
                            <a className="view-records-button">View Records</a>
                          </Link>
                        </div>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .harvest-page {
          padding: 1rem 0;
        }
        
        .page-header {
          margin-bottom: 2rem;
        }
        
        .page-header h1 {
          margin-bottom: 0.5rem;
          font-size: 2rem;
        }
        
        .page-header p {
          color: #666;
          max-width: 800px;
        }
        
        .harvest-container {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 2rem;
        }
        
        .harvest-form-container, .harvest-jobs {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 1.5rem;
        }
        
        .harvest-form h2, .harvest-jobs h2 {
          margin-top: 0;
          margin-bottom: 1.5rem;
          font-size: 1.5rem;
        }
        
        .form-group {
          margin-bottom: 1.5rem;
        }
        
        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
        }
        
        .form-control {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 1rem;
        }
        
        .form-help {
          margin-top: 0.25rem;
          font-size: 0.9rem;
          color: #666;
        }
        
        .checkbox-group {
          display: flex;
          flex-direction: column;
        }
        
        .checkbox-group label {
          display: flex;
          align-items: center;
          margin-bottom: 0.25rem;
          cursor: pointer;
        }
        
        .checkbox-group input {
          margin-right: 0.5rem;
        }
        
        .form-options {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }
        
        .form-actions {
          margin-top: 2rem;
        }
        
        .submit-button {
          width: 100%;
          padding: 0.75rem 1.5rem;
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 1rem;
          cursor: pointer;
        }
        
        .submit-button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }
        
        .loading, .empty-jobs {
          padding: 2rem;
          text-align: center;
          color: #666;
        }
        
        .jobs-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        
        .job-item {
          padding: 1rem;
          border-bottom: 1px solid #eee;
        }
        
        .job-item:last-child {
          border-bottom: none;
        }
        
        .job-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 0.75rem;
        }
        
        .job-source {
          display: flex;
          flex-direction: column;
        }
        
        .source-type {
          font-weight: 500;
          margin-bottom: 0.25rem;
          text-transform: capitalize;
        }
        
        .source-path {
          font-size: 0.9rem;
          color: #666;
          word-break: break-all;
        }
        
        .status-badge {
          display: inline-block;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.8rem;
          font-weight: 500;
          text-transform: capitalize;
        }
        
        .status-completed {
          background-color: #d4edda;
          color: #155724;
        }
        
        .status-running {
          background-color: #cce5ff;
          color: #004085;
        }
        
        .status-failed {
          background-color: #f8d7da;
          color: #721c24;
        }
        
        .status-pending {
          background-color: #f8f9fa;
          color: #6c757d;
        }
        
        .job-details {
          font-size: 0.9rem;
        }
        
        .job-stats {
          display: flex;
          flex-wrap: wrap;
          gap: 1rem;
          margin-bottom: 0.75rem;
        }
        
        .stat-label {
          font-weight: 500;
          margin-right: 0.25rem;
        }
        
        .job-error {
          margin-top: 0.5rem;
          color: #721c24;
        }
        
        .error-label {
          font-weight: 500;
          margin-right: 0.25rem;
        }
        
        .job-actions {
          margin-top: 1rem;
        }
        
        .view-records-button {
          display: inline-block;
          padding: 0.5rem 0.75rem;
          background-color: #e9ecef;
          color: #495057;
          border-radius: 4px;
          text-decoration: none;
          font-size: 0.9rem;
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
        
        @media (max-width: 768px) {
          .harvest-container {
            grid-template-columns: 1fr;
          }
          
          .form-options {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </Layout>
  );
};

export default MetadataHarvestPage;
