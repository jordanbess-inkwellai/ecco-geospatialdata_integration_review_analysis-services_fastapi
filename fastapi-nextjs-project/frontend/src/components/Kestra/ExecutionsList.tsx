import React, { useState } from 'react';
import { formatDistanceToNow, formatDuration, intervalToDuration } from 'date-fns';
import { useKestraExecutions } from '../../hooks/useKestraExecutions';

interface ExecutionsListProps {
  workflowId?: string;
  onSelectExecution?: (executionId: string) => void;
}

const ExecutionsList: React.FC<ExecutionsListProps> = ({ workflowId, onSelectExecution }) => {
  const { 
    executions, 
    runningExecutions,
    completedExecutions,
    loading, 
    error, 
    syncExecutions,
    restartExecution,
    stopExecution
  } = useKestraExecutions(workflowId);
  
  const [syncing, setSyncing] = useState<boolean>(false);
  const [selectedExecution, setSelectedExecution] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'all' | 'running' | 'completed'>('all');
  
  // Handle sync executions
  const handleSyncExecutions = async () => {
    try {
      setSyncing(true);
      await syncExecutions(undefined, undefined, 100);
    } finally {
      setSyncing(false);
    }
  };
  
  // Handle execution selection
  const handleSelectExecution = (executionId: string) => {
    setSelectedExecution(executionId);
    if (onSelectExecution) {
      onSelectExecution(executionId);
    }
  };
  
  // Handle restart execution
  const handleRestartExecution = async (e: React.MouseEvent, executionId: string) => {
    e.stopPropagation();
    try {
      await restartExecution(executionId);
      alert('Execution restarted successfully!');
    } catch (error) {
      alert(`Error restarting execution: ${error}`);
    }
  };
  
  // Handle stop execution
  const handleStopExecution = async (e: React.MouseEvent, executionId: string) => {
    e.stopPropagation();
    try {
      await stopExecution(executionId);
      alert('Execution stopped successfully!');
    } catch (error) {
      alert(`Error stopping execution: ${error}`);
    }
  };
  
  // Format duration
  const formatExecutionDuration = (duration: number | null) => {
    if (!duration) return 'N/A';
    
    const durationObj = intervalToDuration({ start: 0, end: duration });
    
    // Format for human-readable output
    const parts = [];
    if (durationObj.hours) parts.push(`${durationObj.hours}h`);
    if (durationObj.minutes) parts.push(`${durationObj.minutes}m`);
    if (durationObj.seconds) parts.push(`${durationObj.seconds}s`);
    
    // If less than a second, show milliseconds
    if (parts.length === 0) {
      parts.push(`${Math.floor(duration)}ms`);
    }
    
    return parts.join(' ');
  };
  
  // Get executions based on view mode
  const displayedExecutions = viewMode === 'all' 
    ? executions 
    : viewMode === 'running' 
      ? runningExecutions 
      : completedExecutions;
  
  return (
    <div className="executions-list">
      <div className="list-header">
        <h2>Workflow Executions</h2>
        <div className="list-actions">
          <div className="view-mode-selector">
            <button 
              className={`view-mode-button ${viewMode === 'all' ? 'active' : ''}`}
              onClick={() => setViewMode('all')}
            >
              All
            </button>
            <button 
              className={`view-mode-button ${viewMode === 'running' ? 'active' : ''}`}
              onClick={() => setViewMode('running')}
            >
              Running ({runningExecutions.length})
            </button>
            <button 
              className={`view-mode-button ${viewMode === 'completed' ? 'active' : ''}`}
              onClick={() => setViewMode('completed')}
            >
              Completed
            </button>
          </div>
          <button 
            className="sync-button"
            onClick={handleSyncExecutions}
            disabled={syncing}
          >
            {syncing ? 'Syncing...' : 'Sync Executions'}
          </button>
        </div>
      </div>
      
      {error && (
        <div className="error-message">{error}</div>
      )}
      
      {loading ? (
        <div className="loading">Loading executions...</div>
      ) : displayedExecutions.length === 0 ? (
        <div className="no-executions">
          <p>No executions found</p>
          <button 
            className="sync-button"
            onClick={handleSyncExecutions}
            disabled={syncing}
          >
            {syncing ? 'Syncing...' : 'Sync from Kestra'}
          </button>
        </div>
      ) : (
        <div className="executions-table-container">
          <table className="executions-table">
            <thead>
              <tr>
                <th>Status</th>
                <th>ID</th>
                <th>Started</th>
                <th>Duration</th>
                <th>Trigger</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {displayedExecutions.map(execution => (
                <tr 
                  key={execution.id} 
                  className={`execution-row ${selectedExecution === execution.id ? 'selected' : ''}`}
                  onClick={() => handleSelectExecution(execution.id)}
                >
                  <td>
                    <span className={`status-badge ${execution.status.toLowerCase()}`}>
                      {execution.status}
                    </span>
                  </td>
                  <td className="execution-id">{execution.execution_id}</td>
                  <td className="execution-start">
                    {execution.start_date 
                      ? formatDistanceToNow(new Date(execution.start_date), { addSuffix: true })
                      : 'N/A'
                    }
                  </td>
                  <td className="execution-duration">
                    {formatExecutionDuration(execution.duration)}
                  </td>
                  <td className="execution-trigger">
                    {execution.trigger?.type || 'Manual'}
                  </td>
                  <td className="execution-actions">
                    {['FAILED', 'KILLED'].includes(execution.status) && (
                      <button
                        className="restart-button"
                        onClick={(e) => handleRestartExecution(e, execution.execution_id)}
                        title="Restart execution"
                      >
                        Restart
                      </button>
                    )}
                    
                    {['CREATED', 'RUNNING', 'PAUSED', 'RESTARTED'].includes(execution.status) && (
                      <button
                        className="stop-button"
                        onClick={(e) => handleStopExecution(e, execution.execution_id)}
                        title="Stop execution"
                      >
                        Stop
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      <style jsx>{`
        .executions-list {
          padding: 1rem;
        }
        
        .list-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }
        
        .list-header h2 {
          margin: 0;
          font-size: 1.5rem;
          color: #333;
        }
        
        .list-actions {
          display: flex;
          gap: 1rem;
          align-items: center;
        }
        
        .view-mode-selector {
          display: flex;
          border: 1px solid #ddd;
          border-radius: 4px;
          overflow: hidden;
        }
        
        .view-mode-button {
          padding: 0.5rem 1rem;
          background-color: #f8f9fa;
          border: none;
          font-size: 0.9rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .view-mode-button.active {
          background-color: #0070f3;
          color: white;
        }
        
        .sync-button {
          padding: 0.5rem 1rem;
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .sync-button:hover {
          background-color: #0051a8;
        }
        
        .sync-button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }
        
        .error-message {
          background-color: #f8d7da;
          color: #721c24;
          padding: 0.75rem;
          border-radius: 4px;
          margin-bottom: 1.5rem;
        }
        
        .loading, .no-executions {
          padding: 3rem;
          text-align: center;
          color: #666;
          background-color: #f8f9fa;
          border-radius: 4px;
        }
        
        .no-executions button {
          margin-top: 1rem;
        }
        
        .executions-table-container {
          overflow-x: auto;
        }
        
        .executions-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.9rem;
        }
        
        .executions-table th {
          text-align: left;
          padding: 0.75rem;
          background-color: #f8f9fa;
          border-bottom: 2px solid #ddd;
        }
        
        .execution-row {
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .execution-row:hover {
          background-color: #f5f5f5;
        }
        
        .execution-row.selected {
          background-color: #e3f2fd;
        }
        
        .execution-row td {
          padding: 0.75rem;
          border-bottom: 1px solid #ddd;
        }
        
        .status-badge {
          display: inline-block;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.8rem;
          font-weight: 500;
          text-transform: uppercase;
        }
        
        .status-badge.created,
        .status-badge.running,
        .status-badge.paused,
        .status-badge.restarted {
          background-color: #cff4fc;
          color: #055160;
        }
        
        .status-badge.success {
          background-color: #d1e7dd;
          color: #0f5132;
        }
        
        .status-badge.warning {
          background-color: #fff3cd;
          color: #664d03;
        }
        
        .status-badge.failed,
        .status-badge.killed,
        .status-badge.killing {
          background-color: #f8d7da;
          color: #842029;
        }
        
        .execution-id {
          font-family: monospace;
          font-size: 0.8rem;
        }
        
        .execution-actions {
          display: flex;
          gap: 0.5rem;
        }
        
        .restart-button,
        .stop-button {
          padding: 0.25rem 0.5rem;
          border: none;
          border-radius: 4px;
          font-size: 0.8rem;
          cursor: pointer;
        }
        
        .restart-button {
          background-color: #0070f3;
          color: white;
        }
        
        .stop-button {
          background-color: #dc3545;
          color: white;
        }
        
        @media (max-width: 768px) {
          .list-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
          }
          
          .list-actions {
            width: 100%;
            flex-direction: column;
          }
          
          .view-mode-selector {
            width: 100%;
          }
          
          .view-mode-button {
            flex: 1;
            text-align: center;
          }
          
          .sync-button {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default ExecutionsList;
