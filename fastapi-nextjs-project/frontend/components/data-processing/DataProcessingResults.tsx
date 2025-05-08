import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Tabs, 
  Tab, 
  Button,
  Divider,
  Alert,
  List,
  ListItem,
  ListItemText,
  Chip
} from '@mui/material';
import MapIcon from '@mui/icons-material/Map';
import DownloadIcon from '@mui/icons-material/Download';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { useMap } from '../../hooks/useMap';
import { apiClient } from '../../lib/api';

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
      id={`result-tabpanel-${index}`}
      aria-labelledby={`result-tab-${index}`}
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

interface DataProcessingResultsProps {
  result: any;
}

const DataProcessingResults: React.FC<DataProcessingResultsProps> = ({ result }) => {
  const [tabValue, setTabValue] = useState(0);
  const { addGeoJSONToMap } = useMap();
  const [copySuccess, setCopySuccess] = useState<string | null>(null);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleAddToMap = () => {
    if (!result) return;
    
    // For vector data, we can add it directly to the map
    if (result.type === 'vector' && result.sample_features) {
      addGeoJSONToMap(result.sample_features, `Data Processing Result: ${result.file_name}`);
    }
  };

  const handleDownload = () => {
    if (!result || !result.file_path) return;
    
    // Get the file name from the path
    const fileName = result.file_name || result.file_path.split('/').pop();
    
    // Create a download link
    const downloadUrl = `${apiClient.defaults.baseURL}/data-processing/download/${fileName}`;
    
    // Open the download link in a new tab
    window.open(downloadUrl, '_blank');
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(result, null, 2))
      .then(() => {
        setCopySuccess('Copied to clipboard!');
        setTimeout(() => setCopySuccess(null), 2000);
      })
      .catch(err => {
        console.error('Failed to copy: ', err);
        setCopySuccess('Failed to copy');
        setTimeout(() => setCopySuccess(null), 2000);
      });
  };

  if (!result) {
    return (
      <Paper elevation={2} sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Box p={3} textAlign="center">
          <Typography variant="h6" gutterBottom>
            No Results Yet
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Process data to see results here.
          </Typography>
        </Box>
      </Paper>
    );
  }

  const isVector = result.type === 'vector';
  const isRaster = result.type === 'raster';

  return (
    <Paper elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box p={2} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h6">Processing Results</Typography>
        <Box>
          {isVector && (
            <Button 
              startIcon={<MapIcon />} 
              onClick={handleAddToMap}
              sx={{ mr: 1 }}
            >
              Add to Map
            </Button>
          )}
          {result.file_path && (
            <Button 
              startIcon={<DownloadIcon />} 
              onClick={handleDownload}
              sx={{ mr: 1 }}
            >
              Download
            </Button>
          )}
          <Button 
            startIcon={<ContentCopyIcon />} 
            onClick={handleCopy}
          >
            Copy
          </Button>
          {copySuccess && (
            <Typography variant="caption" color="success.main" sx={{ ml: 1 }}>
              {copySuccess}
            </Typography>
          )}
        </Box>
      </Box>
      <Divider />
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="result tabs">
          <Tab label="Summary" id="result-tab-0" aria-controls="result-tabpanel-0" />
          <Tab label="Details" id="result-tab-1" aria-controls="result-tabpanel-1" />
          {isVector && (
            <Tab label="Features" id="result-tab-2" aria-controls="result-tabpanel-2" />
          )}
        </Tabs>
      </Box>
      <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
        <TabPanel value={tabValue} index={0}>
          <Box>
            <Typography variant="h6" gutterBottom>File Information</Typography>
            <List>
              <ListItem>
                <ListItemText primary="File Name" secondary={result.file_name} />
              </ListItem>
              <ListItem>
                <ListItemText primary="Type" secondary={result.type} />
              </ListItem>
              {result.driver && (
                <ListItem>
                  <ListItemText primary="Driver" secondary={result.driver} />
                </ListItem>
              )}
              {result.crs && (
                <ListItem>
                  <ListItemText primary="CRS" secondary={result.crs} />
                </ListItem>
              )}
              {isVector && (
                <>
                  <ListItem>
                    <ListItemText primary="Feature Count" secondary={result.feature_count} />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Geometry Types" 
                      secondary={
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                          {result.geometry_types?.map((type: string) => (
                            <Chip key={type} label={type} size="small" />
                          ))}
                        </Box>
                      } 
                    />
                  </ListItem>
                </>
              )}
              {isRaster && (
                <>
                  <ListItem>
                    <ListItemText primary="Dimensions" secondary={`${result.width} x ${result.height}`} />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Bands" secondary={result.count} />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Data Type" secondary={result.dtype} />
                  </ListItem>
                </>
              )}
            </List>
          </Box>
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <pre style={{ margin: 0, overflow: 'auto', height: '100%' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </TabPanel>
        {isVector && (
          <TabPanel value={tabValue} index={2}>
            <Typography variant="h6" gutterBottom>Sample Features</Typography>
            <pre style={{ margin: 0, overflow: 'auto', height: 'calc(100% - 40px)' }}>
              {JSON.stringify(result.sample_features, null, 2)}
            </pre>
          </TabPanel>
        )}
      </Box>
    </Paper>
  );
};

export default DataProcessingResults;
