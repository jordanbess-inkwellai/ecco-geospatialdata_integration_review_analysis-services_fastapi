import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Grid,
  Alert,
  CircularProgress,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import RefreshIcon from '@mui/icons-material/Refresh';
import { apiClient } from '../../lib/api';

const RcloneConfig: React.FC = () => {
  const [remotes, setRemotes] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState<boolean>(false);
  const [newRemoteName, setNewRemoteName] = useState<string>('');
  const [newRemoteType, setNewRemoteType] = useState<string>('');
  const [newRemoteParams, setNewRemoteParams] = useState<string>('{}');
  const [dialogLoading, setDialogLoading] = useState<boolean>(false);

  // Load remotes on component mount
  useEffect(() => {
    fetchRemotes();
  }, []);

  const fetchRemotes = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get('/api/v1/rclone/remotes');
      setRemotes(response.data.remotes || []);
    } catch (err) {
      console.error('Error fetching remotes:', err);
      setError('Failed to load remotes. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddRemote = async () => {
    setDialogLoading(true);
    setError(null);
    
    try {
      // Validate JSON
      JSON.parse(newRemoteParams);
      
      const formData = new FormData();
      formData.append('name', newRemoteName);
      formData.append('remote_type', newRemoteType);
      formData.append('params', newRemoteParams);
      
      await apiClient.post('/api/v1/rclone/remotes', formData);
      
      setSuccess(`Remote "${newRemoteName}" added successfully`);
      setOpenDialog(false);
      resetForm();
      fetchRemotes();
    } catch (err) {
      console.error('Error adding remote:', err);
      if (err instanceof SyntaxError) {
        setError('Invalid JSON in parameters');
      } else {
        setError('Failed to add remote. Please check your inputs and try again.');
      }
    } finally {
      setDialogLoading(false);
    }
  };

  const handleRemoveRemote = async (name: string) => {
    if (!confirm(`Are you sure you want to remove the remote "${name}"?`)) {
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      await apiClient.delete(`/api/v1/rclone/remotes/${name}`);
      setSuccess(`Remote "${name}" removed successfully`);
      fetchRemotes();
    } catch (err) {
      console.error('Error removing remote:', err);
      setError('Failed to remove remote. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setNewRemoteName('');
    setNewRemoteType('');
    setNewRemoteParams('{}');
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    resetForm();
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Rclone Configuration
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Configured Remotes</Typography>
          <Box>
            <Button 
              startIcon={<RefreshIcon />} 
              onClick={fetchRemotes}
              disabled={loading}
              sx={{ mr: 1 }}
            >
              Refresh
            </Button>
            <Button 
              variant="contained" 
              startIcon={<AddIcon />} 
              onClick={() => setOpenDialog(true)}
              disabled={loading}
            >
              Add Remote
            </Button>
          </Box>
        </Box>
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : remotes.length === 0 ? (
          <Typography variant="body1" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
            No remotes configured. Click "Add Remote" to create one.
          </Typography>
        ) : (
          <List>
            {remotes.map((remote) => (
              <ListItem key={remote} divider>
                <ListItemText 
                  primary={remote} 
                  secondary={`Type: ${remote.includes(':') ? remote.split(':')[0] : 'Unknown'}`} 
                />
                <ListItemSecondaryAction>
                  <IconButton 
                    edge="end" 
                    aria-label="delete" 
                    onClick={() => handleRemoveRemote(remote)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        )}
      </Paper>
      
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>Add New Remote</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Remote Name"
                value={newRemoteName}
                onChange={(e) => setNewRemoteName(e.target.value)}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>Remote Type</InputLabel>
                <Select
                  value={newRemoteType}
                  onChange={(e) => setNewRemoteType(e.target.value)}
                  label="Remote Type"
                >
                  <MenuItem value="s3">Amazon S3</MenuItem>
                  <MenuItem value="azureblob">Azure Blob Storage</MenuItem>
                  <MenuItem value="box">Box</MenuItem>
                  <MenuItem value="drive">Google Drive</MenuItem>
                  <MenuItem value="dropbox">Dropbox</MenuItem>
                  <MenuItem value="onedrive">OneDrive</MenuItem>
                  <MenuItem value="sftp">SFTP</MenuItem>
                  <MenuItem value="webdav">WebDAV</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Parameters (JSON)"
                value={newRemoteParams}
                onChange={(e) => setNewRemoteParams(e.target.value)}
                fullWidth
                multiline
                rows={10}
                required
                helperText="Enter parameters as JSON object"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={dialogLoading}>
            Cancel
          </Button>
          <Button 
            onClick={handleAddRemote} 
            variant="contained" 
            disabled={!newRemoteName || !newRemoteType || dialogLoading}
            startIcon={dialogLoading ? <CircularProgress size={20} /> : null}
          >
            {dialogLoading ? 'Adding...' : 'Add Remote'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RcloneConfig;
