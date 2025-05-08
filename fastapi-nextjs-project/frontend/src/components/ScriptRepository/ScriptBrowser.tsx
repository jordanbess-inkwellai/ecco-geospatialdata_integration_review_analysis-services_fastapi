import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';
import { formatDistanceToNow } from 'date-fns';

interface Script {
  name: string;
  description: string;
  file_path: string;
  file_type: string;
  type: string;
  category: string;
  subcategory?: string;
  author?: string;
  version?: string;
  date_created?: string;
  date_modified?: string;
  tags: string[];
  inputs: any[];
  outputs: any[];
  dependencies?: string[];
}

interface ScriptCatalog {
  scripts: Script[];
  by_type: Record<string, Script[]>;
  by_category: Record<string, Script[]>;
  by_tag: Record<string, Script[]>;
  count: number;
  generated_at: string;
}

interface ScriptBrowserProps {
  onSelectScript?: (script: Script) => void;
}

const ScriptBrowser: React.FC<ScriptBrowserProps> = ({ onSelectScript }) => {
  const [catalog, setCatalog] = useState<ScriptCatalog | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedTag, setSelectedTag] = useState<string>('all');
  const [selectedScript, setSelectedScript] = useState<Script | null>(null);
  
  const router = useRouter();
  
  // Load script catalog
  useEffect(() => {
    const loadCatalog = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await axios.get('/data/script_catalog.json');
        setCatalog(response.data);
        
        setLoading(false);
      } catch (err: any) {
        console.error('Error loading script catalog:', err);
        setError(err.message || 'Error loading script catalog');
        setLoading(false);
      }
    };
    
    loadCatalog();
  }, []);
  
  // Filter scripts based on search and filters
  const filteredScripts = React.useMemo(() => {
    if (!catalog) return [];
    
    let scripts = catalog.scripts;
    
    // Apply category filter
    if (selectedCategory !== 'all') {
      scripts = scripts.filter(script => script.category === selectedCategory);
    }
    
    // Apply type filter
    if (selectedType !== 'all') {
      scripts = scripts.filter(script => script.type === selectedType);
    }
    
    // Apply tag filter
    if (selectedTag !== 'all') {
      scripts = scripts.filter(script => script.tags && script.tags.includes(selectedTag));
    }
    
    // Apply text search
    if (filter) {
      const searchLower = filter.toLowerCase();
      scripts = scripts.filter(script => 
        script.name.toLowerCase().includes(searchLower) ||
        (script.description && script.description.toLowerCase().includes(searchLower)) ||
        script.file_path.toLowerCase().includes(searchLower)
      );
    }
    
    return scripts;
  }, [catalog, filter, selectedCategory, selectedType, selectedTag]);
  
  // Get unique categories, types, and tags
  const categories = React.useMemo(() => {
    if (!catalog) return [];
    return ['all', ...new Set(catalog.scripts.map(script => script.category))];
  }, [catalog]);
  
  const types = React.useMemo(() => {
    if (!catalog) return [];
    return ['all', ...new Set(catalog.scripts.map(script => script.type))];
  }, [catalog]);
  
  const tags = React.useMemo(() => {
    if (!catalog) return [];
    const allTags = new Set<string>();
    catalog.scripts.forEach(script => {
      if (script.tags) {
        script.tags.forEach(tag => allTags.add(tag));
      }
    });
    return ['all', ...Array.from(allTags)];
  }, [catalog]);
  
  // Handle script selection
  const handleSelectScript = (script: Script) => {
    setSelectedScript(script);
    if (onSelectScript) {
      onSelectScript(script);
    }
  };
  
  // Handle script execution
  const handleExecuteScript = async (script: Script) => {
    try {
      // Navigate to the script execution page
      router.push(`/scripts/execute?path=${encodeURIComponent(script.file_path)}`);
    } catch (err: any) {
      console.error('Error navigating to script execution:', err);
    }
  };
  
  // Handle workflow generation
  const handleGenerateWorkflow = async (script: Script) => {
    try {
      // Navigate to the workflow generation page
      router.push(`/workflows/generate?script=${encodeURIComponent(script.file_path)}`);
    } catch (err: any) {
      console.error('Error navigating to workflow generation:', err);
    }
  };
  
  // Render script details
  const renderScriptDetails = () => {
    if (!selectedScript) return null;
    
    return (
      <div className="script-details">
        <div className="details-header">
          <h3>{selectedScript.name}</h3>
          <div className="script-actions">
            <button
              className="execute-button"
              onClick={() => handleExecuteScript(selectedScript)}
            >
              Execute
            </button>
            {(selectedScript.type === 'python_script' || selectedScript.type === 'dlt_pipeline') && (
              <button
                className="workflow-button"
                onClick={() => handleGenerateWorkflow(selectedScript)}
              >
                Generate Workflow
              </button>
            )}
          </div>
        </div>
        
        <div className="script-path">
          <span className="label">Path:</span> {selectedScript.file_path}
        </div>
        
        {selectedScript.description && (
          <div className="script-description">
            {selectedScript.description}
          </div>
        )}
        
        <div className="script-metadata">
          <div className="metadata-item">
            <span className="label">Type:</span>
            <span className="value">{selectedScript.type}</span>
          </div>
          
          {selectedScript.author && (
            <div className="metadata-item">
              <span className="label">Author:</span>
              <span className="value">{selectedScript.author}</span>
            </div>
          )}
          
          {selectedScript.version && (
            <div className="metadata-item">
              <span className="label">Version:</span>
              <span className="value">{selectedScript.version}</span>
            </div>
          )}
          
          {selectedScript.date_created && (
            <div className="metadata-item">
              <span className="label">Created:</span>
              <span className="value">
                {formatDistanceToNow(new Date(selectedScript.date_created), { addSuffix: true })}
              </span>
            </div>
          )}
          
          {selectedScript.date_modified && (
            <div className="metadata-item">
              <span className="label">Modified:</span>
              <span className="value">
                {formatDistanceToNow(new Date(selectedScript.date_modified), { addSuffix: true })}
              </span>
            </div>
          )}
        </div>
        
        {selectedScript.tags && selectedScript.tags.length > 0 && (
          <div className="script-tags">
            {selectedScript.tags.map(tag => (
              <span key={tag} className="tag">{tag}</span>
            ))}
          </div>
        )}
        
        {selectedScript.inputs && selectedScript.inputs.length > 0 && (
          <div className="script-inputs">
            <h4>Inputs</h4>
            <table className="inputs-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Description</th>
                  <th>Required</th>
                  <th>Default</th>
                </tr>
              </thead>
              <tbody>
                {selectedScript.inputs.map(input => (
                  <tr key={input.name}>
                    <td>{input.name}</td>
                    <td>{input.type}</td>
                    <td>{input.description || '-'}</td>
                    <td>{input.required ? 'Yes' : 'No'}</td>
                    <td>{input.default !== undefined ? String(input.default) : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {selectedScript.outputs && selectedScript.outputs.length > 0 && (
          <div className="script-outputs">
            <h4>Outputs</h4>
            <table className="outputs-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {selectedScript.outputs.map(output => (
                  <tr key={output.name}>
                    <td>{output.name}</td>
                    <td>{output.type}</td>
                    <td>{output.description || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {selectedScript.dependencies && selectedScript.dependencies.length > 0 && (
          <div className="script-dependencies">
            <h4>Dependencies</h4>
            <div className="dependencies-list">
              {selectedScript.dependencies.map(dep => (
                <span key={dep} className="dependency">{dep}</span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };
  
  return (
    <div className="script-browser">
      <div className="browser-header">
        <h2>Script Repository</h2>
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search scripts..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="search-input"
          />
        </div>
      </div>
      
      <div className="filters">
        <div className="filter-group">
          <label>Category:</label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="filter-select"
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category === 'all' ? 'All Categories' : category}
              </option>
            ))}
          </select>
        </div>
        
        <div className="filter-group">
          <label>Type:</label>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="filter-select"
          >
            {types.map(type => (
              <option key={type} value={type}>
                {type === 'all' ? 'All Types' : type}
              </option>
            ))}
          </select>
        </div>
        
        <div className="filter-group">
          <label>Tag:</label>
          <select
            value={selectedTag}
            onChange={(e) => setSelectedTag(e.target.value)}
            className="filter-select"
          >
            {tags.map(tag => (
              <option key={tag} value={tag}>
                {tag === 'all' ? 'All Tags' : tag}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      {error && (
        <div className="error-message">{error}</div>
      )}
      
      <div className="browser-content">
        <div className="scripts-list">
          {loading ? (
            <div className="loading">Loading scripts...</div>
          ) : filteredScripts.length === 0 ? (
            <div className="no-scripts">No scripts found</div>
          ) : (
            <ul className="scripts-grid">
              {filteredScripts.map(script => (
                <li
                  key={script.file_path}
                  className={`script-card ${selectedScript?.file_path === script.file_path ? 'selected' : ''}`}
                  onClick={() => handleSelectScript(script)}
                >
                  <div className="script-header">
                    <div className="script-name">{script.name}</div>
                    <div className="script-type">{script.type}</div>
                  </div>
                  
                  <div className="script-description">
                    {script.description || 'No description'}
                  </div>
                  
                  <div className="script-footer">
                    <div className="script-category">
                      {script.category}{script.subcategory ? ` / ${script.subcategory}` : ''}
                    </div>
                    
                    <div className="script-file-type">{script.file_type}</div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
        
        {renderScriptDetails()}
      </div>
      
      <style jsx>{`
        .script-browser {
          display: flex;
          flex-direction: column;
          height: 100%;
          width: 100%;
        }
        
        .browser-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background-color: #f8f9fa;
          border-bottom: 1px solid #ddd;
        }
        
        .browser-header h2 {
          margin: 0;
          font-size: 1.5rem;
          color: #333;
        }
        
        .search-bar {
          flex: 1;
          max-width: 400px;
          margin-left: 1rem;
        }
        
        .search-input {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.9rem;
        }
        
        .filters {
          display: flex;
          padding: 1rem;
          background-color: #f8f9fa;
          border-bottom: 1px solid #ddd;
          gap: 1rem;
        }
        
        .filter-group {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .filter-group label {
          font-size: 0.9rem;
          color: #666;
        }
        
        .filter-select {
          padding: 0.4rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.9rem;
        }
        
        .error-message {
          padding: 1rem;
          background-color: #f8d7da;
          color: #721c24;
          border-radius: 4px;
          margin: 1rem;
        }
        
        .browser-content {
          display: flex;
          flex: 1;
          overflow: hidden;
        }
        
        .scripts-list {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
          border-right: 1px solid #ddd;
        }
        
        .loading, .no-scripts {
          padding: 2rem;
          text-align: center;
          color: #666;
        }
        
        .scripts-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 1rem;
          list-style: none;
          padding: 0;
          margin: 0;
        }
        
        .script-card {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 1rem;
          cursor: pointer;
          transition: all 0.2s;
          display: flex;
          flex-direction: column;
          height: 100%;
        }
        
        .script-card:hover {
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
          transform: translateY(-2px);
        }
        
        .script-card.selected {
          border: 2px solid #0070f3;
        }
        
        .script-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 0.5rem;
        }
        
        .script-name {
          font-weight: bold;
          font-size: 1rem;
          color: #333;
        }
        
        .script-type {
          font-size: 0.8rem;
          background-color: #e9ecef;
          padding: 0.2rem 0.4rem;
          border-radius: 4px;
          color: #495057;
        }
        
        .script-description {
          font-size: 0.9rem;
          color: #666;
          margin-bottom: 0.5rem;
          flex-grow: 1;
        }
        
        .script-footer {
          display: flex;
          justify-content: space-between;
          font-size: 0.8rem;
          color: #666;
        }
        
        .script-details {
          flex: 1;
          padding: 1.5rem;
          overflow-y: auto;
        }
        
        .details-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }
        
        .details-header h3 {
          margin: 0;
          font-size: 1.5rem;
          color: #333;
        }
        
        .script-actions {
          display: flex;
          gap: 0.5rem;
        }
        
        .execute-button, .workflow-button {
          padding: 0.5rem 1rem;
          border-radius: 4px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .execute-button {
          background-color: #0070f3;
          color: white;
          border: none;
        }
        
        .execute-button:hover {
          background-color: #0051a8;
        }
        
        .workflow-button {
          background-color: #f8f9fa;
          color: #333;
          border: 1px solid #ddd;
        }
        
        .workflow-button:hover {
          background-color: #e9ecef;
        }
        
        .script-path {
          font-family: monospace;
          background-color: #f8f9fa;
          padding: 0.5rem;
          border-radius: 4px;
          margin-bottom: 1rem;
          font-size: 0.9rem;
        }
        
        .script-description {
          margin-bottom: 1.5rem;
          line-height: 1.5;
        }
        
        .script-metadata {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 0.5rem;
          margin-bottom: 1.5rem;
        }
        
        .metadata-item {
          font-size: 0.9rem;
        }
        
        .label {
          font-weight: bold;
          color: #666;
          margin-right: 0.5rem;
        }
        
        .script-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-bottom: 1.5rem;
        }
        
        .tag {
          background-color: #e9ecef;
          color: #495057;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.8rem;
        }
        
        .script-inputs, .script-outputs, .script-dependencies {
          margin-bottom: 1.5rem;
        }
        
        .script-inputs h4, .script-outputs h4, .script-dependencies h4 {
          margin-top: 0;
          margin-bottom: 0.5rem;
          font-size: 1.1rem;
          color: #333;
        }
        
        .inputs-table, .outputs-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.9rem;
        }
        
        .inputs-table th, .outputs-table th {
          text-align: left;
          padding: 0.5rem;
          background-color: #f8f9fa;
          border-bottom: 2px solid #ddd;
        }
        
        .inputs-table td, .outputs-table td {
          padding: 0.5rem;
          border-bottom: 1px solid #ddd;
        }
        
        .dependencies-list {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }
        
        .dependency {
          background-color: #f8f9fa;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.8rem;
          font-family: monospace;
        }
        
        @media (max-width: 768px) {
          .browser-content {
            flex-direction: column;
          }
          
          .scripts-list, .script-details {
            flex: none;
            width: 100%;
          }
          
          .scripts-list {
            border-right: none;
            border-bottom: 1px solid #ddd;
          }
          
          .filters {
            flex-direction: column;
            gap: 0.5rem;
          }
          
          .filter-group {
            width: 100%;
          }
          
          .filter-select {
            flex: 1;
          }
        }
      `}</style>
    </div>
  );
};

export default ScriptBrowser;
