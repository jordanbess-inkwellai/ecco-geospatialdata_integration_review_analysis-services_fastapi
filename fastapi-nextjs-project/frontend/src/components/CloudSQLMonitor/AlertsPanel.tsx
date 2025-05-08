import React, { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { useAlerts, Alert, AlertRule } from '../../hooks/useAlerts';

interface AlertsPanelProps {
  databaseId?: string;
}

const AlertsPanel: React.FC<AlertsPanelProps> = ({ databaseId }) => {
  const {
    activeAlerts,
    criticalAlerts,
    warningAlerts,
    infoAlerts,
    alertRules,
    loading,
    error,
    acknowledgeAlert,
    createAlertRule,
    updateAlertRule,
    deleteAlertRule
  } = useAlerts(databaseId);
  
  // State for new rule form
  const [showNewRuleForm, setShowNewRuleForm] = useState<boolean>(false);
  const [newRule, setNewRule] = useState<Partial<AlertRule>>({
    name: '',
    database: databaseId,
    metric: 'status',
    condition: '=',
    value: 'offline',
    severity: 'critical',
    enabled: true,
    notification_channels: ['in_app']
  });
  
  // Handle acknowledging an alert
  const handleAcknowledge = async (alertId: string) => {
    await acknowledgeAlert(alertId);
  };
  
  // Handle creating a new rule
  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newRule.name || !newRule.database || !newRule.metric || !newRule.condition || !newRule.value) {
      return;
    }
    
    const success = await createAlertRule(newRule as Omit<AlertRule, 'id' | 'owner' | 'created' | 'updated'>);
    
    if (success) {
      setShowNewRuleForm(false);
      setNewRule({
        name: '',
        database: databaseId,
        metric: 'status',
        condition: '=',
        value: 'offline',
        severity: 'critical',
        enabled: true,
        notification_channels: ['in_app']
      });
    }
  };
  
  // Handle toggling a rule's enabled state
  const handleToggleRule = async (ruleId: string, enabled: boolean) => {
    await updateAlertRule(ruleId, { enabled: !enabled });
  };
  
  // Handle deleting a rule
  const handleDeleteRule = async (ruleId: string) => {
    if (confirm('Are you sure you want to delete this alert rule?')) {
      await deleteAlertRule(ruleId);
    }
  };
  
  // Format time ago
  const formatTimeAgo = (dateString: string) => {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true });
  };
  
  // Render alert severity badge
  const renderSeverityBadge = (severity: string) => {
    let className = 'severity-badge';
    
    switch (severity) {
      case 'critical':
        className += ' critical';
        break;
      case 'warning':
        className += ' warning';
        break;
      case 'info':
        className += ' info';
        break;
    }
    
    return <span className={className}>{severity}</span>;
  };
  
  return (
    <div className="alerts-panel">
      <div className="panel-header">
        <h3>Alerts & Monitoring</h3>
        
        {databaseId && (
          <button
            className="new-rule-button"
            onClick={() => setShowNewRuleForm(true)}
          >
            New Alert Rule
          </button>
        )}
      </div>
      
      {error && (
        <div className="error-message">{error}</div>
      )}
      
      <div className="alerts-summary">
        <div className="summary-item critical">
          <div className="count">{criticalAlerts.length}</div>
          <div className="label">Critical</div>
        </div>
        <div className="summary-item warning">
          <div className="count">{warningAlerts.length}</div>
          <div className="label">Warning</div>
        </div>
        <div className="summary-item info">
          <div className="count">{infoAlerts.length}</div>
          <div className="label">Info</div>
        </div>
      </div>
      
      <div className="alerts-container">
        <h4>Active Alerts</h4>
        
        {loading ? (
          <div className="loading">Loading alerts...</div>
        ) : activeAlerts.length === 0 ? (
          <div className="no-alerts">No active alerts</div>
        ) : (
          <ul className="alerts-list">
            {activeAlerts.map((alert) => (
              <li key={alert.id} className={`alert-item ${alert.severity}`}>
                <div className="alert-header">
                  <div className="alert-severity">
                    {renderSeverityBadge(alert.severity)}
                  </div>
                  <div className="alert-time">
                    {formatTimeAgo(alert.triggered_at)}
                  </div>
                </div>
                
                <div className="alert-message">{alert.message}</div>
                
                <div className="alert-details">
                  <div className="alert-value">
                    Current value: <strong>{alert.metric_value}</strong>
                  </div>
                  
                  <div className="alert-status">
                    Status: <strong>{alert.status}</strong>
                  </div>
                </div>
                
                {alert.status === 'triggered' && (
                  <div className="alert-actions">
                    <button
                      className="acknowledge-button"
                      onClick={() => handleAcknowledge(alert.id)}
                    >
                      Acknowledge
                    </button>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
      
      <div className="rules-container">
        <h4>Alert Rules</h4>
        
        {loading ? (
          <div className="loading">Loading rules...</div>
        ) : alertRules.length === 0 ? (
          <div className="no-rules">No alert rules configured</div>
        ) : (
          <ul className="rules-list">
            {alertRules.map((rule) => (
              <li key={rule.id} className={`rule-item ${rule.enabled ? 'enabled' : 'disabled'}`}>
                <div className="rule-header">
                  <div className="rule-name">{rule.name}</div>
                  <div className="rule-severity">
                    {renderSeverityBadge(rule.severity)}
                  </div>
                </div>
                
                <div className="rule-condition">
                  {rule.metric} {rule.condition} {rule.value}
                </div>
                
                <div className="rule-actions">
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={rule.enabled}
                      onChange={() => handleToggleRule(rule.id, rule.enabled)}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                  
                  <button
                    className="delete-button"
                    onClick={() => handleDeleteRule(rule.id)}
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
      
      {showNewRuleForm && (
        <div className="form-overlay">
          <div className="rule-form">
            <div className="form-header">
              <h4>New Alert Rule</h4>
              <button
                className="close-button"
                onClick={() => setShowNewRuleForm(false)}
              >
                &times;
              </button>
            </div>
            
            <form onSubmit={handleCreateRule}>
              <div className="form-group">
                <label htmlFor="rule-name">Rule Name</label>
                <input
                  type="text"
                  id="rule-name"
                  value={newRule.name}
                  onChange={(e) => setNewRule({ ...newRule, name: e.target.value })}
                  placeholder="E.g., Database Offline Alert"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="rule-metric">Metric</label>
                <select
                  id="rule-metric"
                  value={newRule.metric}
                  onChange={(e) => setNewRule({ ...newRule, metric: e.target.value })}
                  required
                >
                  <option value="status">Status</option>
                  <option value="connection_count">Connection Count</option>
                  <option value="cache_hit_ratio">Cache Hit Ratio</option>
                  <option value="active_connections">Active Connections</option>
                  <option value="transactions_per_second">Transactions/Second</option>
                  <option value="queries_per_second">Queries/Second</option>
                  <option value="index_hit_ratio">Index Hit Ratio</option>
                  <option value="slow_queries">Slow Queries</option>
                  <option value="deadlocks">Deadlocks</option>
                </select>
              </div>
              
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="rule-condition">Condition</label>
                  <select
                    id="rule-condition"
                    value={newRule.condition}
                    onChange={(e) => setNewRule({ ...newRule, condition: e.target.value })}
                    required
                  >
                    <option value="=">=</option>
                    <option value="!=">!=</option>
                    <option value=">">></option>
                    <option value="<"><</option>
                    <option value=">=">>=</option>
                    <option value="<="><=</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label htmlFor="rule-value">Value</label>
                  <input
                    type="text"
                    id="rule-value"
                    value={newRule.value}
                    onChange={(e) => setNewRule({ ...newRule, value: e.target.value })}
                    placeholder={newRule.metric === 'status' ? 'offline' : '0'}
                    required
                  />
                </div>
              </div>
              
              <div className="form-group">
                <label htmlFor="rule-severity">Severity</label>
                <select
                  id="rule-severity"
                  value={newRule.severity}
                  onChange={(e) => setNewRule({ ...newRule, severity: e.target.value as 'info' | 'warning' | 'critical' })}
                  required
                >
                  <option value="info">Info</option>
                  <option value="warning">Warning</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Notification Channels</label>
                <div className="checkbox-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={newRule.notification_channels?.includes('in_app')}
                      onChange={(e) => {
                        const channels = [...(newRule.notification_channels || [])];
                        if (e.target.checked) {
                          if (!channels.includes('in_app')) {
                            channels.push('in_app');
                          }
                        } else {
                          const index = channels.indexOf('in_app');
                          if (index !== -1) {
                            channels.splice(index, 1);
                          }
                        }
                        setNewRule({ ...newRule, notification_channels: channels });
                      }}
                    />
                    In-App
                  </label>
                  
                  <label>
                    <input
                      type="checkbox"
                      checked={newRule.notification_channels?.includes('email')}
                      onChange={(e) => {
                        const channels = [...(newRule.notification_channels || [])];
                        if (e.target.checked) {
                          if (!channels.includes('email')) {
                            channels.push('email');
                          }
                        } else {
                          const index = channels.indexOf('email');
                          if (index !== -1) {
                            channels.splice(index, 1);
                          }
                        }
                        setNewRule({ ...newRule, notification_channels: channels });
                      }}
                    />
                    Email
                  </label>
                  
                  <label>
                    <input
                      type="checkbox"
                      checked={newRule.notification_channels?.includes('webhook')}
                      onChange={(e) => {
                        const channels = [...(newRule.notification_channels || [])];
                        if (e.target.checked) {
                          if (!channels.includes('webhook')) {
                            channels.push('webhook');
                          }
                        } else {
                          const index = channels.indexOf('webhook');
                          if (index !== -1) {
                            channels.splice(index, 1);
                          }
                        }
                        setNewRule({ ...newRule, notification_channels: channels });
                      }}
                    />
                    Webhook
                  </label>
                </div>
              </div>
              
              {newRule.notification_channels?.includes('webhook') && (
                <div className="form-group">
                  <label htmlFor="webhook-url">Webhook URL</label>
                  <input
                    type="url"
                    id="webhook-url"
                    value={newRule.webhook_url || ''}
                    onChange={(e) => setNewRule({ ...newRule, webhook_url: e.target.value })}
                    placeholder="https://example.com/webhook"
                    required
                  />
                </div>
              )}
              
              <div className="form-actions">
                <button
                  type="button"
                  className="cancel-button"
                  onClick={() => setShowNewRuleForm(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="create-button"
                >
                  Create Rule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      <style jsx>{`
        .alerts-panel {
          padding: 1.5rem;
        }
        
        .panel-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }
        
        .panel-header h3 {
          margin: 0;
          font-size: 1.2rem;
          color: #333;
        }
        
        .new-rule-button {
          padding: 0.5rem 1rem;
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .new-rule-button:hover {
          background-color: #0051a8;
        }
        
        .alerts-summary {
          display: flex;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }
        
        .summary-item {
          flex: 1;
          padding: 1rem;
          border-radius: 8px;
          text-align: center;
          color: white;
        }
        
        .summary-item.critical {
          background-color: #dc3545;
        }
        
        .summary-item.warning {
          background-color: #ffc107;
          color: #333;
        }
        
        .summary-item.info {
          background-color: #0dcaf0;
        }
        
        .summary-item .count {
          font-size: 2rem;
          font-weight: bold;
          margin-bottom: 0.25rem;
        }
        
        .summary-item .label {
          font-size: 0.9rem;
          text-transform: uppercase;
        }
        
        .alerts-container, .rules-container {
          margin-bottom: 2rem;
        }
        
        .alerts-container h4, .rules-container h4 {
          margin: 0 0 1rem;
          font-size: 1.1rem;
          color: #333;
        }
        
        .loading, .no-alerts, .no-rules {
          padding: 2rem;
          text-align: center;
          color: #666;
          background-color: #f8f9fa;
          border-radius: 4px;
        }
        
        .alerts-list, .rules-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        
        .alert-item {
          padding: 1rem;
          border-radius: 4px;
          margin-bottom: 0.75rem;
          border-left: 4px solid #ccc;
        }
        
        .alert-item.critical {
          background-color: #f8d7da;
          border-left-color: #dc3545;
        }
        
        .alert-item.warning {
          background-color: #fff3cd;
          border-left-color: #ffc107;
        }
        
        .alert-item.info {
          background-color: #d1ecf1;
          border-left-color: #0dcaf0;
        }
        
        .alert-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }
        
        .alert-time {
          font-size: 0.8rem;
          color: #666;
        }
        
        .alert-message {
          margin-bottom: 0.75rem;
          font-weight: 500;
        }
        
        .alert-details {
          display: flex;
          justify-content: space-between;
          font-size: 0.9rem;
          margin-bottom: 0.75rem;
        }
        
        .alert-actions {
          display: flex;
          justify-content: flex-end;
        }
        
        .acknowledge-button {
          padding: 0.4rem 0.75rem;
          background-color: #6c757d;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 0.8rem;
          cursor: pointer;
        }
        
        .acknowledge-button:hover {
          background-color: #5a6268;
        }
        
        .severity-badge {
          display: inline-block;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.8rem;
          font-weight: 500;
          text-transform: capitalize;
        }
        
        .severity-badge.critical {
          background-color: #dc3545;
          color: white;
        }
        
        .severity-badge.warning {
          background-color: #ffc107;
          color: #333;
        }
        
        .severity-badge.info {
          background-color: #0dcaf0;
          color: white;
        }
        
        .rule-item {
          padding: 1rem;
          border-radius: 4px;
          margin-bottom: 0.75rem;
          background-color: #f8f9fa;
          border: 1px solid #eee;
        }
        
        .rule-item.disabled {
          opacity: 0.6;
        }
        
        .rule-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }
        
        .rule-name {
          font-weight: 500;
        }
        
        .rule-condition {
          font-size: 0.9rem;
          color: #666;
          margin-bottom: 0.75rem;
        }
        
        .rule-actions {
          display: flex;
          justify-content: space-between;
          align-items: center;
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
        
        .delete-button {
          padding: 0.4rem 0.75rem;
          background-color: #f8d7da;
          color: #721c24;
          border: none;
          border-radius: 4px;
          font-size: 0.8rem;
          cursor: pointer;
        }
        
        .delete-button:hover {
          background-color: #f5c6cb;
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
        
        .rule-form {
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
        
        .form-row {
          display: flex;
          gap: 1rem;
        }
        
        .form-row .form-group {
          flex: 1;
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
        
        .checkbox-group {
          display: flex;
          flex-wrap: wrap;
          gap: 1rem;
        }
        
        .checkbox-group label {
          display: flex;
          align-items: center;
          font-weight: normal;
          margin-bottom: 0;
        }
        
        .checkbox-group input {
          width: auto;
          margin-right: 0.5rem;
        }
        
        .form-actions {
          display: flex;
          justify-content: flex-end;
          gap: 1rem;
          margin-top: 1.5rem;
        }
        
        .cancel-button, .create-button {
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
        
        .create-button {
          background-color: #0070f3;
          color: white;
          border: none;
        }
        
        .error-message {
          background-color: #f8d7da;
          color: #721c24;
          padding: 0.75rem;
          border-radius: 4px;
          margin-bottom: 1.5rem;
        }
        
        @media (max-width: 768px) {
          .alerts-summary {
            flex-direction: column;
          }
          
          .form-row {
            flex-direction: column;
            gap: 0;
          }
        }
      `}</style>
    </div>
  );
};

export default AlertsPanel;
