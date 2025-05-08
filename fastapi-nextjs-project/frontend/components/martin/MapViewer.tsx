import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  IconButton,
  Divider,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Drawer,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Switch,
  FormControlLabel,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip
} from '@mui/material';
import MapIcon from '@mui/icons-material/Map';
import LayersIcon from '@mui/icons-material/Layers';
import StyleIcon from '@mui/icons-material/Style';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import UploadIcon from '@mui/icons-material/Upload';
import DownloadIcon from '@mui/icons-material/Download';
import InfoIcon from '@mui/icons-material/Info';
import TerrainIcon from '@mui/icons-material/Terrain';
import ImageIcon from '@mui/icons-material/Image';
import TableChartIcon from '@mui/icons-material/TableChart';
import { apiClient } from '../../lib/api';
import dynamic from 'next/dynamic';

// Dynamically import the MapLibre components to avoid SSR issues
const MapLibreMap = dynamic(
  () => import('./MapLibreMap'),
  { ssr: false, loading: () => <CircularProgress /> }
);

// Dynamically import the style editor component
const StyleEditor = dynamic(
  () => import('./StyleEditor'),
  { ssr: false, loading: () => <CircularProgress /> }
);

interface MapViewerProps {
  initialStyle?: string;
  initialCenter?: [number, number];
  initialZoom?: number;
}

