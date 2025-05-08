import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../../components/Layout';
import ScriptBrowser from '../../components/ScriptRepository/ScriptBrowser';
import { isAuthenticated } from '../../lib/pocketbase';

const ScriptsPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const router = useRouter();
  
  // Check authentication
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login?redirect=/scripts');
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
      <div className="scripts-page">
        <ScriptBrowser />
      </div>
      
      <style jsx>{`
        .scripts-page {
          padding: 0;
          height: calc(100vh - 64px);
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

export default ScriptsPage;
