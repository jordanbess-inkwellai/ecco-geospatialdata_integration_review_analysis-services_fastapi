import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Alert,
  Button,
  Paper,
  Snackbar
} from '@mui/material';
import Layout from '../../components/layout/Layout';
import DocETLDashboard from '../../components/docetl/DocETLDashboard';
import { useRouter } from 'next/router';

const DocETLPage: React.FC = () => {
  const router = useRouter();
  const docETLEnabled = process.env.NEXT_PUBLIC_DOCETL_ENABLED === 'true';
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });
  
  // Handle error from DocETL dashboard
  const handleError = (error: string) => {
    setNotification({
      open: true,
      message: error,
      severity: 'error'
    });
  };
  
  // Close notification
  const handleCloseNotification = () => {
    setNotification({
      ...notification,
      open: false
    });
  };
  
  // If DocETL is not enabled, show a message and redirect to home
  if (!docETLEnabled) {
    return (
      <Layout title="Document ETL">
        <Container maxWidth={false} sx={{ mt: 4, mb: 4 }}>
          <Alert severity="warning" sx={{ mb: 3 }}>
            DocETL integration is not enabled in this build. Please enable it by setting NEXT_PUBLIC_DOCETL_ENABLED=true in your environment.
          </Alert>
          
          <Button variant="contained" onClick={() => router.push('/')}>
            Return to Dashboard
          </Button>
        </Container>
      </Layout>
    );
  }
  
  return (
    <Layout title="Document ETL">
      <Container maxWidth={false} sx={{ mt: 4, mb: 4, height: 'calc(100vh - 128px)' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">
            Document ETL
          </Typography>
          
          <Box>
            <Typography variant="body2" color="text.secondary">
              Extract, Transform, and Load document data
            </Typography>
          </Box>
        </Box>
        
        <Paper sx={{ height: 'calc(100% - 60px)', overflow: 'hidden' }}>
          <DocETLDashboard onError={handleError} />
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

export default DocETLPage;
