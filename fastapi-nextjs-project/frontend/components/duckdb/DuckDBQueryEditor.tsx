import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  IconButton,
  Divider,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Tooltip,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  Chip
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import SaveIcon from '@mui/icons-material/Save';
import DownloadIcon from '@mui/icons-material/Download';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import BarChartIcon from '@mui/icons-material/BarChart';
import MapIcon from '@mui/icons-material/Map';
import StorageIcon from '@mui/icons-material/Storage';
import { apiClient } from '../../lib/api';
import dynamic from 'next/dynamic';

// Dynamically import the Monaco Editor to avoid SSR issues
const MonacoEditor = dynamic(
  () => import('@monaco-editor/react'),
  { ssr: false }
);

// Dynamically import the visualization components
const DataTable = dynamic(
  () => import('./visualizations/DataTable'),
  { ssr: false, loading: () => <CircularProgress /> }
);

const DataChart = dynamic(
  () => import('./visualizations/DataChart'),
  { ssr: false, loading: () => <CircularProgress /> }
);

const DataMap = dynamic(
  () => import('./visualizations/DataMap'),
  { ssr: false, loading: () => <CircularProgress /> }
);

interface DuckDBQueryEditorProps {
  initialQuery?: string;
  dbPath?: string;
  onQueryExecuted?: (results: any[]) => void;
}

