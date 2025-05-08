import { useState, useEffect } from 'react';
import { getPocketBase } from '../lib/pocketbase';
import axios from 'axios';

export interface KestraWorkflow {
  id: string;
  name: string;
  namespace: string;
  workflow_id: string;
  description: string;
  tags: string[];
  triggers: any[];
  tasks: any[];
  enabled: boolean;
  owner: string;
  created: string;
  updated: string;
}

export const useKestraWorkflows = () => {
  const [workflows, setWorkflows] = useState<KestraWorkflow[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const pb = getPocketBase();
    
    // Function to load workflows
    const loadWorkflows = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const records = await pb.collection('kestra_workflows').getFullList({
          sort: 'name',
          expand: 'owner'
        });
        
        setWorkflows(records.map(record => ({
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
        })));
        
        setLoading(false);
      } catch (err: any) {
        console.error('Error loading workflows:', err);
        setError(err.message || 'Error loading workflows');
        setLoading(false);
      }
    };
    
    // Load workflows initially
    loadWorkflows();
    
    // Subscribe to real-time updates
    const unsubscribe = pb.collection('kestra_workflows').subscribe('*', function(e) {
      if (e.action === 'create') {
        // Add new workflow to the list
        setWorkflows(prev => [...prev, {
          id: e.record.id,
          name: e.record.name,
          namespace: e.record.namespace,
          workflow_id: e.record.workflow_id,
          description: e.record.description,
          tags: JSON.parse(e.record.tags || '[]'),
          triggers: JSON.parse(e.record.triggers || '[]'),
          tasks: JSON.parse(e.record.tasks || '[]'),
          enabled: e.record.enabled,
          owner: e.record.owner,
          created: e.record.created,
          updated: e.record.updated
        }]);
      } else if (e.action === 'update') {
        // Update existing workflow
        setWorkflows(prev => prev.map(workflow => 
          workflow.id === e.record.id ? {
            id: e.record.id,
            name: e.record.name,
            namespace: e.record.namespace,
            workflow_id: e.record.workflow_id,
            description: e.record.description,
            tags: JSON.parse(e.record.tags || '[]'),
            triggers: JSON.parse(e.record.triggers || '[]'),
            tasks: JSON.parse(e.record.tasks || '[]'),
            enabled: e.record.enabled,
            owner: e.record.owner,
            created: e.record.created,
            updated: e.record.updated
          } : workflow
        ));
      } else if (e.action === 'delete') {
        // Remove deleted workflow
        setWorkflows(prev => prev.filter(workflow => workflow.id !== e.record.id));
      }
    });
    
    // Cleanup subscription on unmount
    return () => {
      unsubscribe();
    };
  }, []);
  
  // Function to sync workflows from Kestra
  const syncWorkflows = async (namespace?: string) => {
    try {
      setLoading(true);
      setError(null);
      
      await axios.post('/api/v1/kestra/sync/workflows', { namespace });
      
      // Wait a bit for the background task to complete
      setTimeout(async () => {
        const pb = getPocketBase();
        const records = await pb.collection('kestra_workflows').getFullList({
          sort: 'name',
          expand: 'owner'
        });
        
        setWorkflows(records.map(record => ({
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
        })));
        
        setLoading(false);
      }, 2000);
    } catch (err: any) {
      console.error('Error syncing workflows:', err);
      setError(err.response?.data?.detail || err.message || 'Error syncing workflows');
      setLoading(false);
    }
  };
  
  // Function to trigger a workflow
  const triggerWorkflow = async (namespace: string, flowId: string, inputs?: any) => {
    try {
      const response = await axios.post(`/api/v1/kestra/workflows/trigger/${namespace}/${flowId}`, inputs || {});
      return response.data;
    } catch (err: any) {
      console.error('Error triggering workflow:', err);
      throw new Error(err.response?.data?.detail || err.message || 'Error triggering workflow');
    }
  };
  
  // Function to toggle workflow enabled state
  const toggleWorkflowEnabled = async (id: string, enabled: boolean) => {
    try {
      const pb = getPocketBase();
      await pb.collection('kestra_workflows').update(id, { enabled: !enabled });
      return true;
    } catch (err: any) {
      console.error('Error toggling workflow enabled state:', err);
      setError(err.message || 'Error toggling workflow enabled state');
      return false;
    }
  };
  
  return {
    workflows,
    loading,
    error,
    syncWorkflows,
    triggerWorkflow,
    toggleWorkflowEnabled
  };
};
