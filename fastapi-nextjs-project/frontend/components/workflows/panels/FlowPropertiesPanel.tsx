import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';

interface FlowPropertiesPanelProps {
  flowProperties: any;
  onChange: (properties: any) => void;
  readOnly?: boolean;
}

const FlowPropertiesPanel: React.FC<FlowPropertiesPanelProps> = ({
  flowProperties,
  onChange,
  readOnly = false
}) => {
  const [inputDialogOpen, setInputDialogOpen] = useState(false);
  const [outputDialogOpen, setOutputDialogOpen] = useState(false);
  const [currentInput, setCurrentInput] = useState<any>(null);
  const [currentOutput, setCurrentOutput] = useState<any>(null);
  const [inputErrors, setInputErrors] = useState<any>({});
  const [outputErrors, setOutputErrors] = useState<any>({});

  // Handle flow property changes
  const handlePropertyChange = (property: string, value: any) => {
    onChange({ [property]: value });
  };

  // Open the input dialog
  const openInputDialog = (input: any = null) => {
    setCurrentInput(input || { name: '', type: 'STRING', description: '', required: false });
    setInputErrors({});
    setInputDialogOpen(true);
  };

  // Open the output dialog
  const openOutputDialog = (output: any = null) => {
    setCurrentOutput(output || { name: '', type: 'STRING', description: '' });
    setOutputErrors({});
    setOutputDialogOpen(true);
  };

  // Save the input
  const saveInput = () => {
    // Validate the input
    const errors: any = {};
    if (!currentInput.name) {
      errors.name = 'Name is required';
    }
    if (!currentInput.type) {
      errors.type = 'Type is required';
    }

    if (Object.keys(errors).length > 0) {
      setInputErrors(errors);
      return;
    }

    // Get the current inputs
    const inputs = [...(flowProperties.inputs || [])];

    // Check if we're editing an existing input
    const existingIndex = inputs.findIndex((input) => input.name === currentInput.name);
    if (existingIndex >= 0) {
      // Update the existing input
      inputs[existingIndex] = { ...currentInput };
    } else {
      // Add a new input
      inputs.push({ ...currentInput });
    }

    // Update the flow properties
    onChange({ inputs });
    setInputDialogOpen(false);
  };

  // Save the output
  const saveOutput = () => {
    // Validate the output
    const errors: any = {};
    if (!currentOutput.name) {
      errors.name = 'Name is required';
    }
    if (!currentOutput.type) {
      errors.type = 'Type is required';
    }

    if (Object.keys(errors).length > 0) {
      setOutputErrors(errors);
      return;
    }

    // Get the current outputs
    const outputs = [...(flowProperties.outputs || [])];

    // Check if we're editing an existing output
    const existingIndex = outputs.findIndex((output) => output.name === currentOutput.name);
    if (existingIndex >= 0) {
      // Update the existing output
      outputs[existingIndex] = { ...currentOutput };
    } else {
      // Add a new output
      outputs.push({ ...currentOutput });
    }

    // Update the flow properties
    onChange({ outputs });
    setOutputDialogOpen(false);
  };

  // Delete an input
  const deleteInput = (name: string) => {
    const inputs = (flowProperties.inputs || []).filter((input: any) => input.name !== name);
    onChange({ inputs });
  };

  // Delete an output
  const deleteOutput = (name: string) => {
    const outputs = (flowProperties.outputs || []).filter((output: any) => output.name !== name);
    onChange({ outputs });
  };

  return (
    <Box sx={{ p: 2, overflow: 'auto', height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Flow Properties
      </Typography>
      
      <TextField
        label="Flow ID"
        value={flowProperties.id || ''}
        onChange={(e) => handlePropertyChange('id', e.target.value)}
        fullWidth
        margin="normal"
        required
        error={!flowProperties.id}
        helperText={!flowProperties.id ? 'Flow ID is required' : ''}
        disabled={readOnly}
      />
      
      <TextField
        label="Namespace"
        value={flowProperties.namespace || 'default'}
        onChange={(e) => handlePropertyChange('namespace', e.target.value)}
        fullWidth
        margin="normal"
        required
        disabled={readOnly}
      />
      
      <TextField
        label="Description"
        value={flowProperties.description || ''}
        onChange={(e) => handlePropertyChange('description', e.target.value)}
        fullWidth
        margin="normal"
        multiline
        rows={2}
        disabled={readOnly}
      />
      
      <Divider sx={{ my: 2 }} />
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle1">Inputs</Typography>
        {!readOnly && (
          <Button
            size="small"
            startIcon={<AddIcon />}
            onClick={() => openInputDialog()}
          >
            Add Input
          </Button>
        )}
      </Box>
      
      <List dense>
        {(flowProperties.inputs || []).map((input: any) => (
          <ListItem key={input.name}>
            <ListItemText
              primary={input.name}
              secondary={`${input.type}${input.required ? ' (Required)' : ''}: ${input.description || 'No description'}`}
            />
            {!readOnly && (
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => openInputDialog(input)}>
                  <EditIcon fontSize="small" />
                </IconButton>
                <IconButton edge="end" onClick={() => deleteInput(input.name)}>
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </ListItemSecondaryAction>
            )}
          </ListItem>
        ))}
        {(flowProperties.inputs || []).length === 0 && (
          <ListItem>
            <ListItemText secondary="No inputs defined" />
          </ListItem>
        )}
      </List>
      
      <Divider sx={{ my: 2 }} />
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle1">Outputs</Typography>
        {!readOnly && (
          <Button
            size="small"
            startIcon={<AddIcon />}
            onClick={() => openOutputDialog()}
          >
            Add Output
          </Button>
        )}
      </Box>
      
      <List dense>
        {(flowProperties.outputs || []).map((output: any) => (
          <ListItem key={output.name}>
            <ListItemText
              primary={output.name}
              secondary={`${output.type}: ${output.description || 'No description'}`}
            />
            {!readOnly && (
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => openOutputDialog(output)}>
                  <EditIcon fontSize="small" />
                </IconButton>
                <IconButton edge="end" onClick={() => deleteOutput(output.name)}>
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </ListItemSecondaryAction>
            )}
          </ListItem>
        ))}
        {(flowProperties.outputs || []).length === 0 && (
          <ListItem>
            <ListItemText secondary="No outputs defined" />
          </ListItem>
        )}
      </List>
      
      {/* Input Dialog */}
      <Dialog open={inputDialogOpen} onClose={() => setInputDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{currentInput && currentInput.name ? 'Edit Input' : 'Add Input'}</DialogTitle>
        <DialogContent>
          <TextField
            label="Name"
            value={currentInput?.name || ''}
            onChange={(e) => setCurrentInput({ ...currentInput, name: e.target.value })}
            fullWidth
            margin="normal"
            required
            error={!!inputErrors.name}
            helperText={inputErrors.name}
          />
          
          <FormControl fullWidth margin="normal" required error={!!inputErrors.type}>
            <InputLabel>Type</InputLabel>
            <Select
              value={currentInput?.type || ''}
              onChange={(e) => setCurrentInput({ ...currentInput, type: e.target.value })}
              label="Type"
            >
              <MenuItem value="STRING">STRING</MenuItem>
              <MenuItem value="INT">INT</MenuItem>
              <MenuItem value="FLOAT">FLOAT</MenuItem>
              <MenuItem value="BOOLEAN">BOOLEAN</MenuItem>
              <MenuItem value="DATETIME">DATETIME</MenuItem>
              <MenuItem value="FILE">FILE</MenuItem>
              <MenuItem value="OBJECT">OBJECT</MenuItem>
              <MenuItem value="ARRAY">ARRAY</MenuItem>
            </Select>
            {inputErrors.type && <FormHelperText>{inputErrors.type}</FormHelperText>}
          </FormControl>
          
          <TextField
            label="Description"
            value={currentInput?.description || ''}
            onChange={(e) => setCurrentInput({ ...currentInput, description: e.target.value })}
            fullWidth
            margin="normal"
            multiline
            rows={2}
          />
          
          <FormControl fullWidth margin="normal">
            <InputLabel>Required</InputLabel>
            <Select
              value={currentInput?.required ? 'true' : 'false'}
              onChange={(e) => setCurrentInput({ ...currentInput, required: e.target.value === 'true' })}
              label="Required"
            >
              <MenuItem value="true">Yes</MenuItem>
              <MenuItem value="false">No</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInputDialogOpen(false)}>Cancel</Button>
          <Button onClick={saveInput} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
      
      {/* Output Dialog */}
      <Dialog open={outputDialogOpen} onClose={() => setOutputDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{currentOutput && currentOutput.name ? 'Edit Output' : 'Add Output'}</DialogTitle>
        <DialogContent>
          <TextField
            label="Name"
            value={currentOutput?.name || ''}
            onChange={(e) => setCurrentOutput({ ...currentOutput, name: e.target.value })}
            fullWidth
            margin="normal"
            required
            error={!!outputErrors.name}
            helperText={outputErrors.name}
          />
          
          <FormControl fullWidth margin="normal" required error={!!outputErrors.type}>
            <InputLabel>Type</InputLabel>
            <Select
              value={currentOutput?.type || ''}
              onChange={(e) => setCurrentOutput({ ...currentOutput, type: e.target.value })}
              label="Type"
            >
              <MenuItem value="STRING">STRING</MenuItem>
              <MenuItem value="INT">INT</MenuItem>
              <MenuItem value="FLOAT">FLOAT</MenuItem>
              <MenuItem value="BOOLEAN">BOOLEAN</MenuItem>
              <MenuItem value="DATETIME">DATETIME</MenuItem>
              <MenuItem value="FILE">FILE</MenuItem>
              <MenuItem value="OBJECT">OBJECT</MenuItem>
              <MenuItem value="ARRAY">ARRAY</MenuItem>
            </Select>
            {outputErrors.type && <FormHelperText>{outputErrors.type}</FormHelperText>}
          </FormControl>
          
          <TextField
            label="Description"
            value={currentOutput?.description || ''}
            onChange={(e) => setCurrentOutput({ ...currentOutput, description: e.target.value })}
            fullWidth
            margin="normal"
            multiline
            rows={2}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOutputDialogOpen(false)}>Cancel</Button>
          <Button onClick={saveOutput} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FlowPropertiesPanel;
