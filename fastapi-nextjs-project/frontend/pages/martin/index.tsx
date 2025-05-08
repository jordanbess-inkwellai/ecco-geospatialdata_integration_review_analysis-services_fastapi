import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Container,
  Grid,
  Paper,
  Button,
  Alert,
  Snackbar,
  CircularProgress
} from '@mui/material';
import Layout from '../../components/layout/Layout';
import MapViewer from '../../components/martin/MapViewer';
import { apiClient } from '../../lib/api';

const MartinPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [serverStatus, setServerStatus] = useState<any>(null);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });

  // Check Martin status on component mount
  useEffect(() => {
    checkMartinStatus();
  }, []);

  // Check Martin status
  const checkMartinStatus = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.get('/martin/status');
      setServerStatus(response.data);
      
      if (response.data.status !== 'ok') {
        setError('Martin server is not available');
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error checking Martin status:', err);
      setError('Failed to connect to Martin server');
      setLoading(false);
    }
  };

  // Close notification
  const handleCloseNotification = () => {
    setNotification({
      ...notification,
      open: false
    });
  };

  if (loading) {
    return (
      <Layout title="Martin MapLibre">
        <Container maxWidth={false} sx={{ mt: 4, mb: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
          <CircularProgress />
        </Container>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout title="Martin MapLibre">
        <Container maxWidth={false} sx={{ mt: 4, mb: 4 }}>
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
          
          <Button variant="contained" onClick={checkMartinStatus}>
            Retry Connection
          </Button>
        </Container>
      </Layout>
    );
  }

  return (
    <Layout title="Martin MapLibre">
      <Container maxWidth={false} sx={{ mt: 4, mb: 4, height: 'calc(100vh - 128px)' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">
            Martin MapLibre
          </Typography>
          
          <Box>
            <Typography variant="body2" color="text.secondary">
              Server: {serverStatus.url} • Version: {serverStatus.version}
            </Typography>
          </Box>
        </Box>
        
        <Paper sx={{ height: 'calc(100% - 60px)', overflow: 'hidden' }}>
          <MapViewer />
        </Paper>
      </Container>
      
      {/* Notification */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleCloseNotification}
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Layout>
  );
};

export default MartinPage;
