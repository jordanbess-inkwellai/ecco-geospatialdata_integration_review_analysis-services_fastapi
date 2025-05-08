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
  Alert
} from '@mui/material';
import { apiClient } from '../../lib/api';

interface ERAlchemyDiagramProps {
  onDiagramGenerated?: (imageUrl: string) => void;
}

const ERAlchemyDiagram: React.FC<ERAlchemyDiagramProps> = ({ onDiagramGenerated }) => {
  const [connectionString, setConnectionString] = useState<string>('');
  const [outputFormat, setOutputFormat] = useState<string>('png');
  const [excludeTables, setExcludeTables] = useState<string>('');
  const [excludeColumns, setExcludeColumns] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [diagramUrl, setDiagramUrl] = useState<string | null>(null);

  const handleGenerateDiagram = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Prepare form data
      const formData = new FormData();
      formData.append('connection_string', connectionString);
      formData.append('output_format', outputFormat);
      
      // Add exclude tables if provided
      if (excludeTables) {
        excludeTables.split(',').forEach(table => {
          formData.append('exclude_tables', table.trim());
        });
      }
      
      // Add exclude columns if provided
      if (excludeColumns) {
        excludeColumns.split(',').forEach(column => {
          formData.append('exclude_columns', column.trim());
        });
      }
      
      // Generate diagram
      const response = await apiClient.post('/diagrams/eralchemy/generate-from-db', formData, {
        responseType: 'blob'
      });
      
      // Create URL for the blob
      const blob = new Blob([response.data], { 
        type: outputFormat === 'pdf' ? 'application/pdf' : `image/${outputFormat}` 
      });
      const url = URL.createObjectURL(blob);
      
      setDiagramUrl(url);
      
      // Call callback if provided
      if (onDiagramGenerated) {
        onDiagramGenerated(url);
      }
    } catch (err) {
      console.error('Error generating diagram:', err);
      setError('Failed to generate diagram. Please check your connection string and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (diagramUrl) {
      const a = document.createElement('a');
      a.href = diagramUrl;
      a.download = `eralchemy_diagram.${outputFormat}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Generate ER Diagram with ERAlchemy
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <TextField
            label="Database Connection String"
            fullWidth
            value={connectionString}
            onChange={(e) => setConnectionString(e.target.value)}
            placeholder="postgresql://username:password@localhost:5432/dbname"
            margin="normal"
            helperText="SQLAlchemy connection string format"
          />
        </Box>
        
        <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
          <FormControl fullWidth margin="normal">
            <InputLabel>Output Format</InputLabel>
            <Select
              value={outputFormat}
              onChange={(e) => setOutputFormat(e.target.value)}
              label="Output Format"
            >
              <MenuItem value="png">PNG</MenuItem>
              <MenuItem value="pdf">PDF</MenuItem>
              <MenuItem value="svg">SVG</MenuItem>
            </Select>
          </FormControl>
        </Box>
        
        <Box sx={{ mb: 2 }}>
          <TextField
            label="Exclude Tables (comma-separated)"
            fullWidth
            value={excludeTables}
            onChange={(e) => setExcludeTables(e.target.value)}
            placeholder="temp_table, log_table"
            margin="normal"
          />
        </Box>
        
        <Box sx={{ mb: 2 }}>
          <TextField
            label="Exclude Columns (comma-separated)"
            fullWidth
            value={excludeColumns}
            onChange={(e) => setExcludeColumns(e.target.value)}
            placeholder="created_at, updated_at"
            margin="normal"
          />
        </Box>
        
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleGenerateDiagram}
            disabled={loading || !connectionString}
          >
            {loading ? <CircularProgress size={24} /> : 'Generate Diagram'}
          </Button>
          
          {diagramUrl && (
            <Button
              variant="outlined"
              color="secondary"
              onClick={handleDownload}
            >
              Download Diagram
            </Button>
          )}
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
        
        {diagramUrl && (
          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="subtitle1" gutterBottom>
              Generated Diagram
            </Typography>
            <Paper elevation={3} sx={{ p: 2, overflow: 'auto', maxHeight: 500 }}>
              {outputFormat === 'pdf' ? (
                <iframe
                  src={diagramUrl}
                  style={{ width: '100%', height: 500, border: 'none' }}
                />
              ) : (
                <img
                  src={diagramUrl}
                  alt="ER Diagram"
                  style={{ maxWidth: '100%' }}
                />
              )}
            </Paper>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ERAlchemyDiagram;
