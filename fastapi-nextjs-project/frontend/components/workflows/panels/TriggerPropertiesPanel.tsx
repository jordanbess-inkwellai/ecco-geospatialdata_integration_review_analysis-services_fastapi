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
import WebhookIcon from '@mui/icons-material/Webhook';
import ScheduleIcon from '@mui/icons-material/Schedule';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

interface TriggerPropertiesPanelProps {
  trigger: any;
  onChange: (trigger: any) => void;
  readOnly?: boolean;
}

const TriggerPropertiesPanel: React.FC<TriggerPropertiesPanelProps> = ({
  trigger,
  onChange,
  readOnly = false
}) => {
  const [codeDialogOpen, setCodeDialogOpen] = useState(false);
  const [triggerCode, setTriggerCode] = useState('');
  const [conditionDialogOpen, setConditionDialogOpen] = useState(false);
  const [currentCondition, setCurrentCondition] = useState<any>(null);
  const [conditionErrors, setConditionErrors] = useState<any>({});

  // Get the appropriate icon based on the trigger type
  const getTriggerIcon = () => {
    switch (trigger.type) {
      case 'io.kestra.plugin.webhook.Trigger':
        return <WebhookIcon />;
      case 'io.kestra.plugin.schedules.Schedule':
        return <ScheduleIcon />;
      case 'io.kestra.plugin.core.trigger.Flow':
        return <PlayArrowIcon />;
      default:
        return null;
    }
  };

  // Get a short name for the trigger type
  const getTriggerTypeName = () => {
    switch (trigger.type) {
      case 'io.kestra.plugin.webhook.Trigger':
        return 'Webhook';
      case 'io.kestra.plugin.schedules.Schedule':
        return 'Schedule';
      case 'io.kestra.plugin.core.trigger.Flow':
        return 'Flow';
      default:
        return 'Trigger';
    }
  };

  // Handle trigger property changes
  const handlePropertyChange = (property: string, value: any) => {
    onChange({ ...trigger, [property]: value });
  };

  // Show the trigger code
  const showTriggerCode = () => {
    setTriggerCode(JSON.stringify(trigger, null, 2));
    setCodeDialogOpen(true);
  };

  // Open the condition dialog
  const openConditionDialog = (condition: any = null) => {
    setCurrentCondition(condition || { type: 'io.kestra.plugin.webhook.conditions.JsonPath', path: '', value: '' });
    setConditionErrors({});
    setConditionDialogOpen(true);
  };

  // Save the condition
  const saveCondition = () => {
    // Validate the condition
    const errors: any = {};
    if (!currentCondition.type) {
      errors.type = 'Type is required';
    }
    if (!currentCondition.path) {
      errors.path = 'Path is required';
    }

    if (Object.keys(errors).length > 0) {
      setConditionErrors(errors);
      return;
    }

    // Get the current conditions
    const conditions = [...(trigger.conditions || [])];

    // Check if we're editing an existing condition
    const existingIndex = conditions.findIndex((c) => 
      c.type === currentCondition.type && c.path === currentCondition.path
    );
    
    if (existingIndex >= 0) {
      // Update the existing condition
      conditions[existingIndex] = { ...currentCondition };
    } else {
      // Add a new condition
      conditions.push({ ...currentCondition });
    }

    // Update the trigger properties
    handlePropertyChange('conditions', conditions);
    setConditionDialogOpen(false);
  };

  // Delete a condition
  const deleteCondition = (index: number) => {
    const conditions = [...(trigger.conditions || [])];
    conditions.splice(index, 1);
    handlePropertyChange('conditions', conditions);
  };

  // Render trigger-specific properties
  const renderTriggerProperties = () => {
    switch (trigger.type) {
      case 'io.kestra.plugin.webhook.Trigger':
        return (
          <>
            <TextField
              label="Key"
              value={trigger.key || ''}
              onChange={(e) => handlePropertyChange('key', e.target.value)}
              fullWidth
              margin="normal"
              required
              disabled={readOnly}
            />
            
            <Divider sx={{ my: 2 }} />
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle1">Conditions</Typography>
              {!readOnly && (
                <Button
                  size="small"
                  startIcon={<AddIcon />}
                  onClick={() => openConditionDialog()}
                >
                  Add Condition
                </Button>
              )}
            </Box>
            
            <List dense>
              {(trigger.conditions || []).map((condition: any, index: number) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={condition.type.split('.').pop()}
                    secondary={`${condition.path}: ${condition.value}`}
                  />
                  {!readOnly && (
                    <ListItemSecondaryAction>
                      <IconButton edge="end" onClick={() => openConditionDialog(condition)}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton edge="end" onClick={() => deleteCondition(index)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </ListItemSecondaryAction>
                  )}
                </ListItem>
              ))}
              {(trigger.conditions || []).length === 0 && (
                <ListItem>
                  <ListItemText secondary="No conditions defined" />
                </ListItem>
              )}
            </List>
          </>
        );
      
      case 'io.kestra.plugin.schedules.Schedule':
        return (
          <>
            <TextField
              label="Cron Expression"
              value={trigger.cron || ''}
              onChange={(e) => handlePropertyChange('cron', e.target.value)}
              fullWidth
              margin="normal"
              required
              placeholder="e.g., 0 0 * * *"
              disabled={readOnly}
            />
            
            <TextField
              label="Timezone"
              value={trigger.timezone || ''}
              onChange={(e) => handlePropertyChange('timezone', e.target.value)}
              fullWidth
              margin="normal"
              placeholder="e.g., America/New_York"
              disabled={readOnly}
            />
          </>
        );
      
      case 'io.kestra.plugin.core.trigger.Flow':
        return (
          <>
            <TextField
              label="Namespace"
              value={trigger.namespace || ''}
              onChange={(e) => handlePropertyChange('namespace', e.target.value)}
              fullWidth
              margin="normal"
              required
              disabled={readOnly}
            />
            
            <TextField
              label="Flow ID"
              value={trigger.flowId || ''}
              onChange={(e) => handlePropertyChange('flowId', e.target.value)}
              fullWidth
              margin="normal"
              required
              disabled={readOnly}
            />
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Execution Status</InputLabel>
              <Select
                value={trigger.executionStatus || 'SUCCESS'}
                onChange={(e) => handlePropertyChange('executionStatus', e.target.value)}
                label="Execution Status"
                disabled={readOnly}
              >
                <MenuItem value="SUCCESS">SUCCESS</MenuItem>
                <MenuItem value="FAILED">FAILED</MenuItem>
                <MenuItem value="WARNING">WARNING</MenuItem>
                <MenuItem value="ANY">ANY</MenuItem>
              </Select>
            </FormControl>
          </>
        );
      
      default:
        return (
          <Typography variant="body2" color="text.secondary">
            No specific properties for this trigger type.
          </Typography>
        );
    }
  };

  return (
    <Box sx={{ p: 2, overflow: 'auto', height: '100%' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Box sx={{ mr: 1, color: 'warning.main' }}>
          {getTriggerIcon()}
        </Box>
        <Typography variant="h6">
          {getTriggerTypeName()}
        </Typography>
      </Box>
      
      <TextField
        label="Trigger ID"
        value={trigger.id || ''}
        onChange={(e) => handlePropertyChange('id', e.target.value)}
        fullWidth
        margin="normal"
        required
        error={!trigger.id}
        helperText={!trigger.id ? 'Trigger ID is required' : ''}
        disabled={readOnly}
      />
      
      <TextField
        label="Description"
        value={trigger.description || ''}
        onChange={(e) => handlePropertyChange('description', e.target.value)}
        fullWidth
        margin="normal"
        multiline
        rows={2}
        disabled={readOnly}
      />
      
      <Divider sx={{ my: 2 }} />
      
      <Typography variant="subtitle1" gutterBottom>
        Trigger Properties
      </Typography>
      
      {renderTriggerProperties()}
      
      <Divider sx={{ my: 2 }} />
      
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>Advanced Properties</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Button
            variant="outlined"
            startIcon={<CodeIcon />}
            onClick={showTriggerCode}
            fullWidth
          >
            View Trigger JSON
          </Button>
        </AccordionDetails>
      </Accordion>
      
      {/* Trigger Code Dialog */}
      <Dialog
        open={codeDialogOpen}
        onClose={() => setCodeDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Trigger JSON</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={20}
            value={triggerCode}
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
              navigator.clipboard.writeText(triggerCode);
            }}
          >
            Copy to Clipboard
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Condition Dialog */}
      <Dialog open={conditionDialogOpen} onClose={() => setConditionDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {currentCondition && currentCondition.path ? 'Edit Condition' : 'Add Condition'}
        </DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal" required error={!!conditionErrors.type}>
            <InputLabel>Type</InputLabel>
            <Select
              value={currentCondition?.type || ''}
              onChange={(e) => setCurrentCondition({ ...currentCondition, type: e.target.value })}
              label="Type"
            >
              <MenuItem value="io.kestra.plugin.webhook.conditions.JsonPath">JsonPath</MenuItem>
              <MenuItem value="io.kestra.plugin.webhook.conditions.HeaderEqual">HeaderEqual</MenuItem>
              <MenuItem value="io.kestra.plugin.webhook.conditions.BodyRegexp">BodyRegexp</MenuItem>
            </Select>
            {conditionErrors.type && <FormHelperText>{conditionErrors.type}</FormHelperText>}
          </FormControl>
          
          <TextField
            label="Path"
            value={currentCondition?.path || ''}
            onChange={(e) => setCurrentCondition({ ...currentCondition, path: e.target.value })}
            fullWidth
            margin="normal"
            required
            error={!!conditionErrors.path}
            helperText={conditionErrors.path || (currentCondition?.type === 'io.kestra.plugin.webhook.conditions.JsonPath' ? 'e.g., $.event' : 'e.g., Content-Type')}
          />
          
          <TextField
            label="Value"
            value={currentCondition?.value || ''}
            onChange={(e) => setCurrentCondition({ ...currentCondition, value: e.target.value })}
            fullWidth
            margin="normal"
            required
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConditionDialogOpen(false)}>Cancel</Button>
          <Button onClick={saveCondition} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TriggerPropertiesPanel;
