import { useState } from 'react';
import { apiClient } from '../lib/api';

interface UseExecuteProcessResult {
  executeProcess: (processId: string, inputs: any) => Promise<any>;
  result: any;
  loading: boolean;
  error: string | null;
  resetResult: () => void;
}

export function useExecuteProcess(): UseExecuteProcessResult {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const executeProcess = async (processId: string, inputs: any): Promise<any> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.post(`/processes/${processId}/execution`, inputs);
      const data = response.data;
      setResult(data);
      return data;
    } catch (err) {
      console.error(`Error executing process ${processId}:`, err);
      const errorMessage = err instanceof Error ? err.message : `Failed to execute process ${processId}`;
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const resetResult = () => {
    setResult(null);
    setError(null);
  };

  return { executeProcess, result, loading, error, resetResult };
}
