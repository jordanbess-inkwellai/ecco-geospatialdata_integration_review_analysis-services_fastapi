import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Button,
  Alert,
  Snackbar,
  CircularProgress
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import SaveIcon from '@mui/icons-material/Save';
import Layout from '../../../../components/layout/Layout';
import WorkflowBuilder from '../../../../components/workflows/WorkflowBuilder';
import { apiClient } from '../../../../lib/api';
import { useRouter } from 'next/router';

const EditWorkflowPage: React.FC = () => {
  const router = useRouter();
  const { namespace, id } = router.query;
  const [workflow, setWorkflow] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });

  // Load workflow on component mount
  useEffect(() => {
    if (namespace && id) {
      fetchWorkflow();
    }
  }, [namespace, id]);

  // Fetch workflow from the API
  const fetchWorkflow = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.get(`/workflows/flows/${namespace}/${id}`);
      setWorkflow(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching workflow:', err);
      setError('Failed to fetch workflow');
      setLoading(false);
    }
  };

  // Handle workflow save
  const handleSaveWorkflow = async (updatedWorkflow: any) => {
    try {
      setLoading(true);
      
      const response = await apiClient.put(
        `/workflows/flows/${namespace}/${id}`,
        updatedWorkflow
      );
      
      setNotification({
        open: true,
        message: `Workflow ${id} updated successfully`,
        severity: 'success'
      });
      
      // Update the workflow state
      setWorkflow(response.data);
      
      setLoading(false);
    } catch (err) {
      console.error('Error updating workflow:', err);
      
      setNotification({
        open: true,
        message: 'Failed to update workflow',
        severity: 'error'
      });
      
      setLoading(false);
    }
  };

  // Handle workflow execution
  const handleExecuteWorkflow = async (workflow: any) => {
    try {
      setLoading(true);
      
      await apiClient.post('/workflows/flows/execute', {
        namespace: workflow.namespace,
        flow_id: workflow.id
      });
      
      setNotification({
        open: true,
        message: `Workflow ${workflow.id} execution started`,
        severity: 'success'
      });
      
      setLoading(false);
    } catch (err) {
      console.error('Error executing workflow:', err);
      
      setNotification({
        open: true,
        message: `Failed to execute workflow ${workflow.id}`,
        severity: 'error'
      });
      
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

  // Navigate back to workflows page
  const handleBack = () => {
    router.push('/workflows');
  };

  if (loading && !workflow) {
    return (
      <Layout title="Edit Workflow">
        <Container maxWidth={false} sx={{ mt: 4, mb: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
          <CircularProgress />
        </Container>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout title="Edit Workflow">
        <Container maxWidth={false} sx={{ mt: 4, mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Button
              startIcon={<ArrowBackIcon />}
              onClick={handleBack}
              sx={{ mr: 2 }}
            >
              Back
            </Button>
            
            <Typography variant="h4">
              Edit Workflow
            </Typography>
          </Box>
          
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
          
          <Button variant="contained" onClick={fetchWorkflow}>
            Retry
          </Button>
        </Container>
      </Layout>
    );
  }

  return (
    <Layout title={`Edit Workflow: ${id}`}>
      <Container maxWidth={false} sx={{ mt: 4, mb: 4, height: 'calc(100vh - 128px)' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Button
              startIcon={<ArrowBackIcon />}
              onClick={handleBack}
              sx={{ mr: 2 }}
            >
              Back
            </Button>
            
            <Typography variant="h4">
              Edit Workflow: {id}
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ height: 'calc(100% - 70px)' }}>
          {workflow && (
            <WorkflowBuilder
              initialFlow={workflow}
              onSave={handleSaveWorkflow}
              onExecute={handleExecuteWorkflow}
            />
          )}
        </Box>
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
      
      {/* Loading Overlay */}
      {loading && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'rgba(255, 255, 255, 0.7)',
            zIndex: 9999
          }}
        >
          <CircularProgress />
        </Box>
      )}
    </Layout>
  );
};

export default EditWorkflowPage;
