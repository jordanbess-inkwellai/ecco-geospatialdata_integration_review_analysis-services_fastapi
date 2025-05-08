import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Button,
  Paper,
  Divider,
  Tabs,
  Tab,
} from '@mui/material';

interface QuerybookFrameProps {
  initialPath?: string;
}

const QuerybookFrame: React.FC<QuerybookFrameProps> = ({
  initialPath = '/',
}) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [path, setPath] = useState<string>(initialPath);
  
  const queryBookUrl = process.env.NEXT_PUBLIC_QUERYBOOK_URL || 'http://localhost:10001';
  const iframeUrl = `${queryBookUrl}${path}`;
  
  // Handle iframe load event
  const handleIframeLoad = () => {
    setLoading(false);
  };
  
  // Handle iframe error
  const handleIframeError = () => {
    setLoading(false);
    setError('Failed to load Querybook. Please check if the Querybook server is running.');
  };
  
  // Handle retry
  const handleRetry = () => {
    setLoading(true);
    setError(null);
    
    // Force iframe reload
    const iframe = document.getElementById('querybook-iframe') as HTMLIFrameElement;
    if (iframe) {
      iframe.src = iframeUrl;
    }
  };
  
  // Listen for messages from the iframe
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // Only process messages from Querybook
      if (event.origin !== queryBookUrl) {
        return;
      }
      
      // Handle navigation events
      if (event.data && event.data.type === 'navigation') {
        setPath(event.data.path);
      }
    };
    
    window.addEventListener('message', handleMessage);
    
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, [queryBookUrl]);
  
  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6">
          Data Query Workbench
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Powered by Querybook
        </Typography>
      </Box>
      
      {/* Content */}
      <Box sx={{ flexGrow: 1, position: 'relative' }}>
        {loading && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              zIndex: 10,
              bgcolor: 'rgba(255, 255, 255, 0.8)',
            }}
          >
            <CircularProgress />
          </Box>
        )}
        
        {error && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              p: 3,
            }}
          >
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
            <Button variant="contained" onClick={handleRetry}>
              Retry
            </Button>
          </Box>
        )}
        
        <iframe
          id="querybook-iframe"
          src={iframeUrl}
          style={{
            width: '100%',
            height: '100%',
            border: 'none',
          }}
          onLoad={handleIframeLoad}
          onError={handleIframeError}
        />
      </Box>
    </Box>
  );
};

export default QuerybookFrame;
