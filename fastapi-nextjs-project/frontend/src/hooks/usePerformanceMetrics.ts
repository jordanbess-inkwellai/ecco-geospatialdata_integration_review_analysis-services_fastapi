import { useState, useEffect } from 'react';
import { getPocketBase } from '../lib/pocketbase';

export interface PerformanceMetric {
  id: string;
  database: string;
  cache_hit_ratio: number;
  active_connections: number;
  idle_connections: number;
  transactions_per_second: number;
  queries_per_second: number;
  rows_per_second: number;
  index_hit_ratio: number;
  slow_queries: number;
  deadlocks: number;
  metrics_json: string;
  timestamp: string;
  created: string;
  updated: string;
}

export const usePerformanceMetrics = (databaseId: string, limit: number = 20) => {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    if (!databaseId) {
      setMetrics([]);
      setLoading(false);
      return;
    }
    
    const pb = getPocketBase();
    
    // Function to load metrics
    const loadMetrics = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const records = await pb.collection('performance_metrics').getList(1, limit, {
          filter: `database = "${databaseId}"`,
          sort: '-timestamp'
        });
        
        setMetrics(records.items.map(record => ({
          id: record.id,
          database: record.database,
          cache_hit_ratio: record.cache_hit_ratio,
          active_connections: record.active_connections,
          idle_connections: record.idle_connections,
          transactions_per_second: record.transactions_per_second,
          queries_per_second: record.queries_per_second,
          rows_per_second: record.rows_per_second,
          index_hit_ratio: record.index_hit_ratio,
          slow_queries: record.slow_queries,
          deadlocks: record.deadlocks,
          metrics_json: record.metrics_json,
          timestamp: record.timestamp,
          created: record.created,
          updated: record.updated
        })));
        
        setLoading(false);
      } catch (err: any) {
        console.error('Error loading performance metrics:', err);
        setError(err.message || 'Error loading performance metrics');
        setLoading(false);
      }
    };
    
    // Load metrics initially
    loadMetrics();
    
    // Subscribe to real-time updates
    const unsubscribe = pb.collection('performance_metrics').subscribe(`database = "${databaseId}"`, function(e) {
      if (e.action === 'create') {
        // Add new metric to the beginning of the list
        setMetrics(prev => {
          const newMetrics = [{
            id: e.record.id,
            database: e.record.database,
            cache_hit_ratio: e.record.cache_hit_ratio,
            active_connections: e.record.active_connections,
            idle_connections: e.record.idle_connections,
            transactions_per_second: e.record.transactions_per_second,
            queries_per_second: e.record.queries_per_second,
            rows_per_second: e.record.rows_per_second,
            index_hit_ratio: e.record.index_hit_ratio,
            slow_queries: e.record.slow_queries,
            deadlocks: e.record.deadlocks,
            metrics_json: e.record.metrics_json,
            timestamp: e.record.timestamp,
            created: e.record.created,
            updated: e.record.updated
          }, ...prev];
          
          // Keep only the latest 'limit' metrics
          return newMetrics.slice(0, limit);
        });
      }
    });
    
    // Cleanup subscription on unmount
    return () => {
      unsubscribe();
    };
  }, [databaseId, limit]);
  
  // Function to get the latest metric
  const getLatestMetric = () => {
    if (metrics.length === 0) return null;
    return metrics[0];
  };
  
  // Function to manually refresh metrics
  const refreshMetrics = async () => {
    if (!databaseId) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const pb = getPocketBase();
      const records = await pb.collection('performance_metrics').getList(1, limit, {
        filter: `database = "${databaseId}"`,
        sort: '-timestamp'
      });
      
      setMetrics(records.items.map(record => ({
        id: record.id,
        database: record.database,
        cache_hit_ratio: record.cache_hit_ratio,
        active_connections: record.active_connections,
        idle_connections: record.idle_connections,
        transactions_per_second: record.transactions_per_second,
        queries_per_second: record.queries_per_second,
        rows_per_second: record.rows_per_second,
        index_hit_ratio: record.index_hit_ratio,
        slow_queries: record.slow_queries,
        deadlocks: record.deadlocks,
        metrics_json: record.metrics_json,
        timestamp: record.timestamp,
        created: record.created,
        updated: record.updated
      })));
      
      setLoading(false);
    } catch (err: any) {
      console.error('Error refreshing performance metrics:', err);
      setError(err.message || 'Error refreshing performance metrics');
      setLoading(false);
    }
  };
  
  return {
    metrics,
    latestMetric: getLatestMetric(),
    loading,
    error,
    refreshMetrics
  };
};
