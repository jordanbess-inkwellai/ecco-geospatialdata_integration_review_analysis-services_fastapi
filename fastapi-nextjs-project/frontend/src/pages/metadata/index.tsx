import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import axios from 'axios';
import Layout from '../../components/Layout';

const MetadataPage: React.FC = () => {
  // State for datasets
  const [datasets, setDatasets] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // State for filtering and pagination
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [itemsPerPage, setItemsPerPage] = useState<number>(10);
  
  // Router
  const router = useRouter();
  
  // Load datasets on component mount
  useEffect(() => {
    loadDatasets();
  }, [currentPage, itemsPerPage, searchTerm]);
  
  // Load datasets from API
  const loadDatasets = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('/api/v1/metadata/datasets', {
        params: {
          page: currentPage,
          limit: itemsPerPage,
          search: searchTerm || undefined
        }
      });
      
      setDatasets(response.data.items);
      setTotalPages(Math.ceil(response.data.total / itemsPerPage));
    } catch (error: any) {
      console.error('Error loading datasets:', error);
      setError(error.response?.data?.detail || 'Error loading datasets');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle dataset deletion
  const handleDeleteDataset = async (id: number) => {
    if (!confirm('Are you sure you want to delete this dataset?')) {
      return;
    }
    
    setIsLoading(true);
    
    try {
      await axios.delete(`/api/v1/metadata/datasets/${id}`);
      
      // Reload datasets
      loadDatasets();
    } catch (error: any) {
      console.error('Error deleting dataset:', error);
      setError(error.response?.data?.detail || 'Error deleting dataset');
      setIsLoading(false);
    }
  };
  
  // Handle search
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    loadDatasets();
  };
  
  // Handle page change
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };
  
  // Format date
  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };
  
  // Render pagination
  const renderPagination = () => {
    if (totalPages <= 1) return null;
    
    const pages = [];
    const maxVisiblePages = 5;
    
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    // Previous button
    pages.push(
      <button
        key="prev"
        className={`pagination-button ${currentPage === 1 ? 'disabled' : ''}`}
        onClick={() => handlePageChange(currentPage - 1)}
        disabled={currentPage === 1}
      >
        &laquo;
      </button>
    );
    
    // First page
    if (startPage > 1) {
      pages.push(
        <button
          key="1"
          className="pagination-button"
          onClick={() => handlePageChange(1)}
        >
          1
        </button>
      );
      
      if (startPage > 2) {
        pages.push(
          <span key="ellipsis1" className="pagination-ellipsis">...</span>
        );
      }
    }
    
    // Page numbers
    for (let i = startPage; i <= endPage; i++) {
      pages.push(
        <button
          key={i}
          className={`pagination-button ${currentPage === i ? 'active' : ''}`}
          onClick={() => handlePageChange(i)}
        >
          {i}
        </button>
      );
    }
    
    // Last page
    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        pages.push(
          <span key="ellipsis2" className="pagination-ellipsis">...</span>
        );
      }
      
      pages.push(
        <button
          key={totalPages}
          className="pagination-button"
          onClick={() => handlePageChange(totalPages)}
        >
          {totalPages}
        </button>
      );
    }
    
    // Next button
    pages.push(
      <button
        key="next"
        className={`pagination-button ${currentPage === totalPages ? 'disabled' : ''}`}
        onClick={() => handlePageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        &raquo;
      </button>
    );
    
    return (
      <div className="pagination">
        {pages}
      </div>
    );
  };
  
  return (
    <Layout>
      <div className="metadata-page">
        <div className="page-header">
          <h1>Metadata Catalog</h1>
          <p>
            Manage metadata for geospatial datasets, services, and other resources.
            Create, edit, and publish metadata records to make your data discoverable.
          </p>
          
          <div className="header-actions">
            <form className="search-form" onSubmit={handleSearch}>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search metadata..."
                className="search-input"
              />
              <button type="submit" className="search-button">
                Search
              </button>
            </form>
            
            <Link href="/metadata/create">
              <a className="create-button">Create Metadata</a>
            </Link>
          </div>
        </div>
        
        {error && (
          <div className="error-message">{error}</div>
        )}
        
        <div className="metadata-list">
          {isLoading ? (
            <div className="loading">Loading metadata...</div>
          ) : datasets.length === 0 ? (
            <div className="empty-list">
              <p>No metadata records found.</p>
              <p>
                <Link href="/metadata/create">
                  <a>Create your first metadata record</a>
                </Link>
                {' or '}
                <Link href="/metadata/harvest">
                  <a>harvest metadata from files</a>
                </Link>.
              </p>
            </div>
          ) : (
            <>
              <div className="list-header">
                <div className="header-title">Title</div>
                <div className="header-type">Type</div>
                <div className="header-date">Updated</div>
                <div className="header-status">Status</div>
                <div className="header-actions">Actions</div>
              </div>
              
              <ul className="dataset-list">
                {datasets.map((dataset) => (
                  <li key={dataset.id} className="dataset-item">
                    <div className="dataset-title">
                      <Link href={`/metadata/${dataset.id}`}>
                        <a>{dataset.title}</a>
                      </Link>
                      {dataset.description && (
                        <div className="dataset-description">{dataset.description}</div>
                      )}
                    </div>
                    
                    <div className="dataset-type">
                      <span className={`type-badge ${dataset.resource_type}`}>
                        {dataset.resource_type}
                      </span>
                    </div>
                    
                    <div className="dataset-date">
                      {formatDate(dataset.updated_at)}
                    </div>
                    
                    <div className="dataset-status">
                      <span className={`status-badge ${dataset.is_published ? 'published' : 'draft'}`}>
                        {dataset.is_published ? 'Published' : 'Draft'}
                      </span>
                    </div>
                    
                    <div className="dataset-actions">
                      <Link href={`/metadata/${dataset.id}`}>
                        <a className="view-button">View</a>
                      </Link>
                      
                      <Link href={`/metadata/edit/${dataset.id}`}>
                        <a className="edit-button">Edit</a>
                      </Link>
                      
                      <button
                        className="delete-button"
                        onClick={() => handleDeleteDataset(dataset.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
              
              {renderPagination()}
            </>
          )}
        </div>
        
        <div className="metadata-tools">
          <div className="tools-header">
            <h2>Metadata Tools</h2>
          </div>
          
          <div className="tools-grid">
            <div className="tool-card">
              <h3>Harvest Metadata</h3>
              <p>
                Extract metadata from geospatial files, directories, or services.
                Automatically populate metadata records from existing data.
              </p>
              <Link href="/metadata/harvest">
                <a className="tool-link">Harvest Metadata</a>
              </Link>
            </div>
            
            <div className="tool-card">
              <h3>Validate Metadata</h3>
              <p>
                Validate metadata records against standards like ISO 19115, INSPIRE, or custom profiles.
                Ensure your metadata meets quality requirements.
              </p>
              <Link href="/metadata/validate">
                <a className="tool-link">Validate Metadata</a>
              </Link>
            </div>
            
            <div className="tool-card">
              <h3>Export Metadata</h3>
              <p>
                Export metadata in various formats including ISO 19139 XML, JSON-LD, and DCAT.
                Share metadata with other systems and catalogs.
              </p>
              <Link href="/metadata/export">
                <a className="tool-link">Export Metadata</a>
              </Link>
            </div>
            
            <div className="tool-card">
              <h3>Publish to Catalog</h3>
              <p>
                Publish metadata to external catalogs including GeoNetwork, CKAN, and OGC API Records.
                Make your data discoverable in federated catalogs.
              </p>
              <Link href="/metadata/publish">
                <a className="tool-link">Publish Metadata</a>
              </Link>
            </div>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .metadata-page {
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
          margin-bottom: 1.5rem;
        }
        
        .header-actions {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 1.5rem;
        }
        
        .search-form {
          display: flex;
          flex: 1;
          max-width: 500px;
        }
        
        .search-input {
          flex: 1;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-right: none;
          border-radius: 4px 0 0 4px;
          font-size: 1rem;
        }
        
        .search-button {
          padding: 0.75rem 1.5rem;
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 0 4px 4px 0;
          font-size: 1rem;
          cursor: pointer;
        }
        
        .create-button {
          display: inline-block;
          padding: 0.75rem 1.5rem;
          background-color: #28a745;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 1rem;
          text-decoration: none;
          cursor: pointer;
        }
        
        .metadata-list {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          margin-bottom: 3rem;
        }
        
        .list-header {
          display: grid;
          grid-template-columns: 3fr 1fr 1fr 1fr 1fr;
          gap: 1rem;
          padding: 1rem;
          background-color: #f8f9fa;
          border-bottom: 1px solid #eee;
          border-radius: 8px 8px 0 0;
          font-weight: 500;
        }
        
        .dataset-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        
        .dataset-item {
          display: grid;
          grid-template-columns: 3fr 1fr 1fr 1fr 1fr;
          gap: 1rem;
          padding: 1rem;
          border-bottom: 1px solid #eee;
          align-items: center;
        }
        
        .dataset-item:last-child {
          border-bottom: none;
        }
        
        .dataset-title a {
          color: #0070f3;
          text-decoration: none;
          font-weight: 500;
        }
        
        .dataset-title a:hover {
          text-decoration: underline;
        }
        
        .dataset-description {
          margin-top: 0.25rem;
          font-size: 0.9rem;
          color: #666;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        
        .type-badge {
          display: inline-block;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.8rem;
          font-weight: 500;
          text-transform: capitalize;
        }
        
        .type-badge.dataset {
          background-color: #e3f2fd;
          color: #0d47a1;
        }
        
        .type-badge.service {
          background-color: #e8f5e9;
          color: #1b5e20;
        }
        
        .type-badge.application {
          background-color: #fff3e0;
          color: #e65100;
        }
        
        .type-badge.map {
          background-color: #f3e5f5;
          color: #4a148c;
        }
        
        .status-badge {
          display: inline-block;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.8rem;
          font-weight: 500;
        }
        
        .status-badge.published {
          background-color: #d4edda;
          color: #155724;
        }
        
        .status-badge.draft {
          background-color: #f8f9fa;
          color: #6c757d;
        }
        
        .dataset-actions {
          display: flex;
          gap: 0.5rem;
        }
        
        .view-button, .edit-button, .delete-button {
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.8rem;
          cursor: pointer;
        }
        
        .view-button {
          background-color: #e9ecef;
          color: #495057;
          text-decoration: none;
        }
        
        .edit-button {
          background-color: #e3f2fd;
          color: #0d47a1;
          text-decoration: none;
        }
        
        .delete-button {
          background-color: #f8d7da;
          color: #721c24;
          border: none;
        }
        
        .loading, .empty-list {
          padding: 3rem;
          text-align: center;
          color: #666;
        }
        
        .empty-list p {
          margin: 0.5rem 0;
        }
        
        .empty-list a {
          color: #0070f3;
          text-decoration: none;
        }
        
        .empty-list a:hover {
          text-decoration: underline;
        }
        
        .pagination {
          display: flex;
          justify-content: center;
          gap: 0.25rem;
          padding: 1rem;
          border-top: 1px solid #eee;
        }
        
        .pagination-button {
          padding: 0.5rem 0.75rem;
          border: 1px solid #ddd;
          background-color: white;
          border-radius: 4px;
          font-size: 0.9rem;
          cursor: pointer;
        }
        
        .pagination-button.active {
          background-color: #0070f3;
          color: white;
          border-color: #0070f3;
        }
        
        .pagination-button.disabled {
          color: #ccc;
          cursor: not-allowed;
        }
        
        .pagination-ellipsis {
          padding: 0.5rem 0.25rem;
          font-size: 0.9rem;
        }
        
        .error-message {
          background-color: #f8d7da;
          color: #721c24;
          padding: 0.75rem;
          border-radius: 4px;
          margin-bottom: 1.5rem;
        }
        
        .metadata-tools {
          margin-top: 3rem;
        }
        
        .tools-header {
          margin-bottom: 1.5rem;
        }
        
        .tools-header h2 {
          font-size: 1.5rem;
          margin: 0;
        }
        
        .tools-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 1.5rem;
        }
        
        .tool-card {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 1.5rem;
        }
        
        .tool-card h3 {
          margin-top: 0;
          margin-bottom: 0.75rem;
          font-size: 1.2rem;
        }
        
        .tool-card p {
          color: #666;
          margin-bottom: 1.5rem;
          min-height: 4em;
        }
        
        .tool-link {
          display: inline-block;
          padding: 0.5rem 1rem;
          background-color: #f0f0f0;
          color: #333;
          border-radius: 4px;
          text-decoration: none;
          font-weight: 500;
          transition: background-color 0.2s;
        }
        
        .tool-link:hover {
          background-color: #e0e0e0;
        }
        
        @media (max-width: 768px) {
          .header-actions {
            flex-direction: column;
            align-items: stretch;
            gap: 1rem;
          }
          
          .search-form {
            max-width: none;
          }
          
          .list-header {
            display: none;
          }
          
          .dataset-item {
            grid-template-columns: 1fr;
            gap: 0.5rem;
            padding: 1rem;
          }
          
          .dataset-type, .dataset-date, .dataset-status {
            display: flex;
            align-items: center;
            gap: 0.5rem;
          }
          
          .dataset-type::before {
            content: 'Type:';
            font-weight: 500;
          }
          
          .dataset-date::before {
            content: 'Updated:';
            font-weight: 500;
          }
          
          .dataset-status::before {
            content: 'Status:';
            font-weight: 500;
          }
          
          .dataset-actions {
            margin-top: 0.5rem;
          }
        }
      `}</style>
    </Layout>
  );
};

export default MetadataPage;
