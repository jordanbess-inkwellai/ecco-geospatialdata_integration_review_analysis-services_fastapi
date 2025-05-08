import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Grid,
  Chip
} from '@mui/material';
import dynamic from 'next/dynamic';

// Dynamically import the map components to avoid SSR issues
const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false }
);

const TileLayer = dynamic(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false }
);

const GeoJSON = dynamic(
  () => import('react-leaflet').then((mod) => mod.GeoJSON),
  { ssr: false }
);

const Marker = dynamic(
  () => import('react-leaflet').then((mod) => mod.Marker),
  { ssr: false }
);

const Popup = dynamic(
  () => import('react-leaflet').then((mod) => mod.Popup),
  { ssr: false }
);

// Import Leaflet CSS
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix Leaflet marker icon issue
const defaultIcon = L.icon({
  iconUrl: '/images/marker-icon.png',
  shadowUrl: '/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = defaultIcon;

interface DataMapProps {
  data: any[];
  geometryColumn: string;
}

const DataMap: React.FC<DataMapProps> = ({ data, geometryColumn }) => {
  const [colorBy, setColorBy] = useState<string>('');
  const [columns, setColumns] = useState<string[]>([]);
  const [numericColumns, setNumericColumns] = useState<string[]>([]);
  const [geoJsonData, setGeoJsonData] = useState<any>(null);
  const [mapCenter, setMapCenter] = useState<[number, number]>([0, 0]);
  const [mapZoom, setMapZoom] = useState<number>(2);
  const [colorScale, setColorScale] = useState<number[]>([0, 100]);
  const [minValue, setMinValue] = useState<number>(0);
  const [maxValue, setMaxValue] = useState<number>(100);
  
  const mapRef = useRef<any>(null);

  // Initialize columns and prepare GeoJSON data
  useEffect(() => {
    if (data && data.length > 0 && geometryColumn) {
      // Get columns from the first row
      const allColumns = Object.keys(data[0]).filter(col => col !== geometryColumn);
      setColumns(allColumns);
      
      // Identify numeric columns
      const numeric = allColumns.filter(column => {
        const value = data[0][column];
        return typeof value === 'number';
      });
      setNumericColumns(numeric);
      
      // Set default color column if not already set
      if (!colorBy && numeric.length > 0) {
        setColorBy(numeric[0]);
      }
      
      // Convert data to GeoJSON
      try {
        const features = data.map(row => {
          // Parse WKT geometry
          const wkt = row[geometryColumn];
          const geometry = parseWKT(wkt);
          
          // Create GeoJSON feature
          return {
            type: 'Feature',
            geometry,
            properties: { ...row }
          };
        });
        
        const geojson = {
          type: 'FeatureCollection',
          features
        };
        
        setGeoJsonData(geojson);
        
        // Calculate map center and zoom
        if (features.length > 0) {
          // Create a Leaflet GeoJSON layer to calculate bounds
          const layer = L.geoJSON(geojson);
          const bounds = layer.getBounds();
          
          if (bounds.isValid()) {
            const center = bounds.getCenter();
            setMapCenter([center.lat, center.lng]);
            
            // Calculate appropriate zoom level
            if (mapRef.current) {
              const map = mapRef.current;
              map.fitBounds(bounds);
            }
          }
        }
        
        // Calculate min and max values for the color scale
        if (colorBy && numeric.includes(colorBy)) {
          const values = data.map(row => row[colorBy]).filter(val => val !== null && val !== undefined);
          const min = Math.min(...values);
          const max = Math.max(...values);
          
          setMinValue(min);
          setMaxValue(max);
          setColorScale([min, max]);
        }
      } catch (error) {
        console.error('Error converting data to GeoJSON:', error);
      }
    }
  }, [data, geometryColumn, colorBy]);

  // Parse WKT geometry to GeoJSON
  const parseWKT = (wkt: string): any => {
    if (!wkt) {
      return null;
    }
    
    // Basic WKT parsing for common geometry types
    if (wkt.startsWith('POINT')) {
      // Extract coordinates
      const coordsMatch = wkt.match(/POINT\s*\(\s*([^\s,)]+)\s+([^\s,)]+)\s*\)/i);
      if (coordsMatch) {
        const x = parseFloat(coordsMatch[1]);
        const y = parseFloat(coordsMatch[2]);
        
        return {
          type: 'Point',
          coordinates: [x, y]
        };
      }
    } else if (wkt.startsWith('LINESTRING')) {
      // Extract coordinates
      const coordsMatch = wkt.match(/LINESTRING\s*\(\s*(.*)\s*\)/i);
      if (coordsMatch) {
        const coordsStr = coordsMatch[1];
        const coords = coordsStr.split(',').map(pair => {
          const [x, y] = pair.trim().split(/\s+/).map(parseFloat);
          return [x, y];
        });
        
        return {
          type: 'LineString',
          coordinates: coords
        };
      }
    } else if (wkt.startsWith('POLYGON')) {
      // Extract coordinates
      const coordsMatch = wkt.match(/POLYGON\s*\(\s*\(\s*(.*)\s*\)\s*\)/i);
      if (coordsMatch) {
        const coordsStr = coordsMatch[1];
        const coords = coordsStr.split(',').map(pair => {
          const [x, y] = pair.trim().split(/\s+/).map(parseFloat);
          return [x, y];
        });
        
        return {
          type: 'Polygon',
          coordinates: [coords]
        };
      }
    }
    
    // For more complex geometries, we would need a proper WKT parser
    console.warn('Unsupported WKT geometry type:', wkt);
    return null;
  };

  // Get color based on value
  const getColor = (value: number): string => {
    if (value === null || value === undefined) {
      return '#cccccc';
    }
    
    const [min, max] = colorScale;
    const normalized = (value - min) / (max - min);
    
    // Color gradient from blue to red
    const r = Math.floor(normalized * 255);
    const b = Math.floor((1 - normalized) * 255);
    
    return `rgb(${r}, 0, ${b})`;
  };

  // Style function for GeoJSON features
  const styleFunction = (feature: any) => {
    const value = feature.properties[colorBy];
    
    return {
      fillColor: getColor(value),
      weight: 1,
      opacity: 1,
      color: 'white',
      fillOpacity: 0.7
    };
  };

  // Popup content for GeoJSON features
  const popupContent = (feature: any) => {
    const properties = feature.properties;
    
    return (
      <div>
        {Object.entries(properties)
          .filter(([key]) => key !== geometryColumn)
          .map(([key, value]) => (
            <div key={key}>
              <strong>{key}:</strong> {String(value)}
            </div>
          ))}
      </div>
    );
  };

  // Handle color scale change
  const handleColorScaleChange = (event: Event, newValue: number | number[]) => {
    setColorScale(newValue as number[]);
  };

  // Check if the data is empty
  if (!data || data.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No data to display
        </Typography>
      </Box>
    );
  }

  return (
    <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth size="small">
            <InputLabel>Color By</InputLabel>
            <Select
              value={colorBy}
              onChange={(e) => setColorBy(e.target.value)}
              label="Color By"
            >
              {numericColumns.map((column) => (
                <MenuItem key={column} value={column}>
                  {column}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Typography variant="body2" gutterBottom>
            Color Scale
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Chip
              label={colorScale[0].toFixed(2)}
              size="small"
              sx={{ mr: 1, bgcolor: getColor(colorScale[0]) }}
            />
            <Slider
              value={colorScale}
              onChange={handleColorScaleChange}
              min={minValue}
              max={maxValue}
              step={(maxValue - minValue) / 100}
              valueLabelDisplay="auto"
              sx={{ mx: 2 }}
            />
            <Chip
              label={colorScale[1].toFixed(2)}
              size="small"
              sx={{ ml: 1, bgcolor: getColor(colorScale[1]) }}
            />
          </Box>
        </Grid>
      </Grid>
      
      <Box sx={{ flexGrow: 1, position: 'relative' }}>
        {geoJsonData ? (
          <MapContainer
            center={mapCenter}
            zoom={mapZoom}
            style={{ height: '100%', width: '100%' }}
            ref={mapRef}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            
            <GeoJSON
              data={geoJsonData}
              style={styleFunction}
              onEachFeature={(feature, layer) => {
                layer.bindPopup(popupContent(feature));
              }}
            />
          </MapContainer>
        ) : (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <Typography variant="body1" color="text.secondary">
              Loading map data...
            </Typography>
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default DataMap;
