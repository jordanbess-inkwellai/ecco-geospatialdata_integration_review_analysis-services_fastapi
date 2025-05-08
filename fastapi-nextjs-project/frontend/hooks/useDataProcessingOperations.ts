import { useState, useEffect } from 'react';
import { apiClient } from '../lib/api';

interface Operation {
  id: string;
  name: string;
  description: string;
  inputs: Array<{
    name: string;
    type: string;
    description: string;
    options?: string[];
    required?: boolean;
  }>;
}

interface UseDataProcessingOperationsResult {
  operations: Record<string, Operation[]>;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useDataProcessingOperations(): UseDataProcessingOperationsResult {
  const [operations, setOperations] = useState<Record<string, Operation[]>>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [refetchTrigger, setRefetchTrigger] = useState<number>(0);

  useEffect(() => {
    const fetchOperations = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await apiClient.get('/data-processing/operations');
        setOperations(response.data);
      } catch (err) {
        console.error('Error fetching data processing operations:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch operations');
        setOperations({});
      } finally {
        setLoading(false);
      }
    };
    
    fetchOperations();
  }, [refetchTrigger]);

  const refetch = () => {
    setRefetchTrigger(prev => prev + 1);
  };

  return { operations, loading, error, refetch };
}
