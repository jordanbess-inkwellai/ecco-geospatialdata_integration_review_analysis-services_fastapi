import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  TextField,
  Grid,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import CloudDoneIcon from '@mui/icons-material/CloudDone';
import DescriptionIcon from '@mui/icons-material/Description';
import FolderIcon from '@mui/icons-material/Folder';
import { apiClient } from '../../lib/api';

const BoxIntegration: React.FC = () => {
  const [activeStep, setActiveStep] = useState<number>(0);
  const [clientId, setClientId] = useState<string>('');
  const [clientSecret, setClientSecret] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [scanPath, setScanPath] = useState<string>('box:');
  const [scanResults, setScanResults] = useState<any>(null);
  const [scanning, setScanning] = useState<boolean>(false);

  const handleAuthenticate = async () => {
    if (!clientId || !clientSecret) {
      setError('Client ID and Client Secret are required');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('client_id', clientId);
      formData.append('client_secret', clientSecret);
      
      const response = await apiClient.post('/api/v1/rclone/box/auth', formData);
      
      setSuccess('Box authentication successful');
      setActiveStep(1);
    } catch (err) {
      console.error('Error authenticating with Box:', err);
      setError('Failed to authenticate with Box. Please check your credentials and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleScanFiles = async () => {
    setScanning(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('path', scanPath);
      formData.append('recursive', 'true');
      
      const response = await apiClient.post('/api/v1/rclone/scan', formData);
      
      setScanResults(response.data);
      setSuccess(`Scanned ${response.data.file_count} files`);
      setActiveStep(2);
    } catch (err) {
      console.error('Error scanning Box files:', err);
      setError('Failed to scan Box files. Please try again.');
    } finally {
      setScanning(false);
    }
  };

  const renderAuthStep = () => (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Box.com Authentication
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        To connect to Box.com, you need to provide your Box API credentials.
        You can create these in the Box Developer Console.
      </Typography>
      
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <TextField
            label="Client ID"
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
            fullWidth
            required
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            label="Client Secret"
            value={clientSecret}
            onChange={(e) => setClientSecret(e.target.value)}
            fullWidth
            required
            type="password"
          />
        </Grid>
        <Grid item xs={12}>
          <Button 
            variant="contained" 
            onClick={handleAuthenticate}
            disabled={loading || !clientId || !clientSecret}
            startIcon={loading ? <CircularProgress size={20} /> : null}
            fullWidth
          >
            {loading ? 'Authenticating...' : 'Authenticate with Box'}
          </Button>
        </Grid>
      </Grid>
    </Paper>
  );

  const renderScanStep = () => (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Scan Box.com Files
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Scan your Box.com files to extract metadata. This will help you understand what data is available.
      </Typography>
      
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <TextField
            label="Box Path"
            value={scanPath}
            onChange={(e) => setScanPath(e.target.value)}
            fullWidth
            helperText="Example: box: for root, box:folder_name for a specific folder"
          />
        </Grid>
        <Grid item xs={12}>
          <Button 
            variant="contained" 
            onClick={handleScanFiles}
            disabled={scanning || !scanPath}
            startIcon={scanning ? <CircularProgress size={20} /> : null}
            fullWidth
          >
            {scanning ? 'Scanning...' : 'Scan Files'}
          </Button>
        </Grid>
      </Grid>
    </Paper>
  );

  const renderResultsStep = () => (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Box.com Scan Results
      </Typography>
      
      {scanResults && (
        <>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body1">
              <strong>Path:</strong> {scanResults.remote_path}
            </Typography>
            <Typography variant="body1">
              <strong>Files Found:</strong> {scanResults.file_count}
            </Typography>
          </Box>
          
          <Divider sx={{ mb: 2 }} />
          
          <Typography variant="subtitle1" gutterBottom>
            Files:
          </Typography>
          
          <List sx={{ maxHeight: 400, overflow: 'auto' }}>
            {scanResults.files.map((file: any, index: number) => (
              <ListItem key={index} divider>
                <ListItemIcon>
                  {file.path.endsWith('/') ? <FolderIcon /> : <DescriptionIcon />}
                </ListItemIcon>
                <ListItemText
                  primary={file.name}
                  secondary={
                    <>
                      <Typography component="span" variant="body2">
                        Size: {formatFileSize(file.size)} • Modified: {new Date(file.modified_time).toLocaleString()}
                      </Typography>
                      {file.metadata && (
                        <Typography component="div" variant="body2" sx={{ mt: 1 }}>
                          <strong>Metadata:</strong> {JSON.stringify(file.metadata)}
                        </Typography>
                      )}
                    </>
                  }
                />
              </ListItem>
            ))}
          </List>
          
          <Box sx={{ mt: 2 }}>
            <Button 
              variant="outlined" 
              onClick={() => {
                setScanPath('box:');
                setActiveStep(1);
              }}
            >
              Scan Another Path
            </Button>
          </Box>
        </>
      )}
    </Paper>
  );

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Box.com Integration
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
      
      <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
        <Step>
          <StepLabel>Authenticate</StepLabel>
        </Step>
        <Step>
          <StepLabel>Scan Files</StepLabel>
        </Step>
        <Step>
          <StepLabel>View Results</StepLabel>
        </Step>
      </Stepper>
      
      {activeStep === 0 && renderAuthStep()}
      {activeStep === 1 && renderScanStep()}
      {activeStep === 2 && renderResultsStep()}
      
      {activeStep > 0 && (
        <Card sx={{ mb: 3, bgcolor: 'success.light' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <CloudDoneIcon sx={{ mr: 2, color: 'success.main' }} />
              <Typography variant="body1" color="success.main">
                Box.com is connected and ready to use
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default BoxIntegration;
