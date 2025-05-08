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
  Chip,
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
  TablePagination
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import SaveIcon from '@mui/icons-material/Save';
import InfoIcon from '@mui/icons-material/Info';
import CodeIcon from '@mui/icons-material/Code';
import { apiClient } from '../../lib/api';
import { useSnackbar } from 'notistack';
import CodeEditor from '../common/CodeEditor';

interface Column {
  name: string;
  label: string;
}

interface PivotTableBuilderProps {
  dbPath?: string;
}

const PivotTableBuilder: React.FC<PivotTableBuilderProps> = ({ dbPath }) => {
  const { enqueueSnackbar } = useSnackbar();
  
  // Query state
  const [query, setQuery] = useState<string>('');
  const [isQueryValid, setIsQueryValid] = useState<boolean>(false);
  const [queryColumns, setQueryColumns] = useState<string[]>([]);
  const [queryPreview, setQueryPreview] = useState<any[]>([]);
  const [isQueryLoading, setIsQueryLoading] = useState<boolean>(false);
  const [queryError, setQueryError] = useState<string | null>(null);
  
  // Pivot table configuration
  const [pivotColumn, setPivotColumn] = useState<string>('');
  const [rowIdentifier, setRowIdentifier] = useState<string>('');
  const [valueColumn, setValueColumn] = useState<string>('');
  const [aggregationFunction, setAggregationFunction] = useState<string>('sum');
  const [columnMappings, setColumnMappings] = useState<Column[]>([]);
  const [showColumnMappingDialog, setShowColumnMappingDialog] = useState<boolean>(false);
  const [newColumnName, setNewColumnName] = useState<string>('');
  const [newColumnLabel, setNewColumnLabel] = useState<string>('');
  
  // Pivot table results
  const [pivotData, setPivotData] = useState<any[]>([]);
  const [pivotColumns, setPivotColumns] = useState<string[]>([]);
  const [isPivotLoading, setIsPivotLoading] = useState<boolean>(false);
  const [pivotError, setPivotError] = useState<string | null>(null);
  
  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // SQL preview
  const [showSqlPreview, setShowSqlPreview] = useState<boolean>(false);
  const [sqlPreview, setSqlPreview] = useState<string>('');
  
  // Validate query when it changes
  useEffect(() => {
    setIsQueryValid(query.trim().length > 0 && query.toUpperCase().includes('SELECT'));
  }, [query]);
  
  // Execute the query to get columns and preview data
  const executeQuery = async () => {
    if (!isQueryValid) return;
    
    setIsQueryLoading(true);
    setQueryError(null);
    
    try {
      const response = await apiClient.post('/api/v1/duckdb/query', {
        query: `${query} LIMIT 10`,
        db_path: dbPath
      });
      
      if (response.data && response.data.length > 0) {
        setQueryPreview(response.data);
        setQueryColumns(Object.keys(response.data[0]));
      } else {
        setQueryPreview([]);
        setQueryColumns([]);
        enqueueSnackbar('Query returned no results', { variant: 'warning' });
      }
    } catch (error) {
      console.error('Error executing query:', error);
      setQueryError('Failed to execute query. Please check your SQL syntax.');
      enqueueSnackbar('Failed to execute query', { variant: 'error' });
    } finally {
      setIsQueryLoading(false);
    }
  };
  
  // Generate pivot table
  const generatePivotTable = async () => {
    if (!isQueryValid || !pivotColumn || !rowIdentifier || !valueColumn) {
      enqueueSnackbar('Please fill in all required fields', { variant: 'warning' });
      return;
    }
    
    setIsPivotLoading(true);
    setPivotError(null);
    
    try {
      // Prepare column mappings
      const columnNames: Record<string, string> = {};
      columnMappings.forEach(mapping => {
        columnNames[mapping.name] = mapping.label;
      });
      
      // Prepare value column with aggregation function if needed
      let valueColumnParam = valueColumn;
      if (aggregationFunction !== 'none') {
        valueColumnParam = { [valueColumn]: aggregationFunction };
      }
      
      const response = await apiClient.post('/api/v1/duckdb/pivot/table', {
        query,
        pivot_column: pivotColumn,
        row_identifier: rowIdentifier,
        value_column: valueColumnParam,
        column_names: Object.keys(columnNames).length > 0 ? columnNames : undefined,
        db_path: dbPath
      });
      
      if (response.data) {
        setPivotData(response.data.data);
        setPivotColumns(response.data.columns);
      } else {
        setPivotData([]);
        setPivotColumns([]);
        enqueueSnackbar('Pivot table returned no results', { variant: 'warning' });
      }
    } catch (error) {
      console.error('Error generating pivot table:', error);
      setPivotError('Failed to generate pivot table. Please check your configuration.');
      enqueueSnackbar('Failed to generate pivot table', { variant: 'error' });
    } finally {
      setIsPivotLoading(false);
    }
  };
  
  // Generate SQL preview
  const generateSqlPreview = () => {
    if (!isQueryValid || !pivotColumn || !rowIdentifier || !valueColumn) {
      enqueueSnackbar('Please fill in all required fields', { variant: 'warning' });
      return;
    }
    
    // Prepare column mappings
    const columnNames: Record<string, string> = {};
    columnMappings.forEach(mapping => {
      columnNames[mapping.name] = mapping.label;
    });
    
    // Prepare value column with aggregation function if needed
    let valueColumnParam = `'${valueColumn}'`;
    if (aggregationFunction !== 'none') {
      valueColumnParam = `{'${valueColumn}': '${aggregationFunction}'}`;
    }
    
    // Generate SQL
    let sql = `SELECT * FROM pivot(\n`;
    sql += `  (${query}),\n`;
    sql += `  '${pivotColumn}',\n`;
    sql += `  '${rowIdentifier}',\n`;
    sql += `  ${valueColumnParam}`;
    
    if (Object.keys(columnNames).length > 0) {
      sql += `,\n  ${JSON.stringify(columnNames)}`;
    }
    
    sql += `\n)`;
    
    setSqlPreview(sql);
    setShowSqlPreview(true);
  };
  
  // Add column mapping
  const addColumnMapping = () => {
    if (!newColumnName || !newColumnLabel) return;
    
    setColumnMappings([...columnMappings, { name: newColumnName, label: newColumnLabel }]);
    setNewColumnName('');
    setNewColumnLabel('');
    setShowColumnMappingDialog(false);
  };
  
  // Remove column mapping
  const removeColumnMapping = (index: number) => {
    const newMappings = [...columnMappings];
    newMappings.splice(index, 1);
    setColumnMappings(newMappings);
  };
  
  // Handle pagination
  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };
  
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Pivot Table Builder
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          1. Define Query
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <CodeEditor
            value={query}
            onChange={setQuery}
            language="sql"
            height="150px"
            placeholder="Enter SQL query (e.g., SELECT category, product, sales FROM sales_data)"
          />
        </Box>
        
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
          <Button
            variant="contained"
            onClick={executeQuery}
            disabled={!isQueryValid || isQueryLoading}
            startIcon={isQueryLoading ? <CircularProgress size={20} /> : <PlayArrowIcon />}
          >
            Execute Query
          </Button>
        </Box>
        
        {queryError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {queryError}
          </Alert>
        )}
        
        {queryColumns.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Available Columns:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {queryColumns.map((column) => (
                <Chip key={column} label={column} />
              ))}
            </Box>
          </Box>
        )}
        
        {queryPreview.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Query Preview:
            </Typography>
            <TableContainer component={Paper} sx={{ maxHeight: 300 }}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    {queryColumns.map((column) => (
                      <TableCell key={column}>{column}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {queryPreview.map((row, rowIndex) => (
                    <TableRow key={rowIndex}>
                      {queryColumns.map((column) => (
                        <TableCell key={column}>{row[column]?.toString() || 'NULL'}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}
      </Paper>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          2. Configure Pivot Table
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel id="pivot-column-label">Pivot Column</InputLabel>
              <Select
                labelId="pivot-column-label"
                value={pivotColumn}
                onChange={(e) => setPivotColumn(e.target.value)}
                label="Pivot Column"
                disabled={queryColumns.length === 0}
              >
                {queryColumns.map((column) => (
                  <MenuItem key={column} value={column}>{column}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel id="row-identifier-label">Row Identifier</InputLabel>
              <Select
                labelId="row-identifier-label"
                value={rowIdentifier}
                onChange={(e) => setRowIdentifier(e.target.value)}
                label="Row Identifier"
                disabled={queryColumns.length === 0}
              >
                {queryColumns.map((column) => (
                  <MenuItem key={column} value={column}>{column}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel id="value-column-label">Value Column</InputLabel>
              <Select
                labelId="value-column-label"
                value={valueColumn}
                onChange={(e) => setValueColumn(e.target.value)}
                label="Value Column"
                disabled={queryColumns.length === 0}
              >
                {queryColumns.map((column) => (
                  <MenuItem key={column} value={column}>{column}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel id="aggregation-function-label">Aggregation Function</InputLabel>
              <Select
                labelId="aggregation-function-label"
                value={aggregationFunction}
                onChange={(e) => setAggregationFunction(e.target.value)}
                label="Aggregation Function"
              >
                <MenuItem value="none">None</MenuItem>
                <MenuItem value="sum">Sum</MenuItem>
                <MenuItem value="avg">Average</MenuItem>
                <MenuItem value="min">Minimum</MenuItem>
                <MenuItem value="max">Maximum</MenuItem>
                <MenuItem value="count">Count</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={8}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
                Column Mappings
              </Typography>
              <Tooltip title="Add column mapping">
                <IconButton onClick={() => setShowColumnMappingDialog(true)}>
                  <AddIcon />
                </IconButton>
              </Tooltip>
            </Box>
            
            {columnMappings.length > 0 ? (
              <TableContainer component={Paper} sx={{ maxHeight: 200 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Column Value</TableCell>
                      <TableCell>Display Label</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {columnMappings.map((mapping, index) => (
                      <TableRow key={index}>
                        <TableCell>{mapping.name}</TableCell>
                        <TableCell>{mapping.label}</TableCell>
                        <TableCell align="right">
                          <IconButton size="small" onClick={() => removeColumnMapping(index)}>
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No column mappings defined. Column values will be used as is.
              </Typography>
            )}
          </Grid>
        </Grid>
        
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3, gap: 2 }}>
          <Button
            variant="outlined"
            onClick={generateSqlPreview}
            startIcon={<CodeIcon />}
            disabled={!isQueryValid || !pivotColumn || !rowIdentifier || !valueColumn}
          >
            Preview SQL
          </Button>
          
          <Button
            variant="contained"
            onClick={generatePivotTable}
            disabled={!isQueryValid || !pivotColumn || !rowIdentifier || !valueColumn || isPivotLoading}
            startIcon={isPivotLoading ? <CircularProgress size={20} /> : <PlayArrowIcon />}
          >
            Generate Pivot Table
          </Button>
        </Box>
      </Paper>
      
      {pivotError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {pivotError}
        </Alert>
      )}
      
      {pivotData.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            3. Pivot Table Results
          </Typography>
          
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  {pivotColumns.map((column) => (
                    <TableCell key={column}>{column}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {pivotData
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((row, rowIndex) => (
                    <TableRow key={rowIndex}>
                      {pivotColumns.map((column) => (
                        <TableCell key={column}>{row[column]?.toString() || 'NULL'}</TableCell>
                      ))}
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50]}
            component="div"
            count={pivotData.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
          
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
            <Button
              variant="outlined"
              startIcon={<SaveIcon />}
              onClick={() => {
                const csvContent = [
                  pivotColumns.join(','),
                  ...pivotData.map(row => pivotColumns.map(col => row[col] || '').join(','))
                ].join('\n');
                
                const blob = new Blob([csvContent], { type: 'text/csv' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'pivot_table.csv';
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
      
      {/* Column Mapping Dialog */}
      <Dialog open={showColumnMappingDialog} onClose={() => setShowColumnMappingDialog(false)}>
        <DialogTitle>Add Column Mapping</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Column Value"
              value={newColumnName}
              onChange={(e) => setNewColumnName(e.target.value)}
              margin="normal"
              helperText="The value from the pivot column"
            />
            <TextField
              fullWidth
              label="Display Label"
              value={newColumnLabel}
              onChange={(e) => setNewColumnLabel(e.target.value)}
              margin="normal"
              helperText="The label to display in the pivot table"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowColumnMappingDialog(false)}>Cancel</Button>
          <Button onClick={addColumnMapping} variant="contained" disabled={!newColumnName || !newColumnLabel}>
            Add
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* SQL Preview Dialog */}
      <Dialog
        open={showSqlPreview}
        onClose={() => setShowSqlPreview(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>SQL Preview</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <CodeEditor
              value={sqlPreview}
              onChange={() => {}}
              language="sql"
              height="300px"
              readOnly
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSqlPreview(false)}>Close</Button>
          <Button
            onClick={() => {
              navigator.clipboard.writeText(sqlPreview);
              enqueueSnackbar('SQL copied to clipboard', { variant: 'success' });
            }}
            variant="contained"
          >
            Copy to Clipboard
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PivotTableBuilder;
