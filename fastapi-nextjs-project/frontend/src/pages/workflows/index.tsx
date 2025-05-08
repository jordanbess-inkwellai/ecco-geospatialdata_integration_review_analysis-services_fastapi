import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../../components/Layout';
import WorkflowsList from '../../components/Kestra/WorkflowsList';
import { isAuthenticated } from '../../lib/pocketbase';

const WorkflowsPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const router = useRouter();
  
  // Check authentication
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login?redirect=/workflows');
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
      <div className="workflows-page">
        <WorkflowsList />
      </div>
      
      <style jsx>{`
        .workflows-page {
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

export default WorkflowsPage;
