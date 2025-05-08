import { useState, useEffect } from 'react';
import { getPocketBase } from '../lib/pocketbase';

export interface DatabaseStatus {
  id: string;
  database: string;
  status: 'online' | 'offline' | 'degraded' | 'unknown';
  version: string;
  uptime: string;
  connection_count: number;
  size: string;
  table_count: number;
  has_postgis: boolean;
  postgis_version: string;
  error_message: string;
  last_check: string;
  created: string;
  updated: string;
}

export const useDatabaseStatus = (databaseId: string) => {
  const [status, setStatus] = useState<DatabaseStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    if (!databaseId) {
      setStatus(null);
      setLoading(false);
      return;
    }
    
    const pb = getPocketBase();
    
    // Function to load status
    const loadStatus = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const records = await pb.collection('database_status').getList(1, 1, {
          filter: `database = "${databaseId}"`,
          sort: '-created'
        });
        
        if (records.items.length > 0) {
          const record = records.items[0];
          setStatus({
            id: record.id,
            database: record.database,
            status: record.status,
            version: record.version,
            uptime: record.uptime,
            connection_count: record.connection_count,
            size: record.size,
            table_count: record.table_count,
            has_postgis: record.has_postgis,
            postgis_version: record.postgis_version,
            error_message: record.error_message,
            last_check: record.last_check,
            created: record.created,
            updated: record.updated
          });
        } else {
          setStatus(null);
        }
        
        setLoading(false);
      } catch (err: any) {
        console.error('Error loading database status:', err);
        setError(err.message || 'Error loading database status');
        setLoading(false);
      }
    };
    
    // Load status initially
    loadStatus();
    
    // Subscribe to real-time updates
    const unsubscribe = pb.collection('database_status').subscribe(`database = "${databaseId}"`, function(e) {
      if (e.action === 'create' || e.action === 'update') {
        setStatus({
          id: e.record.id,
          database: e.record.database,
          status: e.record.status,
          version: e.record.version,
          uptime: e.record.uptime,
          connection_count: e.record.connection_count,
          size: e.record.size,
          table_count: e.record.table_count,
          has_postgis: e.record.has_postgis,
          postgis_version: e.record.postgis_version,
          error_message: e.record.error_message,
          last_check: e.record.last_check,
          created: e.record.created,
          updated: e.record.updated
        });
      }
    });
    
    // Cleanup subscription on unmount
    return () => {
      unsubscribe();
    };
  }, [databaseId]);
  
  // Function to manually refresh status
  const refreshStatus = async () => {
    if (!databaseId) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const pb = getPocketBase();
      const records = await pb.collection('database_status').getList(1, 1, {
        filter: `database = "${databaseId}"`,
        sort: '-created'
      });
      
      if (records.items.length > 0) {
        const record = records.items[0];
        setStatus({
          id: record.id,
          database: record.database,
          status: record.status,
          version: record.version,
          uptime: record.uptime,
          connection_count: record.connection_count,
          size: record.size,
          table_count: record.table_count,
          has_postgis: record.has_postgis,
          postgis_version: record.postgis_version,
          error_message: record.error_message,
          last_check: record.last_check,
          created: record.created,
          updated: record.updated
        });
      } else {
        setStatus(null);
      }
      
      setLoading(false);
    } catch (err: any) {
      console.error('Error refreshing database status:', err);
      setError(err.message || 'Error refreshing database status');
      setLoading(false);
    }
  };
  
  return {
    status,
    loading,
    error,
    refreshStatus
  };
};
