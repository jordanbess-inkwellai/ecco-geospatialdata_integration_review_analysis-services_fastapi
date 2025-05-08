import { useState, useEffect } from 'react';
import { apiClient } from '../lib/api';

interface UseAIFeaturesResult {
  aiEnabled: boolean;
  aiStatus: any | null;
  loading: boolean;
  error: string | null;
}

export function useAIFeatures(): UseAIFeaturesResult {
  // Check environment variable first (set at build time)
  const envAiEnabled = process.env.NEXT_PUBLIC_AI_ENABLED === 'true';

  const [aiEnabled, setAiEnabled] = useState<boolean>(envAiEnabled);
  const [aiStatus, setAiStatus] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(envAiEnabled); // Only loading if AI might be enabled
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // If AI is disabled by environment variable, don't even try to check the API
    if (!envAiEnabled) {
      setLoading(false);
      return;
    }

    const checkAIStatus = async () => {
      setLoading(true);
      setError(null);

      try {
        // Try to fetch AI status
        const response = await apiClient.get('/ai/status');
        const status = response.data;

        setAiStatus(status);
        setAiEnabled(status.enabled);
        setLoading(false);
      } catch (err) {
        // If we get a 404, it means the AI endpoints don't exist (build flag disabled)
        // If we get a 400 with "AI features are not enabled", it means the endpoints exist but AI is disabled
        if (err.response && (err.response.status === 404 ||
            (err.response.status === 400 && err.response.data?.error?.includes('AI features are not enabled')))) {
          setAiEnabled(false);
          setAiStatus(null);
        } else {
          console.error('Error checking AI status:', err);
          setError('Failed to check AI status');
        }
        setLoading(false);
      }
    };

    checkAIStatus();
  }, [envAiEnabled]);

  return { aiEnabled, aiStatus, loading, error };
}