const MapViewer: React.FC<MapViewerProps> = ({
  initialStyle,
  initialCenter = [0, 0],
  initialZoom = 2
}) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [serverStatus, setServerStatus] = useState<any>(null);
  const [tables, setTables] = useState<any[]>([]);
  const [pmtiles, setPmtiles] = useState<any[]>([]);
  const [mbtiles, setMbtiles] = useState<any[]>([]);
  const [rasterTiles, setRasterTiles] = useState<any[]>([]);
  const [terrainTiles, setTerrainTiles] = useState<any[]>([]);
  const [styles, setStyles] = useState<any[]>([]);
  const [selectedStyle, setSelectedStyle] = useState<string | null>(initialStyle || null);
  const [selectedLayers, setSelectedLayers] = useState<string[]>([]);
  const [mapCenter, setMapCenter] = useState<[number, number]>(initialCenter);
  const [mapZoom, setMapZoom] = useState<number>(initialZoom);
  const [drawerOpen, setDrawerOpen] = useState<boolean>(true);
  const [drawerWidth, setDrawerWidth] = useState<number>(300);
  const [tabValue, setTabValue] = useState<number>(0);
  const [uploadDialogOpen, setUploadDialogOpen] = useState<boolean>(false);
  const [uploadType, setUploadType] = useState<string>('pmtiles');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [styleEditorOpen, setStyleEditorOpen] = useState<boolean>(false);
  const [currentStyle, setCurrentStyle] = useState<any>(null);
  const [infoDialogOpen, setInfoDialogOpen] = useState<boolean>(false);
  const [selectedInfo, setSelectedInfo] = useState<any>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load data on component mount
  useEffect(() => {
    loadData();
  }, []);

  // Load all data from the API
  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Get server status
      const statusResponse = await apiClient.get('/martin/status');
      setServerStatus(statusResponse.data);
      
      // Check if the server is available
      if (statusResponse.data.status !== 'ok') {
        setError('Martin server is not available');
        setLoading(false);
        return;
      }
      
      // Get tables
      const tablesResponse = await apiClient.get('/martin/tables');
      setTables(tablesResponse.data || []);
      
      // Get PMTiles
      const pmtilesResponse = await apiClient.get('/martin/pmtiles');
      setPmtiles(pmtilesResponse.data || []);
      
      // Get MBTiles
      const mbtilesResponse = await apiClient.get('/martin/mbtiles');
      setMbtiles(mbtilesResponse.data || []);
      
      // Get raster tiles
      const rasterResponse = await apiClient.get('/martin/raster');
      setRasterTiles(rasterResponse.data || []);
      
      // Get terrain tiles
      const terrainResponse = await apiClient.get('/martin/terrain');
      setTerrainTiles(terrainResponse.data || []);
      
      // Get styles
      const stylesResponse = await apiClient.get('/martin/styles');
      setStyles(stylesResponse.data || []);
      
      // Set the selected style if available
      if (initialStyle && stylesResponse.data && stylesResponse.data.length > 0) {
        const style = stylesResponse.data.find((s: any) => s.file_name === initialStyle);
        if (style) {
          setSelectedStyle(style.file_name);
        } else if (stylesResponse.data.length > 0) {
          setSelectedStyle(stylesResponse.data[0].file_name);
        }
      } else if (stylesResponse.data && stylesResponse.data.length > 0) {
        setSelectedStyle(stylesResponse.data[0].file_name);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error loading data:', err);
      setError('Failed to load data');
      setLoading(false);
    }
  };

  // Handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Handle style selection
  const handleStyleSelect = (styleName: string) => {
    setSelectedStyle(styleName);
  };

  // Handle layer visibility toggle
  const handleLayerToggle = (layerId: string) => {
    if (selectedLayers.includes(layerId)) {
      setSelectedLayers(selectedLayers.filter(id => id !== layerId));
    } else {
      setSelectedLayers([...selectedLayers, layerId]);
    }
  };

  // Handle map move
  const handleMapMove = (center: [number, number], zoom: number) => {
    setMapCenter(center);
    setMapZoom(zoom);
  };

  // Handle drawer toggle
  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  // Handle upload dialog open
  const handleUploadDialogOpen = (type: string) => {
    setUploadType(type);
    setUploadDialogOpen(true);
  };

  // Handle upload dialog close
  const handleUploadDialogClose = () => {
    setUploadDialogOpen(false);
    setSelectedFile(null);
  };

  // Handle file selection
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
    }
  };

  // Handle file upload
  const handleFileUpload = async () => {
    if (!selectedFile) {
      return;
    }
    
    setLoading(true);
    
    try {
      // Create form data
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      // Upload the file based on the type
      let response;
      
      switch (uploadType) {
        case 'pmtiles':
          response = await apiClient.post('/martin/pmtiles/upload', formData);
          break;
        case 'mbtiles':
          response = await apiClient.post('/martin/mbtiles/upload', formData);
          break;
        case 'raster':
          response = await apiClient.post('/martin/raster/upload', formData);
          break;
        case 'terrain':
          response = await apiClient.post('/martin/terrain/upload', formData);
          break;
        case 'style':
          response = await apiClient.post('/martin/styles/upload', formData);
          break;
        default:
          throw new Error(`Unsupported upload type: ${uploadType}`);
      }
      
      // Reload data
      await loadData();
      
      setUploadDialogOpen(false);
      setSelectedFile(null);
      setLoading(false);
    } catch (err) {
      console.error('Error uploading file:', err);
      setError('Failed to upload file');
      setLoading(false);
    }
  };

  // Handle style editor open
  const handleStyleEditorOpen = async (styleName: string) => {
    try {
      // Get the style data
      const response = await fetch(`${serverStatus.url}/styles/${styleName}`);
      const styleData = await response.json();
      
      setCurrentStyle({
        name: styleName,
        data: styleData
      });
      
      setStyleEditorOpen(true);
    } catch (err) {
      console.error('Error loading style:', err);
      setError('Failed to load style');
    }
  };

  // Handle style editor close
  const handleStyleEditorClose = () => {
    setStyleEditorOpen(false);
    setCurrentStyle(null);
  };

  // Handle style save
  const handleStyleSave = async (styleData: any) => {
    try {
      setLoading(true);
      
      // Create a blob from the style data
      const blob = new Blob([JSON.stringify(styleData, null, 2)], { type: 'application/json' });
      const file = new File([blob], currentStyle.name);
      
      // Create form data
      const formData = new FormData();
      formData.append('file', file);
      
      // Upload the style
      await apiClient.post('/martin/styles/upload', formData);
      
      // Reload data
      await loadData();
      
      setStyleEditorOpen(false);
      setCurrentStyle(null);
      setLoading(false);
    } catch (err) {
      console.error('Error saving style:', err);
      setError('Failed to save style');
      setLoading(false);
    }
  };

  // Handle info dialog open
  const handleInfoDialogOpen = (info: any) => {
    setSelectedInfo(info);
    setInfoDialogOpen(true);
  };

  // Handle info dialog close
  const handleInfoDialogClose = () => {
    setInfoDialogOpen(false);
    setSelectedInfo(null);
  };

  // Handle delete
  const handleDelete = async (type: string, name: string) => {
    try {
      setLoading(true);
      
      // Delete the item based on the type
      let response;
      
      switch (type) {
        case 'pmtiles':
          response = await apiClient.delete(`/martin/pmtiles/${name}`);
          break;
        case 'mbtiles':
          response = await apiClient.delete(`/martin/mbtiles/${name}`);
          break;
        case 'raster':
          response = await apiClient.delete(`/martin/raster/${name}`);
          break;
        case 'terrain':
          response = await apiClient.delete(`/martin/terrain/${name}`);
          break;
        case 'style':
          response = await apiClient.delete(`/martin/styles/${name}`);
          break;
        default:
          throw new Error(`Unsupported delete type: ${type}`);
      }
      
      // Reload data
      await loadData();
      
      setLoading(false);
    } catch (err) {
      console.error('Error deleting item:', err);
      setError('Failed to delete item');
      setLoading(false);
    }
  };

  // Render the drawer content based on the selected tab
  const renderDrawerContent = () => {
    switch (tabValue) {
      case 0: // Layers
        return (
          <Box>
            <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="subtitle1">Tables</Typography>
              <Tooltip title="Refresh">
                <IconButton size="small" onClick={loadData}>
                  <RefreshIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
            
            <List dense>
              {tables.map((table: any) => (
                <ListItem key={table.name}>
                  <ListItemIcon>
                    <TableChartIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={table.name}
                    secondary={table.schema}
                  />
                  <ListItemSecondaryAction>
                    <Tooltip title="Info">
                      <IconButton edge="end" onClick={() => handleInfoDialogOpen(table)}>
                        <InfoIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
              {tables.length === 0 && (
                <ListItem>
                  <ListItemText secondary="No tables available" />
                </ListItem>
              )}
            </List>
            
            <Divider sx={{ my: 1 }} />
            
            <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="subtitle1">PMTiles</Typography>
              <Tooltip title="Upload PMTiles">
                <IconButton size="small" onClick={() => handleUploadDialogOpen('pmtiles')}>
                  <UploadIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
            
            <List dense>
              {pmtiles.map((tile: any) => (
                <ListItem key={tile.name}>
                  <ListItemIcon>
                    <MapIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={tile.name}
                    secondary={`${(tile.size / 1024 / 1024).toFixed(2)} MB`}
                  />
                  <ListItemSecondaryAction>
                    <Tooltip title="Info">
                      <IconButton edge="end" onClick={() => handleInfoDialogOpen(tile)}>
                        <InfoIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton edge="end" onClick={() => handleDelete('pmtiles', tile.name)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
              {pmtiles.length === 0 && (
                <ListItem>
                  <ListItemText secondary="No PMTiles available" />
                </ListItem>
              )}
            </List>
            
            <Divider sx={{ my: 1 }} />
            
            <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="subtitle1">MBTiles</Typography>
              <Tooltip title="Upload MBTiles">
                <IconButton size="small" onClick={() => handleUploadDialogOpen('mbtiles')}>
                  <UploadIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
            
            <List dense>
              {mbtiles.map((tile: any) => (
                <ListItem key={tile.name}>
                  <ListItemIcon>
                    <MapIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={tile.name}
                    secondary={`${(tile.size / 1024 / 1024).toFixed(2)} MB`}
                  />
                  <ListItemSecondaryAction>
                    <Tooltip title="Info">
                      <IconButton edge="end" onClick={() => handleInfoDialogOpen(tile)}>
                        <InfoIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton edge="end" onClick={() => handleDelete('mbtiles', tile.name)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
              {mbtiles.length === 0 && (
                <ListItem>
                  <ListItemText secondary="No MBTiles available" />
                </ListItem>
              )}
            </List>
            
            <Divider sx={{ my: 1 }} />
            
            <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="subtitle1">Raster Tiles</Typography>
              <Tooltip title="Upload Raster Tiles">
                <IconButton size="small" onClick={() => handleUploadDialogOpen('raster')}>
                  <UploadIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
            
            <List dense>
              {rasterTiles.map((tile: any) => (
                <ListItem key={tile.name}>
                  <ListItemIcon>
                    <ImageIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={tile.name}
                    secondary={`${(tile.size / 1024 / 1024).toFixed(2)} MB`}
                  />
                  <ListItemSecondaryAction>
                    <Tooltip title="Info">
                      <IconButton edge="end" onClick={() => handleInfoDialogOpen(tile)}>
                        <InfoIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton edge="end" onClick={() => handleDelete('raster', tile.name)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
              {rasterTiles.length === 0 && (
                <ListItem>
                  <ListItemText secondary="No raster tiles available" />
                </ListItem>
              )}
            </List>
            
            <Divider sx={{ my: 1 }} />
            
            <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="subtitle1">Terrain Tiles</Typography>
              <Tooltip title="Upload Terrain Tiles">
                <IconButton size="small" onClick={() => handleUploadDialogOpen('terrain')}>
                  <UploadIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
            
            <List dense>
              {terrainTiles.map((tile: any) => (
                <ListItem key={tile.name}>
                  <ListItemIcon>
                    <TerrainIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={tile.name}
                    secondary={`${(tile.size / 1024 / 1024).toFixed(2)} MB`}
                  />
                  <ListItemSecondaryAction>
                    <Tooltip title="Info">
                      <IconButton edge="end" onClick={() => handleInfoDialogOpen(tile)}>
                        <InfoIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton edge="end" onClick={() => handleDelete('terrain', tile.name)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
              {terrainTiles.length === 0 && (
                <ListItem>
                  <ListItemText secondary="No terrain tiles available" />
                </ListItem>
              )}
            </List>
          </Box>
        );
      
      case 1: // Styles
        return (
          <Box>
            <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="subtitle1">Styles</Typography>
              <Tooltip title="Upload Style">
                <IconButton size="small" onClick={() => handleUploadDialogOpen('style')}>
                  <UploadIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
            
            <List dense>
              {styles.map((style: any) => (
                <ListItem
                  key={style.file_name}
                  button
                  selected={selectedStyle === style.file_name}
                  onClick={() => handleStyleSelect(style.file_name)}
                >
                  <ListItemIcon>
                    <StyleIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={style.name}
                    secondary={`Version: ${style.version}`}
                  />
                  <ListItemSecondaryAction>
                    <Tooltip title="Edit">
                      <IconButton edge="end" onClick={() => handleStyleEditorOpen(style.file_name)}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton edge="end" onClick={() => handleDelete('style', style.file_name)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
              {styles.length === 0 && (
                <ListItem>
                  <ListItemText secondary="No styles available" />
                </ListItem>
              )}
            </List>
          </Box>
        );
      
      default:
        return null;
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex' }}>
      {/* Drawer */}
      <Drawer
        variant="persistent"
        anchor="left"
        open={drawerOpen}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            position: 'relative',
            height: '100%'
          }
        }}
      >
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab icon={<LayersIcon />} label="Layers" />
            <Tab icon={<StyleIcon />} label="Styles" />
          </Tabs>
        </Box>
        
        <Box sx={{ overflow: 'auto', flexGrow: 1 }}>
          {renderDrawerContent()}
        </Box>
      </Drawer>
      
      {/* Map Container */}
      <Box
        sx={{
          flexGrow: 1,
          height: '100%',
          position: 'relative',
          transition: 'margin-left 225ms cubic-bezier(0.0, 0, 0.2, 1) 0ms'
        }}
      >
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Box sx={{ p: 2 }}>
            <Alert severity="error">{error}</Alert>
          </Box>
        ) : (
          <MapLibreMap
            style={selectedStyle ? `${serverStatus.url}/styles/${selectedStyle}` : undefined}
            center={mapCenter}
            zoom={mapZoom}
            onMove={handleMapMove}
            visibleLayers={selectedLayers}
          />
        )}
        
        {/* Drawer toggle button */}
        <Button
          variant="contained"
          size="small"
          onClick={handleDrawerToggle}
          sx={{
            position: 'absolute',
            top: 10,
            left: drawerOpen ? drawerWidth + 10 : 10,
            zIndex: 1000,
            minWidth: 0,
            width: 40,
            height: 40,
            borderRadius: '50%'
          }}
        >
          {drawerOpen ? <ChevronLeftIcon /> : <ChevronRightIcon />}
        </Button>
      </Box>
      
      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onClose={handleUploadDialogClose}>
        <DialogTitle>
          Upload {uploadType === 'pmtiles' ? 'PMTiles' :
                 uploadType === 'mbtiles' ? 'MBTiles' :
                 uploadType === 'raster' ? 'Raster Tiles' :
                 uploadType === 'terrain' ? 'Terrain Tiles' :
                 'Style'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <input
              type="file"
              id="file-upload"
              style={{ display: 'none' }}
              onChange={handleFileSelect}
              accept={
                uploadType === 'pmtiles' ? '.pmtiles' :
                uploadType === 'mbtiles' ? '.mbtiles' :
                uploadType === 'raster' ? '.tif,.tiff,.geotiff' :
                uploadType === 'terrain' ? '.terrain' :
                '.json'
              }
              ref={fileInputRef}
            />
            <label htmlFor="file-upload">
              <Button
                variant="outlined"
                component="span"
                startIcon={<UploadIcon />}
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
        </DialogContent>
        <DialogActions>
          <Button onClick={handleUploadDialogClose}>Cancel</Button>
          <Button
            onClick={handleFileUpload}
            variant="contained"
            disabled={!selectedFile}
          >
            Upload
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Style Editor Dialog */}
      {styleEditorOpen && currentStyle && (
        <Dialog
          open={styleEditorOpen}
          onClose={handleStyleEditorClose}
          maxWidth="lg"
          fullWidth
        >
          <DialogTitle>Edit Style: {currentStyle.name}</DialogTitle>
          <DialogContent>
            <StyleEditor
              style={currentStyle.data}
              onSave={handleStyleSave}
              onCancel={handleStyleEditorClose}
            />
          </DialogContent>
        </Dialog>
      )}
      
      {/* Info Dialog */}
      <Dialog
        open={infoDialogOpen}
        onClose={handleInfoDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Information</DialogTitle>
        <DialogContent>
          {selectedInfo && (
            <Box>
              <Typography variant="h6">{selectedInfo.name}</Typography>
              
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle1">Properties</Typography>
                <pre style={{ overflow: 'auto', maxHeight: 400 }}>
                  {JSON.stringify(selectedInfo, null, 2)}
                </pre>
              </Box>
              
              {selectedInfo.url && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle1">URL</Typography>
                  <Typography variant="body2">
                    <a href={selectedInfo.url} target="_blank" rel="noopener noreferrer">
                      {selectedInfo.url}
                    </a>
                  </Typography>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleInfoDialogClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MapViewer;
