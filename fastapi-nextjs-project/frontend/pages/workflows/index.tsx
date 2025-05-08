import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Grid, 
  Paper, 
  Tabs, 
  Tab,
  Button,
  Alert,
  Snackbar,
  CircularProgress
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import Layout from '../../components/layout/Layout';
import WorkflowList from '../../components/workflows/WorkflowList';
import WorkflowExecutions from '../../components/workflows/WorkflowExecutions';
import { apiClient } from '../../lib/api';
import { useRouter } from 'next/router';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`workflow-tabpanel-${index}`}
      aria-labelledby={`workflow-tab-${index}`}
      {...other}
      style={{ height: '100%' }}
    >
      {value === index && (
        <Box sx={{ height: '100%' }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const WorkflowsPage: React.FC = () => {
  const router = useRouter();
  const [tabValue, setTabValue] = useState(0);
  const [kestraStatus, setKestraStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedWorkflow, setSelectedWorkflow] = useState<any | null>(null);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });

  // Check Kestra status on component mount
  useEffect(() => {
    checkKestraStatus();
  }, []);

  // Check Kestra status
  const checkKestraStatus = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.get('/workflows/status');
      setKestraStatus(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error checking Kestra status:', err);
      setError('Failed to connect to Kestra workflow engine');
      setLoading(false);
    }
  };

  // Handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Handle workflow selection
  const handleSelectWorkflow = (workflow: any) => {
    setSelectedWorkflow(workflow);
    setTabValue(1); // Switch to executions tab
  };

  // Handle workflow edit
  const handleEditWorkflow = (workflow: any) => {
    router.push(`/workflows/edit/${workflow.namespace}/${workflow.id}`);
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
      
      // Refresh executions if we're on the executions tab
      if (tabValue === 1) {
        // Wait a moment for the execution to start
        setTimeout(() => {
          setTabValue(1); // This will trigger a re-render
        }, 1000);
      }
      
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

  // Handle workflow deletion
  const handleDeleteWorkflow = async (workflow: any) => {
    try {
      setLoading(true);
      
      await apiClient.delete(`/workflows/flows/${workflow.namespace}/${workflow.id}`);
      
      setNotification({
        open: true,
        message: `Workflow ${workflow.id} deleted successfully`,
        severity: 'success'
      });
      
      // If the deleted workflow was selected, clear the selection
      if (selectedWorkflow && selectedWorkflow.id === workflow.id) {
        setSelectedWorkflow(null);
      }
      
      // Refresh the workflow list
      setTabValue(0); // This will trigger a re-render
      
      setLoading(false);
    } catch (err) {
      console.error('Error deleting workflow:', err);
      
      setNotification({
        open: true,
        message: `Failed to delete workflow ${workflow.id}`,
        severity: 'error'
      });
      
      setLoading(false);
    }
  };

  // Handle view executions
  const handleViewExecutions = (workflow: any) => {
    setSelectedWorkflow(workflow);
    setTabValue(1); // Switch to executions tab
  };

  // Close notification
  const handleCloseNotification = () => {
    setNotification({
      ...notification,
      open: false
    });
  };

  // Create a new workflow
  const handleCreateWorkflow = () => {
    router.push('/workflows/create');
  };

  // Handle back button from executions
  const handleBackFromExecutions = () => {
    setSelectedWorkflow(null);
    setTabValue(0); // Switch to workflows tab
  };

  if (loading && !kestraStatus) {
    return (
      <Layout title="Workflows">
        <Container maxWidth={false} sx={{ mt: 4, mb: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
          <CircularProgress />
        </Container>
      </Layout>
    );
  }

  if (error || (kestraStatus && !kestraStatus.configured)) {
    return (
      <Layout title="Workflows">
        <Container maxWidth={false} sx={{ mt: 4, mb: 4 }}>
          <Alert severity="error" sx={{ mb: 3 }}>
            {error || 'Kestra workflow engine is not configured. Please check your server configuration.'}
          </Alert>
          
          <Button variant="contained" onClick={checkKestraStatus}>
            Retry Connection
          </Button>
        </Container>
      </Layout>
    );
  }

  return (
    <Layout title="Workflows">
      <Container maxWidth={false} sx={{ mt: 4, mb: 4, height: 'calc(100vh - 128px)' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">
            Workflows
          </Typography>
          
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateWorkflow}
          >
            Create Workflow
          </Button>
        </Box>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="Workflows" id="workflow-tab-0" aria-controls="workflow-tabpanel-0" />
            <Tab 
              label="Executions" 
              id="workflow-tab-1" 
              aria-controls="workflow-tabpanel-1"
              disabled={tabValue !== 1 && !selectedWorkflow}
            />
          </Tabs>
        </Box>
        
        <Box sx={{ height: 'calc(100% - 100px)' }}>
          <TabPanel value={tabValue} index={0}>
            <WorkflowList
              onSelectWorkflow={handleSelectWorkflow}
              onEditWorkflow={handleEditWorkflow}
              onExecuteWorkflow={handleExecuteWorkflow}
              onDeleteWorkflow={handleDeleteWorkflow}
              onViewExecutions={handleViewExecutions}
            />
          </TabPanel>
          
          <TabPanel value={tabValue} index={1}>
            <WorkflowExecutions
              workflow={selectedWorkflow}
              onBack={handleBackFromExecutions}
            />
          </TabPanel>
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

export default WorkflowsPage;
