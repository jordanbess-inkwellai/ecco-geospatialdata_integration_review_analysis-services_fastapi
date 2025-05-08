import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { formatDistanceToNow } from 'date-fns';
import { useKestraWorkflows } from '../../hooks/useKestraWorkflows';

interface WorkflowsListProps {
  onSelectWorkflow?: (workflowId: string) => void;
}

const WorkflowsList: React.FC<WorkflowsListProps> = ({ onSelectWorkflow }) => {
  const { workflows, loading, error, syncWorkflows, triggerWorkflow, toggleWorkflowEnabled } = useKestraWorkflows();
  const [namespace, setNamespace] = useState<string>('');
  const [syncing, setSyncing] = useState<boolean>(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);
  const router = useRouter();
  
  // Get unique namespaces
  const namespaces = [...new Set(workflows.map(workflow => workflow.namespace))];
  
  // Filter workflows by namespace
  const filteredWorkflows = namespace 
    ? workflows.filter(workflow => workflow.namespace === namespace)
    : workflows;
  
  // Handle sync workflows
  const handleSyncWorkflows = async () => {
    try {
      setSyncing(true);
      await syncWorkflows(namespace || undefined);
    } finally {
      setSyncing(false);
    }
  };
  
  // Handle workflow selection
  const handleSelectWorkflow = (workflowId: string) => {
    setSelectedWorkflow(workflowId);
    if (onSelectWorkflow) {
      onSelectWorkflow(workflowId);
    } else {
      router.push(`/workflows/${workflowId}`);
    }
  };
  
  // Handle trigger workflow
  const handleTriggerWorkflow = async (e: React.MouseEvent, workflow: any) => {
    e.stopPropagation();
    try {
      await triggerWorkflow(workflow.namespace, workflow.workflow_id);
      alert(`Workflow ${workflow.name} triggered successfully!`);
    } catch (error) {
      alert(`Error triggering workflow: ${error}`);
    }
  };
  
  // Handle toggle workflow enabled
  const handleToggleEnabled = async (e: React.MouseEvent, workflow: any) => {
    e.stopPropagation();
    try {
      await toggleWorkflowEnabled(workflow.id, workflow.enabled);
    } catch (error) {
      alert(`Error toggling workflow enabled state: ${error}`);
    }
  };
  
  return (
    <div className="workflows-list">
      <div className="list-header">
        <h2>Kestra Workflows</h2>
        <div className="list-actions">
          <div className="namespace-filter">
            <select 
              value={namespace} 
              onChange={(e) => setNamespace(e.target.value)}
              className="namespace-select"
            >
              <option value="">All Namespaces</option>
              {namespaces.map(ns => (
                <option key={ns} value={ns}>{ns}</option>
              ))}
            </select>
          </div>
          <button 
            className="sync-button"
            onClick={handleSyncWorkflows}
            disabled={syncing}
          >
            {syncing ? 'Syncing...' : 'Sync Workflows'}
          </button>
        </div>
      </div>
      
      {error && (
        <div className="error-message">{error}</div>
      )}
      
      {loading ? (
        <div className="loading">Loading workflows...</div>
      ) : filteredWorkflows.length === 0 ? (
        <div className="no-workflows">
          <p>No workflows found</p>
          <button 
            className="sync-button"
            onClick={handleSyncWorkflows}
            disabled={syncing}
          >
            {syncing ? 'Syncing...' : 'Sync from Kestra'}
          </button>
        </div>
      ) : (
        <ul className="workflows-grid">
          {filteredWorkflows.map(workflow => (
            <li 
              key={workflow.id} 
              className={`workflow-card ${selectedWorkflow === workflow.id ? 'selected' : ''} ${!workflow.enabled ? 'disabled' : ''}`}
              onClick={() => handleSelectWorkflow(workflow.id)}
            >
              <div className="workflow-header">
                <h3 className="workflow-name">{workflow.name}</h3>
                <div className="workflow-namespace">{workflow.namespace}</div>
              </div>
              
              <div className="workflow-description">
                {workflow.description || 'No description'}
              </div>
              
              <div className="workflow-tags">
                {workflow.tags.map((tag: string) => (
                  <span key={tag} className="tag">{tag}</span>
                ))}
              </div>
              
              <div className="workflow-meta">
                <div className="workflow-id">ID: {workflow.workflow_id}</div>
                <div className="workflow-updated">
                  Updated: {formatDistanceToNow(new Date(workflow.updated), { addSuffix: true })}
                </div>
              </div>
              
              <div className="workflow-actions">
                <button
                  className={`toggle-button ${workflow.enabled ? 'enabled' : 'disabled'}`}
                  onClick={(e) => handleToggleEnabled(e, workflow)}
                  title={workflow.enabled ? 'Disable workflow' : 'Enable workflow'}
                >
                  {workflow.enabled ? 'Enabled' : 'Disabled'}
                </button>
                
                <button
                  className="trigger-button"
                  onClick={(e) => handleTriggerWorkflow(e, workflow)}
                  disabled={!workflow.enabled}
                >
                  Run
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
      
      <style jsx>{`
        .workflows-list {
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
        
        .namespace-filter {
          min-width: 200px;
        }
        
        .namespace-select {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.9rem;
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
        
        .loading, .no-workflows {
          padding: 3rem;
          text-align: center;
          color: #666;
          background-color: #f8f9fa;
          border-radius: 4px;
        }
        
        .no-workflows button {
          margin-top: 1rem;
        }
        
        .workflows-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 1.5rem;
          list-style: none;
          padding: 0;
          margin: 0;
        }
        
        .workflow-card {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 1.5rem;
          cursor: pointer;
          transition: all 0.2s;
          display: flex;
          flex-direction: column;
          height: 100%;
        }
        
        .workflow-card:hover {
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
          transform: translateY(-2px);
        }
        
        .workflow-card.selected {
          border: 2px solid #0070f3;
        }
        
        .workflow-card.disabled {
          opacity: 0.7;
        }
        
        .workflow-header {
          margin-bottom: 1rem;
        }
        
        .workflow-name {
          margin: 0 0 0.25rem;
          font-size: 1.2rem;
          color: #333;
        }
        
        .workflow-namespace {
          font-size: 0.9rem;
          color: #666;
          margin-bottom: 0.5rem;
        }
        
        .workflow-description {
          font-size: 0.9rem;
          color: #333;
          margin-bottom: 1rem;
          flex-grow: 1;
        }
        
        .workflow-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }
        
        .tag {
          background-color: #e9ecef;
          color: #495057;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.8rem;
        }
        
        .workflow-meta {
          font-size: 0.8rem;
          color: #666;
          margin-bottom: 1rem;
        }
        
        .workflow-id {
          margin-bottom: 0.25rem;
        }
        
        .workflow-actions {
          display: flex;
          justify-content: space-between;
          gap: 0.5rem;
        }
        
        .toggle-button, .trigger-button {
          padding: 0.5rem;
          border: none;
          border-radius: 4px;
          font-size: 0.8rem;
          cursor: pointer;
          flex: 1;
        }
        
        .toggle-button.enabled {
          background-color: #28a745;
          color: white;
        }
        
        .toggle-button.disabled {
          background-color: #dc3545;
          color: white;
        }
        
        .trigger-button {
          background-color: #0070f3;
          color: white;
        }
        
        .trigger-button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }
        
        @media (max-width: 768px) {
          .list-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
          }
          
          .list-actions {
            width: 100%;
          }
          
          .workflows-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default WorkflowsList;
