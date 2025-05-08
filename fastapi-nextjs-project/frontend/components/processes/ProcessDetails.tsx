import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Divider, 
  CircularProgress,
  Tabs,
  Tab,
  Alert
} from '@mui/material';
import { useProcess } from '../../hooks/useProcess';
import ProcessInputForm from './ProcessInputForm';
import ProcessInfo from './ProcessInfo';

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
      id={`process-tabpanel-${index}`}
      aria-labelledby={`process-tab-${index}`}
      style={{ height: '100%' }}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 2, height: '100%', overflow: 'auto' }}>
          {children}
        </Box>
      )}
    </div>
  );
}

interface ProcessDetailsProps {
  processId: string;
  onExecute: (processId: string, inputs: any) => void;
}

const ProcessDetails: React.FC<ProcessDetailsProps> = ({ processId, onExecute }) => {
  const { process, loading, error } = useProcess(processId);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    // Reset to the info tab when changing processes
    setTabValue(0);
  }, [processId]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleExecute = (inputs: any) => {
    onExecute(processId, inputs);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={2}>
        <Alert severity="error">Error loading process details: {error}</Alert>
      </Box>
    );
  }

  if (!process) {
    return (
      <Box p={2}>
        <Alert severity="info">Select a process to view details</Alert>
      </Box>
    );
  }

  return (
    <Paper elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box p={2}>
        <Typography variant="h6">{process.title}</Typography>
        <Typography variant="body2" color="text.secondary">
          {process.id}
        </Typography>
      </Box>
      <Divider />
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="process tabs">
          <Tab label="Information" id="process-tab-0" aria-controls="process-tabpanel-0" />
          <Tab label="Execute" id="process-tab-1" aria-controls="process-tabpanel-1" />
          {process.examples && process.examples.length > 0 && (
            <Tab label="Examples" id="process-tab-2" aria-controls="process-tabpanel-2" />
          )}
        </Tabs>
      </Box>
      <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
        <TabPanel value={tabValue} index={0}>
          <ProcessInfo process={process} />
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <ProcessInputForm 
            process={process} 
            onSubmit={handleExecute} 
          />
        </TabPanel>
        {process.examples && process.examples.length > 0 && (
          <TabPanel value={tabValue} index={2}>
            <Typography variant="h6" gutterBottom>Examples</Typography>
            {process.examples.map((example, index) => (
              <Box key={index} mb={3}>
                <Typography variant="subtitle1">{example.title || `Example ${index + 1}`}</Typography>
                <Paper variant="outlined" sx={{ p: 2, mt: 1 }}>
                  <pre style={{ margin: 0, overflow: 'auto' }}>
                    {JSON.stringify(example.inputs, null, 2)}
                  </pre>
                </Paper>
              </Box>
            ))}
          </TabPanel>
        )}
      </Box>
    </Paper>
  );
};

export default ProcessDetails;
