import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Grid,
  Divider,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Card,
  CardContent,
  CardActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Tabs,
  Tab
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import RefreshIcon from '@mui/icons-material/Refresh';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import SaveIcon from '@mui/icons-material/Save';
import DatabaseIcon from '@mui/icons-material/Storage';
import TableIcon from '@mui/icons-material/TableChart';
import { apiClient } from '../../lib/api';
import { useSnackbar } from 'notistack';
import CodeEditor from '../common/CodeEditor';

interface OdbcConnection {
  name: string;
  connection_string: string;
  driver?: string;
  server?: string;
  database?: string;
}

interface OdbcConnectionManagerProps {
  dbPath?: string;
}

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
      id={`odbc-tabpanel-${index}`}
      aria-labelledby={`odbc-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const OdbcConnectionManager: React.FC<OdbcConnectionManagerProps> = ({ dbPath }) => {
  const { enqueueSnackbar } = useSnackbar();
  const [tabValue, setTabValue] = useState(0);
  
  // Connection state
  const [connections, setConnections] = useState<OdbcConnection[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // New connection dialog
  const [showConnectionDialog, setShowConnectionDialog] = useState<boolean>(false);
  const [connectionName, setConnectionName] = useState<string>('');
  const [connectionString, setConnectionString] = useState<string>('');
  const [selectedDriver, setSelectedDriver] = useState<string>('');
  const [server, setServer] = useState<string>('');
  const [database, setDatabase] = useState<string>('');
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [isEditMode, setIsEditMode] = useState<boolean>(false);
  
  // Query state
  const [selectedConnection, setSelectedConnection] = useState<string>('');
  const [query, setQuery] = useState<string>('');
  const [queryResults, setQueryResults] = useState<any[]>([]);
  const [queryColumns, setQueryColumns] = useState<string[]>([]);
  const [isQueryLoading, setIsQueryLoading] = useState<boolean>(false);
  const [queryError, setQueryError] = useState<string | null>(null);
  
  // Import state
  const [importConnection, setImportConnection] = useState<string>('');
  const [importQuery, setImportQuery] = useState<string>('');
  const [targetTable, setTargetTable] = useState<string>('');
  const [isImportLoading, setIsImportLoading] = useState<boolean>(false);
  const [importError, setImportError] = useState<string | null>(null);
  
  // Extension status
  const [extensionStatus, setExtensionStatus] = useState<any>(null);
  const [isStatusLoading, setIsStatusLoading] = useState<boolean>(false);
  
  // Load connections on mount
  useEffect(() => {
    fetchConnections();
    fetchExtensionStatus();
  }, []);
  
  // Fetch ODBC connections
  const fetchConnections = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.get('/api/v1/duckdb/odbc/connections');
      setConnections(response.data.connections || []);
    } catch (error) {
      console.error('Error fetching ODBC connections:', error);
      setError('Failed to fetch ODBC connections');
      enqueueSnackbar('Failed to fetch ODBC connections', { variant: 'error' });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Fetch extension status
  const fetchExtensionStatus = async () => {
    setIsStatusLoading(true);
    
    try {
      const response = await apiClient.get('/api/v1/duckdb/odbc/status');
      setExtensionStatus(response.data);
    } catch (error) {
      console.error('Error fetching extension status:', error);
    } finally {
      setIsStatusLoading(false);
    }
  };
  
  // Open connection dialog
  const openConnectionDialog = (connection?: OdbcConnection) => {
    if (connection) {
      // Edit mode
      setIsEditMode(true);
      setConnectionName(connection.name);
      setConnectionString(connection.connection_string);
      
      // Try to parse connection string
      const driverMatch = connection.connection_string.match(/Driver=\{([^}]*)\}/i);
      if (driverMatch) {
        setSelectedDriver(driverMatch[1]);
      }
      
      const serverMatch = connection.connection_string.match(/Server=([^;]*)/i);
      if (serverMatch) {
        setServer(serverMatch[1]);
      }
      
      const databaseMatch = connection.connection_string.match(/Database=([^;]*)/i);
      if (databaseMatch) {
        setDatabase(databaseMatch[1]);
      }
      
      const usernameMatch = connection.connection_string.match(/(UID|User ID)=([^;]*)/i);
      if (usernameMatch) {
        setUsername(usernameMatch[2]);
      }
      
      // Don't set password - it's masked in the connection string
    } else {
      // New connection mode
      setIsEditMode(false);
      setConnectionName('');
      setConnectionString('');
      setSelectedDriver('');
      setServer('');
      setDatabase('');
      setUsername('');
      setPassword('');
    }
    
    setShowConnectionDialog(true);
  };
  
  // Close connection dialog
  const closeConnectionDialog = () => {
    setShowConnectionDialog(false);
  };
  
  // Build connection string from form
  const buildConnectionString = () => {
    if (!selectedDriver) return '';
    
    let connStr = `Driver={${selectedDriver}};`;
    
    if (server) {
      connStr += `Server=${server};`;
    }
    
    if (database) {
      connStr += `Database=${database};`;
    }
    
    if (username) {
      connStr += `UID=${username};`;
    }
    
    if (password) {
      connStr += `PWD=${password};`;
    }
    
    return connStr;
  };
  
  // Update connection string when form changes
  useEffect(() => {
    if (selectedDriver) {
      setConnectionString(buildConnectionString());
    }
  }, [selectedDriver, server, database, username, password]);
  
  // Save connection
  const saveConnection = async () => {
    if (!connectionName || !connectionString) {
      enqueueSnackbar('Please fill in all required fields', { variant: 'warning' });
      return;
    }
    
    try {
      const response = await apiClient.post('/api/v1/duckdb/odbc/connect', {
        name: connectionName,
        connection_string: connectionString,
        db_path: dbPath
      });
      
      enqueueSnackbar(response.data.message || 'Connection saved successfully', { variant: 'success' });
      closeConnectionDialog();
      fetchConnections();
    } catch (error) {
      console.error('Error saving connection:', error);
      enqueueSnackbar('Failed to save connection', { variant: 'error' });
    }
  };
  
  // Execute query
  const executeQuery = async () => {
    if (!selectedConnection || !query) {
      enqueueSnackbar('Please select a connection and enter a query', { variant: 'warning' });
      return;
    }
    
    setIsQueryLoading(true);
    setQueryError(null);
    
    try {
      const response = await apiClient.post('/api/v1/duckdb/odbc/query', {
        connection_name: selectedConnection,
        query,
        db_path: dbPath
      });
      
      if (response.data && response.data.length > 0) {
        setQueryResults(response.data);
        setQueryColumns(Object.keys(response.data[0]));
      } else {
        setQueryResults([]);
        setQueryColumns([]);
        enqueueSnackbar('Query returned no results', { variant: 'info' });
      }
    } catch (error) {
      console.error('Error executing query:', error);
      setQueryError('Failed to execute query');
      enqueueSnackbar('Failed to execute query', { variant: 'error' });
    } finally {
      setIsQueryLoading(false);
    }
  };
  
  // Import table
  const importTable = async () => {
    if (!importConnection || !importQuery || !targetTable) {
      enqueueSnackbar('Please fill in all required fields', { variant: 'warning' });
      return;
    }
    
    setIsImportLoading(true);
    setImportError(null);
    
    try {
      const response = await apiClient.post('/api/v1/duckdb/odbc/import', {
        connection_name: importConnection,
        source_query: importQuery,
        target_table: targetTable,
        db_path: dbPath
      });
      
      enqueueSnackbar(response.data.message || 'Table imported successfully', { variant: 'success' });
      setImportQuery('');
      setTargetTable('');
    } catch (error) {
      console.error('Error importing table:', error);
      setImportError('Failed to import table');
      enqueueSnackbar('Failed to import table', { variant: 'error' });
    } finally {
      setIsImportLoading(false);
    }
  };
  
  // Handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        ODBC Connection Manager
      </Typography>
      
      {extensionStatus && (
        <Paper sx={{ p: 2, mb: 3, display: 'flex', alignItems: 'center' }}>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="subtitle1">
              Nanodbc Extension Status: 
              <Chip 
                label={extensionStatus.loaded ? 'Loaded' : 'Not Loaded'} 
                color={extensionStatus.loaded ? 'success' : 'error'}
                size="small"
                sx={{ ml: 1 }}
              />
            </Typography>
            {extensionStatus.version && (
              <Typography variant="body2" color="text.secondary">
                Version: {extensionStatus.version}
              </Typography>
            )}
          </Box>
          <Button
            startIcon={<RefreshIcon />}
            onClick={fetchExtensionStatus}
            disabled={isStatusLoading}
          >
            Refresh
          </Button>
        </Paper>
      )}
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="ODBC tabs">
          <Tab label="Connections" id="odbc-tab-0" aria-controls="odbc-tabpanel-0" />
          <Tab label="Query" id="odbc-tab-1" aria-controls="odbc-tabpanel-1" />
          <Tab label="Import" id="odbc-tab-2" aria-controls="odbc-tabpanel-2" />
        </Tabs>
      </Box>
      
      <TabPanel value={tabValue} index={0}>
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            ODBC Connections
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => openConnectionDialog()}
          >
            Add Connection
          </Button>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : connections.length === 0 ? (
          <Alert severity="info" sx={{ mb: 3 }}>
            No ODBC connections configured. Click "Add Connection" to create one.
          </Alert>
        ) : (
          <Grid container spacing={3}>
            {connections.map((connection) => (
              <Grid item xs={12} md={6} lg={4} key={connection.name}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {connection.name}
                    </Typography>
                    
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {connection.connection_string}
                    </Typography>
                    
                    <Box sx={{ mt: 2 }}>
                      {connection.driver && (
                        <Chip 
                          label={`Driver: ${connection.driver}`} 
                          size="small" 
                          sx={{ mr: 1, mb: 1 }} 
                        />
                      )}
                      {connection.server && (
                        <Chip 
                          label={`Server: ${connection.server}`} 
                          size="small" 
                          sx={{ mr: 1, mb: 1 }} 
                        />
                      )}
                      {connection.database && (
                        <Chip 
                          label={`Database: ${connection.database}`} 
                          size="small" 
                          sx={{ mr: 1, mb: 1 }} 
                        />
                      )}
                    </Box>
                  </CardContent>
                  <CardActions>
                    <Button 
                      size="small" 
                      startIcon={<EditIcon />}
                      onClick={() => openConnectionDialog(connection)}
                    >
                      Edit
                    </Button>
                    <Button 
                      size="small" 
                      startIcon={<TableIcon />}
                      onClick={() => {
                        setSelectedConnection(connection.name);
                        setTabValue(1);
                      }}
                    >
                      Query
                    </Button>
                    <Button 
                      size="small" 
                      startIcon={<DatabaseIcon />}
                      onClick={() => {
                        setImportConnection(connection.name);
                        setTabValue(2);
                      }}
                    >
                      Import
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </TabPanel>
      
      <TabPanel value={tabValue} index={1}>
        <Typography variant="h6" gutterBottom>
          Query ODBC Database
        </Typography>
        
        <Paper sx={{ p: 3, mb: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel id="connection-select-label">Connection</InputLabel>
                <Select
                  labelId="connection-select-label"
                  value={selectedConnection}
                  onChange={(e) => setSelectedConnection(e.target.value)}
                  label="Connection"
                >
                  {connections.map((conn) => (
                    <MenuItem key={conn.name} value={conn.name}>{conn.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                SQL Query
              </Typography>
              <CodeEditor
                value={query}
                onChange={setQuery}
                language="sql"
                height="150px"
                placeholder="Enter SQL query (e.g., SELECT * FROM customers)"
              />
            </Grid>
          </Grid>
          
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
            <Button
              variant="contained"
              onClick={executeQuery}
              disabled={!selectedConnection || !query || isQueryLoading}
              startIcon={isQueryLoading ? <CircularProgress size={20} /> : <PlayArrowIcon />}
            >
              Execute Query
            </Button>
          </Box>
        </Paper>
        
        {queryError && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {queryError}
          </Alert>
        )}
        
        {queryResults.length > 0 && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Query Results
            </Typography>
            
            <TableContainer sx={{ maxHeight: 400 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    {queryColumns.map((column) => (
                      <TableCell key={column}>{column}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {queryResults.map((row, rowIndex) => (
                    <TableRow key={rowIndex}>
                      {queryColumns.map((column) => (
                        <TableCell key={column}>{row[column]?.toString() || 'NULL'}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
              <Button
                variant="outlined"
                startIcon={<SaveIcon />}
                onClick={() => {
                  const csvContent = [
                    queryColumns.join(','),
                    ...queryResults.map(row => queryColumns.map(col => row[col] || '').join(','))
                  ].join('\n');
                  
                  const blob = new Blob([csvContent], { type: 'text/csv' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = 'query_results.csv';
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                  URL.revokeObjectURL(url);
                }}
              >
                Export CSV
              </Button>
            </Box>
          </Paper>
        )}
      </TabPanel>
      
      <TabPanel value={tabValue} index={2}>
        <Typography variant="h6" gutterBottom>
          Import Data from ODBC
        </Typography>
        
        <Paper sx={{ p: 3, mb: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="import-connection-label">Connection</InputLabel>
                <Select
                  labelId="import-connection-label"
                  value={importConnection}
                  onChange={(e) => setImportConnection(e.target.value)}
                  label="Connection"
                >
                  {connections.map((conn) => (
                    <MenuItem key={conn.name} value={conn.name}>{conn.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Target Table Name"
                value={targetTable}
                onChange={(e) => setTargetTable(e.target.value)}
                helperText="Name of the table to create in DuckDB"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Source Query
              </Typography>
              <CodeEditor
                value={importQuery}
                onChange={setImportQuery}
                language="sql"
                height="150px"
                placeholder="Enter SQL query to import data (e.g., SELECT * FROM customers)"
              />
            </Grid>
          </Grid>
          
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
            <Button
              variant="contained"
              onClick={importTable}
              disabled={!importConnection || !importQuery || !targetTable || isImportLoading}
              startIcon={isImportLoading ? <CircularProgress size={20} /> : <DatabaseIcon />}
            >
              Import Data
            </Button>
          </Box>
        </Paper>
        
        {importError && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {importError}
          </Alert>
        )}
      </TabPanel>
      
      {/* Connection Dialog */}
      <Dialog 
        open={showConnectionDialog} 
        onClose={closeConnectionDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>{isEditMode ? 'Edit Connection' : 'Add Connection'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 0 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Connection Name"
                value={connectionName}
                onChange={(e) => setConnectionName(e.target.value)}
                disabled={isEditMode}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="driver-select-label">Driver</InputLabel>
                <Select
                  labelId="driver-select-label"
                  value={selectedDriver}
                  onChange={(e) => setSelectedDriver(e.target.value)}
                  label="Driver"
                >
                  <MenuItem value="SQL Server">SQL Server</MenuItem>
                  <MenuItem value="MySQL ODBC 8.0 Driver">MySQL</MenuItem>
                  <MenuItem value="PostgreSQL ODBC Driver">PostgreSQL</MenuItem>
                  <MenuItem value="Oracle in OraClient12Home1">Oracle</MenuItem>
                  <MenuItem value="Snowflake">Snowflake</MenuItem>
                  <MenuItem value="ODBC Driver 17 for SQL Server">ODBC Driver 17 for SQL Server</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Server"
                value={server}
                onChange={(e) => setServer(e.target.value)}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Database"
                value={database}
                onChange={(e) => setDatabase(e.target.value)}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>Connection String</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <TextField
                    fullWidth
                    label="Connection String"
                    value={connectionString}
                    onChange={(e) => setConnectionString(e.target.value)}
                    multiline
                    rows={3}
                    required
                  />
                </AccordionDetails>
              </Accordion>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeConnectionDialog}>Cancel</Button>
          <Button 
            onClick={saveConnection} 
            variant="contained"
            disabled={!connectionName || !connectionString}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OdbcConnectionManager;
