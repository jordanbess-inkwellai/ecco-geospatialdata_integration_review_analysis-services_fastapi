import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Grid, 
  Paper, 
  Tabs, 
  Tab,
  Alert,
  Snackbar
} from '@mui/material';
import Layout from '../../components/layout/Layout';
import BoxBrowser from '../../components/box-integration/BoxBrowser';

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
      id={`box-tabpanel-${index}`}
      aria-labelledby={`box-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3, height: '100%' }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const BoxIntegrationPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [selectedFile, setSelectedFile] = useState<any | null>(null);
  const [importedFile, setImportedFile] = useState<any | null>(null);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleFileSelect = (fileInfo: any) => {
    setSelectedFile(fileInfo);
  };

  const handleFileImport = (fileInfo: any) => {
    setImportedFile(fileInfo);
    setNotification({
      open: true,
      message: `Successfully imported ${fileInfo.name}`,
      severity: 'success'
    });
  };

  const handleCloseNotification = () => {
    setNotification({
      ...notification,
      open: false
    });
  };

  // Define file extension filters for different tabs
  const geospatialExtensions = ['shp', 'geojson', 'json', 'kml', 'gpkg', 'gdb', 'zip'];
  const tabularExtensions = ['csv', 'xlsx', 'xls', 'txt', 'tsv'];
  const imageExtensions = ['jpg', 'jpeg', 'png', 'tif', 'tiff', 'bmp'];

  return (
    <Layout title="Box.com Integration">
      <Container maxWidth={false} sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Box.com Integration
        </Typography>
        <Typography variant="body1" paragraph>
          Browse, import, and manage files from your Box.com account.
        </Typography>
        
        <Paper sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              aria-label="box integration tabs"
            >
              <Tab label="Geospatial Data" id="box-tab-0" aria-controls="box-tabpanel-0" />
              <Tab label="Tabular Data" id="box-tab-1" aria-controls="box-tabpanel-1" />
              <Tab label="Images" id="box-tab-2" aria-controls="box-tabpanel-2" />
              <Tab label="All Files" id="box-tab-3" aria-controls="box-tabpanel-3" />
            </Tabs>
          </Box>
          
          <Box sx={{ height: 'calc(100vh - 300px)' }}>
            <TabPanel value={tabValue} index={0}>
              <BoxBrowser 
                onFileSelect={handleFileSelect} 
                onFileImport={handleFileImport}
                fileExtensionFilter={geospatialExtensions}
              />
            </TabPanel>
            
            <TabPanel value={tabValue} index={1}>
              <BoxBrowser 
                onFileSelect={handleFileSelect} 
                onFileImport={handleFileImport}
                fileExtensionFilter={tabularExtensions}
              />
            </TabPanel>
            
            <TabPanel value={tabValue} index={2}>
              <BoxBrowser 
                onFileSelect={handleFileSelect} 
                onFileImport={handleFileImport}
                fileExtensionFilter={imageExtensions}
              />
            </TabPanel>
            
            <TabPanel value={tabValue} index={3}>
              <BoxBrowser 
                onFileSelect={handleFileSelect} 
                onFileImport={handleFileImport}
              />
            </TabPanel>
          </Box>
        </Paper>
        
        {importedFile && (
          <Paper sx={{ mt: 3, p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Last Imported File
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1">
                  {importedFile.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Imported from Box.com
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                {importedFile.metadata && (
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Metadata
                    </Typography>
                    <Grid container spacing={1}>
                      {importedFile.metadata.crs && (
                        <Grid item xs={6}>
                          <Typography variant="body2">
                            <strong>CRS:</strong> {importedFile.metadata.crs}
                          </Typography>
                        </Grid>
                      )}
                      {importedFile.metadata.geometryType && (
                        <Grid item xs={6}>
                          <Typography variant="body2">
                            <strong>Geometry Type:</strong> {importedFile.metadata.geometryType}
                          </Typography>
                        </Grid>
                      )}
                      {importedFile.metadata.featureCount && (
                        <Grid item xs={6}>
                          <Typography variant="body2">
                            <strong>Feature Count:</strong> {importedFile.metadata.featureCount}
                          </Typography>
                        </Grid>
                      )}
                      {importedFile.metadata.dataFormat && (
                        <Grid item xs={6}>
                          <Typography variant="body2">
                            <strong>Format:</strong> {importedFile.metadata.dataFormat}
                          </Typography>
                        </Grid>
                      )}
                    </Grid>
                  </Box>
                )}
              </Grid>
            </Grid>
          </Paper>
        )}
      </Container>
      
      <Snackbar 
        open={notification.open} 
        autoHideDuration={6000} 
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseNotification} 
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Layout>
  );
};

export default BoxIntegrationPage;
