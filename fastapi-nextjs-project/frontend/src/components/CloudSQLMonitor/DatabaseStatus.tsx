import React from 'react';
import { formatDistanceToNow } from 'date-fns';

interface DatabaseStatusProps {
  data: any;
  onRefresh: () => void;
}

const DatabaseStatus: React.FC<DatabaseStatusProps> = ({ data, onRefresh }) => {
  if (!data) {
    return (
      <div className="database-status">
        <div className="status-header">
          <h3>Database Status</h3>
          <button className="refresh-button" onClick={onRefresh}>
            Refresh
          </button>
        </div>
        <div className="no-data">
          <p>No status data available</p>
        </div>
      </div>
    );
  }
  
  // Check if database is online
  const isOnline = data.status === 'online';
  
  // Format timestamp
  const timestamp = new Date(data.timestamp);
  const timeAgo = formatDistanceToNow(timestamp, { addSuffix: true });
  
  return (
    <div className="database-status">
      <div className="status-header">
        <h3>Database Status</h3>
        <div className="status-actions">
          <span className="last-updated">Updated: {timeAgo}</span>
          <button className="refresh-button" onClick={onRefresh}>
            Refresh
          </button>
        </div>
      </div>
      
      <div className="status-content">
        <div className="status-overview">
          <div className={`status-indicator ${isOnline ? 'online' : 'offline'}`}>
            <div className="status-dot"></div>
            <div className="status-text">{isOnline ? 'Online' : 'Offline'}</div>
          </div>
          
          {!isOnline && data.error && (
            <div className="status-error">
              <h4>Error</h4>
              <p>{data.error}</p>
            </div>
          )}
          
          {isOnline && (
            <div className="status-details">
              <div className="status-item">
                <div className="item-label">Version</div>
                <div className="item-value">{data.version}</div>
              </div>
              
              <div className="status-item">
                <div className="item-label">Uptime</div>
                <div className="item-value">{data.uptime}</div>
              </div>
              
              <div className="status-item">
                <div className="item-label">Connections</div>
                <div className="item-value">{data.connection_count}</div>
              </div>
              
              <div className="status-item">
                <div className="item-label">Database Size</div>
                <div className="item-value">{data.size}</div>
              </div>
              
              <div className="status-item">
                <div className="item-label">Tables</div>
                <div className="item-value">{data.table_count}</div>
              </div>
            </div>
          )}
        </div>
        
        {isOnline && data.has_postgis && (
          <div className="postgis-status">
            <h4>PostGIS</h4>
            <div className="postgis-version">
              <div className="item-label">Version</div>
              <div className="item-value">{data.postgis_version}</div>
            </div>
          </div>
        )}
      </div>
      
      <style jsx>{`
        .database-status {
          padding: 1.5rem;
        }
        
        .status-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }
        
        .status-header h3 {
          margin: 0;
          font-size: 1.2rem;
          color: #333;
        }
        
        .status-actions {
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        
        .last-updated {
          font-size: 0.9rem;
          color: #666;
        }
        
        .refresh-button {
          padding: 0.5rem 1rem;
          background-color: #f0f0f0;
          color: #333;
          border: none;
          border-radius: 4px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .refresh-button:hover {
          background-color: #e0e0e0;
        }
        
        .status-content {
          display: grid;
          grid-template-columns: 1fr;
          gap: 1.5rem;
        }
        
        .status-overview {
          background-color: #f8f9fa;
          border-radius: 8px;
          padding: 1.5rem;
        }
        
        .status-indicator {
          display: flex;
          align-items: center;
          margin-bottom: 1.5rem;
        }
        
        .status-dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          margin-right: 0.5rem;
        }
        
        .status-indicator.online .status-dot {
          background-color: #28a745;
          box-shadow: 0 0 0 4px rgba(40, 167, 69, 0.2);
        }
        
        .status-indicator.offline .status-dot {
          background-color: #dc3545;
          box-shadow: 0 0 0 4px rgba(220, 53, 69, 0.2);
        }
        
        .status-text {
          font-weight: 500;
        }
        
        .status-indicator.online .status-text {
          color: #28a745;
        }
        
        .status-indicator.offline .status-text {
          color: #dc3545;
        }
        
        .status-error {
          background-color: #f8d7da;
          border-radius: 4px;
          padding: 1rem;
          margin-bottom: 1.5rem;
        }
        
        .status-error h4 {
          margin: 0 0 0.5rem;
          color: #721c24;
          font-size: 1rem;
        }
        
        .status-error p {
          margin: 0;
          color: #721c24;
          font-size: 0.9rem;
        }
        
        .status-details {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1rem;
        }
        
        .status-item {
          padding: 1rem;
          background-color: white;
          border-radius: 4px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }
        
        .item-label {
          font-size: 0.8rem;
          color: #666;
          margin-bottom: 0.25rem;
        }
        
        .item-value {
          font-size: 1rem;
          font-weight: 500;
          color: #333;
          word-break: break-word;
        }
        
        .postgis-status {
          background-color: #f8f9fa;
          border-radius: 8px;
          padding: 1.5rem;
        }
        
        .postgis-status h4 {
          margin: 0 0 1rem;
          font-size: 1.1rem;
          color: #333;
        }
        
        .postgis-version {
          padding: 1rem;
          background-color: white;
          border-radius: 4px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }
        
        .no-data {
          padding: 3rem;
          text-align: center;
          color: #666;
        }
        
        @media (min-width: 768px) {
          .status-content {
            grid-template-columns: 2fr 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default DatabaseStatus;