const DuckDBQueryEditor: React.FC<DuckDBQueryEditorProps> = ({
  initialQuery = 'SELECT * FROM information_schema.tables LIMIT 10;',
  dbPath,
  onQueryExecuted
}) => {
  const [query, setQuery] = useState<string>(initialQuery);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState<number>(0);
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [tableSchema, setTableSchema] = useState<any[]>([]);
  const [tableMenuAnchorEl, setTableMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [exportDialogOpen, setExportDialogOpen] = useState<boolean>(false);
  const [exportFormat, setExportFormat] = useState<string>('csv');
  const [hasGeometryColumn, setHasGeometryColumn] = useState<boolean>(false);
  const [geometryColumn, setGeometryColumn] = useState<string>('');
  
  const editorRef = useRef<any>(null);

  // Load tables on component mount
  useEffect(() => {
    fetchTables();
  }, [dbPath]);

  // Check if results have a geometry column
  useEffect(() => {
    if (results.length > 0) {
      const firstRow = results[0];
      const geometryColumns = Object.keys(firstRow).filter(key => {
        const value = firstRow[key];
        return typeof value === 'string' && (
          value.startsWith('POINT') ||
          value.startsWith('LINESTRING') ||
          value.startsWith('POLYGON') ||
          value.startsWith('MULTIPOINT') ||
          value.startsWith('MULTILINESTRING') ||
          value.startsWith('MULTIPOLYGON') ||
          value.startsWith('GEOMETRYCOLLECTION')
        );
      });
      
      setHasGeometryColumn(geometryColumns.length > 0);
      if (geometryColumns.length > 0) {
        setGeometryColumn(geometryColumns[0]);
      }
    } else {
      setHasGeometryColumn(false);
      setGeometryColumn('');
    }
  }, [results]);

  // Fetch tables from the API
  const fetchTables = async () => {
    try {
      const response = await apiClient.get('/duckdb/tables', {
        params: { db_path: dbPath }
      });
      
      setTables(response.data || []);
    } catch (err) {
      console.error('Error fetching tables:', err);
      setError('Failed to fetch tables');
    }
  };

  // Fetch table schema from the API
  const fetchTableSchema = async (tableName: string) => {
    try {
      const response = await apiClient.get(`/duckdb/tables/${tableName}/schema`, {
        params: { db_path: dbPath }
      });
      
      setTableSchema(response.data || []);
    } catch (err) {
      console.error(`Error fetching schema for table ${tableName}:`, err);
      setError(`Failed to fetch schema for table ${tableName}`);
    }
  };

  // Handle editor mount
  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;
  };

  // Handle query change
  const handleQueryChange = (value: string | undefined) => {
    setQuery(value || '');
  };

  // Execute the query
  const executeQuery = async () => {
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.post('/duckdb/query', {
        query,
        db_path: dbPath
      });
      
      setResults(response.data || []);
      setTabValue(0); // Switch to results tab
      
      if (onQueryExecuted) {
        onQueryExecuted(response.data || []);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error executing query:', err);
      setError('Failed to execute query');
      setLoading(false);
    }
  };

  // Handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Handle table click
  const handleTableClick = (tableName: string) => {
    setSelectedTable(tableName);
    fetchTableSchema(tableName);
    setQuery(`SELECT * FROM ${tableName} LIMIT 100;`);
  };

  // Handle table menu open
  const handleTableMenuOpen = (event: React.MouseEvent<HTMLElement>, tableName: string) => {
    event.stopPropagation();
    setTableMenuAnchorEl(event.currentTarget);
    setSelectedTable(tableName);
  };

  // Handle table menu close
  const handleTableMenuClose = () => {
    setTableMenuAnchorEl(null);
  };

  // Handle preview table
  const handlePreviewTable = () => {
    handleTableMenuClose();
    if (selectedTable) {
      setQuery(`SELECT * FROM ${selectedTable} LIMIT 100;`);
      executeQuery();
    }
  };

  // Handle export table
  const handleExportTable = () => {
    handleTableMenuClose();
    setExportDialogOpen(true);
  };

  // Handle export dialog close
  const handleExportDialogClose = () => {
    setExportDialogOpen(false);
  };

  // Handle export confirm
  const handleExportConfirm = async () => {
    if (!selectedTable) {
      return;
    }
    
    try {
      // For download, we need to use a different approach
      const url = `/api/v1/duckdb/tables/export/download?table_name=${selectedTable}&output_format=${exportFormat}${dbPath ? `&db_path=${dbPath}` : ''}`;
      
      // Open the URL in a new tab
      window.open(url, '_blank');
      
      setExportDialogOpen(false);
    } catch (err) {
      console.error('Error exporting table:', err);
      setError('Failed to export table');
    }
  };

  // Handle copy query
  const handleCopyQuery = () => {
    navigator.clipboard.writeText(query);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', p: 1, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          DuckDB Query Editor
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<PlayArrowIcon />}
            onClick={executeQuery}
            disabled={loading}
          >
            Execute
          </Button>
          
          <Tooltip title="Copy Query">
            <IconButton onClick={handleCopyQuery}>
              <ContentCopyIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      
      <Box sx={{ display: 'flex', height: 'calc(100% - 56px)' }}>
        {/* Left sidebar - Tables */}
        <Box sx={{ width: 250, borderRight: 1, borderColor: 'divider', overflow: 'auto' }}>
          <Box sx={{ p: 1, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="subtitle1">Tables</Typography>
          </Box>
          
          <Box sx={{ p: 1 }}>
            {tables.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No tables found
              </Typography>
            ) : (
              tables.map((table) => (
                <Box
                  key={table}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    p: 1,
                    borderRadius: 1,
                    cursor: 'pointer',
                    '&:hover': {
                      bgcolor: 'action.hover'
                    }
                  }}
                  onClick={() => handleTableClick(table)}
                >
                  <StorageIcon sx={{ mr: 1, fontSize: 20 }} />
                  <Typography variant="body2" sx={{ flexGrow: 1 }}>
                    {table}
                  </Typography>
                  <IconButton
                    size="small"
                    onClick={(e) => handleTableMenuOpen(e, table)}
                  >
                    <MoreVertIcon fontSize="small" />
                  </IconButton>
                </Box>
              ))
            )}
          </Box>
        </Box>
        
        {/* Main content */}
        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
          {/* Query editor */}
          <Box sx={{ height: '40%', borderBottom: 1, borderColor: 'divider' }}>
            <MonacoEditor
              height="100%"
              language="sql"
              theme="vs-dark"
              value={query}
              onChange={handleQueryChange}
              onMount={handleEditorDidMount}
              options={{
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                automaticLayout: true
              }}
            />
          </Box>
          
          {/* Results */}
          <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
            {error && (
              <Alert severity="error" sx={{ m: 1 }}>
                {error}
              </Alert>
            )}
            
            <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tab label="Results" icon={<VisibilityIcon />} iconPosition="start" />
              {hasGeometryColumn && <Tab label="Map" icon={<MapIcon />} iconPosition="start" />}
              <Tab label="Chart" icon={<BarChartIcon />} iconPosition="start" />
            </Tabs>
            
            <Box sx={{ flexGrow: 1, overflow: 'auto', p: 1 }}>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                  <CircularProgress />
                </Box>
              ) : (
                <>
                  {tabValue === 0 && (
                    <DataTable data={results} />
                  )}
                  
                  {tabValue === 1 && hasGeometryColumn && (
                    <DataMap data={results} geometryColumn={geometryColumn} />
                  )}
                  
                  {tabValue === (hasGeometryColumn ? 2 : 1) && (
                    <DataChart data={results} />
                  )}
                </>
              )}
            </Box>
          </Box>
        </Box>
        
        {/* Right sidebar - Schema */}
        {selectedTable && (
          <Box sx={{ width: 250, borderLeft: 1, borderColor: 'divider', overflow: 'auto' }}>
            <Box sx={{ p: 1, borderBottom: 1, borderColor: 'divider' }}>
              <Typography variant="subtitle1">Schema: {selectedTable}</Typography>
            </Box>
            
            <Box sx={{ p: 1 }}>
              {tableSchema.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No schema information available
                </Typography>
              ) : (
                tableSchema.map((column) => (
                  <Box
                    key={column.name}
                    sx={{
                      display: 'flex',
                      flexDirection: 'column',
                      p: 1,
                      borderBottom: 1,
                      borderColor: 'divider'
                    }}
                  >
                    <Typography variant="body2" fontWeight="bold">
                      {column.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {column.type}
                    </Typography>
                  </Box>
                ))
              )}
            </Box>
          </Box>
        )}
      </Box>
      
      {/* Table Menu */}
      <Menu
        anchorEl={tableMenuAnchorEl}
        open={Boolean(tableMenuAnchorEl)}
        onClose={handleTableMenuClose}
      >
        <MenuItem onClick={handlePreviewTable}>
          <ListItemIcon>
            <VisibilityIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Preview" />
        </MenuItem>
        <MenuItem onClick={handleExportTable}>
          <ListItemIcon>
            <DownloadIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Export" />
        </MenuItem>
      </Menu>
      
      {/* Export Dialog */}
      <Dialog open={exportDialogOpen} onClose={handleExportDialogClose}>
        <DialogTitle>Export Table</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Format</InputLabel>
            <Select
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value)}
              label="Format"
            >
              <MenuItem value="csv">CSV</MenuItem>
              <MenuItem value="parquet">Parquet</MenuItem>
              <MenuItem value="json">JSON</MenuItem>
              {hasGeometryColumn && (
                <>
                  <MenuItem value="geojson">GeoJSON</MenuItem>
                  <MenuItem value="shp">Shapefile</MenuItem>
                  <MenuItem value="gpkg">GeoPackage</MenuItem>
                </>
              )}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleExportDialogClose}>Cancel</Button>
          <Button onClick={handleExportConfirm} variant="contained">Export</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DuckDBQueryEditor;
