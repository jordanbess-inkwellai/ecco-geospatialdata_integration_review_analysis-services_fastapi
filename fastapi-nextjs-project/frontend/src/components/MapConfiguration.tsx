import React, { useState, useEffect, useRef } from 'react';
import { Map, NavigationControl, ScaleControl, GeolocateControl } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import axios from 'axios';

// Import custom components
import LayerPanel from './map/LayerPanel';
import SearchWidget from './map/SearchWidget';
import AttributeTable from './map/AttributeTable';
import ExportPanel from './map/ExportPanel';
import StyleEditor from './map/StyleEditor';

// Types
interface MapConfigurationProps {
  height?: string;
  width?: string;
  initialCenter?: [number, number];
  initialZoom?: number;
  martinUrl?: string;
  pgFeatureservUrl?: string;
}

interface Layer {
  id: string;
  name: string;
  type: 'vector' | 'raster' | 'geojson';
  source: string;
  sourceLayer?: string;
  visible: boolean;
  style?: any;
  metadata?: any;
}

const MapConfiguration: React.FC<MapConfigurationProps> = ({
  height = '600px',
  width = '100%',
  initialCenter = [0, 0],
  initialZoom = 2,
  martinUrl = process.env.NEXT_PUBLIC_MARTIN_URL || 'http://localhost:3001',
  pgFeatureservUrl = process.env.NEXT_PUBLIC_PG_FEATURESERV_URL || 'http://localhost:9000',
}) => {
  // Refs
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<Map | null>(null);
  
  // State
  const [layers, setLayers] = useState<Layer[]>([]);
  const [availableSources, setAvailableSources] = useState<any[]>([]);
  const [selectedLayer, setSelectedLayer] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [cqlFilter, setCqlFilter] = useState<string>('');
  const [featureData, setFeatureData] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Initialize map
  useEffect(() => {
    if (map.current) return; // Map already initialized
    
    if (mapContainer.current) {
      map.current = new Map({
        container: mapContainer.current,
        style: {
          version: 8,
          sources: {},
          layers: [],
        },
        center: initialCenter,
        zoom: initialZoom,
      });
      
      // Add controls
      map.current.addControl(new NavigationControl(), 'top-right');
      map.current.addControl(new ScaleControl(), 'bottom-left');
      map.current.addControl(new GeolocateControl({
        positionOptions: {
          enableHighAccuracy: true
        },
        trackUserLocation: true
      }), 'top-right');
      
      // Load available sources
      fetchAvailableSources();
    }
    
    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [initialCenter, initialZoom]);
  
  // Fetch available sources from Martin and pg_featureserv
  const fetchAvailableSources = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch Martin sources (vector tiles)
      const martinResponse = await axios.get(`${martinUrl}/index.json`);
      
      // Fetch pg_featureserv collections
      const pgFeatureservResponse = await axios.get(`${pgFeatureservUrl}/collections`);
      
      // Combine sources
      const sources = [
        ...Object.entries(martinResponse.data.vector_layers || {}).map(([id, layer]: [string, any]) => ({
          id,
          name: layer.description || id,
          type: 'vector',
          url: `${martinUrl}/tiles/${id}/{z}/{x}/{y}.pbf`,
          sourceLayer: id,
        })),
        ...(pgFeatureservResponse.data.collections || []).map((collection: any) => ({
          id: collection.name,
          name: collection.title || collection.name,
          type: 'geojson',
          url: `${pgFeatureservUrl}/collections/${collection.name}/items.json`,
          description: collection.description,
        })),
      ];
      
      setAvailableSources(sources);
    } catch (err) {
      console.error('Error fetching available sources:', err);
      setError('Failed to load available map sources. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };
  
  // Add layer to map
  const addLayer = (source: any, style: any = {}) => {
    if (!map.current) return;
    
    const newLayer: Layer = {
      id: `layer-${source.id}`,
      name: source.name,
      type: source.type,
      source: source.id,
      sourceLayer: source.sourceLayer,
      visible: true,
      style,
      metadata: {
        originalSource: source,
      },
    };
    
    // Add source to map
    if (source.type === 'vector') {
      map.current.addSource(source.id, {
        type: 'vector',
        tiles: [source.url],
      });
      
      // Add layer to map
      map.current.addLayer({
        id: newLayer.id,
        type: style.type || 'fill',
        source: source.id,
        'source-layer': source.sourceLayer,
        paint: style.paint || {
          'fill-color': 'rgba(0, 100, 200, 0.5)',
          'fill-outline-color': 'rgba(0, 100, 200, 1)',
        },
      });
    } else if (source.type === 'geojson') {
      map.current.addSource(source.id, {
        type: 'geojson',
        data: source.url,
      });
      
      // Add layer to map
      map.current.addLayer({
        id: newLayer.id,
        type: style.type || 'circle',
        source: source.id,
        paint: style.paint || {
          'circle-radius': 5,
          'circle-color': 'rgba(0, 100, 200, 0.5)',
          'circle-stroke-width': 1,
          'circle-stroke-color': 'rgba(0, 100, 200, 1)',
        },
      });
    }
    
    // Update layers state
    setLayers(prevLayers => [...prevLayers, newLayer]);
    
    // Set as selected layer
    setSelectedLayer(newLayer.id);
  };
  
  // Remove layer from map
  const removeLayer = (layerId: string) => {
    if (!map.current) return;
    
    const layer = layers.find(l => l.id === layerId);
    if (!layer) return;
    
    // Remove layer from map
    if (map.current.getLayer(layerId)) {
      map.current.removeLayer(layerId);
    }
    
    // Remove source from map if no other layers use it
    const otherLayersUsingSource = layers.filter(l => l.source === layer.source && l.id !== layerId);
    if (otherLayersUsingSource.length === 0 && map.current.getSource(layer.source)) {
      map.current.removeSource(layer.source);
    }
    
    // Update layers state
    setLayers(prevLayers => prevLayers.filter(l => l.id !== layerId));
    
    // Update selected layer
    if (selectedLayer === layerId) {
      setSelectedLayer(null);
    }
  };
  
  // Toggle layer visibility
  const toggleLayerVisibility = (layerId: string) => {
    if (!map.current) return;
    
    const layer = layers.find(l => l.id === layerId);
    if (!layer) return;
    
    const newVisibility = !layer.visible;
    
    // Update map
    map.current.setLayoutProperty(
      layerId,
      'visibility',
      newVisibility ? 'visible' : 'none'
    );
    
    // Update layers state
    setLayers(prevLayers => 
      prevLayers.map(l => 
        l.id === layerId ? { ...l, visible: newVisibility } : l
      )
    );
  };
  
  // Update layer style
  const updateLayerStyle = (layerId: string, style: any) => {
    if (!map.current) return;
    
    const layer = layers.find(l => l.id === layerId);
    if (!layer) return;
    
    // Update paint properties
    Object.entries(style.paint || {}).forEach(([property, value]) => {
      map.current?.setPaintProperty(layerId, property, value);
    });
    
    // Update layout properties
    Object.entries(style.layout || {}).forEach(([property, value]) => {
      map.current?.setLayoutProperty(layerId, property, value);
    });
    
    // Update layers state
    setLayers(prevLayers => 
      prevLayers.map(l => 
        l.id === layerId ? { ...l, style: { ...l.style, ...style } } : l
      )
    );
  };
  
  // Handle search with CQL filtering
  const handleSearch = async () => {
    if (!selectedLayer) return;
    
    const layer = layers.find(l => l.id === selectedLayer);
    if (!layer) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Construct CQL filter if search query exists
      let filter = cqlFilter;
      if (searchQuery && !cqlFilter) {
        // Simple text search across all string properties
        filter = `ILIKE('%${searchQuery}%')`;
      } else if (searchQuery && cqlFilter) {
        // Combine search query with existing filter
        filter = `${cqlFilter} AND ILIKE('%${searchQuery}%')`;
      }
      
      // Get current map bounds for spatial filtering
      const bounds = map.current?.getBounds();
      let bbox = '';
      if (bounds) {
        bbox = `${bounds.getWest()},${bounds.getSouth()},${bounds.getEast()},${bounds.getNorth()}`;
      }
      
      // Fetch data from pg_featureserv with filters
      const url = new URL(`${pgFeatureservUrl}/collections/${layer.metadata.originalSource.id}/items.json`);
      
      // Add parameters
      if (filter) {
        url.searchParams.append('filter', filter);
      }
      if (bbox) {
        url.searchParams.append('bbox', bbox);
      }
      
      const response = await axios.get(url.toString());
      
      // Update feature data
      setFeatureData(response.data.features || []);
      
      // Update map source if it's a GeoJSON source
      if (layer.type === 'geojson' && map.current?.getSource(layer.source)) {
        (map.current.getSource(layer.source) as any).setData(response.data);
      }
    } catch (err) {
      console.error('Error searching features:', err);
      setError('Failed to search features. Please check your query and try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // Export data in different formats
  const exportData = async (format: string) => {
    if (!selectedLayer) return;
    
    const layer = layers.find(l => l.id === selectedLayer);
    if (!layer) return;
    
    setLoading(true);
    
    try {
      // Construct URL with current filters
      let url = `${pgFeatureservUrl}/collections/${layer.metadata.originalSource.id}/items`;
      
      // Add format extension
      switch (format) {
        case 'geojson':
          url += '.json';
          break;
        case 'html':
          url += '.html';
          break;
        case 'geoparquet':
        case 'flatgeobuf':
        case 'kml':
        case 'shapefile':
          // These are custom formats we'll implement in our backend
          url = `/api/v1/export/${layer.metadata.originalSource.id}?format=${format}`;
          break;
      }
      
      // Add filters if any
      const params = new URLSearchParams();
      if (cqlFilter) {
        params.append('filter', cqlFilter);
      }
      if (searchQuery) {
        params.append('q', searchQuery);
      }
      
      // Get current map bounds for spatial filtering
      const bounds = map.current?.getBounds();
      if (bounds) {
        const bbox = `${bounds.getWest()},${bounds.getSouth()},${bounds.getEast()},${bounds.getNorth()}`;
        params.append('bbox', bbox);
      }
      
      // Add parameters to URL
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      
      // Trigger download
      window.open(url, '_blank');
    } catch (err) {
      console.error('Error exporting data:', err);
      setError('Failed to export data. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="map-configuration">
      <div className="map-container" ref={mapContainer} style={{ height, width }}></div>
      
      <div className="map-panels">
        <LayerPanel
          layers={layers}
          availableSources={availableSources}
          selectedLayer={selectedLayer}
          onAddLayer={addLayer}
          onRemoveLayer={removeLayer}
          onToggleVisibility={toggleLayerVisibility}
          onSelectLayer={setSelectedLayer}
        />
        
        <div className="map-tools">
          <SearchWidget
            searchQuery={searchQuery}
            cqlFilter={cqlFilter}
            onSearchQueryChange={setSearchQuery}
            onCqlFilterChange={setCqlFilter}
            onSearch={handleSearch}
            loading={loading}
          />
          
          {selectedLayer && (
            <StyleEditor
              layer={layers.find(l => l.id === selectedLayer)}
              onStyleChange={(style) => updateLayerStyle(selectedLayer, style)}
            />
          )}
          
          <ExportPanel
            formats={['geojson', 'geoparquet', 'flatgeobuf', 'kml', 'shapefile', 'html']}
            onExport={exportData}
            disabled={!selectedLayer || loading}
          />
        </div>
      </div>
      
      {selectedLayer && (
        <AttributeTable
          data={featureData}
          loading={loading}
          error={error}
          onRowClick={(feature) => {
            // Fly to feature
            if (map.current && feature.geometry) {
              // Calculate center of feature
              let center;
              if (feature.geometry.type === 'Point') {
                center = feature.geometry.coordinates;
              } else if (feature.bbox) {
                // Use bbox center if available
                center = [
                  (feature.bbox[0] + feature.bbox[2]) / 2,
                  (feature.bbox[1] + feature.bbox[3]) / 2
                ];
              }
              
              if (center) {
                map.current.flyTo({
                  center,
                  zoom: 14,
                  duration: 1000
                });
              }
            }
          }}
        />
      )}
      
      <style jsx>{`
        .map-configuration {
          display: flex;
          flex-direction: column;
          height: ${height};
          width: ${width};
          position: relative;
        }
        
        .map-container {
          flex: 1;
          min-height: 400px;
        }
        
        .map-panels {
          position: absolute;
          top: 10px;
          left: 10px;
          z-index: 1;
          display: flex;
          flex-direction: column;
          gap: 10px;
          max-width: 300px;
          max-height: calc(100% - 20px);
          overflow-y: auto;
        }
        
        .map-tools {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
      `}</style>
    </div>
  );
};

export default MapConfiguration;
