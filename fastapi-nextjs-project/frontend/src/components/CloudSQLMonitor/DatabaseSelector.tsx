import React, { useState } from 'react';

interface DatabaseSelectorProps {
  savedConfigs: any[];
  onSelect: (config: any) => void;
  onSave: (name: string) => void;
  selectedConfig: any;
}

const DatabaseSelector: React.FC<DatabaseSelectorProps> = ({
  savedConfigs,
  onSelect,
  onSave,
  selectedConfig
}) => {
  // State for new connection form
  const [showNewConnectionForm, setShowNewConnectionForm] = useState<boolean>(false);
  const [connectionName, setConnectionName] = useState<string>('');
  const [instanceConnectionName, setInstanceConnectionName] = useState<string>('');
  const [database, setDatabase] = useState<string>('');
  const [user, setUser] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [ipType, setIpType] = useState<string>('PUBLIC');
  
  // State for save form
  const [showSaveForm, setShowSaveForm] = useState<boolean>(false);
  const [saveName, setSaveName] = useState<string>('');
  
  // Handle new connection form submission
  const handleNewConnectionSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Create new connection config
    const newConfig = {
      instance_connection_name: instanceConnectionName,
      database,
      user,
      password,
      ip_type: ipType
    };
    
    // Select the new connection
    onSelect(newConfig);
    
    // Reset form
    setShowNewConnectionForm(false);
  };
  
  // Handle save form submission
  const handleSaveSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Save the current connection
    onSave(saveName);
    
    // Reset form
    setShowSaveForm(false);
    setSaveName('');
  };
  
  return (
    <div className="database-selector">
      <div className="selector-header">
        <h3>Database Connections</h3>
        <button
          className="new-connection-button"
          onClick={() => setShowNewConnectionForm(true)}
        >
          New Connection
        </button>
      </div>
      
      {savedConfigs.length > 0 ? (
        <ul className="saved-connections">
          {savedConfigs.map((config) => (
            <li
              key={config.id}
              className={`connection-item ${selectedConfig && selectedConfig.instance_connection_name === config.instance_connection_name && selectedConfig.database === config.database ? 'selected' : ''}`}
              onClick={() => onSelect({
                instance_connection_name: config.instance_connection_name,
                database: config.database,
                user: config.user,
                password: config.password,
                ip_type: config.ip_type
              })}
            >
              <div className="connection-name">{config.name}</div>
              <div className="connection-details">
                <div className="connection-database">{config.database}</div>
                <div className="connection-instance">{config.instance_connection_name}</div>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <div className="no-connections">
          <p>No saved connections</p>
        </div>
      )}
      
      {selectedConfig && (
        <div className="current-connection">
          <h4>Current Connection</h4>
          <div className="connection-details">
            <div className="detail-item">
              <span className="detail-label">Instance:</span>
              <span className="detail-value">{selectedConfig.instance_connection_name}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Database:</span>
              <span className="detail-value">{selectedConfig.database}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">User:</span>
              <span className="detail-value">{selectedConfig.user}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Connection:</span>
              <span className="detail-value">{selectedConfig.ip_type || 'PUBLIC'}</span>
            </div>
          </div>
          
          <button
            className="save-button"
            onClick={() => setShowSaveForm(true)}
          >
            Save Connection
          </button>
        </div>
      )}
      
      {showNewConnectionForm && (
        <div className="form-overlay">
          <div className="connection-form">
            <div className="form-header">
              <h4>New Connection</h4>
              <button
                className="close-button"
                onClick={() => setShowNewConnectionForm(false)}
              >
                &times;
              </button>
            </div>
            
            <form onSubmit={handleNewConnectionSubmit}>
              <div className="form-group">
                <label htmlFor="instanceConnectionName">Instance Connection Name</label>
                <input
                  type="text"
                  id="instanceConnectionName"
                  value={instanceConnectionName}
                  onChange={(e) => setInstanceConnectionName(e.target.value)}
                  placeholder="project:region:instance"
                  required
                />
                <div className="form-help">
                  Format: project:region:instance
                </div>
              </div>
              
              <div className="form-group">
                <label htmlFor="database">Database</label>
                <input
                  type="text"
                  id="database"
                  value={database}
                  onChange={(e) => setDatabase(e.target.value)}
                  placeholder="Database name"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="user">User</label>
                <input
                  type="text"
                  id="user"
                  value={user}
                  onChange={(e) => setUser(e.target.value)}
                  placeholder="Username"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="password">Password</label>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="ipType">Connection Type</label>
                <select
                  id="ipType"
                  value={ipType}
                  onChange={(e) => setIpType(e.target.value)}
                >
                  <option value="PUBLIC">Public IP</option>
                  <option value="PRIVATE">Private IP</option>
                </select>
              </div>
              
              <div className="form-actions">
                <button
                  type="button"
                  className="cancel-button"
                  onClick={() => setShowNewConnectionForm(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="connect-button"
                >
                  Connect
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {showSaveForm && (
        <div className="form-overlay">
          <div className="save-form">
            <div className="form-header">
              <h4>Save Connection</h4>
              <button
                className="close-button"
                onClick={() => setShowSaveForm(false)}
              >
                &times;
              </button>
            </div>
            
            <form onSubmit={handleSaveSubmit}>
              <div className="form-group">
                <label htmlFor="saveName">Connection Name</label>
                <input
                  type="text"
                  id="saveName"
                  value={saveName}
                  onChange={(e) => setSaveName(e.target.value)}
                  placeholder="My Database"
                  required
                />
              </div>
              
              <div className="form-actions">
                <button
                  type="button"
                  className="cancel-button"
                  onClick={() => setShowSaveForm(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="save-button"
                >
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      <style jsx>{`
        .database-selector {
          padding: 1.5rem;
        }
        
        .selector-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }
        
        .selector-header h3 {
          margin: 0;
          font-size: 1.2rem;
          color: #333;
        }
        
        .new-connection-button {
          padding: 0.5rem 1rem;
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .new-connection-button:hover {
          background-color: #0051a8;
        }
        
        .saved-connections {
          list-style: none;
          padding: 0;
          margin: 0 0 1.5rem;
        }
        
        .connection-item {
          padding: 1rem;
          border-radius: 4px;
          margin-bottom: 0.5rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .connection-item:hover {
          background-color: #f5f5f5;
        }
        
        .connection-item.selected {
          background-color: #e6f7ff;
          border-left: 3px solid #0070f3;
        }
        
        .connection-name {
          font-weight: 500;
          margin-bottom: 0.25rem;
        }
        
        .connection-details {
          font-size: 0.9rem;
          color: #666;
        }
        
        .connection-database {
          margin-bottom: 0.25rem;
        }
        
        .connection-instance {
          font-size: 0.8rem;
          word-break: break-all;
        }
        
        .no-connections {
          padding: 2rem;
          text-align: center;
          color: #666;
          background-color: #f8f9fa;
          border-radius: 4px;
        }
        
        .current-connection {
          margin-top: 1.5rem;
          padding: 1.5rem;
          background-color: #f8f9fa;
          border-radius: 4px;
        }
        
        .current-connection h4 {
          margin: 0 0 1rem;
          font-size: 1.1rem;
          color: #333;
        }
        
        .detail-item {
          margin-bottom: 0.5rem;
        }
        
        .detail-label {
          font-weight: 500;
          margin-right: 0.5rem;
        }
        
        .detail-value {
          color: #666;
          word-break: break-all;
        }
        
        .save-button {
          margin-top: 1rem;
          padding: 0.5rem 1rem;
          background-color: #28a745;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .save-button:hover {
          background-color: #218838;
        }
        
        .form-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(0, 0, 0, 0.5);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 1000;
        }
        
        .connection-form, .save-form {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          width: 100%;
          max-width: 500px;
          padding: 1.5rem;
        }
        
        .form-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }
        
        .form-header h4 {
          margin: 0;
          font-size: 1.2rem;
          color: #333;
        }
        
        .close-button {
          background: none;
          border: none;
          font-size: 1.5rem;
          color: #666;
          cursor: pointer;
        }
        
        .form-group {
          margin-bottom: 1.5rem;
        }
        
        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
        }
        
        .form-group input, .form-group select {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 1rem;
        }
        
        .form-help {
          margin-top: 0.25rem;
          font-size: 0.8rem;
          color: #666;
        }
        
        .form-actions {
          display: flex;
          justify-content: flex-end;
          gap: 1rem;
        }
        
        .cancel-button, .connect-button {
          padding: 0.75rem 1.5rem;
          border-radius: 4px;
          font-size: 1rem;
          cursor: pointer;
        }
        
        .cancel-button {
          background-color: #f8f9fa;
          color: #333;
          border: 1px solid #ddd;
        }
        
        .connect-button {
          background-color: #0070f3;
          color: white;
          border: none;
        }
      `}</style>
    </div>
  );
};

export default DatabaseSelector;
