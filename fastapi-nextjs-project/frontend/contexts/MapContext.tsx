import React, { createContext, useState, useCallback, useRef, ReactNode } from 'react';
import maplibregl from 'maplibre-gl';

interface MapContextType {
  map: maplibregl.Map | null;
  initializeMap: (container: HTMLElement, options?: maplibregl.MapOptions) => void;
  addGeoJSONToMap: (geojson: any, layerId: string) => void;
  selectFeatureFromMap: () => Promise<any>;
  zoomToFeature: (geojson: any) => void;
  removeLayer: (layerId: string) => void;
}

export const MapContext = createContext<MapContextType | null>(null);

interface MapProviderProps {
  children: ReactNode;
}

export const MapProvider: React.FC<MapProviderProps> = ({ children }) => {
  const [map, setMap] = useState<maplibregl.Map | null>(null);
  const selectModeRef = useRef<{
    active: boolean;
    resolve: ((value: any) => void) | null;
    reject: ((reason: any) => void) | null;
  }>({
    active: false,
    resolve: null,
    reject: null
  });

  const initializeMap = useCallback((container: HTMLElement, options?: maplibregl.MapOptions) => {
    if (map) {
      map.remove();
    }

    const defaultOptions: maplibregl.MapOptions = {
      container,
      style: {
        version: 8,
        sources: {
          'osm': {
            type: 'raster',
            tiles: [
              'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
              'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
              'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png'
            ],
            tileSize: 256,
            attribution: '© OpenStreetMap contributors'
          }
        },
        layers: [
          {
            id: 'osm-tiles',
            type: 'raster',
            source: 'osm',
            minzoom: 0,
            maxzoom: 19
          }
        ]
      },
      center: [0, 0],
      zoom: 2
    };

    const newMap = new maplibregl.Map({
      ...defaultOptions,
      ...options
    });

    newMap.on('load', () => {
      console.log('Map loaded');
    });

    // Setup click handler for feature selection
    newMap.on('click', (e) => {
      if (selectModeRef.current.active && selectModeRef.current.resolve) {
        // Get clicked point
        const point = {
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: [e.lngLat.lng, e.lngLat.lat]
          },
          properties: {}
        };
        
        selectModeRef.current.active = false;
        selectModeRef.current.resolve(point);
      }
    });

    setMap(newMap);
    return newMap;
  }, [map]);

  const addGeoJSONToMap = useCallback((geojson: any, layerId: string) => {
    if (!map) return;

    // Remove existing layer and source if they exist
    if (map.getLayer(layerId)) {
      map.removeLayer(layerId);
    }
    if (map.getSource(layerId)) {
      map.removeSource(layerId);
    }

    // Add the GeoJSON source
    map.addSource(layerId, {
      type: 'geojson',
      data: geojson
    });

    // Determine the geometry type to style appropriately
    let type = 'fill';
    let paint: any = {
      'fill-color': '#0080ff',
      'fill-opacity': 0.5,
      'fill-outline-color': '#0066cc'
    };

    if (geojson.type === 'Feature') {
      if (geojson.geometry.type === 'Point' || geojson.geometry.type === 'MultiPoint') {
        type = 'circle';
        paint = {
          'circle-radius': 6,
          'circle-color': '#0080ff',
          'circle-stroke-width': 1,
          'circle-stroke-color': '#ffffff'
        };
      } else if (geojson.geometry.type === 'LineString' || geojson.geometry.type === 'MultiLineString') {
        type = 'line';
        paint = {
          'line-color': '#0080ff',
          'line-width': 3
        };
      }
    } else if (geojson.type === 'FeatureCollection' && geojson.features.length > 0) {
      const firstFeature = geojson.features[0];
      if (firstFeature.geometry.type === 'Point' || firstFeature.geometry.type === 'MultiPoint') {
        type = 'circle';
        paint = {
          'circle-radius': 6,
          'circle-color': '#0080ff',
          'circle-stroke-width': 1,
          'circle-stroke-color': '#ffffff'
        };
      } else if (firstFeature.geometry.type === 'LineString' || firstFeature.geometry.type === 'MultiLineString') {
        type = 'line';
        paint = {
          'line-color': '#0080ff',
          'line-width': 3
        };
      }
    }

    // Add the layer
    map.addLayer({
      id: layerId,
      type,
      source: layerId,
      paint
    });

    // Zoom to the feature
    zoomToFeature(geojson);
  }, [map]);

  const selectFeatureFromMap = useCallback((): Promise<any> => {
    if (!map) {
      return Promise.reject(new Error('Map not initialized'));
    }

    return new Promise((resolve, reject) => {
      selectModeRef.current = {
        active: true,
        resolve,
        reject
      };

      // Change cursor to indicate selection mode
      map.getCanvas().style.cursor = 'crosshair';

      // Add a timeout to cancel selection mode after 30 seconds
      setTimeout(() => {
        if (selectModeRef.current.active) {
          selectModeRef.current.active = false;
          map.getCanvas().style.cursor = '';
          reject(new Error('Selection timed out'));
        }
      }, 30000);
    }).finally(() => {
      // Reset cursor
      if (map) {
        map.getCanvas().style.cursor = '';
      }
    });
  }, [map]);

  const zoomToFeature = useCallback((geojson: any) => {
    if (!map || !geojson) return;

    try {
      // Calculate bounds
      const bounds = new maplibregl.LngLatBounds();
      
      if (geojson.type === 'Feature') {
        extendBoundsWithGeometry(bounds, geojson.geometry);
      } else if (geojson.type === 'FeatureCollection') {
        geojson.features.forEach((feature: any) => {
          extendBoundsWithGeometry(bounds, feature.geometry);
        });
      } else if (geojson.type && geojson.coordinates) {
        // It's a geometry object
        extendBoundsWithGeometry(bounds, geojson);
      }

      // Only fit bounds if we have coordinates
      if (!bounds.isEmpty()) {
        map.fitBounds(bounds, {
          padding: 50,
          maxZoom: 16
        });
      }
    } catch (error) {
      console.error('Error zooming to feature:', error);
    }
  }, [map]);

  const extendBoundsWithGeometry = (bounds: maplibregl.LngLatBounds, geometry: any) => {
    if (!geometry || !geometry.type || !geometry.coordinates) return;

    switch (geometry.type) {
      case 'Point':
        bounds.extend(geometry.coordinates);
        break;
      case 'LineString':
      case 'MultiPoint':
        geometry.coordinates.forEach((coord: [number, number]) => {
          bounds.extend(coord);
        });
        break;
      case 'Polygon':
      case 'MultiLineString':
        geometry.coordinates.forEach((line: [number, number][]) => {
          line.forEach((coord: [number, number]) => {
            bounds.extend(coord);
          });
        });
        break;
      case 'MultiPolygon':
        geometry.coordinates.forEach((polygon: [number, number][][]) => {
          polygon.forEach((ring: [number, number][]) => {
            ring.forEach((coord: [number, number]) => {
              bounds.extend(coord);
            });
          });
        });
        break;
    }
  };

  const removeLayer = useCallback((layerId: string) => {
    if (!map) return;

    if (map.getLayer(layerId)) {
      map.removeLayer(layerId);
    }
    if (map.getSource(layerId)) {
      map.removeSource(layerId);
    }
  }, [map]);

  return (
    <MapContext.Provider
      value={{
        map,
        initializeMap,
        addGeoJSONToMap,
        selectFeatureFromMap,
        zoomToFeature,
        removeLayer
      }}
    >
      {children}
    </MapContext.Provider>
  );
};
