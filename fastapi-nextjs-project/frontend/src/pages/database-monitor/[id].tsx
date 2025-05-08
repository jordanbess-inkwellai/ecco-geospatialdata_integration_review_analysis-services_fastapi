import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../../components/Layout';
import DatabaseDashboard from '../../components/CloudSQLMonitor/DatabaseDashboard';
import { getPocketBase, isAuthenticated } from '../../lib/pocketbase';

const DatabaseDetailPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [database, setDatabase] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { id } = router.query;
  
  // Load database
  useEffect(() => {
    if (!id || !isAuthenticated()) {
      if (!isAuthenticated()) {
        router.push('/login?redirect=/database-monitor');
      }
      return;
    }
    
    const loadDatabase = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const pb = getPocketBase();
        const record = await pb.collection('monitored_databases').getOne(id as string);
        
        // Convert to instance config format
        const instanceConfig = {
          pocketbase_id: record.id,
          instance_connection_name: record.instance_connection_name,
          database: record.database,
          user: record.user,
          password: record.password,
          ip_type: record.ip_type
        };
        
        setDatabase(instanceConfig);
        setIsLoading(false);
      } catch (err: any) {
        console.error('Error loading database:', err);
        setError(err.message || 'Error loading database');
        setIsLoading(false);
      }
    };
    
    loadDatabase();
  }, [id, router]);
  
  if (isLoading) {
    return (
      <Layout>
        <div className="loading-container">
          <p>Loading database...</p>
        </div>
      </Layout>
    );
  }
  
  if (error) {
    return (
      <Layout>
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <button
            className="back-button"
            onClick={() => router.push('/database-monitor')}
          >
            Back to Database Monitor
          </button>
        </div>
      </Layout>
    );
  }
  
  return (
    <Layout>
      <div className="database-detail-page">
        {database ? (
          <DatabaseDashboard initialInstanceConfig={database} />
        ) : (
          <div className="not-found">
            <h2>Database Not Found</h2>
            <p>The requested database could not be found.</p>
            <button
              className="back-button"
              onClick={() => router.push('/database-monitor')}
            >
              Back to Database Monitor
            </button>
          </div>
        )}
      </div>
      
      <style jsx>{`
        .database-detail-page {
          padding: 1rem 0;
        }
        
        .loading-container {
          display: flex;
          justify-content: center;
          align-items: center;
          height: 50vh;
          font-size: 1.2rem;
          color: #666;
        }
        
        .error-container, .not-found {
          max-width: 600px;
          margin: 3rem auto;
          padding: 2rem;
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          text-align: center;
        }
        
        .error-container h2, .not-found h2 {
          margin-top: 0;
          color: #333;
        }
        
        .error-container p, .not-found p {
          margin-bottom: 2rem;
          color: #666;
        }
        
        .back-button {
          padding: 0.75rem 1.5rem;
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 1rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .back-button:hover {
          background-color: #0051a8;
        }
      `}</style>
    </Layout>
  );
};

export default DatabaseDetailPage;
