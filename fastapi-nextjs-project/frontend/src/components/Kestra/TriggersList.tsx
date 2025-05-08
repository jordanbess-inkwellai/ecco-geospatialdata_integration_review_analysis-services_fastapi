import React, { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { useKestraTriggers } from '../../hooks/useKestraTriggers';

interface TriggersListProps {
  workflowId?: string;
}

const TriggersList: React.FC<TriggersListProps> = ({ workflowId }) => {
  const { 
    triggers, 
    loading, 
    error, 
    createPocketBaseEventTrigger,
    createDatabaseAlertTrigger,
    toggleTriggerEnabled,
    deleteTrigger
  } = useKestraTriggers(workflowId);
  
  const [showNewTriggerForm, setShowNewTriggerForm] = useState<boolean>(false);
  const [triggerType, setTriggerType] = useState<'pocketbase_event' | 'database_alert'>('pocketbase_event');
  const [newTrigger, setNewTrigger] = useState({
    name: '',
    collection: 'monitored_databases',
    eventType: 'create',
    filter: '',
    inputs: {}
  });
  
  // Handle creating a new trigger
  const handleCreateTrigger = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (triggerType === 'pocketbase_event') {
        if (!workflowId || !newTrigger.name || !newTrigger.collection || !newTrigger.eventType) {
          alert('Please fill in all required fields');
          return;
        }
        
        await createPocketBaseEventTrigger(
          newTrigger.name,
          workflowId,
          newTrigger.collection,
          newTrigger.eventType as any,
          newTrigger.filter || undefined,
          newTrigger.inputs
        );
      } else {
        if (!workflowId || !newTrigger.name) {
          alert('Please fill in all required fields');
          return;
        }
        
        await createDatabaseAlertTrigger(
          newTrigger.name,
          workflowId,
          newTrigger.inputs
        );
      }
      
      // Reset form
      setNewTrigger({
        name: '',
        collection: 'monitored_databases',
        eventType: 'create',
        filter: '',
        inputs: {}
      });
      
      setShowNewTriggerForm(false);
    } catch (error) {
      alert(`Error creating trigger: ${error}`);
    }
  };
  
  // Handle toggling a trigger's enabled state
  const handleToggleTrigger = async (triggerId: string, enabled: boolean) => {
    try {
      await toggleTriggerEnabled(triggerId, enabled);
    } catch (error) {
      alert(`Error toggling trigger: ${error}`);
    }
  };
  
  // Handle deleting a trigger
  const handleDeleteTrigger = async (triggerId: string) => {
    if (confirm('Are you sure you want to delete this trigger?')) {
      try {
        await deleteTrigger(triggerId);
      } catch (error) {
        alert(`Error deleting trigger: ${error}`);
      }
    }
  };
  
  // Get trigger type display name
  const getTriggerTypeDisplay = (type: string) => {
    switch (type) {
      case 'pocketbase_event':
        return 'PocketBase Event';
      case 'database_alert':
        return 'Database Alert';
      case 'schedule':
        return 'Schedule';
      case 'webhook':
        return 'Webhook';
      case 'manual':
        return 'Manual';
      default:
        return type;
    }
  };
  
  return (
    <div className="triggers-list">
      <div className="list-header">
        <h2>Workflow Triggers</h2>
        {workflowId && (
          <button 
            className="new-trigger-button"
            onClick={() => setShowNewTriggerForm(true)}
          >
            New Trigger
          </button>
        )}
      </div>
      
      {error && (
        <div className="error-message">{error}</div>
      )}
      
      {loading ? (
        <div className="loading">Loading triggers...</div>
      ) : triggers.length === 0 ? (
        <div className="no-triggers">
          <p>No triggers configured for this workflow</p>
          {workflowId && (
            <button 
              className="new-trigger-button"
              onClick={() => setShowNewTriggerForm(true)}
            >
              Create Trigger
            </button>
          )}
        </div>
      ) : (
        <div className="triggers-table-container">
          <table className="triggers-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Details</th>
                <th>Last Triggered</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {triggers.map(trigger => (
                <tr key={trigger.id} className={`trigger-row ${!trigger.enabled ? 'disabled' : ''}`}>
                  <td className="trigger-name">{trigger.name}</td>
                  <td className="trigger-type">{getTriggerTypeDisplay(trigger.trigger_type)}</td>
                  <td className="trigger-details">
                    {trigger.trigger_type === 'pocketbase_event' && (
                      <>
                        <div>Collection: {trigger.collection}</div>
                        <div>Event: {trigger.event_type}</div>
                        {trigger.filter && <div>Filter: {trigger.filter}</div>}
                      </>
                    )}
                    {trigger.trigger_type === 'database_alert' && (
                      <div>Listens for database alerts</div>
                    )}
                    {trigger.trigger_type === 'schedule' && (
                      <div>Schedule: {trigger.schedule}</div>
                    )}
                  </td>
                  <td className="trigger-last-triggered">
                    {trigger.last_triggered 
                      ? formatDistanceToNow(new Date(trigger.last_triggered), { addSuffix: true })
                      : 'Never'
                    }
                  </td>
                  <td className="trigger-status">
                    <span className={`status-badge ${trigger.enabled ? 'enabled' : 'disabled'}`}>
                      {trigger.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </td>
                  <td className="trigger-actions">
                    <button
                      className={`toggle-button ${trigger.enabled ? 'enabled' : 'disabled'}`}
                      onClick={() => handleToggleTrigger(trigger.id, trigger.enabled)}
                      title={trigger.enabled ? 'Disable trigger' : 'Enable trigger'}
                    >
                      {trigger.enabled ? 'Disable' : 'Enable'}
                    </button>
                    
                    <button
                      className="delete-button"
                      onClick={() => handleDeleteTrigger(trigger.id)}
                      title="Delete trigger"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {showNewTriggerForm && (
        <div className="form-overlay">
          <div className="trigger-form">
            <div className="form-header">
              <h3>New Trigger</h3>
              <button
                className="close-button"
                onClick={() => setShowNewTriggerForm(false)}
              >
                &times;
              </button>
            </div>
            
            <form onSubmit={handleCreateTrigger}>
              <div className="form-group">
                <label htmlFor="trigger-name">Trigger Name</label>
                <input
                  type="text"
                  id="trigger-name"
                  value={newTrigger.name}
                  onChange={(e) => setNewTrigger({ ...newTrigger, name: e.target.value })}
                  placeholder="E.g., Database Created Trigger"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="trigger-type">Trigger Type</label>
                <select
                  id="trigger-type"
                  value={triggerType}
                  onChange={(e) => setTriggerType(e.target.value as any)}
                  required
                >
                  <option value="pocketbase_event">PocketBase Event</option>
                  <option value="database_alert">Database Alert</option>
                </select>
              </div>
              
              {triggerType === 'pocketbase_event' && (
                <>
                  <div className="form-group">
                    <label htmlFor="trigger-collection">Collection</label>
                    <select
                      id="trigger-collection"
                      value={newTrigger.collection}
                      onChange={(e) => setNewTrigger({ ...newTrigger, collection: e.target.value })}
                      required
                    >
                      <option value="monitored_databases">Monitored Databases</option>
                      <option value="database_status">Database Status</option>
                      <option value="performance_metrics">Performance Metrics</option>
                      <option value="alert_rules">Alert Rules</option>
                      <option value="alerts">Alerts</option>
                      <option value="kestra_workflows">Kestra Workflows</option>
                      <option value="kestra_executions">Kestra Executions</option>
                      <option value="kestra_triggers">Kestra Triggers</option>
                    </select>
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="trigger-event-type">Event Type</label>
                    <select
                      id="trigger-event-type"
                      value={newTrigger.eventType}
                      onChange={(e) => setNewTrigger({ ...newTrigger, eventType: e.target.value })}
                      required
                    >
                      <option value="create">Create</option>
                      <option value="update">Update</option>
                      <option value="delete">Delete</option>
                    </select>
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="trigger-filter">Filter (Optional)</label>
                    <input
                      type="text"
                      id="trigger-filter"
                      value={newTrigger.filter}
                      onChange={(e) => setNewTrigger({ ...newTrigger, filter: e.target.value })}
                      placeholder="E.g., status = 'offline'"
                    />
                    <div className="form-help">
                      Simple filter expression, e.g., "status = 'offline'" or "connection_count > 10"
                    </div>
                  </div>
                </>
              )}
              
              <div className="form-actions">
                <button
                  type="button"
                  className="cancel-button"
                  onClick={() => setShowNewTriggerForm(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="create-button"
                >
                  Create Trigger
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      <style jsx>{`
        .triggers-list {
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
        
        .new-trigger-button {
          padding: 0.5rem 1rem;
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .new-trigger-button:hover {
          background-color: #0051a8;
        }
        
        .error-message {
          background-color: #f8d7da;
          color: #721c24;
          padding: 0.75rem;
          border-radius: 4px;
          margin-bottom: 1.5rem;
        }
        
        .loading, .no-triggers {
          padding: 3rem;
          text-align: center;
          color: #666;
          background-color: #f8f9fa;
          border-radius: 4px;
        }
        
        .no-triggers button {
          margin-top: 1rem;
        }
        
        .triggers-table-container {
          overflow-x: auto;
        }
        
        .triggers-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.9rem;
        }
        
        .triggers-table th {
          text-align: left;
          padding: 0.75rem;
          background-color: #f8f9fa;
          border-bottom: 2px solid #ddd;
        }
        
        .trigger-row {
          transition: background-color 0.2s;
        }
        
        .trigger-row:hover {
          background-color: #f5f5f5;
        }
        
        .trigger-row.disabled {
          opacity: 0.7;
        }
        
        .trigger-row td {
          padding: 0.75rem;
          border-bottom: 1px solid #ddd;
        }
        
        .trigger-name {
          font-weight: 500;
        }
        
        .trigger-details {
          font-size: 0.85rem;
          color: #666;
        }
        
        .status-badge {
          display: inline-block;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.8rem;
          font-weight: 500;
        }
        
        .status-badge.enabled {
          background-color: #d1e7dd;
          color: #0f5132;
        }
        
        .status-badge.disabled {
          background-color: #f8d7da;
          color: #842029;
        }
        
        .trigger-actions {
          display: flex;
          gap: 0.5rem;
        }
        
        .toggle-button,
        .delete-button {
          padding: 0.25rem 0.5rem;
          border: none;
          border-radius: 4px;
          font-size: 0.8rem;
          cursor: pointer;
        }
        
        .toggle-button.enabled {
          background-color: #f8d7da;
          color: #842029;
        }
        
        .toggle-button.disabled {
          background-color: #d1e7dd;
          color: #0f5132;
        }
        
        .delete-button {
          background-color: #dc3545;
          color: white;
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
        
        .trigger-form {
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
        
        .form-header h3 {
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
        
        .form-group input,
        .form-group select {
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
          margin-top: 1.5rem;
        }
        
        .cancel-button,
        .create-button {
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
        
        @media (max-width: 768px) {
          .list-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
          }
          
          .new-trigger-button {
            width: 100%;
          }
          
          .trigger-actions {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default TriggersList;
