import React, { useState, useRef, useEffect } from 'react';
import { Map } from 'react-map-gl';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { DeckGL } from '@deck.gl/react';
import { GeoJsonLayer, ScatterplotLayer, IconLayer } from '@deck.gl/layers';
import { H3HexagonLayer } from '@deck.gl/geo-layers';
import { FlyToInterpolator } from '@deck.gl/core';
import * as turf from '@turf/turf';

// Define types for props
interface MapComponentProps {
  initialViewState?: {
    longitude: number;
    latitude: number;
    zoom: number;
    pitch?: number;
    bearing?: number;
  };
  geojsonData?: any;
  pointData?: any[];
  hexagonData?: any[];
  onMapClick?: (info: any) => void;
  onMapLoad?: () => void;
  height?: string;
  width?: string;
  mapStyle?: string;
  showControls?: boolean;
}

const MapComponent: React.FC<MapComponentProps> = ({
  initialViewState = {
    longitude: 0,
    latitude: 0,
    zoom: 1,
    pitch: 0,
    bearing: 0
  },
  geojsonData,
  pointData,
  hexagonData,
  onMapClick,
  onMapLoad,
  height = '500px',
  width = '100%',
  mapStyle = 'https://demotiles.maplibre.org/style.json',
  showControls = true
}) => {
  const [viewState, setViewState] = useState(initialViewState);
  const mapRef = useRef(null);
  const deckRef = useRef(null);

  // Handle view state changes
  const handleViewStateChange = ({ viewState }) => {
    setViewState(viewState);
  };

  // Create layers based on provided data
  const layers = [];

  // Add GeoJSON layer if data is provided
  if (geojsonData) {
    layers.push(
      new GeoJsonLayer({
        id: 'geojson-layer',
        data: geojsonData,
        pickable: true,
        stroked: true,
        filled: true,
        extruded: false,
        lineWidthScale: 1,
        lineWidthMinPixels: 2,
        getFillColor: d => d.properties.fillColor || [160, 160, 180, 200],
        getLineColor: d => d.properties.lineColor || [0, 0, 0, 255],
        getLineWidth: d => d.properties.lineWidth || 1,
        getElevation: d => d.properties.elevation || 0,
        onHover: info => {
          // You can implement custom hover behavior here
        },
        onClick: info => {
          if (onMapClick) onMapClick(info);
        }
      })
    );
  }

  // Add point data layer if provided
  if (pointData) {
    layers.push(
      new ScatterplotLayer({
        id: 'scatterplot-layer',
        data: pointData,
        pickable: true,
        opacity: 0.8,
        stroked: true,
        filled: true,
        radiusScale: 6,
        radiusMinPixels: 3,
        radiusMaxPixels: 100,
        lineWidthMinPixels: 1,
        getPosition: d => d.coordinates,
        getRadius: d => d.radius || 5,
        getFillColor: d => d.fillColor || [255, 140, 0],
        getLineColor: d => d.lineColor || [0, 0, 0],
        onClick: info => {
          if (onMapClick) onMapClick(info);
        }
      })
    );
  }

  // Add hexagon layer if data is provided
  if (hexagonData) {
    layers.push(
      new H3HexagonLayer({
        id: 'h3-hexagon-layer',
        data: hexagonData,
        pickable: true,
        wireframe: false,
        filled: true,
        extruded: true,
        elevationScale: 20,
        getHexagon: d => d.hexagonId,
        getFillColor: d => d.fillColor || [255, 165, 0, 200],
        getElevation: d => d.elevation || 1,
        onClick: info => {
          if (onMapClick) onMapClick(info);
        }
      })
    );
  }

  // Fly to a specific location
  const flyToLocation = (longitude, latitude, zoom = 12) => {
    setViewState({
      ...viewState,
      longitude,
      latitude,
      zoom,
      transitionDuration: 1000,
      transitionInterpolator: new FlyToInterpolator()
    });
  };

  // Fit bounds to GeoJSON data
  const fitBounds = (geojson) => {
    if (!geojson) return;
    
    try {
      const bbox = turf.bbox(geojson);
      const [minLng, minLat, maxLng, maxLat] = bbox;
      
      // Get the map container dimensions
      const mapContainer = mapRef.current.getMap().getContainer();
      const { width, height } = mapContainer.getBoundingClientRect();
      
      // Calculate the appropriate viewport to fit the bounds
      const viewport = new WebMercatorViewport({ width, height })
        .fitBounds([[minLng, minLat], [maxLng, maxLat]], { padding: 40 });
      
      setViewState({
        ...viewState,
        longitude: viewport.longitude,
        latitude: viewport.latitude,
        zoom: viewport.zoom,
        transitionDuration: 1000,
        transitionInterpolator: new FlyToInterpolator()
      });
    } catch (error) {
      console.error('Error fitting bounds:', error);
    }
  };

  // Expose methods to parent components
  useEffect(() => {
    if (mapRef.current) {
      // Add the fitBounds and flyToLocation methods to the map ref
      mapRef.current.fitBounds = fitBounds;
      mapRef.current.flyToLocation = flyToLocation;
      
      // Call onMapLoad callback if provided
      if (onMapLoad) onMapLoad();
    }
  }, [mapRef.current]);

  return (
    <div style={{ position: 'relative', height, width }}>
      <DeckGL
        ref={deckRef}
        viewState={viewState}
        onViewStateChange={handleViewStateChange}
        controller={true}
        layers={layers}
        pickingRadius={5}
        getCursor={({isDragging, isHovering}) => 
          isDragging ? 'grabbing' : (isHovering ? 'pointer' : 'grab')
        }
      >
        <Map
          ref={mapRef}
          reuseMaps
          mapLib={maplibregl}
          mapStyle={mapStyle}
          preventStyleDiffing={true}
        >
          {showControls && (
            <>
              <div className="maplibregl-ctrl-top-right" style={{ position: 'absolute', right: 10, top: 10 }}>
                <div className="maplibregl-ctrl maplibregl-ctrl-group">
                  <button 
                    className="maplibregl-ctrl-zoom-in" 
                    onClick={() => setViewState({...viewState, zoom: viewState.zoom + 1})}
                  >
                    <span className="maplibregl-ctrl-icon">+</span>
                  </button>
                  <button 
                    className="maplibregl-ctrl-zoom-out" 
                    onClick={() => setViewState({...viewState, zoom: viewState.zoom - 1})}
                  >
                    <span className="maplibregl-ctrl-icon">-</span>
                  </button>
                </div>
              </div>
            </>
          )}
        </Map>
      </DeckGL>
      
      <style jsx>{`
        .maplibregl-ctrl-group {
          background-color: #fff;
          border-radius: 4px;
          box-shadow: 0 0 0 2px rgba(0,0,0,0.1);
        }
        
        .maplibregl-ctrl-group button {
          width: 30px;
          height: 30px;
          display: block;
          padding: 0;
          outline: none;
          border: 0;
          box-sizing: border-box;
          background-color: transparent;
          cursor: pointer;
          text-align: center;
        }
        
        .maplibregl-ctrl-icon {
          display: block;
          width: 100%;
          height: 100%;
          font-size: 18px;
          line-height: 30px;
        }
      `}</style>
    </div>
  );
};

export default MapComponent;
