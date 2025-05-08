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
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import SaveIcon from '@mui/icons-material/Save';
import Layout from '../../components/layout/Layout';
import WorkflowBuilder from '../../components/workflows/WorkflowBuilder';
import ScriptToWorkflow from '../../components/workflows/ScriptToWorkflow';
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
      id={`create-workflow-tabpanel-${index}`}
      aria-labelledby={`create-workflow-tab-${index}`}
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

const CreateWorkflowPage: React.FC = () => {
  const router = useRouter();
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
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
  const [templates, setTemplates] = useState<any[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<any | null>(null);

  // Load templates on component mount
  useEffect(() => {
    fetchTemplates();
  }, []);

  // Fetch templates from the API
  const fetchTemplates = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.get('/workflows/templates');
      setTemplates(response.data || []);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching templates:', err);
      setError('Failed to fetch workflow templates');
      setLoading(false);
    }
  };

  // Handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Handle workflow save
  const handleSaveWorkflow = async (workflow: any) => {
    try {
      setLoading(true);
      
      const response = await apiClient.post('/workflows/flows', workflow);
      
      setNotification({
        open: true,
        message: `Workflow ${workflow.id} created successfully`,
        severity: 'success'
      });
      
      // Navigate to the workflows page after a short delay
      setTimeout(() => {
        router.push('/workflows');
      }, 1500);
      
      setLoading(false);
    } catch (err) {
      console.error('Error creating workflow:', err);
      
      setNotification({
        open: true,
        message: 'Failed to create workflow',
        severity: 'error'
      });
      
      setLoading(false);
    }
  };

  // Handle workflow created from script
  const handleWorkflowCreated = (workflow: any) => {
    setNotification({
      open: true,
      message: `Workflow ${workflow.id} created successfully`,
      severity: 'success'
    });
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

  return (
    <Layout title="Create Workflow">
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
              Create Workflow
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="Visual Builder" id="create-workflow-tab-0" aria-controls="create-workflow-tabpanel-0" />
            <Tab label="From Scripts" id="create-workflow-tab-1" aria-controls="create-workflow-tabpanel-1" />
          </Tabs>
        </Box>
        
        <Box sx={{ height: 'calc(100% - 100px)' }}>
          <TabPanel value={tabValue} index={0}>
            <WorkflowBuilder onSave={handleSaveWorkflow} />
          </TabPanel>
          
          <TabPanel value={tabValue} index={1}>
            <ScriptToWorkflow onWorkflowCreated={handleWorkflowCreated} />
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

export default CreateWorkflowPage;
