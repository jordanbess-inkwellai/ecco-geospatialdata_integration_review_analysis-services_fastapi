import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  FormControl,
  FormControlLabel,
  FormGroup,
  InputLabel,
  MenuItem,
  Select,
  Switch,
  TextField,
  Typography,
  Chip,
  Paper,
  Divider,
  Alert,
  Tabs,
  Tab
} from '@mui/material';
import { apiClient } from '../../lib/api';

interface PgModelerDiagramProps {
  onModelGenerated?: (modelUrl: string) => void;
  onDiagramGenerated?: (imageUrl: string) => void;
}

const PgModelerDiagram: React.FC<PgModelerDiagramProps> = ({ 
  onModelGenerated, 
  onDiagramGenerated 
}) => {
  const [tabValue, setTabValue] = useState<number>(0);
  const [connectionString, setConnectionString] = useState<string>('');
  const [importSystemObjects, setImportSystemObjects] = useState<boolean>(false);
  const [importExtensionObjects, setImportExtensionObjects] = useState<boolean>(true);
  const [outputFormat, setOutputFormat] = useState<string>('png');
  const [modelFile, setModelFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [modelUrl, setModelUrl] = useState<string | null>(null);
  const [diagramUrl, setDiagramUrl] = useState<string | null>(null);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleImportDatabase = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Prepare form data
      const formData = new FormData();
      formData.append('connection_string', connectionString);
      formData.append('import_system_objects', importSystemObjects.toString());
      formData.append('import_extension_objects', importExtensionObjects.toString());
      
      // Import database
      const response = await apiClient.post('/diagrams/pgmodeler/import-db', formData, {
        responseType: 'blob'
      });
      
      // Create URL for the blob
      const blob = new Blob([response.data], { type: 'application/octet-stream' });
      const url = URL.createObjectURL(blob);
      
      setModelUrl(url);
      
      // Call callback if provided
      if (onModelGenerated) {
        onModelGenerated(url);
      }
    } catch (err) {
      console.error('Error importing database:', err);
      setError('Failed to import database. Please check your connection string and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleExportModel = async () => {
    if (!modelFile) {
      setError('Please select a model file first.');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Prepare form data
      const formData = new FormData();
      formData.append('model_file', modelFile);
      formData.append('output_format', outputFormat);
      
      // Export model
      const response = await apiClient.post('/diagrams/pgmodeler/export-model', formData, {
        responseType: 'blob'
      });
      
      // Determine content type
      const contentType = {
        'png': 'image/png',
        'svg': 'image/svg+xml',
        'pdf': 'application/pdf',
        'sql': 'text/plain',
        'data-dict': 'text/html'
      }[outputFormat] || 'application/octet-stream';
      
      // Create URL for the blob
      const blob = new Blob([response.data], { type: contentType });
      const url = URL.createObjectURL(blob);
      
      setDiagramUrl(url);
      
      // Call callback if provided
      if (onDiagramGenerated) {
        onDiagramGenerated(url);
      }
    } catch (err) {
      console.error('Error exporting model:', err);
      setError('Failed to export model. Please check your model file and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleModelFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setModelFile(event.target.files[0]);
    }
  };

  const handleDownloadModel = () => {
    if (modelUrl) {
      const a = document.createElement('a');
      a.href = modelUrl;
      a.download = 'pgmodeler_model.dbm';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  const handleDownloadDiagram = () => {
    if (diagramUrl) {
      const a = document.createElement('a');
      a.href = diagramUrl;
      a.download = `pgmodeler_export.${outputFormat}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          PgModeler Database Modeling
        </Typography>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="Import Database" />
            <Tab label="Export Model" />
          </Tabs>
        </Box>
        
        {tabValue === 0 && (
          <Box>
            <TextField
              label="Database Connection String"
              fullWidth
              value={connectionString}
              onChange={(e) => setConnectionString(e.target.value)}
              placeholder="postgresql://username:password@localhost:5432/dbname"
              margin="normal"
              helperText="PostgreSQL connection string format"
            />
            
            <FormGroup sx={{ mt: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={importSystemObjects}
                    onChange={(e) => setImportSystemObjects(e.target.checked)}
                  />
                }
                label="Import System Objects"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={importExtensionObjects}
                    onChange={(e) => setImportExtensionObjects(e.target.checked)}
                  />
                }
                label="Import Extension Objects"
              />
            </FormGroup>
            
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleImportDatabase}
                disabled={loading || !connectionString}
              >
                {loading ? <CircularProgress size={24} /> : 'Import Database'}
              </Button>
              
              {modelUrl && (
                <Button
                  variant="outlined"
                  color="secondary"
                  onClick={handleDownloadModel}
                >
                  Download Model
                </Button>
              )}
            </Box>
            
            {modelUrl && (
              <Alert severity="success" sx={{ mt: 2 }}>
                Database model successfully imported! You can download it or switch to the Export tab to generate diagrams.
              </Alert>
            )}
          </Box>
        )}
        
        {tabValue === 1 && (
          <Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Upload PgModeler Model (.dbm)
              </Typography>
              <input
                accept=".dbm"
                style={{ display: 'none' }}
                id="model-file-upload"
                type="file"
                onChange={handleModelFileChange}
              />
              <label htmlFor="model-file-upload">
                <Button variant="outlined" component="span">
                  Select Model File
                </Button>
              </label>
              {modelFile && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Selected file: {modelFile.name}
                </Typography>
              )}
            </Box>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Output Format</InputLabel>
              <Select
                value={outputFormat}
                onChange={(e) => setOutputFormat(e.target.value)}
                label="Output Format"
              >
                <MenuItem value="png">PNG</MenuItem>
                <MenuItem value="svg">SVG</MenuItem>
                <MenuItem value="pdf">PDF</MenuItem>
                <MenuItem value="sql">SQL</MenuItem>
                <MenuItem value="data-dict">Data Dictionary (HTML)</MenuItem>
              </Select>
            </FormControl>
            
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleExportModel}
                disabled={loading || !modelFile}
              >
                {loading ? <CircularProgress size={24} /> : 'Export Model'}
              </Button>
              
              {diagramUrl && (
                <Button
                  variant="outlined"
                  color="secondary"
                  onClick={handleDownloadDiagram}
                >
                  Download Export
                </Button>
              )}
            </Box>
            
            {diagramUrl && (
              <Box sx={{ mt: 3, textAlign: 'center' }}>
                <Typography variant="subtitle1" gutterBottom>
                  Exported {outputFormat.toUpperCase()}
                </Typography>
                <Paper elevation={3} sx={{ p: 2, overflow: 'auto', maxHeight: 500 }}>
                  {outputFormat === 'png' || outputFormat === 'svg' ? (
                    <img
                      src={diagramUrl}
                      alt="PgModeler Diagram"
                      style={{ maxWidth: '100%' }}
                    />
                  ) : outputFormat === 'pdf' ? (
                    <iframe
                      src={diagramUrl}
                      style={{ width: '100%', height: 500, border: 'none' }}
                    />
                  ) : outputFormat === 'sql' ? (
                    <iframe
                      src={diagramUrl}
                      style={{ width: '100%', height: 500, border: 'none' }}
                    />
                  ) : (
                    <iframe
                      src={diagramUrl}
                      style={{ width: '100%', height: 500, border: 'none' }}
                    />
                  )}
                </Paper>
              </Box>
            )}
          </Box>
        )}
        
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default PgModelerDiagram;
