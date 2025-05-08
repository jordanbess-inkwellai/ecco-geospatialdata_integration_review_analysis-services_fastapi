import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Button,
  Divider,
  TextField,
  InputAdornment,
  CircularProgress,
  Alert,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import VisibilityIcon from '@mui/icons-material/Visibility';
import RefreshIcon from '@mui/icons-material/Refresh';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { apiClient } from '../../lib/api';
import { formatDate, formatDuration } from '../../utils/formatters';

interface WorkflowExecutionsProps {
  workflow?: any;
  namespace?: string;
  onBack?: () => void;
}

const WorkflowExecutions: React.FC<WorkflowExecutionsProps> = ({
  workflow,
  namespace = 'default',
  onBack
}) => {
  const [executions, setExecutions] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedExecution, setSelectedExecution] = useState<any | null>(null);
  const [executionDetailsOpen, setExecutionDetailsOpen] = useState<boolean>(false);
  const [logs, setLogs] = useState<any[]>([]);
  const [logsLoading, setLogsLoading] = useState<boolean>(false);
  const [tabValue, setTabValue] = useState<number>(0);
  const [autoRefresh, setAutoRefresh] = useState<boolean>(false);
  const [refreshInterval, setRefreshInterval] = useState<any>(null);

  // Load executions on component mount
  useEffect(() => {
    fetchExecutions();
    
    return () => {
      // Clean up refresh interval
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [workflow, namespace]);

  // Set up auto-refresh
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchExecutions(false);
      }, 5000);
      setRefreshInterval(interval);
    } else {
      if (refreshInterval) {
        clearInterval(refreshInterval);
        setRefreshInterval(null);
      }
    }
    
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [autoRefresh]);

  // Fetch executions from the API
  const fetchExecutions = async (showLoading = true) => {
    if (showLoading) {
      setLoading(true);
    }
    setError(null);
    
    try {
      const params: any = {
        namespace: namespace,
        limit: 20
      };
      
      if (workflow) {
        params.flow_id = workflow.id;
      }
      
      const response = await apiClient.get('/workflows/executions', { params });
      setExecutions(response.data || []);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching executions:', err);
      setError('Failed to fetch executions');
      setExecutions([]);
      setLoading(false);
    }
  };

  // Fetch logs for an execution
  const fetchLogs = async (executionId: string) => {
    setLogsLoading(true);
    
    try {
      const response = await apiClient.get(`/workflows/logs/${executionId}`);
      setLogs(response.data || []);
      setLogsLoading(false);
    } catch (err) {
      console.error('Error fetching logs:', err);
      setLogs([]);
      setLogsLoading(false);
    }
  };

  // Handle execution selection
  const handleSelectExecution = async (execution: any) => {
    setSelectedExecution(execution);
    setExecutionDetailsOpen(true);
    fetchLogs(execution.id);
  };

  // Handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Get status icon for execution
  const getStatusIcon = (state: string) => {
    switch (state) {
      case 'SUCCESS':
        return <CheckCircleIcon color="success" />;
      case 'FAILED':
        return <ErrorIcon color="error" />;
      case 'WARNING':
        return <WarningIcon color="warning" />;
      case 'RUNNING':
      case 'CREATED':
      case 'RESTARTED':
        return <HourglassEmptyIcon color="info" />;
      default:
        return <HourglassEmptyIcon />;
    }
  };

  // Get color for status chip
  const getStatusColor = (state: string): 'success' | 'error' | 'warning' | 'info' | 'default' => {
    switch (state) {
      case 'SUCCESS':
        return 'success';
      case 'FAILED':
        return 'error';
      case 'WARNING':
        return 'warning';
      case 'RUNNING':
      case 'CREATED':
      case 'RESTARTED':
        return 'info';
      default:
        return 'default';
    }
  };

  // Calculate execution duration
  const calculateDuration = (execution: any) => {
    if (!execution.startDate) {
      return 'Not started';
    }
    
    const start = new Date(execution.startDate).getTime();
    const end = execution.endDate ? new Date(execution.endDate).getTime() : Date.now();
    const durationMs = end - start;
    
    return formatDuration(durationMs / 1000);
  };

  return (
    <Paper elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box p={2} display="flex" alignItems="center" borderBottom={1} borderColor="divider">
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          {workflow ? `Executions: ${workflow.id}` : 'All Executions'}
        </Typography>
        
        <Box display="flex" alignItems="center">
          <Button
            variant="outlined"
            size="small"
            startIcon={<RefreshIcon />}
            onClick={() => fetchExecutions()}
            disabled={loading}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          
          <Chip
            label={autoRefresh ? 'Auto-refresh: On' : 'Auto-refresh: Off'}
            color={autoRefresh ? 'primary' : 'default'}
            onClick={() => setAutoRefresh(!autoRefresh)}
          />
          
          {onBack && (
            <Button
              variant="outlined"
              size="small"
              onClick={onBack}
              sx={{ ml: 1 }}
            >
              Back
            </Button>
          )}
        </Box>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ m: 2 }}>
          {error}
        </Alert>
      )}
      
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" height="100%">
            <CircularProgress />
          </Box>
        ) : executions.length === 0 ? (
          <Box display="flex" justifyContent="center" alignItems="center" height="100%" p={3}>
            <Typography variant="body1" color="text.secondary">
              No executions found.
            </Typography>
          </Box>
        ) : (
          <List>
            {executions.map((execution) => (
              <ListItem
                key={execution.id}
                button
                onClick={() => handleSelectExecution(execution)}
              >
                <ListItemIcon>
                  {getStatusIcon(execution.state)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center">
                      <Typography variant="body1" sx={{ mr: 1 }}>
                        {execution.flowId}
                      </Typography>
                      <Chip
                        label={execution.state}
                        size="small"
                        color={getStatusColor(execution.state)}
                      />
                    </Box>
                  }
                  secondary={
                    <React.Fragment>
                      <Typography variant="caption" display="block">
                        Execution ID: {execution.id}
                      </Typography>
                      <Typography variant="caption" display="block">
                        Started: {formatDate(execution.startDate)} • Duration: {calculateDuration(execution)}
                      </Typography>
                    </React.Fragment>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton edge="end" onClick={() => handleSelectExecution(execution)}>
                    <VisibilityIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        )}
      </Box>
      
      {/* Execution Details Dialog */}
      <Dialog
        open={executionDetailsOpen}
        onClose={() => setExecutionDetailsOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center">
            {getStatusIcon(selectedExecution?.state || '')}
            <Typography variant="h6" sx={{ ml: 1 }}>
              Execution Details
            </Typography>
            <Chip
              label={selectedExecution?.state}
              size="small"
              color={getStatusColor(selectedExecution?.state || '')}
              sx={{ ml: 1 }}
            />
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {selectedExecution && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Flow: {selectedExecution.flowId}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Execution ID: {selectedExecution.id}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Namespace: {selectedExecution.namespace}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Started: {formatDate(selectedExecution.startDate)}
              </Typography>
              {selectedExecution.endDate && (
                <Typography variant="body2" gutterBottom>
                  Ended: {formatDate(selectedExecution.endDate)}
                </Typography>
              )}
              <Typography variant="body2" gutterBottom>
                Duration: {calculateDuration(selectedExecution)}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tab label="Logs" />
                <Tab label="Inputs" />
                <Tab label="Outputs" />
              </Tabs>
              
              <Box sx={{ mt: 2 }}>
                {tabValue === 0 && (
                  <Box>
                    {logsLoading ? (
                      <Box display="flex" justifyContent="center" alignItems="center" p={3}>
                        <CircularProgress />
                      </Box>
                    ) : logs.length === 0 ? (
                      <Typography variant="body2" color="text.secondary">
                        No logs available.
                      </Typography>
                    ) : (
                      <Box sx={{ maxHeight: '400px', overflow: 'auto', bgcolor: '#f5f5f5', p: 2, borderRadius: 1 }}>
                        {logs.map((log, index) => (
                          <Box key={index} sx={{ mb: 1, fontFamily: 'monospace', fontSize: '0.875rem' }}>
                            <Typography
                              variant="body2"
                              component="span"
                              sx={{
                                color: log.level === 'ERROR' ? 'error.main' : 
                                       log.level === 'WARN' ? 'warning.main' : 
                                       log.level === 'INFO' ? 'info.main' : 'text.primary'
                              }}
                            >
                              [{formatDate(log.timestamp)}] [{log.level}] {log.taskId ? `[${log.taskId}] ` : ''}
                            </Typography>
                            <Typography variant="body2" component="span">
                              {log.message}
                            </Typography>
                          </Box>
                        ))}
                      </Box>
                    )}
                  </Box>
                )}
                
                {tabValue === 1 && (
                  <Box>
                    {selectedExecution.inputs && Object.keys(selectedExecution.inputs).length > 0 ? (
                      <Box>
                        {Object.entries(selectedExecution.inputs).map(([key, value]: [string, any]) => (
                          <Accordion key={key}>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                              <Typography>{key}</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                              <TextField
                                fullWidth
                                multiline
                                rows={4}
                                value={typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                                InputProps={{ readOnly: true }}
                                variant="outlined"
                                size="small"
                              />
                            </AccordionDetails>
                          </Accordion>
                        ))}
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No inputs available.
                      </Typography>
                    )}
                  </Box>
                )}
                
                {tabValue === 2 && (
                  <Box>
                    {selectedExecution.outputs && Object.keys(selectedExecution.outputs).length > 0 ? (
                      <Box>
                        {Object.entries(selectedExecution.outputs).map(([key, value]: [string, any]) => (
                          <Accordion key={key}>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                              <Typography>{key}</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                              <TextField
                                fullWidth
                                multiline
                                rows={4}
                                value={typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                                InputProps={{ readOnly: true }}
                                variant="outlined"
                                size="small"
                              />
                            </AccordionDetails>
                          </Accordion>
                        ))}
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No outputs available.
                      </Typography>
                    )}
                  </Box>
                )}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExecutionDetailsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default WorkflowExecutions;
