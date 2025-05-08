import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Divider,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  Paper
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import LayersIcon from '@mui/icons-material/Layers';
import MapIcon from '@mui/icons-material/Map';
import PaletteIcon from '@mui/icons-material/Palette';
import FormatColorFillIcon from '@mui/icons-material/FormatColorFill';
import LineStyleIcon from '@mui/icons-material/LineStyle';
import CircleIcon from '@mui/icons-material/Circle';
import TextFieldsIcon from '@mui/icons-material/TextFields';
import ImageIcon from '@mui/icons-material/Image';
import TerrainIcon from '@mui/icons-material/Terrain';
import dynamic from 'next/dynamic';

// Dynamically import the Monaco Editor to avoid SSR issues
const MonacoEditor = dynamic(
  () => import('@monaco-editor/react'),
  { ssr: false }
);

interface StyleEditorProps {
  style: any;
  onSave: (style: any) => void;
  onCancel: () => void;
}

const StyleEditor: React.FC<StyleEditorProps> = ({
  style,
  onSave,
  onCancel
}) => {
  const [tabValue, setTabValue] = useState<number>(0);
  const [editedStyle, setEditedStyle] = useState<any>(style);
  const [selectedLayer, setSelectedLayer] = useState<any>(null);
  const [selectedSource, setSelectedSource] = useState<any>(null);
  const [layerDialogOpen, setLayerDialogOpen] = useState<boolean>(false);
  const [sourceDialogOpen, setSourceDialogOpen] = useState<boolean>(false);
  const [jsonMode, setJsonMode] = useState<boolean>(false);
  const [jsonError, setJsonError] = useState<string | null>(null);

  // Handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Handle style name change
  const handleStyleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setEditedStyle({
      ...editedStyle,
      name: event.target.value
    });
  };

  // Handle layer selection
  const handleLayerSelect = (layer: any) => {
    setSelectedLayer(layer);
  };

  // Handle source selection
  const handleSourceSelect = (sourceName: string) => {
    setSelectedSource({
      name: sourceName,
      ...editedStyle.sources[sourceName]
    });
  };

  // Handle layer visibility toggle
  const handleLayerVisibilityToggle = (layerId: string) => {
    const layers = [...editedStyle.layers];
    const layerIndex = layers.findIndex(layer => layer.id === layerId);
    
    if (layerIndex >= 0) {
      const layer = layers[layerIndex];
      const layout = layer.layout || {};
      
      layers[layerIndex] = {
        ...layer,
        layout: {
          ...layout,
          visibility: layout.visibility === 'none' ? 'visible' : 'none'
        }
      };
      
      setEditedStyle({
        ...editedStyle,
        layers
      });
    }
  };

  // Handle layer dialog open
  const handleLayerDialogOpen = (layer: any = null) => {
    setSelectedLayer(layer || {
      id: '',
      type: 'fill',
      source: Object.keys(editedStyle.sources)[0] || '',
      'source-layer': '',
      paint: {}
    });
    setLayerDialogOpen(true);
  };

  // Handle layer dialog close
  const handleLayerDialogClose = () => {
    setLayerDialogOpen(false);
  };

  // Handle layer save
  const handleLayerSave = () => {
    const layers = [...editedStyle.layers];
    const layerIndex = layers.findIndex(layer => layer.id === selectedLayer.id);
    
    if (layerIndex >= 0) {
      // Update existing layer
      layers[layerIndex] = selectedLayer;
    } else {
      // Add new layer
      layers.push(selectedLayer);
    }
    
    setEditedStyle({
      ...editedStyle,
      layers
    });
    
    setLayerDialogOpen(false);
  };

  // Handle layer delete
  const handleLayerDelete = (layerId: string) => {
    const layers = editedStyle.layers.filter((layer: any) => layer.id !== layerId);
    
    setEditedStyle({
      ...editedStyle,
      layers
    });
  };

  // Handle source dialog open
  const handleSourceDialogOpen = (sourceName: string = '') => {
    if (sourceName) {
      setSelectedSource({
        name: sourceName,
        ...editedStyle.sources[sourceName]
      });
    } else {
      setSelectedSource({
        name: '',
        type: 'vector',
        url: ''
      });
    }
    
    setSourceDialogOpen(true);
  };

  // Handle source dialog close
  const handleSourceDialogClose = () => {
    setSourceDialogOpen(false);
  };

  // Handle source save
  const handleSourceSave = () => {
    const { name, ...sourceData } = selectedSource;
    const sources = { ...editedStyle.sources };
    
    sources[name] = sourceData;
    
    setEditedStyle({
      ...editedStyle,
      sources
    });
    
    setSourceDialogOpen(false);
  };

  // Handle source delete
  const handleSourceDelete = (sourceName: string) => {
    const sources = { ...editedStyle.sources };
    delete sources[sourceName];
    
    // Also remove layers that use this source
    const layers = editedStyle.layers.filter((layer: any) => layer.source !== sourceName);
    
    setEditedStyle({
      ...editedStyle,
      sources,
      layers
    });
  };

  // Handle JSON edit
  const handleJsonEdit = (value: string | undefined) => {
    try {
      const parsedStyle = JSON.parse(value || '{}');
      setEditedStyle(parsedStyle);
      setJsonError(null);
    } catch (err) {
      setJsonError('Invalid JSON');
    }
  };

  // Handle save
  const handleSave = () => {
    onSave(editedStyle);
  };

  // Get layer icon based on type
  const getLayerIcon = (type: string) => {
    switch (type) {
      case 'fill':
        return <FormatColorFillIcon />;
      case 'line':
        return <LineStyleIcon />;
      case 'circle':
        return <CircleIcon />;
      case 'symbol':
        return <TextFieldsIcon />;
      case 'raster':
        return <ImageIcon />;
      case 'hillshade':
        return <TerrainIcon />;
      default:
        return <LayersIcon />;
    }
  };

  // Get source icon based on type
  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'vector':
        return <MapIcon />;
      case 'raster':
        return <ImageIcon />;
      case 'raster-dem':
        return <TerrainIcon />;
      default:
        return <MapIcon />;
    }
  };

  // Render the editor content based on the selected tab
  const renderEditorContent = () => {
    switch (tabValue) {
      case 0: // Layers
        return (
          <Box>
            <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="subtitle1">Layers</Typography>
              <Button
                size="small"
                startIcon={<AddIcon />}
                onClick={() => handleLayerDialogOpen()}
              >
                Add Layer
              </Button>
            </Box>
            
            <List dense>
              {editedStyle.layers.map((layer: any) => (
                <ListItem
                  key={layer.id}
                  button
                  selected={selectedLayer && selectedLayer.id === layer.id}
                  onClick={() => handleLayerSelect(layer)}
                >
                  <ListItemIcon>
                    {getLayerIcon(layer.type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={layer.id}
                    secondary={`${layer.type} - ${layer.source}`}
                  />
                  <ListItemSecondaryAction>
                    <Tooltip title={layer.layout?.visibility === 'none' ? 'Show' : 'Hide'}>
                      <IconButton
                        edge="end"
                        onClick={() => handleLayerVisibilityToggle(layer.id)}
                      >
                        {layer.layout?.visibility === 'none' ? (
                          <VisibilityOffIcon fontSize="small" />
                        ) : (
                          <VisibilityIcon fontSize="small" />
                        )}
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit">
                      <IconButton
                        edge="end"
                        onClick={() => handleLayerDialogOpen(layer)}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        edge="end"
                        onClick={() => handleLayerDelete(layer.id)}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
              {editedStyle.layers.length === 0 && (
                <ListItem>
                  <ListItemText secondary="No layers available" />
                </ListItem>
              )}
            </List>
          </Box>
        );
      
      case 1: // Sources
        return (
          <Box>
            <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="subtitle1">Sources</Typography>
              <Button
                size="small"
                startIcon={<AddIcon />}
                onClick={() => handleSourceDialogOpen()}
              >
                Add Source
              </Button>
            </Box>
            
            <List dense>
              {Object.entries(editedStyle.sources).map(([name, source]: [string, any]) => (
                <ListItem
                  key={name}
                  button
                  selected={selectedSource && selectedSource.name === name}
                  onClick={() => handleSourceSelect(name)}
                >
                  <ListItemIcon>
                    {getSourceIcon(source.type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={name}
                    secondary={source.type}
                  />
                  <ListItemSecondaryAction>
                    <Tooltip title="Edit">
                      <IconButton
                        edge="end"
                        onClick={() => handleSourceDialogOpen(name)}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        edge="end"
                        onClick={() => handleSourceDelete(name)}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
              {Object.keys(editedStyle.sources).length === 0 && (
                <ListItem>
                  <ListItemText secondary="No sources available" />
                </ListItem>
              )}
            </List>
          </Box>
        );
      
      case 2: // JSON
        return (
          <Box sx={{ height: '100%' }}>
            <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="subtitle1">JSON Editor</Typography>
              {jsonError && (
                <Typography variant="body2" color="error">
                  {jsonError}
                </Typography>
              )}
            </Box>
            
            <Box sx={{ height: 'calc(100% - 40px)' }}>
              <MonacoEditor
                height="100%"
                language="json"
                theme="vs-dark"
                value={JSON.stringify(editedStyle, null, 2)}
                onChange={handleJsonEdit}
                options={{
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  automaticLayout: true
                }}
              />
            </Box>
          </Box>
        );
      
      default:
        return null;
    }
  };

  return (
    <Box sx={{ height: 600, display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 1, borderBottom: 1, borderColor: 'divider' }}>
        <TextField
          label="Style Name"
          value={editedStyle.name || ''}
          onChange={handleStyleNameChange}
          fullWidth
          margin="dense"
          variant="outlined"
        />
      </Box>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab icon={<LayersIcon />} label="Layers" />
          <Tab icon={<MapIcon />} label="Sources" />
          <Tab icon={<CodeIcon />} label="JSON" />
        </Tabs>
      </Box>
      
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        {renderEditorContent()}
      </Box>
      
      <Box sx={{ p: 1, borderTop: 1, borderColor: 'divider', display: 'flex', justifyContent: 'flex-end' }}>
        <Button onClick={onCancel} sx={{ mr: 1 }}>
          Cancel
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={handleSave}
          disabled={!!jsonError}
        >
          Save
        </Button>
      </Box>
      
      {/* Layer Dialog */}
      <Dialog
        open={layerDialogOpen}
        onClose={handleLayerDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedLayer && selectedLayer.id ? 'Edit Layer' : 'Add Layer'}
        </DialogTitle>
        <DialogContent>
          <TextField
            label="Layer ID"
            value={selectedLayer?.id || ''}
            onChange={(e) => setSelectedLayer({ ...selectedLayer, id: e.target.value })}
            fullWidth
            margin="normal"
            required
          />
          
          <FormControl fullWidth margin="normal">
            <InputLabel>Layer Type</InputLabel>
            <Select
              value={selectedLayer?.type || 'fill'}
              onChange={(e) => setSelectedLayer({ ...selectedLayer, type: e.target.value })}
              label="Layer Type"
            >
              <MenuItem value="fill">Fill</MenuItem>
              <MenuItem value="line">Line</MenuItem>
              <MenuItem value="circle">Circle</MenuItem>
              <MenuItem value="symbol">Symbol</MenuItem>
              <MenuItem value="raster">Raster</MenuItem>
              <MenuItem value="hillshade">Hillshade</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl fullWidth margin="normal">
            <InputLabel>Source</InputLabel>
            <Select
              value={selectedLayer?.source || ''}
              onChange={(e) => setSelectedLayer({ ...selectedLayer, source: e.target.value })}
              label="Source"
            >
              {Object.keys(editedStyle.sources).map((name) => (
                <MenuItem key={name} value={name}>
                  {name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          {selectedLayer?.source && editedStyle.sources[selectedLayer.source]?.type === 'vector' && (
            <TextField
              label="Source Layer"
              value={selectedLayer?.['source-layer'] || ''}
              onChange={(e) => setSelectedLayer({ ...selectedLayer, 'source-layer': e.target.value })}
              fullWidth
              margin="normal"
            />
          )}
          
          <FormControl fullWidth margin="normal">
            <InputLabel>Visibility</InputLabel>
            <Select
              value={(selectedLayer?.layout?.visibility || 'visible')}
              onChange={(e) => setSelectedLayer({
                ...selectedLayer,
                layout: {
                  ...(selectedLayer?.layout || {}),
                  visibility: e.target.value
                }
              })}
              label="Visibility"
            >
              <MenuItem value="visible">Visible</MenuItem>
              <MenuItem value="none">Hidden</MenuItem>
            </Select>
          </FormControl>
          
          <Typography variant="subtitle1" sx={{ mt: 2 }}>
            Paint Properties
          </Typography>
          
          <Paper sx={{ p: 2, mt: 1 }}>
            <MonacoEditor
              height="200px"
              language="json"
              theme="vs-dark"
              value={JSON.stringify(selectedLayer?.paint || {}, null, 2)}
              onChange={(value) => {
                try {
                  const paint = JSON.parse(value || '{}');
                  setSelectedLayer({ ...selectedLayer, paint });
                } catch (err) {
                  // Ignore JSON parse errors
                }
              }}
              options={{
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                automaticLayout: true
              }}
            />
          </Paper>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleLayerDialogClose}>Cancel</Button>
          <Button
            onClick={handleLayerSave}
            variant="contained"
            color="primary"
            disabled={!selectedLayer?.id || !selectedLayer?.source}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Source Dialog */}
      <Dialog
        open={sourceDialogOpen}
        onClose={handleSourceDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedSource && selectedSource.name ? 'Edit Source' : 'Add Source'}
        </DialogTitle>
        <DialogContent>
          <TextField
            label="Source Name"
            value={selectedSource?.name || ''}
            onChange={(e) => setSelectedSource({ ...selectedSource, name: e.target.value })}
            fullWidth
            margin="normal"
            required
          />
          
          <FormControl fullWidth margin="normal">
            <InputLabel>Source Type</InputLabel>
            <Select
              value={selectedSource?.type || 'vector'}
              onChange={(e) => setSelectedSource({ ...selectedSource, type: e.target.value })}
              label="Source Type"
            >
              <MenuItem value="vector">Vector</MenuItem>
              <MenuItem value="raster">Raster</MenuItem>
              <MenuItem value="raster-dem">Raster DEM</MenuItem>
              <MenuItem value="geojson">GeoJSON</MenuItem>
              <MenuItem value="image">Image</MenuItem>
              <MenuItem value="video">Video</MenuItem>
            </Select>
          </FormControl>
          
          {selectedSource?.type === 'vector' && (
            <TextField
              label="TileJSON URL"
              value={selectedSource?.url || ''}
              onChange={(e) => setSelectedSource({ ...selectedSource, url: e.target.value })}
              fullWidth
              margin="normal"
              placeholder="e.g., http://localhost:3000/tilejson/table_name.json"
            />
          )}
          
          {selectedSource?.type === 'raster' && (
            <TextField
              label="TileJSON URL"
              value={selectedSource?.url || ''}
              onChange={(e) => setSelectedSource({ ...selectedSource, url: e.target.value })}
              fullWidth
              margin="normal"
              placeholder="e.g., http://localhost:3000/raster/file_name.json"
            />
          )}
          
          {selectedSource?.type === 'raster-dem' && (
            <TextField
              label="TileJSON URL"
              value={selectedSource?.url || ''}
              onChange={(e) => setSelectedSource({ ...selectedSource, url: e.target.value })}
              fullWidth
              margin="normal"
              placeholder="e.g., http://localhost:3000/terrain/file_name.json"
            />
          )}
          
          {selectedSource?.type === 'geojson' && (
            <Paper sx={{ p: 2, mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                GeoJSON Data
              </Typography>
              <MonacoEditor
                height="200px"
                language="json"
                theme="vs-dark"
                value={JSON.stringify(selectedSource?.data || {}, null, 2)}
                onChange={(value) => {
                  try {
                    const data = JSON.parse(value || '{}');
                    setSelectedSource({ ...selectedSource, data });
                  } catch (err) {
                    // Ignore JSON parse errors
                  }
                }}
                options={{
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  automaticLayout: true
                }}
              />
            </Paper>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleSourceDialogClose}>Cancel</Button>
          <Button
            onClick={handleSourceSave}
            variant="contained"
            color="primary"
            disabled={!selectedSource?.name || !selectedSource?.type}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default StyleEditor;
