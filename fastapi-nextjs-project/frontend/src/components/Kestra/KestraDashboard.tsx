import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { formatDistanceToNow } from 'date-fns';
import { useKestraWorkflows } from '../../hooks/useKestraWorkflows';
import { useKestraExecutions } from '../../hooks/useKestraExecutions';
import WorkflowsList from './WorkflowsList';
import ExecutionsList from './ExecutionsList';

interface KestraDashboardProps {
  initialNamespace?: string;
}

const KestraDashboard: React.FC<KestraDashboardProps> = ({ initialNamespace }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'workflows' | 'executions' | 'metrics'>('overview');
  const [selectedNamespace, setSelectedNamespace] = useState<string>(initialNamespace || '');
  const [refreshInterval, setRefreshInterval] = useState<number>(30); // seconds
  const [isAutoRefresh, setIsAutoRefresh] = useState<boolean>(true);
  
  const { 
    workflows, 
    loading: workflowsLoading, 
    error: workflowsError,
    syncWorkflows
  } = useKestraWorkflows();
  
  const {
    executions,
    runningExecutions,
    completedExecutions,
    successfulExecutions,
    failedExecutions,
    loading: executionsLoading,
    error: executionsError,
    syncExecutions
  } = useKestraExecutions();
  
  const router = useRouter();
  
  // Auto-refresh data
  useEffect(() => {
    if (!isAutoRefresh) return;
    
    const refreshData = async () => {
      try {
        await syncWorkflows(selectedNamespace || undefined);
        await syncExecutions(selectedNamespace || undefined);
      } catch (error) {
        console.error('Error refreshing data:', error);
      }
    };
    
    // Initial refresh
    refreshData();
    
    // Set up interval
    const intervalId = setInterval(refreshData, refreshInterval * 1000);
    
    // Clean up
    return () => {
      clearInterval(intervalId);
    };
  }, [isAutoRefresh, refreshInterval, selectedNamespace, syncWorkflows, syncExecutions]);
  
  // Get unique namespaces
  const namespaces = [...new Set(workflows.map(workflow => workflow.namespace))];
  
  // Calculate statistics
  const totalWorkflows = workflows.length;
  const enabledWorkflows = workflows.filter(w => w.enabled).length;
  const disabledWorkflows = totalWorkflows - enabledWorkflows;
  
  const totalExecutions = executions.length;
  const runningCount = runningExecutions.length;
  const successCount = successfulExecutions.length;
  const failedCount = failedExecutions.length;
  
  // Calculate success rate
  const completedCount = completedExecutions.length;
  const successRate = completedCount > 0 
    ? Math.round((successCount / completedCount) * 100) 
    : 0;
  
  // Handle refresh
  const handleRefresh = async () => {
    try {
      await syncWorkflows(selectedNamespace || undefined);
      await syncExecutions(selectedNamespace || undefined);
    } catch (error) {
      console.error('Error refreshing data:', error);
    }
  };
  
  // Render metrics cards
  const renderMetricsCards = () => {
    return (
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-title">Workflows</div>
          <div className="metric-value">{totalWorkflows}</div>
          <div className="metric-details">
            <div className="metric-detail">
              <span className="detail-label">Enabled:</span>
              <span className="detail-value">{enabledWorkflows}</span>
            </div>
            <div className="metric-detail">
              <span className="detail-label">Disabled:</span>
              <span className="detail-value">{disabledWorkflows}</span>
            </div>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-title">Executions</div>
          <div className="metric-value">{totalExecutions}</div>
          <div className="metric-details">
            <div className="metric-detail">
              <span className="detail-label">Running:</span>
              <span className="detail-value">{runningCount}</span>
            </div>
            <div className="metric-detail">
              <span className="detail-label">Completed:</span>
              <span className="detail-value">{completedCount}</span>
            </div>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-title">Success Rate</div>
          <div className="metric-value">{successRate}%</div>
          <div className="metric-details">
            <div className="metric-detail">
              <span className="detail-label">Success:</span>
              <span className="detail-value success">{successCount}</span>
            </div>
            <div className="metric-detail">
              <span className="detail-label">Failed:</span>
              <span className="detail-value error">{failedCount}</span>
            </div>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-title">Last Refresh</div>
          <div className="metric-value">
            {new Date().toLocaleTimeString()}
          </div>
          <div className="metric-details">
            <div className="metric-detail">
              <span className="detail-label">Auto-refresh:</span>
              <span className="detail-value">
                {isAutoRefresh ? `Every ${refreshInterval}s` : 'Off'}
              </span>
            </div>
            <div className="metric-detail">
              <button 
                className="refresh-button"
                onClick={handleRefresh}
              >
                Refresh Now
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  // Render recent executions
  const renderRecentExecutions = () => {
    const recentExecutions = [...executions].sort((a, b) => {
      return new Date(b.created).getTime() - new Date(a.created).getTime();
    }).slice(0, 5);
    
    return (
      <div className="recent-executions">
        <h3>Recent Executions</h3>
        
        {recentExecutions.length === 0 ? (
          <div className="no-data">No recent executions found</div>
        ) : (
          <table className="executions-table">
            <thead>
              <tr>
                <th>Status</th>
                <th>Workflow</th>
                <th>Started</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              {recentExecutions.map(execution => (
                <tr 
                  key={execution.id}
                  className="execution-row"
                  onClick={() => router.push(`/workflows/${execution.workflow}/executions/${execution.id}`)}
                >
                  <td>
                    <span className={`status-badge ${execution.status.toLowerCase()}`}>
                      {execution.status}
                    </span>
                  </td>
                  <td>{workflows.find(w => w.id === execution.workflow)?.name || execution.workflow_id}</td>
                  <td>
                    {execution.start_date 
                      ? formatDistanceToNow(new Date(execution.start_date), { addSuffix: true })
                      : 'N/A'
                    }
                  </td>
                  <td>
                    {execution.duration 
                      ? `${Math.round(execution.duration / 1000)}s`
                      : 'N/A'
                    }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        
        <div className="view-all">
          <button 
            className="view-all-button"
            onClick={() => setActiveTab('executions')}
          >
            View All Executions
          </button>
        </div>
      </div>
    );
  };
  
  return (
    <div className="kestra-dashboard">
      <div className="dashboard-header">
        <h1>Kestra Workflows Dashboard</h1>
        
        <div className="dashboard-controls">
          <div className="namespace-selector">
            <select
              value={selectedNamespace}
              onChange={(e) => setSelectedNamespace(e.target.value)}
              className="namespace-select"
            >
              <option value="">All Namespaces</option>
              {namespaces.map(ns => (
                <option key={ns} value={ns}>{ns}</option>
              ))}
            </select>
          </div>
          
          <div className="refresh-controls">
            <div className="auto-refresh-toggle">
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={isAutoRefresh}
                  onChange={() => setIsAutoRefresh(!isAutoRefresh)}
                />
                <span className="toggle-slider"></span>
              </label>
              <span className="toggle-label">Auto-refresh</span>
            </div>
            
            {isAutoRefresh && (
              <select
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(Number(e.target.value))}
                className="interval-select"
              >
                <option value="10">10s</option>
                <option value="30">30s</option>
                <option value="60">1m</option>
                <option value="300">5m</option>
              </select>
            )}
          </div>
        </div>
      </div>
      
      <div className="tabs">
        <button
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab-button ${activeTab === 'workflows' ? 'active' : ''}`}
          onClick={() => setActiveTab('workflows')}
        >
          Workflows
        </button>
        <button
          className={`tab-button ${activeTab === 'executions' ? 'active' : ''}`}
          onClick={() => setActiveTab('executions')}
        >
          Executions
        </button>
        <button
          className={`tab-button ${activeTab === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveTab('metrics')}
        >
          Metrics
        </button>
      </div>
      
      <div className="tab-content">
        {(workflowsLoading || executionsLoading) && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <div className="loading-text">Loading data...</div>
          </div>
        )}
        
        {(workflowsError || executionsError) && (
          <div className="error-message">
            {workflowsError || executionsError}
          </div>
        )}
        
        {activeTab === 'overview' && (
          <div className="overview-tab">
            {renderMetricsCards()}
            {renderRecentExecutions()}
          </div>
        )}
        
        {activeTab === 'workflows' && (
          <WorkflowsList />
        )}
        
        {activeTab === 'executions' && (
          <ExecutionsList />
        )}
        
        {activeTab === 'metrics' && (
          <div className="metrics-tab">
            <h2>Workflow Metrics</h2>
            
            <div className="metrics-charts">
              <div className="chart-container">
                <h3>Execution Status Distribution</h3>
                <div className="status-distribution">
                  <div className="status-bar">
                    <div 
                      className="status-segment success" 
                      style={{ width: `${successRate}%` }}
                      title={`Success: ${successCount} (${successRate}%)`}
                    ></div>
                    <div 
                      className="status-segment failed" 
                      style={{ width: `${100 - successRate}%` }}
                      title={`Failed: ${failedCount} (${100 - successRate}%)`}
                    ></div>
                  </div>
                  <div className="status-legend">
                    <div className="legend-item">
                      <div className="legend-color success"></div>
                      <div className="legend-label">Success ({successRate}%)</div>
                    </div>
                    <div className="legend-item">
                      <div className="legend-color failed"></div>
                      <div className="legend-label">Failed ({100 - successRate}%)</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="chart-container">
                <h3>Workflow Status</h3>
                <div className="workflow-status-chart">
                  <div className="status-item">
                    <div className="status-label">Enabled</div>
                    <div className="status-bar-container">
                      <div 
                        className="status-bar-value enabled"
                        style={{ width: `${(enabledWorkflows / totalWorkflows) * 100}%` }}
                      ></div>
                    </div>
                    <div className="status-count">{enabledWorkflows}</div>
                  </div>
                  <div className="status-item">
                    <div className="status-label">Disabled</div>
                    <div className="status-bar-container">
                      <div 
                        className="status-bar-value disabled"
                        style={{ width: `${(disabledWorkflows / totalWorkflows) * 100}%` }}
                      ></div>
                    </div>
                    <div className="status-count">{disabledWorkflows}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <style jsx>{`
        .kestra-dashboard {
          padding: 1.5rem;
        }
        
        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
        }
        
        .dashboard-header h1 {
          margin: 0;
          font-size: 1.8rem;
          color: #333;
        }
        
        .dashboard-controls {
          display: flex;
          gap: 1rem;
          align-items: center;
        }
        
        .namespace-selector {
          min-width: 200px;
        }
        
        .namespace-select, .interval-select {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.9rem;
        }
        
        .refresh-controls {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .auto-refresh-toggle {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .toggle-switch {
          position: relative;
          display: inline-block;
          width: 40px;
          height: 24px;
        }
        
        .toggle-switch input {
          opacity: 0;
          width: 0;
          height: 0;
        }
        
        .toggle-slider {
          position: absolute;
          cursor: pointer;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: #ccc;
          transition: .4s;
          border-radius: 24px;
        }
        
        .toggle-slider:before {
          position: absolute;
          content: "";
          height: 16px;
          width: 16px;
          left: 4px;
          bottom: 4px;
          background-color: white;
          transition: .4s;
          border-radius: 50%;
        }
        
        input:checked + .toggle-slider {
          background-color: #0070f3;
        }
        
        input:checked + .toggle-slider:before {
          transform: translateX(16px);
        }
        
        .toggle-label {
          font-size: 0.9rem;
          color: #666;
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
        
        .tab-content {
          position: relative;
          min-height: 400px;
        }
        
        .loading-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(255, 255, 255, 0.8);
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          z-index: 10;
        }
        
        .loading-spinner {
          border: 4px solid #f3f3f3;
          border-top: 4px solid #0070f3;
          border-radius: 50%;
          width: 40px;
          height: 40px;
          animation: spin 1s linear infinite;
          margin-bottom: 1rem;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .loading-text {
          font-size: 1rem;
          color: #666;
        }
        
        .error-message {
          background-color: #f8d7da;
          color: #721c24;
          padding: 0.75rem;
          border-radius: 4px;
          margin-bottom: 1.5rem;
        }
        
        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }
        
        .metric-card {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 1.5rem;
        }
        
        .metric-title {
          font-size: 1rem;
          color: #666;
          margin-bottom: 0.5rem;
        }
        
        .metric-value {
          font-size: 2rem;
          font-weight: 500;
          color: #333;
          margin-bottom: 1rem;
        }
        
        .metric-details {
          font-size: 0.9rem;
        }
        
        .metric-detail {
          display: flex;
          justify-content: space-between;
          margin-bottom: 0.25rem;
        }
        
        .detail-label {
          color: #666;
        }
        
        .detail-value {
          font-weight: 500;
        }
        
        .detail-value.success {
          color: #28a745;
        }
        
        .detail-value.error {
          color: #dc3545;
        }
        
        .refresh-button {
          padding: 0.25rem 0.5rem;
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 0.8rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .refresh-button:hover {
          background-color: #0051a8;
        }
        
        .recent-executions {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 1.5rem;
        }
        
        .recent-executions h3 {
          margin-top: 0;
          margin-bottom: 1rem;
          font-size: 1.2rem;
          color: #333;
        }
        
        .no-data {
          padding: 2rem;
          text-align: center;
          color: #666;
          background-color: #f8f9fa;
          border-radius: 4px;
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
        
        .view-all {
          margin-top: 1rem;
          text-align: center;
        }
        
        .view-all-button {
          padding: 0.5rem 1rem;
          background-color: #f8f9fa;
          color: #333;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .view-all-button:hover {
          background-color: #e9ecef;
        }
        
        .metrics-charts {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
          gap: 1.5rem;
        }
        
        .chart-container {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 1.5rem;
        }
        
        .chart-container h3 {
          margin-top: 0;
          margin-bottom: 1rem;
          font-size: 1.2rem;
          color: #333;
        }
        
        .status-distribution {
          margin-top: 2rem;
        }
        
        .status-bar {
          height: 30px;
          display: flex;
          border-radius: 4px;
          overflow: hidden;
          margin-bottom: 1rem;
        }
        
        .status-segment {
          height: 100%;
        }
        
        .status-segment.success {
          background-color: #28a745;
        }
        
        .status-segment.failed {
          background-color: #dc3545;
        }
        
        .status-legend {
          display: flex;
          gap: 1rem;
        }
        
        .legend-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.9rem;
        }
        
        .legend-color {
          width: 16px;
          height: 16px;
          border-radius: 4px;
        }
        
        .legend-color.success {
          background-color: #28a745;
        }
        
        .legend-color.failed {
          background-color: #dc3545;
        }
        
        .workflow-status-chart {
          margin-top: 2rem;
        }
        
        .status-item {
          display: flex;
          align-items: center;
          margin-bottom: 1rem;
        }
        
        .status-label {
          width: 80px;
          font-size: 0.9rem;
          color: #666;
        }
        
        .status-bar-container {
          flex: 1;
          height: 20px;
          background-color: #f8f9fa;
          border-radius: 4px;
          overflow: hidden;
          margin: 0 1rem;
        }
        
        .status-bar-value {
          height: 100%;
        }
        
        .status-bar-value.enabled {
          background-color: #0070f3;
        }
        
        .status-bar-value.disabled {
          background-color: #6c757d;
        }
        
        .status-count {
          width: 40px;
          text-align: right;
          font-weight: 500;
          font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
          .dashboard-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
          }
          
          .dashboard-controls {
            width: 100%;
            flex-direction: column;
          }
          
          .namespace-selector {
            width: 100%;
          }
          
          .refresh-controls {
            width: 100%;
            justify-content: space-between;
          }
          
          .tabs {
            overflow-x: auto;
          }
          
          .metrics-charts {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default KestraDashboard;
