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
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Chip,
  Tooltip
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import SearchIcon from '@mui/icons-material/Search';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import HistoryIcon from '@mui/icons-material/History';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { apiClient } from '../../lib/api';
import { formatDate } from '../../utils/formatters';

interface WorkflowListProps {
  onSelectWorkflow?: (workflow: any) => void;
  onEditWorkflow?: (workflow: any) => void;
  onExecuteWorkflow?: (workflow: any) => void;
  onDeleteWorkflow?: (workflow: any) => void;
  onViewExecutions?: (workflow: any) => void;
}

const WorkflowList: React.FC<WorkflowListProps> = ({
  onSelectWorkflow,
  onEditWorkflow,
  onExecuteWorkflow,
  onDeleteWorkflow,
  onViewExecutions
}) => {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [filteredWorkflows, setFilteredWorkflows] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedWorkflow, setSelectedWorkflow] = useState<any | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState<boolean>(false);
  const [namespaces, setNamespaces] = useState<string[]>(['default']);
  const [selectedNamespace, setSelectedNamespace] = useState<string>('default');

  // Load workflows on component mount and when namespace changes
  useEffect(() => {
    fetchWorkflows();
  }, [selectedNamespace]);

  // Filter workflows when search query changes
  useEffect(() => {
    if (searchQuery) {
      const filtered = workflows.filter((workflow) => 
        workflow.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (workflow.description && workflow.description.toLowerCase().includes(searchQuery.toLowerCase()))
      );
      setFilteredWorkflows(filtered);
    } else {
      setFilteredWorkflows(workflows);
    }
  }, [searchQuery, workflows]);

  // Fetch workflows from the API
  const fetchWorkflows = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch namespaces if we haven't already
      if (namespaces.length === 1 && namespaces[0] === 'default') {
        try {
          const namespacesResponse = await apiClient.get('/workflows/namespaces');
          if (namespacesResponse.data && namespacesResponse.data.length > 0) {
            setNamespaces(namespacesResponse.data);
          }
        } catch (err) {
          console.error('Error fetching namespaces:', err);
          // Continue with default namespace
        }
      }
      
      // Fetch workflows for the selected namespace
      const response = await apiClient.get(`/workflows/flows?namespace=${selectedNamespace}`);
      setWorkflows(response.data || []);
      setFilteredWorkflows(response.data || []);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching workflows:', err);
      setError('Failed to fetch workflows');
      setWorkflows([]);
      setFilteredWorkflows([]);
      setLoading(false);
    }
  };

  // Handle workflow selection
  const handleSelectWorkflow = (workflow: any) => {
    if (onSelectWorkflow) {
      onSelectWorkflow(workflow);
    }
  };

  // Handle workflow menu open
  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, workflow: any) => {
    event.stopPropagation();
    setMenuAnchorEl(event.currentTarget);
    setSelectedWorkflow(workflow);
  };

  // Handle workflow menu close
  const handleMenuClose = () => {
    setMenuAnchorEl(null);
  };

  // Handle workflow edit
  const handleEditWorkflow = () => {
    handleMenuClose();
    if (onEditWorkflow && selectedWorkflow) {
      onEditWorkflow(selectedWorkflow);
    }
  };

  // Handle workflow execution
  const handleExecuteWorkflow = () => {
    handleMenuClose();
    if (onExecuteWorkflow && selectedWorkflow) {
      onExecuteWorkflow(selectedWorkflow);
    }
  };

  // Handle workflow deletion
  const handleDeleteClick = () => {
    handleMenuClose();
    setDeleteDialogOpen(true);
  };

  // Confirm workflow deletion
  const handleConfirmDelete = () => {
    setDeleteDialogOpen(false);
    if (onDeleteWorkflow && selectedWorkflow) {
      onDeleteWorkflow(selectedWorkflow);
    }
  };

  // Handle view executions
  const handleViewExecutions = () => {
    handleMenuClose();
    if (onViewExecutions && selectedWorkflow) {
      onViewExecutions(selectedWorkflow);
    }
  };

  // Handle duplicate workflow
  const handleDuplicateWorkflow = async () => {
    handleMenuClose();
    if (!selectedWorkflow) return;
    
    try {
      setLoading(true);
      
      // Get the full workflow details
      const response = await apiClient.get(`/workflows/flows/${selectedWorkflow.namespace}/${selectedWorkflow.id}`);
      const workflow = response.data;
      
      // Create a duplicate with a new ID
      const duplicate = {
        ...workflow,
        id: `${workflow.id}_copy`,
        revision: 1
      };
      
      // Create the new workflow
      await apiClient.post('/workflows/flows', duplicate);
      
      // Refresh the workflow list
      fetchWorkflows();
    } catch (err) {
      console.error('Error duplicating workflow:', err);
      setError('Failed to duplicate workflow');
      setLoading(false);
    }
  };

  // Handle namespace change
  const handleNamespaceChange = (namespace: string) => {
    setSelectedNamespace(namespace);
  };

  return (
    <Paper elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box p={2} display="flex" alignItems="center" borderBottom={1} borderColor="divider">
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Workflows
        </Typography>
        
        <Button
          variant="outlined"
          size="small"
          onClick={fetchWorkflows}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>
      
      <Box p={2} display="flex" alignItems="center" borderBottom={1} borderColor="divider">
        <TextField
          placeholder="Search workflows..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          variant="outlined"
          size="small"
          fullWidth
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            )
          }}
        />
      </Box>
      
      <Box p={2} display="flex" alignItems="center" borderBottom={1} borderColor="divider">
        <Typography variant="body2" sx={{ mr: 2 }}>
          Namespace:
        </Typography>
        
        {namespaces.map((namespace) => (
          <Chip
            key={namespace}
            label={namespace}
            onClick={() => handleNamespaceChange(namespace)}
            color={namespace === selectedNamespace ? 'primary' : 'default'}
            sx={{ mr: 1 }}
          />
        ))}
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
        ) : filteredWorkflows.length === 0 ? (
          <Box display="flex" justifyContent="center" alignItems="center" height="100%" p={3}>
            <Typography variant="body1" color="text.secondary">
              {searchQuery ? 'No workflows match your search.' : 'No workflows found.'}
            </Typography>
          </Box>
        ) : (
          <List>
            {filteredWorkflows.map((workflow) => (
              <ListItem
                key={workflow.id}
                button
                onClick={() => handleSelectWorkflow(workflow)}
              >
                <ListItemIcon>
                  <PlayArrowIcon color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary={workflow.id}
                  secondary={
                    <React.Fragment>
                      {workflow.description || 'No description'}
                      <br />
                      <Typography variant="caption" color="text.secondary">
                        Revision: {workflow.revision} • Last updated: {formatDate(workflow.updatedDate || workflow.createdDate)}
                      </Typography>
                    </React.Fragment>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton edge="end" onClick={(e) => handleMenuOpen(e, workflow)}>
                    <MoreVertIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        )}
      </Box>
      
      {/* Workflow Actions Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleEditWorkflow}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Edit" />
        </MenuItem>
        <MenuItem onClick={handleExecuteWorkflow}>
          <ListItemIcon>
            <PlayArrowIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Execute" />
        </MenuItem>
        <MenuItem onClick={handleViewExecutions}>
          <ListItemIcon>
            <HistoryIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="View Executions" />
        </MenuItem>
        <MenuItem onClick={handleDuplicateWorkflow}>
          <ListItemIcon>
            <ContentCopyIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Duplicate" />
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleDeleteClick}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText primary="Delete" primaryTypographyProps={{ color: 'error' }} />
        </MenuItem>
      </Menu>
      
      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete Workflow</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the workflow "{selectedWorkflow?.id}"? This action cannot be undone.
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

export default WorkflowList;
