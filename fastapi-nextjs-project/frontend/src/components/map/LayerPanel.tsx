import React, { useState } from 'react';

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

interface Source {
  id: string;
  name: string;
  type: string;
  url: string;
  sourceLayer?: string;
  description?: string;
}

interface LayerPanelProps {
  layers: Layer[];
  availableSources: Source[];
  selectedLayer: string | null;
  onAddLayer: (source: Source, style?: any) => void;
  onRemoveLayer: (layerId: string) => void;
  onToggleVisibility: (layerId: string) => void;
  onSelectLayer: (layerId: string | null) => void;
}

const LayerPanel: React.FC<LayerPanelProps> = ({
  layers,
  availableSources,
  selectedLayer,
  onAddLayer,
  onRemoveLayer,
  onToggleVisibility,
  onSelectLayer,
}) => {
  const [showAddPanel, setShowAddPanel] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSourceType, setSelectedSourceType] = useState<string | null>(null);

  // Filter available sources based on search term and type
  const filteredSources = availableSources.filter(source => {
    const matchesSearch = searchTerm === '' || 
      source.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (source.description && source.description.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesType = selectedSourceType === null || source.type === selectedSourceType;
    
    return matchesSearch && matchesType;
  });

  return (
    <div className="layer-panel">
      <div className="panel-header">
        <h3>Layers</h3>
        <button 
          className="add-button"
          onClick={() => setShowAddPanel(!showAddPanel)}
        >
          {showAddPanel ? 'Cancel' : 'Add Layer'}
        </button>
      </div>

      {showAddPanel && (
        <div className="add-layer-panel">
          <div className="search-filter">
            <input
              type="text"
              placeholder="Search sources..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <div className="type-filters">
              <button
                className={selectedSourceType === null ? 'active' : ''}
                onClick={() => setSelectedSourceType(null)}
              >
                All
              </button>
              <button
                className={selectedSourceType === 'vector' ? 'active' : ''}
                onClick={() => setSelectedSourceType('vector')}
              >
                Vector
              </button>
              <button
                className={selectedSourceType === 'geojson' ? 'active' : ''}
                onClick={() => setSelectedSourceType('geojson')}
              >
                GeoJSON
              </button>
            </div>
          </div>

          <div className="sources-list">
            {filteredSources.length === 0 ? (
              <div className="no-sources">No sources found</div>
            ) : (
              filteredSources.map(source => (
                <div key={source.id} className="source-item">
                  <div className="source-info">
                    <div className="source-name">{source.name}</div>
                    <div className="source-type">{source.type}</div>
                    {source.description && (
                      <div className="source-description">{source.description}</div>
                    )}
                  </div>
                  <button
                    className="add-source-button"
                    onClick={() => {
                      onAddLayer(source);
                      setShowAddPanel(false);
                    }}
                  >
                    Add
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      <div className="layers-list">
        {layers.length === 0 ? (
          <div className="no-layers">No layers added yet</div>
        ) : (
          layers.map(layer => (
            <div 
              key={layer.id} 
              className={`layer-item ${selectedLayer === layer.id ? 'selected' : ''}`}
              onClick={() => onSelectLayer(layer.id)}
            >
              <div className="layer-controls">
                <button
                  className={`visibility-toggle ${layer.visible ? 'visible' : 'hidden'}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleVisibility(layer.id);
                  }}
                >
                  {layer.visible ? '👁️' : '👁️‍🗨️'}
                </button>
                <button
                  className="remove-button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveLayer(layer.id);
                  }}
                >
                  ✕
                </button>
              </div>
              <div className="layer-info">
                <div className="layer-name">{layer.name}</div>
                <div className="layer-type">{layer.type}</div>
              </div>
            </div>
          ))
        )}
      </div>

      <style jsx>{`
        .layer-panel {
          background-color: white;
          border-radius: 4px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 12px;
          width: 280px;
          max-height: 500px;
          display: flex;
          flex-direction: column;
        }

        .panel-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .panel-header h3 {
          margin: 0;
          font-size: 16px;
        }

        .add-button {
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          padding: 4px 8px;
          font-size: 12px;
          cursor: pointer;
        }

        .add-layer-panel {
          margin-bottom: 12px;
          border: 1px solid #eaeaea;
          border-radius: 4px;
          padding: 8px;
        }

        .search-filter {
          margin-bottom: 8px;
        }

        .search-input {
          width: 100%;
          padding: 6px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
          margin-bottom: 8px;
        }

        .type-filters {
          display: flex;
          gap: 4px;
        }

        .type-filters button {
          background-color: #f0f0f0;
          border: 1px solid #ddd;
          border-radius: 4px;
          padding: 4px 8px;
          font-size: 12px;
          cursor: pointer;
          flex: 1;
        }

        .type-filters button.active {
          background-color: #0070f3;
          color: white;
          border-color: #0070f3;
        }

        .sources-list {
          max-height: 200px;
          overflow-y: auto;
          border: 1px solid #eaeaea;
          border-radius: 4px;
        }

        .source-item {
          padding: 8px;
          border-bottom: 1px solid #eaeaea;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .source-item:last-child {
          border-bottom: none;
        }

        .source-info {
          flex: 1;
        }

        .source-name {
          font-weight: 500;
          font-size: 14px;
        }

        .source-type {
          font-size: 12px;
          color: #666;
        }

        .source-description {
          font-size: 12px;
          color: #666;
          margin-top: 4px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .add-source-button {
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          padding: 4px 8px;
          font-size: 12px;
          cursor: pointer;
        }

        .layers-list {
          flex: 1;
          overflow-y: auto;
          border: 1px solid #eaeaea;
          border-radius: 4px;
        }

        .no-layers, .no-sources {
          padding: 12px;
          text-align: center;
          color: #666;
          font-size: 14px;
        }

        .layer-item {
          padding: 8px;
          border-bottom: 1px solid #eaeaea;
          display: flex;
          justify-content: space-between;
          align-items: center;
          cursor: pointer;
        }

        .layer-item:last-child {
          border-bottom: none;
        }

        .layer-item.selected {
          background-color: #f0f7ff;
          border-left: 3px solid #0070f3;
        }

        .layer-controls {
          display: flex;
          gap: 4px;
        }

        .visibility-toggle, .remove-button {
          background: none;
          border: none;
          cursor: pointer;
          font-size: 16px;
          padding: 2px;
        }

        .visibility-toggle.hidden {
          opacity: 0.5;
        }

        .layer-info {
          flex: 1;
          margin-left: 8px;
        }

        .layer-name {
          font-weight: 500;
          font-size: 14px;
        }

        .layer-type {
          font-size: 12px;
          color: #666;
        }
      `}</style>
    </div>
  );
};

export default LayerPanel;
