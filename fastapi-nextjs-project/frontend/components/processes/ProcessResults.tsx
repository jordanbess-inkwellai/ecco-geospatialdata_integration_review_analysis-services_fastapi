import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Tabs, 
  Tab, 
  Button,
  CircularProgress,
  Alert,
  Divider
} from '@mui/material';
import MapIcon from '@mui/icons-material/Map';
import DownloadIcon from '@mui/icons-material/Download';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { useMap } from '../../hooks/useMap';

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

interface ProcessResultsProps {
  processId: string;
  result: any;
  loading: boolean;
  error: string | null;
}

const ProcessResults: React.FC<ProcessResultsProps> = ({ 
  processId, 
  result, 
  loading, 
  error 
}) => {
  const [tabValue, setTabValue] = useState(0);
  const { addGeoJSONToMap } = useMap();
  const [copySuccess, setCopySuccess] = useState<string | null>(null);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleAddToMap = () => {
    const geojson = extractGeoJSON(result);
    if (geojson) {
      addGeoJSONToMap(geojson, `Process Result: ${processId}`);
    }
  };

  const handleDownload = () => {
    const jsonString = JSON.stringify(result, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `${processId}-result.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
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

  const containsGeoJSON = result ? Boolean(extractGeoJSON(result)) : false;

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
        <Alert severity="error">Error executing process: {error}</Alert>
      </Box>
    );
  }

  if (!result) {
    return (
      <Box p={2}>
        <Alert severity="info">Execute a process to see results</Alert>
      </Box>
    );
  }

  return (
    <Paper elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box p={2} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h6">Process Results</Typography>
        <Box>
          {containsGeoJSON && (
            <Button 
              startIcon={<MapIcon />} 
              onClick={handleAddToMap}
              sx={{ mr: 1 }}
            >
              Add to Map
            </Button>
          )}
          <Button 
            startIcon={<DownloadIcon />} 
            onClick={handleDownload}
            sx={{ mr: 1 }}
          >
            Download
          </Button>
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
          <Tab label="JSON" id="result-tab-0" aria-controls="result-tabpanel-0" />
          {containsGeoJSON && (
            <Tab label="GeoJSON" id="result-tab-1" aria-controls="result-tabpanel-1" />
          )}
        </Tabs>
      </Box>
      <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
        <TabPanel value={tabValue} index={0}>
          <pre style={{ margin: 0, overflow: 'auto', height: '100%' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </TabPanel>
        {containsGeoJSON && (
          <TabPanel value={tabValue} index={1}>
            <pre style={{ margin: 0, overflow: 'auto', height: '100%' }}>
              {JSON.stringify(extractGeoJSON(result), null, 2)}
            </pre>
          </TabPanel>
        )}
      </Box>
    </Paper>
  );
};

// Helper function to extract GeoJSON from result
function extractGeoJSON(obj: any): any {
  if (!obj) return null;
  
  // Check if this is a GeoJSON object
  if (obj.type && obj.coordinates) {
    return obj;
  }
  
  // Check if this is a GeoJSON FeatureCollection
  if (obj.type === 'FeatureCollection' && obj.features) {
    return obj;
  }
  
  // Check if this is a GeoJSON Feature
  if (obj.type === 'Feature' && obj.geometry) {
    return obj;
  }
  
  // Check for result key
  if (obj.result) {
    const extracted = extractGeoJSON(obj.result);
    if (extracted) return extracted;
  }
  
  // Check for specific keys that might contain GeoJSON
  const geoJsonKeys = [
    'geometry', 'geojson', 'features', 'buffered_geometry', 
    'intersection_geometry', 'convex_hull', 'simplified_geometry', 
    'voronoi_polygons', 'contours', 'path', 'service_area'
  ];
  
  for (const key of geoJsonKeys) {
    if (obj[key]) {
      const extracted = extractGeoJSON(obj[key]);
      if (extracted) return extracted;
    }
  }
  
  // Recursively check all values if object
  if (typeof obj === 'object') {
    for (const key in obj) {
      const extracted = extractGeoJSON(obj[key]);
      if (extracted) return extracted;
    }
  }
  
  // If this is an array, check each item
  if (Array.isArray(obj)) {
    // If this is a list of features, wrap in a FeatureCollection
    if (obj.every(item => item.type === 'Feature')) {
      return {
        type: 'FeatureCollection',
        features: obj
      };
    }
    
    // Otherwise check each item
    for (const item of obj) {
      const extracted = extractGeoJSON(item);
      if (extracted) return extracted;
    }
  }
  
  return null;
}

export default ProcessResults;
