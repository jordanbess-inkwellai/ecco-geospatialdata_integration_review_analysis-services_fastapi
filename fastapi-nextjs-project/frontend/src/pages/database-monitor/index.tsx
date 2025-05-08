import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../../components/Layout';
import DatabaseDashboard from '../../components/CloudSQLMonitor/DatabaseDashboard';
import { getPocketBase, isAuthenticated } from '../../lib/pocketbase';

const DatabaseMonitorPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const router = useRouter();
  
  // Check authentication
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login?redirect=/database-monitor');
      return;
    }
    
    setIsLoading(false);
  }, [router]);
  
  if (isLoading) {
    return (
      <Layout>
        <div className="loading-container">
          <p>Loading...</p>
        </div>
      </Layout>
    );
  }
  
  return (
    <Layout>
      <div className="database-monitor-page">
        <DatabaseDashboard />
      </div>
      
      <style jsx>{`
        .database-monitor-page {
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
      `}</style>
    </Layout>
  );
};

export default DatabaseMonitorPage;
