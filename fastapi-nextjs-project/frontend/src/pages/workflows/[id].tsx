import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../../components/Layout';
import ExecutionsList from '../../components/Kestra/ExecutionsList';
import TriggersList from '../../components/Kestra/TriggersList';
import { getPocketBase, isAuthenticated } from '../../lib/pocketbase';

const WorkflowDetailPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [workflow, setWorkflow] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'executions' | 'triggers' | 'details'>('executions');
  const router = useRouter();
  const { id } = router.query;
  
  // Load workflow
  useEffect(() => {
    if (!id || !isAuthenticated()) {
      if (!isAuthenticated()) {
        router.push('/login?redirect=/workflows');
      }
      return;
    }
    
    const loadWorkflow = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const pb = getPocketBase();
        const record = await pb.collection('kestra_workflows').getOne(id as string);
        
        setWorkflow({
          id: record.id,
          name: record.name,
          namespace: record.namespace,
          workflow_id: record.workflow_id,
          description: record.description,
          tags: JSON.parse(record.tags || '[]'),
          triggers: JSON.parse(record.triggers || '[]'),
          tasks: JSON.parse(record.tasks || '[]'),
          enabled: record.enabled,
          owner: record.owner,
          created: record.created,
          updated: record.updated
        });
        
        setIsLoading(false);
      } catch (err: any) {
        console.error('Error loading workflow:', err);
        setError(err.message || 'Error loading workflow');
        setIsLoading(false);
      }
    };
    
    loadWorkflow();
  }, [id, router]);
  
  if (isLoading) {
    return (
      <Layout>
        <div className="loading-container">
          <p>Loading workflow...</p>
        </div>
      </Layout>
    );
  }
  
  if (error) {
    return (
      <Layout>
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <button
            className="back-button"
            onClick={() => router.push('/workflows')}
          >
            Back to Workflows
          </button>
        </div>
      </Layout>
    );
  }
  
  return (
    <Layout>
      <div className="workflow-detail-page">
        {workflow ? (
          <>
            <div className="workflow-header">
              <div className="workflow-info">
                <h1 className="workflow-name">{workflow.name}</h1>
                <div className="workflow-meta">
                  <div className="workflow-namespace">Namespace: {workflow.namespace}</div>
                  <div className="workflow-id">ID: {workflow.workflow_id}</div>
                  <div className={`workflow-status ${workflow.enabled ? 'enabled' : 'disabled'}`}>
                    Status: {workflow.enabled ? 'Enabled' : 'Disabled'}
                  </div>
                </div>
                {workflow.description && (
                  <div className="workflow-description">
                    {workflow.description}
                  </div>
                )}
                {workflow.tags.length > 0 && (
                  <div className="workflow-tags">
                    {workflow.tags.map((tag: string) => (
                      <span key={tag} className="tag">{tag}</span>
                    ))}
                  </div>
                )}
              </div>
              <div className="workflow-actions">
                <button
                  className="back-button"
                  onClick={() => router.push('/workflows')}
                >
                  Back to Workflows
                </button>
              </div>
            </div>
            
            <div className="tabs">
              <button
                className={`tab-button ${activeTab === 'executions' ? 'active' : ''}`}
                onClick={() => setActiveTab('executions')}
              >
                Executions
              </button>
              <button
                className={`tab-button ${activeTab === 'triggers' ? 'active' : ''}`}
                onClick={() => setActiveTab('triggers')}
              >
                Triggers
              </button>
              <button
                className={`tab-button ${activeTab === 'details' ? 'active' : ''}`}
                onClick={() => setActiveTab('details')}
              >
                Details
              </button>
            </div>
            
            <div className="tab-content">
              {activeTab === 'executions' && (
                <ExecutionsList workflowId={workflow.id} />
              )}
              
              {activeTab === 'triggers' && (
                <TriggersList workflowId={workflow.id} />
              )}
              
              {activeTab === 'details' && (
                <div className="workflow-details">
                  <h2>Workflow Details</h2>
                  
                  <div className="details-section">
                    <h3>Tasks</h3>
                    {workflow.tasks.length > 0 ? (
                      <pre className="json-viewer">
                        {JSON.stringify(workflow.tasks, null, 2)}
                      </pre>
                    ) : (
                      <p>No tasks defined</p>
                    )}
                  </div>
                  
                  <div className="details-section">
                    <h3>Kestra Triggers</h3>
                    {workflow.triggers.length > 0 ? (
                      <pre className="json-viewer">
                        {JSON.stringify(workflow.triggers, null, 2)}
                      </pre>
                    ) : (
                      <p>No Kestra triggers defined</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="not-found">
            <h2>Workflow Not Found</h2>
            <p>The requested workflow could not be found.</p>
            <button
              className="back-button"
              onClick={() => router.push('/workflows')}
            >
              Back to Workflows
            </button>
          </div>
        )}
      </div>
      
      <style jsx>{`
        .workflow-detail-page {
          padding: 1.5rem;
        }
        
        .loading-container {
          display: flex;
          justify-content: center;
          align-items: center;
          height: 50vh;
          font-size: 1.2rem;
          color: #666;
        }
        
        .error-container, .not-found {
          max-width: 600px;
          margin: 3rem auto;
          padding: 2rem;
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          text-align: center;
        }
        
        .error-container h2, .not-found h2 {
          margin-top: 0;
          color: #333;
        }
        
        .error-container p, .not-found p {
          margin-bottom: 2rem;
          color: #666;
        }
        
        .workflow-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 2rem;
        }
        
        .workflow-name {
          margin: 0 0 0.5rem;
          font-size: 2rem;
          color: #333;
        }
        
        .workflow-meta {
          display: flex;
          flex-wrap: wrap;
          gap: 1rem;
          margin-bottom: 1rem;
          font-size: 0.9rem;
          color: #666;
        }
        
        .workflow-status {
          font-weight: 500;
        }
        
        .workflow-status.enabled {
          color: #0f5132;
        }
        
        .workflow-status.disabled {
          color: #842029;
        }
        
        .workflow-description {
          margin-bottom: 1rem;
          color: #333;
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
        
        .workflow-actions {
          display: flex;
          gap: 1rem;
        }
        
        .back-button {
          padding: 0.75rem 1.5rem;
          background-color: #f8f9fa;
          color: #333;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .back-button:hover {
          background-color: #e9ecef;
        }
        
        .tabs {
          display: flex;
          border-bottom: 1px solid #ddd;
          margin-bottom: 1.5rem;
        }
        
        .tab-button {
          padding: 0.75rem 1.5rem;
          background: none;
          border: none;
          border-bottom: 3px solid transparent;
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .tab-button:hover {
          background-color: #f8f9fa;
        }
        
        .tab-button.active {
          border-bottom-color: #0070f3;
          color: #0070f3;
          font-weight: 500;
        }
        
        .workflow-details {
          padding: 1rem;
        }
        
        .workflow-details h2 {
          margin-top: 0;
          font-size: 1.5rem;
          color: #333;
        }
        
        .details-section {
          margin-bottom: 2rem;
        }
        
        .details-section h3 {
          margin-top: 0;
          font-size: 1.2rem;
          color: #333;
        }
        
        .json-viewer {
          background-color: #f8f9fa;
          padding: 1rem;
          border-radius: 4px;
          overflow: auto;
          font-size: 0.9rem;
          max-height: 400px;
        }
        
        @media (max-width: 768px) {
          .workflow-header {
            flex-direction: column;
            gap: 1rem;
          }
          
          .workflow-actions {
            width: 100%;
          }
          
          .back-button {
            width: 100%;
          }
          
          .tabs {
            overflow-x: auto;
          }
        }
      `}</style>
    </Layout>
  );
};

export default WorkflowDetailPage;
