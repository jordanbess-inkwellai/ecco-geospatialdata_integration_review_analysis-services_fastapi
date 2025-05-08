import { useState, useEffect } from 'react';
import { apiClient } from '../lib/api';

interface Process {
  id: string;
  title: string;
  description: string;
}

interface UseProcessesResult {
  processes: Process[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useProcesses(): UseProcessesResult {
  const [processes, setProcesses] = useState<Process[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [refetchTrigger, setRefetchTrigger] = useState<number>(0);

  useEffect(() => {
    const fetchProcesses = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await apiClient.get('/processes');
        if (response.data && response.data.processes) {
          setProcesses(response.data.processes);
        } else {
          setProcesses([]);
        }
      } catch (err) {
        console.error('Error fetching processes:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch processes');
        setProcesses([]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchProcesses();
  }, [refetchTrigger]);

  const refetch = () => {
    setRefetchTrigger(prev => prev + 1);
  };

  return { processes, loading, error, refetch };
}
