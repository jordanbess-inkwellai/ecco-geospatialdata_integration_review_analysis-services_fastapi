import React, { useRef, useEffect, useState } from 'react';
import { Box } from '@mui/material';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

interface MapLibreMapProps {
  style?: string;
  center: [number, number];
  zoom: number;
  onMove?: (center: [number, number], zoom: number) => void;
  visibleLayers?: string[];
}

const MapLibreMap: React.FC<MapLibreMapProps> = ({
  style,
  center,
  zoom,
  onMove,
  visibleLayers = []
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [mapLoaded, setMapLoaded] = useState<boolean>(false);

  // Initialize the map
  useEffect(() => {
    if (map.current) return;
    
    if (mapContainer.current) {
      map.current = new maplibregl.Map({
        container: mapContainer.current,
        style: style || {
          version: 8,
          sources: {},
          layers: []
        },
        center: center,
        zoom: zoom
      });
      
      map.current.on('load', () => {
        setMapLoaded(true);
      });
      
      map.current.on('move', () => {
        if (map.current && onMove) {
          const center = map.current.getCenter();
          const zoom = map.current.getZoom();
          onMove([center.lat, center.lng], zoom);
        }
      });
    }
    
    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  // Update the map style
  useEffect(() => {
    if (map.current && style) {
      map.current.setStyle(style);
    }
  }, [style]);

  // Update the map center and zoom
  useEffect(() => {
    if (map.current) {
      map.current.setCenter([center[1], center[0]]);
      map.current.setZoom(zoom);
    }
  }, [center, zoom]);

  // Update layer visibility
  useEffect(() => {
    if (map.current && mapLoaded) {
      // Get all layers from the map
      const layers = map.current.getStyle().layers || [];
      
      // Update visibility for each layer
      layers.forEach(layer => {
        if (layer.id) {
          const visibility = visibleLayers.includes(layer.id) ? 'visible' : 'none';
          map.current?.setLayoutProperty(layer.id, 'visibility', visibility);
        }
      });
    }
  }, [visibleLayers, mapLoaded]);

  return (
    <Box
      ref={mapContainer}
      sx={{
        width: '100%',
        height: '100%'
      }}
    />
  );
};

export default MapLibreMap;
