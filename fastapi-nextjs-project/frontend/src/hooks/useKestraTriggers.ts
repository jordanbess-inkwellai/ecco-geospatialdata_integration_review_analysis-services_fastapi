import { useState, useEffect } from 'react';
import { getPocketBase } from '../lib/pocketbase';
import axios from 'axios';

export interface KestraTrigger {
  id: string;
  name: string;
  workflow: string;
  trigger_type: 'pocketbase_event' | 'database_alert' | 'schedule' | 'webhook' | 'manual';
  collection?: string;
  event_type?: 'create' | 'update' | 'delete' | 'alert';
  filter?: string;
  schedule?: string;
  inputs: any;
  enabled: boolean;
  last_triggered?: string;
  owner: string;
  created: string;
  updated: string;
}

export const useKestraTriggers = (workflowId?: string) => {
  const [triggers, setTriggers] = useState<KestraTrigger[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const pb = getPocketBase();
    
    // Function to load triggers
    const loadTriggers = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Build filter
        let filter = '';
        if (workflowId) {
          filter = `workflow = "${workflowId}"`;
        }
        
        const records = await pb.collection('kestra_triggers').getList(1, 100, {
          filter,
          sort: 'name',
          expand: 'workflow,owner'
        });
        
        setTriggers(records.items.map(record => ({
          id: record.id,
          name: record.name,
          workflow: record.workflow,
          trigger_type: record.trigger_type,
          collection: record.collection,
          event_type: record.event_type,
          filter: record.filter,
          schedule: record.schedule,
          inputs: JSON.parse(record.inputs || '{}'),
          enabled: record.enabled,
          last_triggered: record.last_triggered,
          owner: record.owner,
          created: record.created,
          updated: record.updated
        })));
        
        setLoading(false);
      } catch (err: any) {
        console.error('Error loading triggers:', err);
        setError(err.message || 'Error loading triggers');
        setLoading(false);
      }
    };
    
    // Load triggers initially
    loadTriggers();
    
    // Subscribe to real-time updates
    const filter = workflowId ? `workflow = "${workflowId}"` : '';
    const unsubscribe = pb.collection('kestra_triggers').subscribe(filter, function(e) {
      if (e.action === 'create') {
        // Add new trigger to the list
        setTriggers(prev => [...prev, {
          id: e.record.id,
          name: e.record.name,
          workflow: e.record.workflow,
          trigger_type: e.record.trigger_type,
          collection: e.record.collection,
          event_type: e.record.event_type,
          filter: e.record.filter,
          schedule: e.record.schedule,
          inputs: JSON.parse(e.record.inputs || '{}'),
          enabled: e.record.enabled,
          last_triggered: e.record.last_triggered,
          owner: e.record.owner,
          created: e.record.created,
          updated: e.record.updated
        }]);
      } else if (e.action === 'update') {
        // Update existing trigger
        setTriggers(prev => prev.map(trigger => 
          trigger.id === e.record.id ? {
            id: e.record.id,
            name: e.record.name,
            workflow: e.record.workflow,
            trigger_type: e.record.trigger_type,
            collection: e.record.collection,
            event_type: e.record.event_type,
            filter: e.record.filter,
            schedule: e.record.schedule,
            inputs: JSON.parse(e.record.inputs || '{}'),
            enabled: e.record.enabled,
            last_triggered: e.record.last_triggered,
            owner: e.record.owner,
            created: e.record.created,
            updated: e.record.updated
          } : trigger
        ));
      } else if (e.action === 'delete') {
        // Remove deleted trigger
        setTriggers(prev => prev.filter(trigger => trigger.id !== e.record.id));
      }
    });
    
    // Cleanup subscription on unmount
    return () => {
      unsubscribe();
    };
  }, [workflowId]);
  
  // Function to create a PocketBase event trigger
  const createPocketBaseEventTrigger = async (
    name: string,
    workflowId: string,
    collection: string,
    eventType: 'create' | 'update' | 'delete',
    filter?: string,
    inputs?: any
  ) => {
    try {
      const response = await axios.post('/api/v1/kestra/triggers', {
        name,
        workflow_id: workflowId,
        collection,
        event_type: eventType,
        filter,
        inputs
      });
      
      return response.data;
    } catch (err: any) {
      console.error('Error creating PocketBase event trigger:', err);
      throw new Error(err.response?.data?.detail || err.message || 'Error creating trigger');
    }
  };
  
  // Function to create a database alert trigger
  const createDatabaseAlertTrigger = async (
    name: string,
    workflowId: string,
    inputs?: any
  ) => {
    try {
      const response = await axios.post('/api/v1/kestra/triggers/database-alert', {
        name,
        workflow_id: workflowId,
        inputs
      });
      
      return response.data;
    } catch (err: any) {
      console.error('Error creating database alert trigger:', err);
      throw new Error(err.response?.data?.detail || err.message || 'Error creating trigger');
    }
  };
  
  // Function to toggle trigger enabled state
  const toggleTriggerEnabled = async (id: string, enabled: boolean) => {
    try {
      const pb = getPocketBase();
      await pb.collection('kestra_triggers').update(id, { enabled: !enabled });
      return true;
    } catch (err: any) {
      console.error('Error toggling trigger enabled state:', err);
      setError(err.message || 'Error toggling trigger enabled state');
      return false;
    }
  };
  
  // Function to delete a trigger
  const deleteTrigger = async (id: string) => {
    try {
      const pb = getPocketBase();
      await pb.collection('kestra_triggers').delete(id);
      return true;
    } catch (err: any) {
      console.error('Error deleting trigger:', err);
      setError(err.message || 'Error deleting trigger');
      return false;
    }
  };
  
  // Get triggers by type
  const pocketbaseEventTriggers = triggers.filter(trigger => trigger.trigger_type === 'pocketbase_event');
  const databaseAlertTriggers = triggers.filter(trigger => trigger.trigger_type === 'database_alert');
  const scheduleTriggers = triggers.filter(trigger => trigger.trigger_type === 'schedule');
  const webhookTriggers = triggers.filter(trigger => trigger.trigger_type === 'webhook');
  const manualTriggers = triggers.filter(trigger => trigger.trigger_type === 'manual');
  
  return {
    triggers,
    pocketbaseEventTriggers,
    databaseAlertTriggers,
    scheduleTriggers,
    webhookTriggers,
    manualTriggers,
    loading,
    error,
    createPocketBaseEventTrigger,
    createDatabaseAlertTrigger,
    toggleTriggerEnabled,
    deleteTrigger
  };
};
