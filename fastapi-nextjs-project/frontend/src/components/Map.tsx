import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet icon issues with Next.js
useEffect(() => {
  delete L.Icon.Default.prototype._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: '/icons/marker-icon-2x.png',
    iconUrl: '/icons/marker-icon.png',
    shadowUrl: '/icons/marker-shadow.png',
  });
}, []);

interface MapProps {
  center?: [number, number];
  zoom?: number;
  geojsonData?: any;
  onMapClick?: (latlng: L.LatLng) => void;
  height?: string;
  width?: string;
}

const Map: React.FC<MapProps> = ({
  center = [0, 0],
  zoom = 2,
  geojsonData,
  onMapClick,
  height = '500px',
  width = '100%',
}) => {
  const mapRef = useRef<L.Map | null>(null);
  const geojsonLayerRef = useRef<L.GeoJSON | null>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Initialize map if it doesn't exist
    if (!mapRef.current) {
      mapRef.current = L.map(mapContainerRef.current).setView(center, zoom);

      // Add OpenStreetMap tile layer
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
      }).addTo(mapRef.current);

      // Add click handler if provided
      if (onMapClick) {
        mapRef.current.on('click', (e) => {
          onMapClick(e.latlng);
        });
      }
    } else {
      // Update center and zoom if map already exists
      mapRef.current.setView(center, zoom);
    }

    // Clean up on unmount
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [center, zoom, onMapClick]);

  // Handle GeoJSON data changes
  useEffect(() => {
    if (!mapRef.current) return;

    // Remove existing GeoJSON layer if it exists
    if (geojsonLayerRef.current) {
      geojsonLayerRef.current.removeFrom(mapRef.current);
      geojsonLayerRef.current = null;
    }

    // Add new GeoJSON layer if data is provided
    if (geojsonData) {
      geojsonLayerRef.current = L.geoJSON(geojsonData, {
        style: (feature) => {
          return {
            color: feature?.properties?.color || '#3388ff',
            weight: feature?.properties?.weight || 3,
            opacity: feature?.properties?.opacity || 0.8,
            fillColor: feature?.properties?.fillColor || '#3388ff',
            fillOpacity: feature?.properties?.fillOpacity || 0.2,
          };
        },
        pointToLayer: (feature, latlng) => {
          return L.circleMarker(latlng, {
            radius: feature?.properties?.radius || 8,
            fillColor: feature?.properties?.fillColor || '#3388ff',
            color: feature?.properties?.color || '#000',
            weight: feature?.properties?.weight || 1,
            opacity: feature?.properties?.opacity || 1,
            fillOpacity: feature?.properties?.fillOpacity || 0.8,
          });
        },
        onEachFeature: (feature, layer) => {
          if (feature.properties && feature.properties.popupContent) {
            layer.bindPopup(feature.properties.popupContent);
          } else if (feature.properties && feature.properties.name) {
            layer.bindPopup(`<b>${feature.properties.name}</b><br>${feature.properties.description || ''}`);
          }
        },
      }).addTo(mapRef.current);

      // Fit bounds to GeoJSON data
      const bounds = geojsonLayerRef.current.getBounds();
      if (bounds.isValid()) {
        mapRef.current.fitBounds(bounds);
      }
    }
  }, [geojsonData]);

  return (
    <div 
      ref={mapContainerRef} 
      style={{ height, width }} 
      className="leaflet-map"
    />
  );
};

export default Map;
