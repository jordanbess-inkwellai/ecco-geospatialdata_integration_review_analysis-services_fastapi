import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Container,
  Grid,
  Paper,
  Tabs,
  Tab,
  Button,
  Alert,
  Snackbar,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import StorageIcon from '@mui/icons-material/Storage';
import Layout from '../../components/layout/Layout';
import DuckDBQueryEditor from '../../components/duckdb/DuckDBQueryEditor';
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
      id={`duckdb-tabpanel-${index}`}
      aria-labelledby={`duckdb-tab-${index}`}
      {...other}
      style={{ height: '100%' }}
    >
      {value === index && (
        <Box sx={{ height: '100%' }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const DuckDBPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [duckdbStatus, setDuckdbStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [databases, setDatabases] = useState<string[]>([]);
  const [selectedDatabase, setSelectedDatabase] = useState<string | null>(null);
  const [createDatabaseDialogOpen, setCreateDatabaseDialogOpen] = useState(false);
  const [newDatabaseName, setNewDatabaseName] = useState('');
  const [uploadFileDialogOpen, setUploadFileDialogOpen] = useState(false);
  const [uploadTableName, setUploadTableName] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });

  // Check DuckDB status on component mount
  useEffect(() => {
    checkDuckDBStatus();
  }, []);

  // Check DuckDB status
  const checkDuckDBStatus = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.get('/duckdb/status');
      setDuckdbStatus(response.data);
      
      // Get list of databases
      const dbDir = response.data.data_dir;
      
      // TODO: Replace with actual API call to list databases
      // For now, we'll just use a mock list
      setDatabases(['default.duckdb', 'geospatial.duckdb', 'analytics.duckdb']);
      
      setLoading(false);
    } catch (err) {
      console.error('Error checking DuckDB status:', err);
      setError('Failed to connect to DuckDB');
      setLoading(false);
    }
  };

  // Handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Handle database selection
  const handleDatabaseSelect = (dbName: string) => {
    setSelectedDatabase(dbName);
    setTabValue(0); // Switch to query tab
  };

  // Handle create database dialog open
  const handleCreateDatabaseDialogOpen = () => {
    setCreateDatabaseDialogOpen(true);
  };

  // Handle create database dialog close
  const handleCreateDatabaseDialogClose = () => {
    setCreateDatabaseDialogOpen(false);
    setNewDatabaseName('');
  };

  // Handle create database
  const handleCreateDatabase = async () => {
    if (!newDatabaseName) {
      setNotification({
        open: true,
        message: 'Please enter a database name',
        severity: 'error'
      });
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await apiClient.post('/duckdb/databases', {
        db_name: newDatabaseName
      });
      
      // Add the new database to the list
      setDatabases([...databases, `${newDatabaseName}.duckdb`]);
      
      setNotification({
        open: true,
        message: `Database ${newDatabaseName} created successfully`,
        severity: 'success'
      });
      
      // Select the new database
      setSelectedDatabase(`${newDatabaseName}.duckdb`);
      
      setCreateDatabaseDialogOpen(false);
      setNewDatabaseName('');
      setLoading(false);
    } catch (err) {
      console.error('Error creating database:', err);
      
      setNotification({
        open: true,
        message: 'Failed to create database',
        severity: 'error'
      });
      
      setLoading(false);
    }
  };

  // Handle upload file dialog open
  const handleUploadFileDialogOpen = () => {
    setUploadFileDialogOpen(true);
  };

  // Handle upload file dialog close
  const handleUploadFileDialogClose = () => {
    setUploadFileDialogOpen(false);
    setUploadTableName('');
    setSelectedFile(null);
  };

  // Handle file selection
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
      
      // Set default table name based on file name
      const fileName = event.target.files[0].name;
      const tableName = fileName.split('.')[0].replace(/[^a-zA-Z0-9_]/g, '_');
      setUploadTableName(tableName);
    }
  };

  // Handle file upload
  const handleFileUpload = async () => {
    if (!selectedFile || !uploadTableName) {
      setNotification({
        open: true,
        message: 'Please select a file and enter a table name',
        severity: 'error'
      });
      return;
    }
    
    setLoading(true);
    
    try {
      // Create form data
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('table_name', uploadTableName);
      
      if (selectedDatabase) {
        formData.append('db_path', `${duckdbStatus.data_dir}/${selectedDatabase}`);
      }
      
      // Upload the file
      const response = await apiClient.post('/duckdb/tables/upload', formData);
      
      setNotification({
        open: true,
        message: `Table ${uploadTableName} created successfully`,
        severity: 'success'
      });
      
      setUploadFileDialogOpen(false);
      setUploadTableName('');
      setSelectedFile(null);
      setLoading(false);
    } catch (err) {
      console.error('Error uploading file:', err);
      
      setNotification({
        open: true,
        message: 'Failed to upload file',
        severity: 'error'
      });
      
      setLoading(false);
    }
  };

  // Close notification
  const handleCloseNotification = () => {
    setNotification({
      ...notification,
      open: false
    });
  };

  if (loading && !duckdbStatus) {
    return (
      <Layout title="DuckDB Analytics">
        <Container maxWidth={false} sx={{ mt: 4, mb: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
          <CircularProgress />
        </Container>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout title="DuckDB Analytics">
        <Container maxWidth={false} sx={{ mt: 4, mb: 4 }}>
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
          
          <Button variant="contained" onClick={checkDuckDBStatus}>
            Retry Connection
          </Button>
        </Container>
      </Layout>
    );
  }

  return (
    <Layout title="DuckDB Analytics">
      <Container maxWidth={false} sx={{ mt: 4, mb: 4, height: 'calc(100vh - 128px)' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">
            DuckDB Analytics
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={handleCreateDatabaseDialogOpen}
            >
              New Database
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<UploadFileIcon />}
              onClick={handleUploadFileDialogOpen}
              disabled={!selectedDatabase}
            >
              Upload File
            </Button>
          </Box>
        </Box>
        
        <Grid container spacing={3} sx={{ height: 'calc(100% - 60px)' }}>
          {/* Database Sidebar */}
          <Grid item xs={12} md={3} lg={2}>
            <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom>
                Databases
              </Typography>
              
              <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
                {databases.map((db) => (
                  <Box
                    key={db}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      p: 1,
                      borderRadius: 1,
                      cursor: 'pointer',
                      bgcolor: selectedDatabase === db ? 'primary.light' : 'transparent',
                      '&:hover': {
                        bgcolor: selectedDatabase === db ? 'primary.light' : 'action.hover'
                      }
                    }}
                    onClick={() => handleDatabaseSelect(db)}
                  >
                    <StorageIcon sx={{ mr: 1, fontSize: 20 }} />
                    <Typography variant="body2">
                      {db}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Paper>
          </Grid>
          
          {/* Main Content */}
          <Grid item xs={12} md={9} lg={10} sx={{ height: '100%' }}>
            {selectedDatabase ? (
              <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                  <Tabs value={tabValue} onChange={handleTabChange}>
                    <Tab label="Query" id="duckdb-tab-0" aria-controls="duckdb-tabpanel-0" />
                    <Tab label="Tables" id="duckdb-tab-1" aria-controls="duckdb-tabpanel-1" />
                    <Tab label="Visualizations" id="duckdb-tab-2" aria-controls="duckdb-tabpanel-2" />
                  </Tabs>
                </Box>
                
                <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
                  <TabPanel value={tabValue} index={0}>
                    <DuckDBQueryEditor
                      dbPath={`${duckdbStatus.data_dir}/${selectedDatabase}`}
                    />
                  </TabPanel>
                  
                  <TabPanel value={tabValue} index={1}>
                    <Typography variant="h6">Tables</Typography>
                    {/* Table list component will go here */}
                  </TabPanel>
                  
                  <TabPanel value={tabValue} index={2}>
                    <Typography variant="h6">Visualizations</Typography>
                    {/* Visualization component will go here */}
                  </TabPanel>
                </Box>
              </Box>
            ) : (
              <Paper sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
                <Typography variant="h6" gutterBottom>
                  Select a database or create a new one
                </Typography>
                
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleCreateDatabaseDialogOpen}
                  sx={{ mt: 2 }}
                >
                  Create Database
                </Button>
              </Paper>
            )}
          </Grid>
        </Grid>
      </Container>
      
      {/* Create Database Dialog */}
      <Dialog open={createDatabaseDialogOpen} onClose={handleCreateDatabaseDialogClose}>
        <DialogTitle>Create Database</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Database Name"
            fullWidth
            value={newDatabaseName}
            onChange={(e) => setNewDatabaseName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCreateDatabaseDialogClose}>Cancel</Button>
          <Button onClick={handleCreateDatabase} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>
      
      {/* Upload File Dialog */}
      <Dialog open={uploadFileDialogOpen} onClose={handleUploadFileDialogClose}>
        <DialogTitle>Upload File</DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <input
              type="file"
              id="file-upload"
              style={{ display: 'none' }}
              onChange={handleFileSelect}
            />
            <label htmlFor="file-upload">
              <Button
                variant="outlined"
                component="span"
                startIcon={<UploadFileIcon />}
              >
                Select File
              </Button>
            </label>
            
            {selectedFile && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                Selected file: {selectedFile.name}
              </Typography>
            )}
          </Box>
          
          <TextField
            margin="dense"
            label="Table Name"
            fullWidth
            value={uploadTableName}
            onChange={(e) => setUploadTableName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleUploadFileDialogClose}>Cancel</Button>
          <Button
            onClick={handleFileUpload}
            variant="contained"
            disabled={!selectedFile || !uploadTableName}
          >
            Upload
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Notification */}
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
      
      {/* Loading Overlay */}
      {loading && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'rgba(255, 255, 255, 0.7)',
            zIndex: 9999
          }}
        >
          <CircularProgress />
        </Box>
      )}
    </Layout>
  );
};

export default DuckDBPage;
