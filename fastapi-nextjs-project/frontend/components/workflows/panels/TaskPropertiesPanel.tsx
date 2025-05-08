import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormHelperText
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import CodeIcon from '@mui/icons-material/Code';
import TerminalIcon from '@mui/icons-material/Terminal';
import HttpIcon from '@mui/icons-material/Http';
import FolderIcon from '@mui/icons-material/Folder';
import StorageIcon from '@mui/icons-material/Storage';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

interface TaskPropertiesPanelProps {
  task: any;
  onChange: (task: any) => void;
  readOnly?: boolean;
}

const TaskPropertiesPanel: React.FC<TaskPropertiesPanelProps> = ({
  task,
  onChange,
  readOnly = false
}) => {
  const [codeDialogOpen, setCodeDialogOpen] = useState(false);
  const [taskCode, setTaskCode] = useState('');

  // Get the appropriate icon based on the task type
  const getTaskIcon = () => {
    switch (task.type) {
      case 'io.kestra.plugin.scripts.python.Script':
        return <CodeIcon />;
      case 'io.kestra.plugin.scripts.shell.Script':
        return <TerminalIcon />;
      case 'io.kestra.plugin.http.Request':
        return <HttpIcon />;
      case 'io.kestra.plugin.fs.http.Read':
      case 'io.kestra.plugin.fs.http.Write':
        return <FolderIcon />;
      case 'io.kestra.plugin.jdbc.Query':
        return <StorageIcon />;
      case 'io.kestra.plugin.core.flow.Trigger':
        return <PlayArrowIcon />;
      default:
        return null;
    }
  };

  // Get a short name for the task type
  const getTaskTypeName = () => {
    switch (task.type) {
      case 'io.kestra.plugin.scripts.python.Script':
        return 'Python Script';
      case 'io.kestra.plugin.scripts.shell.Script':
        return 'Shell Script';
      case 'io.kestra.plugin.http.Request':
        return 'HTTP Request';
      case 'io.kestra.plugin.fs.http.Read':
        return 'File Read';
      case 'io.kestra.plugin.fs.http.Write':
        return 'File Write';
      case 'io.kestra.plugin.jdbc.Query':
        return 'SQL Query';
      case 'io.kestra.plugin.core.flow.Trigger':
        return 'Flow Trigger';
      default:
        return 'Task';
    }
  };

  // Handle task property changes
  const handlePropertyChange = (property: string, value: any) => {
    onChange({ ...task, [property]: value });
  };

  // Show the task code
  const showTaskCode = () => {
    setTaskCode(JSON.stringify(task, null, 2));
    setCodeDialogOpen(true);
  };

  // Render task-specific properties
  const renderTaskProperties = () => {
    switch (task.type) {
      case 'io.kestra.plugin.scripts.python.Script':
        return (
          <>
            <TextField
              label="Script"
              value={task.script || ''}
              onChange={(e) => handlePropertyChange('script', e.target.value)}
              fullWidth
              margin="normal"
              multiline
              rows={10}
              disabled={readOnly}
            />
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Isolation</InputLabel>
              <Select
                value={task.isolation || 'NONE'}
                onChange={(e) => handlePropertyChange('isolation', e.target.value)}
                label="Isolation"
                disabled={readOnly}
              >
                <MenuItem value="NONE">None</MenuItem>
                <MenuItem value="PROCESS">Process</MenuItem>
                <MenuItem value="DOCKER">Docker</MenuItem>
              </Select>
            </FormControl>
          </>
        );
      
      case 'io.kestra.plugin.scripts.shell.Script':
        return (
          <>
            <FormControl fullWidth margin="normal">
              <InputLabel>Shell</InputLabel>
              <Select
                value={task.shell || 'BASH'}
                onChange={(e) => handlePropertyChange('shell', e.target.value)}
                label="Shell"
                disabled={readOnly}
              >
                <MenuItem value="BASH">Bash</MenuItem>
                <MenuItem value="SH">Sh</MenuItem>
                <MenuItem value="POWERSHELL">PowerShell</MenuItem>
                <MenuItem value="CMD">CMD</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              label="Commands"
              value={Array.isArray(task.commands) ? task.commands.join('\n') : task.commands || ''}
              onChange={(e) => handlePropertyChange('commands', e.target.value.split('\n'))}
              fullWidth
              margin="normal"
              multiline
              rows={10}
              disabled={readOnly}
            />
          </>
        );
      
      case 'io.kestra.plugin.http.Request':
        return (
          <>
            <FormControl fullWidth margin="normal">
              <InputLabel>Method</InputLabel>
              <Select
                value={task.method || 'GET'}
                onChange={(e) => handlePropertyChange('method', e.target.value)}
                label="Method"
                disabled={readOnly}
              >
                <MenuItem value="GET">GET</MenuItem>
                <MenuItem value="POST">POST</MenuItem>
                <MenuItem value="PUT">PUT</MenuItem>
                <MenuItem value="DELETE">DELETE</MenuItem>
                <MenuItem value="PATCH">PATCH</MenuItem>
                <MenuItem value="HEAD">HEAD</MenuItem>
                <MenuItem value="OPTIONS">OPTIONS</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              label="URI"
              value={task.uri || ''}
              onChange={(e) => handlePropertyChange('uri', e.target.value)}
              fullWidth
              margin="normal"
              required
              disabled={readOnly}
            />
            
            <TextField
              label="Body"
              value={task.body || ''}
              onChange={(e) => handlePropertyChange('body', e.target.value)}
              fullWidth
              margin="normal"
              multiline
              rows={5}
              disabled={readOnly}
            />
          </>
        );
      
      case 'io.kestra.plugin.jdbc.Query':
        return (
          <>
            <TextField
              label="URL"
              value={task.url || ''}
              onChange={(e) => handlePropertyChange('url', e.target.value)}
              fullWidth
              margin="normal"
              required
              disabled={readOnly}
            />
            
            <TextField
              label="Username"
              value={task.username || ''}
              onChange={(e) => handlePropertyChange('username', e.target.value)}
              fullWidth
              margin="normal"
              disabled={readOnly}
            />
            
            <TextField
              label="Password"
              value={task.password || ''}
              onChange={(e) => handlePropertyChange('password', e.target.value)}
              fullWidth
              margin="normal"
              type="password"
              disabled={readOnly}
            />
            
            <TextField
              label="SQL Query"
              value={task.sql || ''}
              onChange={(e) => handlePropertyChange('sql', e.target.value)}
              fullWidth
              margin="normal"
              multiline
              rows={5}
              required
              disabled={readOnly}
            />
          </>
        );
      
      default:
        return (
          <Typography variant="body2" color="text.secondary">
            No specific properties for this task type.
          </Typography>
        );
    }
  };

  return (
    <Box sx={{ p: 2, overflow: 'auto', height: '100%' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Box sx={{ mr: 1, color: 'primary.main' }}>
          {getTaskIcon()}
        </Box>
        <Typography variant="h6">
          {getTaskTypeName()}
        </Typography>
      </Box>
      
      <TextField
        label="Task ID"
        value={task.id || ''}
        onChange={(e) => handlePropertyChange('id', e.target.value)}
        fullWidth
        margin="normal"
        required
        error={!task.id}
        helperText={!task.id ? 'Task ID is required' : ''}
        disabled={readOnly}
      />
      
      <TextField
        label="Description"
        value={task.description || ''}
        onChange={(e) => handlePropertyChange('description', e.target.value)}
        fullWidth
        margin="normal"
        multiline
        rows={2}
        disabled={readOnly}
      />
      
      <Divider sx={{ my: 2 }} />
      
      <Typography variant="subtitle1" gutterBottom>
        Task Properties
      </Typography>
      
      {renderTaskProperties()}
      
      <Divider sx={{ my: 2 }} />
      
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>Advanced Properties</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Button
            variant="outlined"
            startIcon={<CodeIcon />}
            onClick={showTaskCode}
            fullWidth
          >
            View Task JSON
          </Button>
          
          <TextField
            label="Timeout"
            value={task.timeout || ''}
            onChange={(e) => handlePropertyChange('timeout', e.target.value)}
            fullWidth
            margin="normal"
            placeholder="e.g., PT10M (10 minutes)"
            disabled={readOnly}
          />
          
          <TextField
            label="Retry Policy"
            value={task.retry?.type || ''}
            onChange={(e) => handlePropertyChange('retry', { type: e.target.value })}
            fullWidth
            margin="normal"
            placeholder="e.g., constant, exponential"
            disabled={readOnly}
          />
        </AccordionDetails>
      </Accordion>
      
      {/* Task Code Dialog */}
      <Dialog
        open={codeDialogOpen}
        onClose={() => setCodeDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Task JSON</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={20}
            value={taskCode}
            InputProps={{
              readOnly: true
            }}
            sx={{ fontFamily: 'monospace' }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCodeDialogOpen(false)}>Close</Button>
          <Button
            onClick={() => {
              navigator.clipboard.writeText(taskCode);
            }}
          >
            Copy to Clipboard
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaskPropertiesPanel;
