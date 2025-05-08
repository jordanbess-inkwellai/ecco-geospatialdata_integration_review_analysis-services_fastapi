import { useState, useEffect } from 'react';
import { getPocketBase } from '../lib/pocketbase';

export interface Alert {
  id: string;
  rule: string;
  database: string;
  status: 'triggered' | 'acknowledged' | 'resolved';
  severity: 'info' | 'warning' | 'critical';
  message: string;
  metric_value: string;
  triggered_at: string;
  acknowledged_at: string | null;
  resolved_at: string | null;
  acknowledged_by: string | null;
  created: string;
  updated: string;
}

export interface AlertRule {
  id: string;
  name: string;
  database: string;
  metric: string;
  condition: string;
  value: string;
  severity: 'info' | 'warning' | 'critical';
  enabled: boolean;
  notification_channels: string[];
  webhook_url: string | null;
  owner: string;
  created: string;
  updated: string;
}

export const useAlerts = (databaseId?: string) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [alertRules, setAlertRules] = useState<AlertRule[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const pb = getPocketBase();
    
    // Function to load alerts
    const loadAlerts = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Build filter
        let filter = '';
        if (databaseId) {
          filter = `database = "${databaseId}"`;
        }
        
        // Get alerts
        const alertRecords = await pb.collection('alerts').getList(1, 100, {
          filter,
          sort: '-triggered_at',
          expand: 'rule,database'
        });
        
        setAlerts(alertRecords.items.map(record => ({
          id: record.id,
          rule: record.rule,
          database: record.database,
          status: record.status,
          severity: record.severity,
          message: record.message,
          metric_value: record.metric_value,
          triggered_at: record.triggered_at,
          acknowledged_at: record.acknowledged_at,
          resolved_at: record.resolved_at,
          acknowledged_by: record.acknowledged_by,
          created: record.created,
          updated: record.updated
        })));
        
        // Get alert rules
        const ruleFilter = databaseId ? `database = "${databaseId}"` : '';
        const ruleRecords = await pb.collection('alert_rules').getList(1, 100, {
          filter: ruleFilter,
          sort: 'name'
        });
        
        setAlertRules(ruleRecords.items.map(record => ({
          id: record.id,
          name: record.name,
          database: record.database,
          metric: record.metric,
          condition: record.condition,
          value: record.value,
          severity: record.severity,
          enabled: record.enabled,
          notification_channels: record.notification_channels,
          webhook_url: record.webhook_url,
          owner: record.owner,
          created: record.created,
          updated: record.updated
        })));
        
        setLoading(false);
      } catch (err: any) {
        console.error('Error loading alerts:', err);
        setError(err.message || 'Error loading alerts');
        setLoading(false);
      }
    };
    
    // Load alerts initially
    loadAlerts();
    
    // Subscribe to real-time updates for alerts
    const alertFilter = databaseId ? `database = "${databaseId}"` : '';
    const alertsUnsubscribe = pb.collection('alerts').subscribe(alertFilter, function(e) {
      if (e.action === 'create') {
        // Add new alert to the list
        setAlerts(prev => [{
          id: e.record.id,
          rule: e.record.rule,
          database: e.record.database,
          status: e.record.status,
          severity: e.record.severity,
          message: e.record.message,
          metric_value: e.record.metric_value,
          triggered_at: e.record.triggered_at,
          acknowledged_at: e.record.acknowledged_at,
          resolved_at: e.record.resolved_at,
          acknowledged_by: e.record.acknowledged_by,
          created: e.record.created,
          updated: e.record.updated
        }, ...prev]);
      } else if (e.action === 'update') {
        // Update existing alert
        setAlerts(prev => prev.map(alert => 
          alert.id === e.record.id ? {
            id: e.record.id,
            rule: e.record.rule,
            database: e.record.database,
            status: e.record.status,
            severity: e.record.severity,
            message: e.record.message,
            metric_value: e.record.metric_value,
            triggered_at: e.record.triggered_at,
            acknowledged_at: e.record.acknowledged_at,
            resolved_at: e.record.resolved_at,
            acknowledged_by: e.record.acknowledged_by,
            created: e.record.created,
            updated: e.record.updated
          } : alert
        ));
      } else if (e.action === 'delete') {
        // Remove deleted alert
        setAlerts(prev => prev.filter(alert => alert.id !== e.record.id));
      }
    });
    
    // Subscribe to real-time updates for alert rules
    const ruleFilter = databaseId ? `database = "${databaseId}"` : '';
    const rulesUnsubscribe = pb.collection('alert_rules').subscribe(ruleFilter, function(e) {
      if (e.action === 'create') {
        // Add new rule to the list
        setAlertRules(prev => [...prev, {
          id: e.record.id,
          name: e.record.name,
          database: e.record.database,
          metric: e.record.metric,
          condition: e.record.condition,
          value: e.record.value,
          severity: e.record.severity,
          enabled: e.record.enabled,
          notification_channels: e.record.notification_channels,
          webhook_url: e.record.webhook_url,
          owner: e.record.owner,
          created: e.record.created,
          updated: e.record.updated
        }]);
      } else if (e.action === 'update') {
        // Update existing rule
        setAlertRules(prev => prev.map(rule => 
          rule.id === e.record.id ? {
            id: e.record.id,
            name: e.record.name,
            database: e.record.database,
            metric: e.record.metric,
            condition: e.record.condition,
            value: e.record.value,
            severity: e.record.severity,
            enabled: e.record.enabled,
            notification_channels: e.record.notification_channels,
            webhook_url: e.record.webhook_url,
            owner: e.record.owner,
            created: e.record.created,
            updated: e.record.updated
          } : rule
        ));
      } else if (e.action === 'delete') {
        // Remove deleted rule
        setAlertRules(prev => prev.filter(rule => rule.id !== e.record.id));
      }
    });
    
    // Cleanup subscriptions on unmount
    return () => {
      alertsUnsubscribe();
      rulesUnsubscribe();
    };
  }, [databaseId]);
  
  // Function to acknowledge an alert
  const acknowledgeAlert = async (alertId: string) => {
    try {
      const pb = getPocketBase();
      await pb.collection('alerts').update(alertId, {
        status: 'acknowledged',
        acknowledged_at: new Date().toISOString(),
        acknowledged_by: pb.authStore.model?.id
      });
      return true;
    } catch (err: any) {
      console.error('Error acknowledging alert:', err);
      setError(err.message || 'Error acknowledging alert');
      return false;
    }
  };
  
  // Function to create a new alert rule
  const createAlertRule = async (ruleData: Omit<AlertRule, 'id' | 'owner' | 'created' | 'updated'>) => {
    try {
      const pb = getPocketBase();
      await pb.collection('alert_rules').create(ruleData);
      return true;
    } catch (err: any) {
      console.error('Error creating alert rule:', err);
      setError(err.message || 'Error creating alert rule');
      return false;
    }
  };
  
  // Function to update an alert rule
  const updateAlertRule = async (ruleId: string, ruleData: Partial<AlertRule>) => {
    try {
      const pb = getPocketBase();
      await pb.collection('alert_rules').update(ruleId, ruleData);
      return true;
    } catch (err: any) {
      console.error('Error updating alert rule:', err);
      setError(err.message || 'Error updating alert rule');
      return false;
    }
  };
  
  // Function to delete an alert rule
  const deleteAlertRule = async (ruleId: string) => {
    try {
      const pb = getPocketBase();
      await pb.collection('alert_rules').delete(ruleId);
      return true;
    } catch (err: any) {
      console.error('Error deleting alert rule:', err);
      setError(err.message || 'Error deleting alert rule');
      return false;
    }
  };
  
  // Get active alerts (triggered or acknowledged)
  const activeAlerts = alerts.filter(alert => alert.status !== 'resolved');
  
  // Get alerts by severity
  const criticalAlerts = activeAlerts.filter(alert => alert.severity === 'critical');
  const warningAlerts = activeAlerts.filter(alert => alert.severity === 'warning');
  const infoAlerts = activeAlerts.filter(alert => alert.severity === 'info');
  
  return {
    alerts,
    alertRules,
    activeAlerts,
    criticalAlerts,
    warningAlerts,
    infoAlerts,
    loading,
    error,
    acknowledgeAlert,
    createAlertRule,
    updateAlertRule,
    deleteAlertRule
  };
};
