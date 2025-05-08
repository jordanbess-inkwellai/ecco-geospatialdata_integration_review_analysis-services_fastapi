import React, { useState } from 'react';
import { 
  Box, 
  Grid, 
  Typography, 
  Container, 
  Paper,
  Alert,
  Snackbar
} from '@mui/material';
import Layout from '../../components/layout/Layout';
import ProcessList from '../../components/processes/ProcessList';
import ProcessDetails from '../../components/processes/ProcessDetails';
import ProcessResults from '../../components/processes/ProcessResults';
import { useExecuteProcess } from '../../hooks/useExecuteProcess';

const ProcessesPage: React.FC = () => {
  const [selectedProcessId, setSelectedProcessId] = useState<string | null>(null);
  const { 
    executeProcess, 
    result, 
    loading, 
    error, 
    resetResult 
  } = useExecuteProcess();
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });

  const handleSelectProcess = (processId: string) => {
    setSelectedProcessId(processId);
    resetResult();
  };

  const handleExecuteProcess = async (processId: string, inputs: any) => {
    try {
      await executeProcess(processId, inputs);
      setNotification({
        open: true,
        message: 'Process executed successfully',
        severity: 'success'
      });
    } catch (err) {
      setNotification({
        open: true,
        message: `Error executing process: ${err instanceof Error ? err.message : String(err)}`,
        severity: 'error'
      });
    }
  };

  const handleCloseNotification = () => {
    setNotification({
      ...notification,
      open: false
    });
  };

  return (
    <Layout title="OGC API Processes">
      <Container maxWidth={false} sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          OGC API Processes
        </Typography>
        <Typography variant="body1" paragraph>
          Discover and execute geospatial analysis processes using the OGC API Processes standard.
        </Typography>
        
        <Grid container spacing={3} sx={{ height: 'calc(100vh - 200px)' }}>
          {/* Process List */}
          <Grid item xs={12} md={3} sx={{ height: '100%' }}>
            <ProcessList 
              onSelectProcess={handleSelectProcess}
              selectedProcessId={selectedProcessId || undefined}
            />
          </Grid>
          
          {/* Process Details */}
          <Grid item xs={12} md={4} sx={{ height: '100%' }}>
            {selectedProcessId ? (
              <ProcessDetails 
                processId={selectedProcessId}
                onExecute={handleExecuteProcess}
              />
            ) : (
              <Paper elevation={2} sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Box p={3} textAlign="center">
                  <Typography variant="h6" gutterBottom>
                    Select a Process
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Choose a process from the list to view details and execute it.
                  </Typography>
                </Box>
              </Paper>
            )}
          </Grid>
          
          {/* Process Results */}
          <Grid item xs={12} md={5} sx={{ height: '100%' }}>
            <ProcessResults 
              processId={selectedProcessId || ''}
              result={result}
              loading={loading}
              error={error}
            />
          </Grid>
        </Grid>
      </Container>
      
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

export default ProcessesPage;
