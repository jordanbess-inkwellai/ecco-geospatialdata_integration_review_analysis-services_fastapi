import { useState, useEffect } from 'react';
import { getPocketBase } from '../lib/pocketbase';
import axios from 'axios';

export interface KestraExecution {
  id: string;
  workflow: string;
  execution_id: string;
  namespace: string;
  workflow_id: string;
  status: 'CREATED' | 'RUNNING' | 'PAUSED' | 'RESTARTED' | 'KILLING' | 'SUCCESS' | 'WARNING' | 'FAILED' | 'KILLED';
  start_date: string;
  end_date: string | null;
  duration: number | null;
  inputs: any;
  outputs: any;
  task_runs: any[];
  trigger: any;
  created: string;
  updated: string;
}

export const useKestraExecutions = (workflowId?: string) => {
  const [executions, setExecutions] = useState<KestraExecution[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const pb = getPocketBase();
    
    // Function to load executions
    const loadExecutions = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Build filter
        let filter = '';
        if (workflowId) {
          filter = `workflow = "${workflowId}"`;
        }
        
        const records = await pb.collection('kestra_executions').getList(1, 100, {
          filter,
          sort: '-created',
          expand: 'workflow'
        });
        
        setExecutions(records.items.map(record => ({
          id: record.id,
          workflow: record.workflow,
          execution_id: record.execution_id,
          namespace: record.namespace,
          workflow_id: record.workflow_id,
          status: record.status,
          start_date: record.start_date,
          end_date: record.end_date,
          duration: record.duration,
          inputs: JSON.parse(record.inputs || '{}'),
          outputs: JSON.parse(record.outputs || '{}'),
          task_runs: JSON.parse(record.task_runs || '[]'),
          trigger: JSON.parse(record.trigger || '{}'),
          created: record.created,
          updated: record.updated
        })));
        
        setLoading(false);
      } catch (err: any) {
        console.error('Error loading executions:', err);
        setError(err.message || 'Error loading executions');
        setLoading(false);
      }
    };
    
    // Load executions initially
    loadExecutions();
    
    // Subscribe to real-time updates
    const filter = workflowId ? `workflow = "${workflowId}"` : '';
    const unsubscribe = pb.collection('kestra_executions').subscribe(filter, function(e) {
      if (e.action === 'create') {
        // Add new execution to the list
        setExecutions(prev => [{
          id: e.record.id,
          workflow: e.record.workflow,
          execution_id: e.record.execution_id,
          namespace: e.record.namespace,
          workflow_id: e.record.workflow_id,
          status: e.record.status,
          start_date: e.record.start_date,
          end_date: e.record.end_date,
          duration: e.record.duration,
          inputs: JSON.parse(e.record.inputs || '{}'),
          outputs: JSON.parse(e.record.outputs || '{}'),
          task_runs: JSON.parse(e.record.task_runs || '[]'),
          trigger: JSON.parse(e.record.trigger || '{}'),
          created: e.record.created,
          updated: e.record.updated
        }, ...prev]);
      } else if (e.action === 'update') {
        // Update existing execution
        setExecutions(prev => prev.map(execution => 
          execution.id === e.record.id ? {
            id: e.record.id,
            workflow: e.record.workflow,
            execution_id: e.record.execution_id,
            namespace: e.record.namespace,
            workflow_id: e.record.workflow_id,
            status: e.record.status,
            start_date: e.record.start_date,
            end_date: e.record.end_date,
            duration: e.record.duration,
            inputs: JSON.parse(e.record.inputs || '{}'),
            outputs: JSON.parse(e.record.outputs || '{}'),
            task_runs: JSON.parse(e.record.task_runs || '[]'),
            trigger: JSON.parse(e.record.trigger || '{}'),
            created: e.record.created,
            updated: e.record.updated
          } : execution
        ));
      } else if (e.action === 'delete') {
        // Remove deleted execution
        setExecutions(prev => prev.filter(execution => execution.id !== e.record.id));
      }
    });
    
    // Cleanup subscription on unmount
    return () => {
      unsubscribe();
    };
  }, [workflowId]);
  
  // Function to sync executions from Kestra
  const syncExecutions = async (namespace?: string, flowId?: string, limit: number = 100) => {
    try {
      setLoading(true);
      setError(null);
      
      await axios.post('/api/v1/kestra/sync/executions', { 
        namespace,
        flow_id: flowId,
        limit
      });
      
      // Wait a bit for the background task to complete
      setTimeout(async () => {
        const pb = getPocketBase();
        
        // Build filter
        let filter = '';
        if (workflowId) {
          filter = `workflow = "${workflowId}"`;
        }
        
        const records = await pb.collection('kestra_executions').getList(1, 100, {
          filter,
          sort: '-created',
          expand: 'workflow'
        });
        
        setExecutions(records.items.map(record => ({
          id: record.id,
          workflow: record.workflow,
          execution_id: record.execution_id,
          namespace: record.namespace,
          workflow_id: record.workflow_id,
          status: record.status,
          start_date: record.start_date,
          end_date: record.end_date,
          duration: record.duration,
          inputs: JSON.parse(record.inputs || '{}'),
          outputs: JSON.parse(record.outputs || '{}'),
          task_runs: JSON.parse(record.task_runs || '[]'),
          trigger: JSON.parse(record.trigger || '{}'),
          created: record.created,
          updated: record.updated
        })));
        
        setLoading(false);
      }, 2000);
    } catch (err: any) {
      console.error('Error syncing executions:', err);
      setError(err.response?.data?.detail || err.message || 'Error syncing executions');
      setLoading(false);
    }
  };
  
  // Function to get execution logs
  const getExecutionLogs = async (executionId: string) => {
    try {
      const response = await axios.get(`/api/v1/kestra/logs/${executionId}`);
      return response.data;
    } catch (err: any) {
      console.error('Error getting execution logs:', err);
      throw new Error(err.response?.data?.detail || err.message || 'Error getting execution logs');
    }
  };
  
  // Function to restart an execution
  const restartExecution = async (executionId: string) => {
    try {
      const response = await axios.post(`/api/v1/kestra/executions/${executionId}/restart`);
      return response.data;
    } catch (err: any) {
      console.error('Error restarting execution:', err);
      throw new Error(err.response?.data?.detail || err.message || 'Error restarting execution');
    }
  };
  
  // Function to stop an execution
  const stopExecution = async (executionId: string) => {
    try {
      const response = await axios.post(`/api/v1/kestra/executions/${executionId}/stop`);
      return response.data;
    } catch (err: any) {
      console.error('Error stopping execution:', err);
      throw new Error(err.response?.data?.detail || err.message || 'Error stopping execution');
    }
  };
  
  // Get executions by status
  const runningExecutions = executions.filter(execution => 
    ['CREATED', 'RUNNING', 'PAUSED', 'RESTARTED', 'KILLING'].includes(execution.status)
  );
  
  const completedExecutions = executions.filter(execution => 
    ['SUCCESS', 'WARNING', 'FAILED', 'KILLED'].includes(execution.status)
  );
  
  const successfulExecutions = executions.filter(execution => 
    execution.status === 'SUCCESS'
  );
  
  const failedExecutions = executions.filter(execution => 
    execution.status === 'FAILED'
  );
  
  return {
    executions,
    runningExecutions,
    completedExecutions,
    successfulExecutions,
    failedExecutions,
    loading,
    error,
    syncExecutions,
    getExecutionLogs,
    restartExecution,
    stopExecution
  };
};
