import React, { useState } from 'react';
import { 
  Box, 
  Grid, 
  Typography, 
  Container, 
  Snackbar,
  Alert
} from '@mui/material';
import Layout from '../../components/layout/Layout';
import DataProcessingMenu from '../../components/data-processing/DataProcessingMenu';
import DataProcessingForm from '../../components/data-processing/DataProcessingForm';
import DataProcessingResults from '../../components/data-processing/DataProcessingResults';
import { MapProvider } from '../../contexts/MapContext';

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

const DataProcessingPage: React.FC = () => {
  const [selectedOperation, setSelectedOperation] = useState<Operation | null>(null);
  const [processingResult, setProcessingResult] = useState<any>(null);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });

  const handleSelectOperation = (operation: Operation) => {
    setSelectedOperation(operation);
    setProcessingResult(null);
  };

  const handleProcessingComplete = (result: any) => {
    setProcessingResult(result);
    setNotification({
      open: true,
      message: 'Processing completed successfully',
      severity: 'success'
    });
  };

  const handleCloseNotification = () => {
    setNotification({
      ...notification,
      open: false
    });
  };

  return (
    <Layout title="Data Processing">
      <MapProvider>
        <Container maxWidth={false} sx={{ mt: 4, mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Geospatial Data Processing
          </Typography>
          <Typography variant="body1" paragraph>
            Process and transform geospatial data using a variety of tools.
          </Typography>
          
          <Grid container spacing={3} sx={{ height: 'calc(100vh - 200px)' }}>
            {/* Operations Menu */}
            <Grid item xs={12} md={3} sx={{ height: '100%' }}>
              <DataProcessingMenu 
                onSelectOperation={handleSelectOperation}
                selectedOperationId={selectedOperation?.id}
              />
            </Grid>
            
            {/* Processing Form */}
            <Grid item xs={12} md={4} sx={{ height: '100%' }}>
              <DataProcessingForm 
                operation={selectedOperation}
                onProcessingComplete={handleProcessingComplete}
              />
            </Grid>
            
            {/* Processing Results */}
            <Grid item xs={12} md={5} sx={{ height: '100%' }}>
              <DataProcessingResults result={processingResult} />
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
      </MapProvider>
    </Layout>
  );
};

export default DataProcessingPage;
