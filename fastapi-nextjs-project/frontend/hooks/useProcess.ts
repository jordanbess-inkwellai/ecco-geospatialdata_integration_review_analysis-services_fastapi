import { useState, useEffect } from 'react';
import { apiClient } from '../lib/api';

interface UseProcessResult {
  process: any;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useProcess(processId: string): UseProcessResult {
  const [process, setProcess] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [refetchTrigger, setRefetchTrigger] = useState<number>(0);

  useEffect(() => {
    if (!processId) {
      setProcess(null);
      setLoading(false);
      setError(null);
      return;
    }
    
    const fetchProcess = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await apiClient.get(`/processes/${processId}`);
        setProcess(response.data);
      } catch (err) {
        console.error(`Error fetching process ${processId}:`, err);
        setError(err instanceof Error ? err.message : `Failed to fetch process ${processId}`);
        setProcess(null);
      } finally {
        setLoading(false);
      }
    };
    
    fetchProcess();
  }, [processId, refetchTrigger]);

  const refetch = () => {
    setRefetchTrigger(prev => prev + 1);
  };

  return { process, loading, error, refetch };
}
