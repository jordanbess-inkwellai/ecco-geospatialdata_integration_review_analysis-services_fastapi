import { useState, useEffect } from 'react';
import { getPocketBase } from '../lib/pocketbase';

export interface MonitoredDatabase {
  id: string;
  name: string;
  instance_connection_name: string;
  database: string;
  user: string;
  password: string;
  ip_type: 'PUBLIC' | 'PRIVATE';
  check_interval_minutes: number;
  owner: string;
  created: string;
  updated: string;
}

export const useMonitoredDatabases = () => {
  const [databases, setDatabases] = useState<MonitoredDatabase[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const pb = getPocketBase();
    
    // Function to load databases
    const loadDatabases = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const records = await pb.collection('monitored_databases').getFullList({
          sort: 'name',
          expand: 'owner'
        });
        
        setDatabases(records.map(record => ({
          id: record.id,
          name: record.name,
          instance_connection_name: record.instance_connection_name,
          database: record.database,
          user: record.user,
          password: record.password,
          ip_type: record.ip_type,
          check_interval_minutes: record.check_interval_minutes,
          owner: record.owner,
          created: record.created,
          updated: record.updated
        })));
        
        setLoading(false);
      } catch (err: any) {
        console.error('Error loading databases:', err);
        setError(err.message || 'Error loading databases');
        setLoading(false);
      }
    };
    
    // Load databases initially
    loadDatabases();
    
    // Subscribe to real-time updates
    const unsubscribe = pb.collection('monitored_databases').subscribe('*', function(e) {
      if (e.action === 'create') {
        // Add new database to the list
        setDatabases(prev => [...prev, {
          id: e.record.id,
          name: e.record.name,
          instance_connection_name: e.record.instance_connection_name,
          database: e.record.database,
          user: e.record.user,
          password: e.record.password,
          ip_type: e.record.ip_type,
          check_interval_minutes: e.record.check_interval_minutes,
          owner: e.record.owner,
          created: e.record.created,
          updated: e.record.updated
        }]);
      } else if (e.action === 'update') {
        // Update existing database
        setDatabases(prev => prev.map(db => 
          db.id === e.record.id ? {
            id: e.record.id,
            name: e.record.name,
            instance_connection_name: e.record.instance_connection_name,
            database: e.record.database,
            user: e.record.user,
            password: e.record.password,
            ip_type: e.record.ip_type,
            check_interval_minutes: e.record.check_interval_minutes,
            owner: e.record.owner,
            created: e.record.created,
            updated: e.record.updated
          } : db
        ));
      } else if (e.action === 'delete') {
        // Remove deleted database
        setDatabases(prev => prev.filter(db => db.id !== e.record.id));
      }
    });
    
    // Cleanup subscription on unmount
    return () => {
      unsubscribe();
    };
  }, []);
  
  // Function to add a new database
  const addDatabase = async (databaseData: Omit<MonitoredDatabase, 'id' | 'owner' | 'created' | 'updated'>) => {
    try {
      const pb = getPocketBase();
      await pb.collection('monitored_databases').create(databaseData);
      return true;
    } catch (err: any) {
      console.error('Error adding database:', err);
      setError(err.message || 'Error adding database');
      return false;
    }
  };
  
  // Function to update a database
  const updateDatabase = async (id: string, databaseData: Partial<MonitoredDatabase>) => {
    try {
      const pb = getPocketBase();
      await pb.collection('monitored_databases').update(id, databaseData);
      return true;
    } catch (err: any) {
      console.error('Error updating database:', err);
      setError(err.message || 'Error updating database');
      return false;
    }
  };
  
  // Function to delete a database
  const deleteDatabase = async (id: string) => {
    try {
      const pb = getPocketBase();
      await pb.collection('monitored_databases').delete(id);
      return true;
    } catch (err: any) {
      console.error('Error deleting database:', err);
      setError(err.message || 'Error deleting database');
      return false;
    }
  };
  
  return {
    databases,
    loading,
    error,
    addDatabase,
    updateDatabase,
    deleteDatabase
  };
};
