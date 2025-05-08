import React, { useState, useRef } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  TextField,
  CircularProgress,
  Alert,
  Divider,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Chip
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import FolderIcon from '@mui/icons-material/Folder';
import CodeIcon from '@mui/icons-material/Code';
import TerminalIcon from '@mui/icons-material/Terminal';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import DeleteIcon from '@mui/icons-material/Delete';
import { apiClient } from '../../lib/api';

interface ScriptToWorkflowProps {
  onWorkflowCreated?: (workflow: any) => void;
}

const ScriptToWorkflow: React.FC<ScriptToWorkflowProps> = ({
  onWorkflowCreated
}) => {
  const [tabValue, setTabValue] = useState(0);
  const [directoryPath, setDirectoryPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [createdWorkflows, setCreatedWorkflows] = useState<any[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState<{ [key: string]: number }>({});
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [workflowToDelete, setWorkflowToDelete] = useState<any | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Handle directory path change
  const handleDirectoryPathChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setDirectoryPath(event.target.value);
  };

  // Handle file selection
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      const files = Array.from(event.target.files);
      setSelectedFiles(files);
    }
  };

  // Trigger file input click
  const handleBrowseClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Create workflows from directory
  const handleCreateFromDirectory = async () => {
    if (!directoryPath) {
      setError('Please enter a directory path');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await apiClient.post('/workflows/flows/from-directory', {
        directory_path: directoryPath
      });
      
      setCreatedWorkflows(response.data || []);
      setSuccess(`Successfully created ${response.data.length} workflow(s)`);
      setLoading(false);
    } catch (err) {
      console.error('Error creating workflows from directory:', err);
      setError('Failed to create workflows from directory');
      setLoading(false);
    }
  };

  // Upload scripts and create workflows
  const handleUploadScripts = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one script file');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    setCreatedWorkflows([]);
    
    const newWorkflows = [];
    const newUploadProgress = { ...uploadProgress };
    
    for (const file of selectedFiles) {
      try {
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        
        // Upload the file and create a workflow
        const response = await apiClient.post('/workflows/flows/upload-script', formData, {
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            newUploadProgress[file.name] = percentCompleted;
            setUploadProgress({ ...newUploadProgress });
          }
        });
        
        newWorkflows.push(response.data);
        
        // Call the callback if provided
        if (onWorkflowCreated) {
          onWorkflowCreated(response.data);
        }
      } catch (err) {
        console.error(`Error uploading script ${file.name}:`, err);
        setError(`Failed to upload script ${file.name}`);
      }
    }
    
    setCreatedWorkflows(newWorkflows);
    setSuccess(`Successfully created ${newWorkflows.length} workflow(s)`);
    setLoading(false);
  };

  // Handle workflow deletion
  const handleDeleteClick = (workflow: any) => {
    setWorkflowToDelete(workflow);
    setDeleteDialogOpen(true);
  };

  // Confirm workflow deletion
  const handleConfirmDelete = async () => {
    if (!workflowToDelete) {
      setDeleteDialogOpen(false);
      return;
    }
    
    setLoading(true);
    
    try {
      await apiClient.delete(`/workflows/flows/${workflowToDelete.namespace}/${workflowToDelete.id}`);
      
      // Remove the workflow from the list
      setCreatedWorkflows(createdWorkflows.filter(w => w.id !== workflowToDelete.id));
      
      setSuccess(`Successfully deleted workflow ${workflowToDelete.id}`);
    } catch (err) {
      console.error('Error deleting workflow:', err);
      setError(`Failed to delete workflow ${workflowToDelete.id}`);
    }
    
    setDeleteDialogOpen(false);
    setWorkflowToDelete(null);
    setLoading(false);
  };

  // Get icon for script type
  const getScriptIcon = (fileName: string) => {
    if (fileName.endsWith('.py')) {
      return <CodeIcon />;
    } else if (fileName.endsWith('.sh') || fileName.endsWith('.bash') || fileName.endsWith('.ps1')) {
      return <TerminalIcon />;
    } else {
      return <FolderIcon />;
    }
  };

  return (
    <Paper elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box p={2} borderBottom={1} borderColor="divider">
        <Typography variant="h6" gutterBottom>
          Convert Scripts to Workflows
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Convert Python and shell scripts into Kestra workflows automatically.
        </Typography>
      </Box>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Upload Scripts" />
          <Tab label="From Directory" />
        </Tabs>
      </Box>
      
      <Box p={2} sx={{ flexGrow: 1, overflow: 'auto' }}>
        {tabValue === 0 && (
          <Box>
            <Box
              sx={{
                border: '2px dashed #ccc',
                borderRadius: 2,
                p: 3,
                textAlign: 'center',
                mb: 2
              }}
            >
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                onChange={handleFileSelect}
                multiple
                accept=".py,.sh,.bash,.ps1"
              />
              <Button
                variant="outlined"
                startIcon={<UploadFileIcon />}
                onClick={handleBrowseClick}
                sx={{ mb: 2 }}
              >
                Browse Files
              </Button>
              <Typography variant="body2" color="text.secondary">
                Supported file types: .py, .sh, .bash, .ps1
              </Typography>
            </Box>
            
            {selectedFiles.length > 0 && (
              <Box mb={2}>
                <Typography variant="subtitle1" gutterBottom>
                  Selected Files ({selectedFiles.length})
                </Typography>
                <List dense>
                  {selectedFiles.map((file, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        {getScriptIcon(file.name)}
                      </ListItemIcon>
                      <ListItemText
                        primary={file.name}
                        secondary={`${(file.size / 1024).toFixed(2)} KB`}
                      />
                      {uploadProgress[file.name] && (
                        <Chip
                          label={`${uploadProgress[file.name]}%`}
                          color={uploadProgress[file.name] === 100 ? 'success' : 'primary'}
                          size="small"
                          sx={{ mr: 1 }}
                        />
                      )}
                    </ListItem>
                  ))}
                </List>
                
                <Button
                  variant="contained"
                  onClick={handleUploadScripts}
                  disabled={loading}
                  sx={{ mt: 2 }}
                >
                  {loading ? <CircularProgress size={24} /> : 'Convert to Workflows'}
                </Button>
              </Box>
            )}
          </Box>
        )}
        
        {tabValue === 1 && (
          <Box>
            <TextField
              label="Directory Path"
              value={directoryPath}
              onChange={handleDirectoryPathChange}
              fullWidth
              margin="normal"
              placeholder="/path/to/scripts"
              helperText="Enter the path to a directory containing Python and shell scripts"
            />
            
            <Button
              variant="contained"
              onClick={handleCreateFromDirectory}
              disabled={loading || !directoryPath}
              sx={{ mt: 2 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Convert to Workflows'}
            </Button>
          </Box>
        )}
        
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ mt: 2 }}>
            {success}
          </Alert>
        )}
        
        {createdWorkflows.length > 0 && (
          <Box mt={3}>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Created Workflows
            </Typography>
            <List>
              {createdWorkflows.map((workflow, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary={workflow.id}
                    secondary={`Namespace: ${workflow.namespace}`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton edge="end" onClick={() => handleDeleteClick(workflow)}>
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </Box>
      
      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete Workflow</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the workflow "{workflowToDelete?.id}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleConfirmDelete} color="error">Delete</Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default ScriptToWorkflow;
