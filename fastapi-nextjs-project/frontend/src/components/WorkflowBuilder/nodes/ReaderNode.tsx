import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

const ReaderNode: React.FC<NodeProps> = ({ data, isConnectable }) => {
  const sourceType = data.sourceType || 'Unknown';
  
  return (
    <div className="reader-node">
      <div className="node-header">
        <div className="node-type">Reader</div>
        <div className="node-source-type">{sourceType}</div>
      </div>
      <div className="node-content">
        <div className="node-label">{data.label}</div>
        {data.sourceConfig && (
          <div className="node-details">
            {data.sourceConfig.query && (
              <div className="node-detail">
                <span className="detail-label">Query:</span>
                <span className="detail-value">{truncateText(data.sourceConfig.query, 30)}</span>
              </div>
            )}
            {data.sourceConfig.url && (
              <div className="node-detail">
                <span className="detail-label">URL:</span>
                <span className="detail-value">{truncateText(data.sourceConfig.url, 30)}</span>
              </div>
            )}
            {data.sourceConfig.path && (
              <div className="node-detail">
                <span className="detail-label">Path:</span>
                <span className="detail-value">{truncateText(data.sourceConfig.path, 30)}</span>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        id="output"
        style={{ background: '#0041d0' }}
        isConnectable={isConnectable}
      />
      
      <style jsx>{`
        .reader-node {
          padding: 10px;
          border-radius: 5px;
          background-color: #e3f2fd;
          border: 1px solid #90caf9;
          width: 200px;
          color: #333;
          font-family: sans-serif;
        }
        
        .node-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
          padding-bottom: 8px;
          border-bottom: 1px solid #90caf9;
        }
        
        .node-type {
          font-weight: bold;
          font-size: 12px;
          color: #0277bd;
        }
        
        .node-source-type {
          font-size: 11px;
          background-color: #bbdefb;
          padding: 2px 6px;
          border-radius: 10px;
          color: #0277bd;
        }
        
        .node-content {
          padding: 5px 0;
        }
        
        .node-label {
          font-weight: bold;
          margin-bottom: 8px;
          font-size: 14px;
        }
        
        .node-details {
          font-size: 12px;
        }
        
        .node-detail {
          margin-bottom: 4px;
          display: flex;
          flex-direction: column;
        }
        
        .detail-label {
          color: #666;
          margin-right: 5px;
        }
        
        .detail-value {
          font-family: monospace;
          background-color: #f5f5f5;
          padding: 2px 4px;
          border-radius: 3px;
          word-break: break-all;
        }
      `}</style>
    </div>
  );
};

// Helper function to truncate text
const truncateText = (text: string, maxLength: number) => {
  if (!text) return '';
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
};

export default memo(ReaderNode);
