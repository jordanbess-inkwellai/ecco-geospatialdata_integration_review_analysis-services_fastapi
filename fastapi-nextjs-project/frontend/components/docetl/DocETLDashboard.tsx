import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  IconButton,
  Divider,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Badge
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import RefreshIcon from '@mui/icons-material/Refresh';
import SettingsIcon from '@mui/icons-material/Settings';
import InfoIcon from '@mui/icons-material/Info';
import DescriptionIcon from '@mui/icons-material/Description';
import ExtensionIcon from '@mui/icons-material/Extension';
import TransformIcon from '@mui/icons-material/Transform';
import SaveIcon from '@mui/icons-material/Save';
import { apiClient } from '../../lib/api';
import dynamic from 'next/dynamic';

// Dynamically import the Monaco Editor to avoid SSR issues
const MonacoEditor = dynamic(
  () => import('@monaco-editor/react'),
  { ssr: false }
);

interface DocETLDashboardProps {
  onError?: (error: string) => void;
}

const DocETLDashboard: React.FC<DocETLDashboardProps> = ({
  onError
}) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState<number>(0);
  const [pipelines, setPipelines] = useState<any[]>([]);
  const [selectedPipeline, setSelectedPipeline] = useState<any>(null);
  const [pipelineRuns, setPipelineRuns] = useState<any[]>([]);
  const [extractors, setExtractors] = useState<any[]>([]);
  const [transformers, setTransformers] = useState<any[]>([]);
  const [loaders, setLoaders] = useState<any[]>([]);
  const [createDialogOpen, setCreateDialogOpen] = useState<boolean>(false);
  const [editDialogOpen, setEditDialogOpen] = useState<boolean>(false);
  const [runDialogOpen, setRunDialogOpen] = useState<boolean>(false);
  const [runParameters, setRunParameters] = useState<string>('{}');
  const [newPipelineConfig, setNewPipelineConfig] = useState<string>('{\n  "name": "",\n  "description": "",\n  "extractor": {\n    "type": "",\n    "config": {}\n  },\n  "transformers": [],\n  "loader": {\n    "type": "",\n    "config": {}\n  }\n}');
  const [editPipelineConfig, setEditPipelineConfig] = useState<string>('{}');
  const [logsDialogOpen, setLogsDialogOpen] = useState<boolean>(false);
  const [selectedRun, setSelectedRun] = useState<any>(null);
  const [runLogs, setRunLogs] = useState<any[]>([]);
  
  // Load data on component mount
  useEffect(() => {
    loadData();
  }, []);
  
  // Load all data from the API
  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Get DocETL status
      const statusResponse = await apiClient.get('/docetl/status');
      
      if (statusResponse.data.status !== 'ok') {
        setError(statusResponse.data.message || 'DocETL service is not available');
        setLoading(false);
        if (onError) {
          onError(statusResponse.data.message || 'DocETL service is not available');
        }
        return;
      }
      
      // Get pipelines
      const pipelinesResponse = await apiClient.get('/docetl/pipelines');
      setPipelines(pipelinesResponse.data || []);
      
      // Get extractors
      const extractorsResponse = await apiClient.get('/docetl/extractors');
      setExtractors(extractorsResponse.data || []);
      
      // Get transformers
      const transformersResponse = await apiClient.get('/docetl/transformers');
      setTransformers(transformersResponse.data || []);
      
      // Get loaders
      const loadersResponse = await apiClient.get('/docetl/loaders');
      setLoaders(loadersResponse.data || []);
      
      setLoading(false);
    } catch (err) {
      console.error('Error loading data:', err);
      setError('Failed to load data from DocETL service');
      setLoading(false);
      if (onError) {
        onError('Failed to load data from DocETL service');
      }
    }
  };
  
  // Load pipeline runs
  const loadPipelineRuns = async (pipelineId: string) => {
    try {
      const response = await apiClient.get(`/docetl/pipelines/${pipelineId}/runs`);
      setPipelineRuns(response.data || []);
    } catch (err) {
      console.error(`Error loading runs for pipeline ${pipelineId}:`, err);
      setError(`Failed to load runs for pipeline ${pipelineId}`);
    }
  };
  
  // Load run logs
  const loadRunLogs = async (pipelineId: string, runId: string) => {
    try {
      const response = await apiClient.get(`/docetl/pipelines/${pipelineId}/runs/${runId}/logs`);
      setRunLogs(response.data || []);
    } catch (err) {
      console.error(`Error loading logs for run ${runId}:`, err);
      setError(`Failed to load logs for run ${runId}`);
    }
  };
  
  // Handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  
  // Handle pipeline selection
  const handlePipelineSelect = async (pipeline: any) => {
    setSelectedPipeline(pipeline);
    await loadPipelineRuns(pipeline.id);
  };
  
  // Handle create dialog open
  const handleCreateDialogOpen = () => {
    setCreateDialogOpen(true);
  };
  
  // Handle create dialog close
  const handleCreateDialogClose = () => {
    setCreateDialogOpen(false);
  };
  
  // Handle edit dialog open
  const handleEditDialogOpen = (pipeline: any) => {
    setSelectedPipeline(pipeline);
    setEditPipelineConfig(JSON.stringify(pipeline, null, 2));
    setEditDialogOpen(true);
  };
  
  // Handle edit dialog close
  const handleEditDialogClose = () => {
    setEditDialogOpen(false);
  };
  
  // Handle run dialog open
  const handleRunDialogOpen = (pipeline: any) => {
    setSelectedPipeline(pipeline);
    setRunParameters('{}');
    setRunDialogOpen(true);
  };
  
  // Handle run dialog close
  const handleRunDialogClose = () => {
    setRunDialogOpen(false);
  };
  
  // Handle logs dialog open
  const handleLogsDialogOpen = async (pipeline: any, run: any) => {
    setSelectedPipeline(pipeline);
    setSelectedRun(run);
    await loadRunLogs(pipeline.id, run.id);
    setLogsDialogOpen(true);
  };
  
  // Handle logs dialog close
  const handleLogsDialogClose = () => {
    setLogsDialogOpen(false);
  };
  
  // Handle create pipeline
  const handleCreatePipeline = async () => {
    try {
      setLoading(true);
      
      // Parse the pipeline configuration
      const pipelineConfig = JSON.parse(newPipelineConfig);
      
      // Create the pipeline
      const response = await apiClient.post('/docetl/pipelines', pipelineConfig);
      
      // Reload pipelines
      await loadData();
      
      setCreateDialogOpen(false);
      setLoading(false);
    } catch (err) {
      console.error('Error creating pipeline:', err);
      setError('Failed to create pipeline');
      setLoading(false);
    }
  };
  
  // Handle edit pipeline
  const handleEditPipeline = async () => {
    if (!selectedPipeline) {
      return;
    }
    
    try {
      setLoading(true);
      
      // Parse the pipeline configuration
      const pipelineConfig = JSON.parse(editPipelineConfig);
      
      // Update the pipeline
      const response = await apiClient.put(`/docetl/pipelines/${selectedPipeline.id}`, pipelineConfig);
      
      // Reload pipelines
      await loadData();
      
      setEditDialogOpen(false);
      setLoading(false);
    } catch (err) {
      console.error('Error updating pipeline:', err);
      setError('Failed to update pipeline');
      setLoading(false);
    }
  };
  
  // Handle delete pipeline
  const handleDeletePipeline = async (pipeline: any) => {
    if (!confirm(`Are you sure you want to delete pipeline "${pipeline.name}"?`)) {
      return;
    }
    
    try {
      setLoading(true);
      
      // Delete the pipeline
      const response = await apiClient.delete(`/docetl/pipelines/${pipeline.id}`);
      
      // Reload pipelines
      await loadData();
      
      if (selectedPipeline && selectedPipeline.id === pipeline.id) {
        setSelectedPipeline(null);
        setPipelineRuns([]);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error deleting pipeline:', err);
      setError('Failed to delete pipeline');
      setLoading(false);
    }
  };
  
  // Handle run pipeline
  const handleRunPipeline = async () => {
    if (!selectedPipeline) {
      return;
    }
    
    try {
      setLoading(true);
      
      // Parse the run parameters
      const parameters = JSON.parse(runParameters);
      
      // Run the pipeline
      const response = await apiClient.post(`/docetl/pipelines/${selectedPipeline.id}/run`, parameters);
      
      // Reload pipeline runs
      await loadPipelineRuns(selectedPipeline.id);
      
      setRunDialogOpen(false);
      setLoading(false);
    } catch (err) {
      console.error('Error running pipeline:', err);
      setError('Failed to run pipeline');
      setLoading(false);
    }
  };
  
  // Render the dashboard content based on the selected tab
  const renderDashboardContent = () => {
    switch (tabValue) {
      case 0: // Pipelines
        return (
          <Box>
            <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">Pipelines</Typography>
              <Box>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleCreateDialogOpen}
                  sx={{ mr: 1 }}
                >
                  Create Pipeline
                </Button>
                <IconButton onClick={loadData}>
                  <RefreshIcon />
                </IconButton>
              </Box>
            </Box>
            
            <Grid container spacing={2} sx={{ p: 1 }}>
              {pipelines.map((pipeline) => (
                <Grid item xs={12} sm={6} md={4} key={pipeline.id}>
                  <Card
                    sx={{
                      cursor: 'pointer',
                      bgcolor: selectedPipeline && selectedPipeline.id === pipeline.id ? 'primary.light' : 'background.paper'
                    }}
                    onClick={() => handlePipelineSelect(pipeline)}
                  >
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {pipeline.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" noWrap>
                        {pipeline.description || 'No description'}
                      </Typography>
                      <Box sx={{ mt: 1 }}>
                        <Chip
                          label={`Extractor: ${pipeline.extractor.type}`}
                          size="small"
                          icon={<ExtensionIcon />}
                          sx={{ mr: 0.5, mb: 0.5 }}
                        />
                        {pipeline.transformers && pipeline.transformers.length > 0 && (
                          <Chip
                            label={`Transformers: ${pipeline.transformers.length}`}
                            size="small"
                            icon={<TransformIcon />}
                            sx={{ mr: 0.5, mb: 0.5 }}
                          />
                        )}
                        <Chip
                          label={`Loader: ${pipeline.loader.type}`}
                          size="small"
                          icon={<SaveIcon />}
                          sx={{ mr: 0.5, mb: 0.5 }}
                        />
                      </Box>
                    </CardContent>
                    <CardActions>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRunDialogOpen(pipeline);
                        }}
                      >
                        <PlayArrowIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEditDialogOpen(pipeline);
                        }}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeletePipeline(pipeline);
                        }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
              
              {pipelines.length === 0 && (
                <Grid item xs={12}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="body1" color="text.secondary">
                      No pipelines available
                    </Typography>
                    <Button
                      variant="contained"
                      startIcon={<AddIcon />}
                      onClick={handleCreateDialogOpen}
                      sx={{ mt: 2 }}
                    >
                      Create Pipeline
                    </Button>
                  </Paper>
                </Grid>
              )}
            </Grid>
          </Box>
        );
      
      case 1: // Runs
        return (
          <Box>
            <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">
                {selectedPipeline ? `Runs for ${selectedPipeline.name}` : 'Pipeline Runs'}
              </Typography>
              <Box>
                {selectedPipeline && (
                  <Button
                    variant="contained"
                    startIcon={<PlayArrowIcon />}
                    onClick={() => handleRunDialogOpen(selectedPipeline)}
                    sx={{ mr: 1 }}
                  >
                    Run Pipeline
                  </Button>
                )}
                <IconButton
                  onClick={() => selectedPipeline && loadPipelineRuns(selectedPipeline.id)}
                  disabled={!selectedPipeline}
                >
                  <RefreshIcon />
                </IconButton>
              </Box>
            </Box>
            
            {!selectedPipeline ? (
              <Paper sx={{ p: 2, m: 1, textAlign: 'center' }}>
                <Typography variant="body1" color="text.secondary">
                  Select a pipeline to view its runs
                </Typography>
              </Paper>
            ) : pipelineRuns.length === 0 ? (
              <Paper sx={{ p: 2, m: 1, textAlign: 'center' }}>
                <Typography variant="body1" color="text.secondary">
                  No runs available for this pipeline
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<PlayArrowIcon />}
                  onClick={() => handleRunDialogOpen(selectedPipeline)}
                  sx={{ mt: 2 }}
                >
                  Run Pipeline
                </Button>
              </Paper>
            ) : (
              <List>
                {pipelineRuns.map((run) => (
                  <ListItem
                    key={run.id}
                    button
                    onClick={() => handleLogsDialogOpen(selectedPipeline, run)}
                  >
                    <ListItemIcon>
                      <Badge
                        color={run.status === 'success' ? 'success' : run.status === 'failed' ? 'error' : 'warning'}
                        variant="dot"
                      >
                        <DescriptionIcon />
                      </Badge>
                    </ListItemIcon>
                    <ListItemText
                      primary={`Run ID: ${run.id}`}
                      secondary={`Status: ${run.status} • Started: ${new Date(run.start_time).toLocaleString()} • Duration: ${run.duration || 'N/A'}`}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Box>
        );
      
      case 2: // Components
        return (
          <Box>
            <Tabs value={tabValue === 2 ? 0 : tabValue === 3 ? 1 : 2} onChange={(e, v) => setTabValue(v + 2)}>
              <Tab label="Extractors" />
              <Tab label="Transformers" />
              <Tab label="Loaders" />
            </Tabs>
            
            <Box sx={{ p: 1 }}>
              {tabValue === 2 && (
                <>
                  <Typography variant="h6" gutterBottom>
                    Available Extractors
                  </Typography>
                  <List>
                    {extractors.map((extractor) => (
                      <ListItem key={extractor.type}>
                        <ListItemIcon>
                          <ExtensionIcon />
                        </ListItemIcon>
                        <ListItemText
                          primary={extractor.type}
                          secondary={extractor.description || 'No description'}
                        />
                      </ListItem>
                    ))}
                    {extractors.length === 0 && (
                      <ListItem>
                        <ListItemText secondary="No extractors available" />
                      </ListItem>
                    )}
                  </List>
                </>
              )}
              
              {tabValue === 3 && (
                <>
                  <Typography variant="h6" gutterBottom>
                    Available Transformers
                  </Typography>
                  <List>
                    {transformers.map((transformer) => (
                      <ListItem key={transformer.type}>
                        <ListItemIcon>
                          <TransformIcon />
                        </ListItemIcon>
                        <ListItemText
                          primary={transformer.type}
                          secondary={transformer.description || 'No description'}
                        />
                      </ListItem>
                    ))}
                    {transformers.length === 0 && (
                      <ListItem>
                        <ListItemText secondary="No transformers available" />
                      </ListItem>
                    )}
                  </List>
                </>
              )}
              
              {tabValue === 4 && (
                <>
                  <Typography variant="h6" gutterBottom>
                    Available Loaders
                  </Typography>
                  <List>
                    {loaders.map((loader) => (
                      <ListItem key={loader.type}>
                        <ListItemIcon>
                          <SaveIcon />
                        </ListItemIcon>
                        <ListItemText
                          primary={loader.type}
                          secondary={loader.description || 'No description'}
                        />
                      </ListItem>
                    ))}
                    {loaders.length === 0 && (
                      <ListItem>
                        <ListItemText secondary="No loaders available" />
                      </ListItem>
                    )}
                  </List>
                </>
              )}
            </Box>
          </Box>
        );
      
      default:
        return null;
    }
  };
  
  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Pipelines" />
          <Tab label="Runs" />
          <Tab label="Components" />
        </Tabs>
      </Box>
      
      {/* Content */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Box sx={{ p: 2 }}>
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
            <Button variant="contained" onClick={loadData}>
              Retry
            </Button>
          </Box>
        ) : (
          renderDashboardContent()
        )}
      </Box>
      
      {/* Create Pipeline Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={handleCreateDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create Pipeline</DialogTitle>
        <DialogContent>
          <Box sx={{ height: 400, mt: 2 }}>
            <MonacoEditor
              height="100%"
              language="json"
              theme="vs-dark"
              value={newPipelineConfig}
              onChange={(value) => setNewPipelineConfig(value || '')}
              options={{
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                automaticLayout: true
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCreateDialogClose}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreatePipeline}
            disabled={loading}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Edit Pipeline Dialog */}
      <Dialog
        open={editDialogOpen}
        onClose={handleEditDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Edit Pipeline</DialogTitle>
        <DialogContent>
          <Box sx={{ height: 400, mt: 2 }}>
            <MonacoEditor
              height="100%"
              language="json"
              theme="vs-dark"
              value={editPipelineConfig}
              onChange={(value) => setEditPipelineConfig(value || '')}
              options={{
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                automaticLayout: true
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleEditDialogClose}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleEditPipeline}
            disabled={loading}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Run Pipeline Dialog */}
      <Dialog
        open={runDialogOpen}
        onClose={handleRunDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Run Pipeline</DialogTitle>
        <DialogContent>
          <Typography variant="subtitle1" gutterBottom>
            {selectedPipeline?.name}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {selectedPipeline?.description || 'No description'}
          </Typography>
          
          <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
            Parameters (JSON)
          </Typography>
          
          <Box sx={{ height: 300 }}>
            <MonacoEditor
              height="100%"
              language="json"
              theme="vs-dark"
              value={runParameters}
              onChange={(value) => setRunParameters(value || '')}
              options={{
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                automaticLayout: true
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleRunDialogClose}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleRunPipeline}
            disabled={loading}
            startIcon={<PlayArrowIcon />}
          >
            Run
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Logs Dialog */}
      <Dialog
        open={logsDialogOpen}
        onClose={handleLogsDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Run Logs</DialogTitle>
        <DialogContent>
          <Typography variant="subtitle1" gutterBottom>
            {selectedPipeline?.name} - Run ID: {selectedRun?.id}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Status: {selectedRun?.status} • Started: {selectedRun && new Date(selectedRun.start_time).toLocaleString()} • Duration: {selectedRun?.duration || 'N/A'}
          </Typography>
          
          <Paper
            sx={{
              mt: 2,
              p: 1,
              height: 400,
              overflow: 'auto',
              bgcolor: 'background.default',
              fontFamily: 'monospace',
              fontSize: '0.875rem'
            }}
          >
            {runLogs.length === 0 ? (
              <Typography variant="body2" color="text.secondary" sx={{ p: 1 }}>
                No logs available
              </Typography>
            ) : (
              runLogs.map((log, index) => (
                <Box
                  key={index}
                  sx={{
                    p: 0.5,
                    borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
                    color: log.level === 'ERROR' ? 'error.main' : log.level === 'WARNING' ? 'warning.main' : 'text.primary'
                  }}
                >
                  <Typography variant="body2" component="span" sx={{ mr: 1, color: 'text.secondary' }}>
                    [{new Date(log.timestamp).toLocaleTimeString()}]
                  </Typography>
                  <Typography variant="body2" component="span" sx={{ mr: 1, fontWeight: 'bold' }}>
                    [{log.level}]
                  </Typography>
                  <Typography variant="body2" component="span">
                    {log.message}
                  </Typography>
                </Box>
              ))
            )}
          </Paper>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleLogsDialogClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DocETLDashboard;
