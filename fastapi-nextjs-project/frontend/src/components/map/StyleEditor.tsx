import React, { useState, useEffect } from 'react';
import {
  Style as GeoStylerStyle,
  Rule as GeoStylerRule,
  Symbolizer as GeoStylerSymbolizer,
  PointSymbolizer,
  LineSymbolizer,
  FillSymbolizer,
  TextSymbolizer,
  Filter as GeoStylerFilter
} from 'geostyler-style';
import {
  StyleParser as GeoStylerStyleParser,
  SldStyleParser,
  MapboxStyleParser,
  OpenLayersStyleParser
} from 'geostyler-style';

interface StyleEditorProps {
  layer: any;
  onStyleChange: (style: any) => void;
  outputFormat?: 'mapbox' | 'sld' | 'openlayers';
}

const StyleEditor: React.FC<StyleEditorProps> = ({
  layer,
  onStyleChange,
  outputFormat = 'mapbox'
}) => {
  // State for style configuration
  const [styleConfig, setStyleConfig] = useState<any>({
    type: 'simple',
    color: '#3388ff',
    opacity: 0.7,
    outlineColor: '#000000',
    outlineWidth: 1,
    outlineOpacity: 1,
    size: 5,
    width: 2,
    symbol: 'circle',
    label: '',
    labelField: '',
    labelSize: 12,
    labelColor: '#000000',
    labelHalo: true,
    labelHaloColor: '#ffffff',
    labelHaloWidth: 2
  });

  // State for classification
  const [classificationConfig, setClassificationConfig] = useState<any>({
    field: '',
    method: 'equalInterval',
    classes: 5,
    colorRamp: 'viridis'
  });

  // State for rule-based styling
  const [rules, setRules] = useState<any[]>([]);

  // State for available fields
  const [availableFields, setAvailableFields] = useState<string[]>([]);

  // State for the current tab
  const [activeTab, setActiveTab] = useState<'simple' | 'classified' | 'rule-based'>('simple');

  // State for SLD output
  const [sldOutput, setSldOutput] = useState<string>('');

  // Initialize style based on layer type
  useEffect(() => {
    if (!layer) return;

    // Determine layer geometry type
    const geometryType = getGeometryType(layer);

    // Set default style based on geometry type
    if (geometryType === 'point') {
      setStyleConfig(prev => ({
        ...prev,
        type: 'simple',
        color: '#3388ff',
        opacity: 0.7,
        outlineColor: '#000000',
        outlineWidth: 1,
        size: 5,
        symbol: 'circle'
      }));
    } else if (geometryType === 'line') {
      setStyleConfig(prev => ({
        ...prev,
        type: 'simple',
        color: '#3388ff',
        opacity: 0.7,
        width: 2,
        dashArray: ''
      }));
    } else if (geometryType === 'polygon') {
      setStyleConfig(prev => ({
        ...prev,
        type: 'simple',
        color: '#3388ff',
        opacity: 0.7,
        outlineColor: '#000000',
        outlineWidth: 1
      }));
    }

    // Extract available fields from layer metadata
    if (layer.metadata?.originalSource?.layers) {
      const fields = layer.metadata.originalSource.layers.flatMap((l: any) =>
        l.fields ? Object.keys(l.fields) : []
      );
      setAvailableFields([...new Set(fields)]);
    }
  }, [layer]);

  // Update style when configuration changes
  useEffect(() => {
    if (!layer) return;

    // Generate style based on active tab
    let style: any;

    if (activeTab === 'simple') {
      style = generateSimpleStyle();
    } else if (activeTab === 'classified') {
      style = generateClassifiedStyle();
    } else if (activeTab === 'rule-based') {
      style = generateRuleBasedStyle();
    }

    // Apply style to layer
    if (style) {
      onStyleChange(style);

      // Generate SLD if needed
      if (outputFormat === 'sld') {
        generateSLD(style);
      }
    }
  }, [styleConfig, classificationConfig, rules, activeTab]);

  // Helper function to determine geometry type
  const getGeometryType = (layer: any): 'point' | 'line' | 'polygon' => {
    if (!layer) return 'point';

    const type = layer.type;

    if (type === 'circle' || type === 'symbol') {
      return 'point';
    } else if (type === 'line') {
      return 'line';
    } else if (type === 'fill') {
      return 'polygon';
    }

    return 'point';
  };

  // Generate simple style
  const generateSimpleStyle = () => {
    const geometryType = getGeometryType(layer);

    if (geometryType === 'point') {
      return {
        type: 'circle',
        paint: {
          'circle-radius': styleConfig.size,
          'circle-color': styleConfig.color,
          'circle-opacity': styleConfig.opacity,
          'circle-stroke-width': styleConfig.outlineWidth,
          'circle-stroke-color': styleConfig.outlineColor,
          'circle-stroke-opacity': styleConfig.outlineOpacity
        },
        layout: styleConfig.label ? {
          'text-field': styleConfig.labelField ? ['get', styleConfig.labelField] : styleConfig.label,
          'text-size': styleConfig.labelSize,
          'text-offset': [0, 1.5],
          'text-anchor': 'top',
          'text-allow-overlap': false,
          'text-ignore-placement': false
        } : {}
      };
    } else if (geometryType === 'line') {
      return {
        type: 'line',
        paint: {
          'line-color': styleConfig.color,
          'line-opacity': styleConfig.opacity,
          'line-width': styleConfig.width,
          'line-dasharray': styleConfig.dashArray ? styleConfig.dashArray.split(',').map(Number) : undefined
        },
        layout: styleConfig.label ? {
          'text-field': styleConfig.labelField ? ['get', styleConfig.labelField] : styleConfig.label,
          'text-size': styleConfig.labelSize,
          'text-offset': [0, 1],
          'text-anchor': 'top',
          'text-allow-overlap': false,
          'text-ignore-placement': false
        } : {}
      };
    } else if (geometryType === 'polygon') {
      return {
        type: 'fill',
        paint: {
          'fill-color': styleConfig.color,
          'fill-opacity': styleConfig.opacity,
          'fill-outline-color': styleConfig.outlineColor
        },
        layout: styleConfig.label ? {
          'text-field': styleConfig.labelField ? ['get', styleConfig.labelField] : styleConfig.label,
          'text-size': styleConfig.labelSize,
          'text-offset': [0, 0],
          'text-anchor': 'center',
          'text-allow-overlap': false,
          'text-ignore-placement': false
        } : {}
      };
    }
  };

  // Generate classified style
  const generateClassifiedStyle = () => {
    // This is a simplified implementation
    // In a real application, you would compute class breaks and colors

    const geometryType = getGeometryType(layer);
    const field = classificationConfig.field;

    if (!field) return generateSimpleStyle();

    // Generate color ramp
    const colorRamp = generateColorRamp(
      classificationConfig.colorRamp,
      classificationConfig.classes
    );

    // Generate style based on geometry type
    if (geometryType === 'point') {
      return {
        type: 'circle',
        paint: {
          'circle-radius': styleConfig.size,
          'circle-color': [
            'step',
            ['get', field],
            colorRamp[0],
            20, colorRamp[1],
            40, colorRamp[2],
            60, colorRamp[3],
            80, colorRamp[4]
          ],
          'circle-opacity': styleConfig.opacity,
          'circle-stroke-width': styleConfig.outlineWidth,
          'circle-stroke-color': styleConfig.outlineColor
        }
      };
    } else if (geometryType === 'line') {
      return {
        type: 'line',
        paint: {
          'line-color': [
            'step',
            ['get', field],
            colorRamp[0],
            20, colorRamp[1],
            40, colorRamp[2],
            60, colorRamp[3],
            80, colorRamp[4]
          ],
          'line-opacity': styleConfig.opacity,
          'line-width': styleConfig.width
        }
      };
    } else if (geometryType === 'polygon') {
      return {
        type: 'fill',
        paint: {
          'fill-color': [
            'step',
            ['get', field],
            colorRamp[0],
            20, colorRamp[1],
            40, colorRamp[2],
            60, colorRamp[3],
            80, colorRamp[4]
          ],
          'fill-opacity': styleConfig.opacity,
          'fill-outline-color': styleConfig.outlineColor
        }
      };
    }
  };

  // Generate rule-based style
  const generateRuleBasedStyle = () => {
    // This would be implemented with a more complex rule system
    // For now, we'll return a simple style
    return generateSimpleStyle();
  };

  // Generate color ramp
  const generateColorRamp = (name: string, count: number): string[] => {
    // Predefined color ramps
    const colorRamps: Record<string, string[]> = {
      viridis: ['#440154', '#3b528b', '#21918c', '#5ec962', '#fde725'],
      magma: ['#000004', '#51127c', '#b63679', '#fb8861', '#fcfdbf'],
      plasma: ['#0d0887', '#6a00a8', '#b12a90', '#e16462', '#fca636'],
      inferno: ['#000004', '#51127c', '#b63679', '#fb8861', '#fcfdbf'],
      blues: ['#f7fbff', '#c6dbef', '#6baed6', '#2171b5', '#08306b'],
      reds: ['#fff5f0', '#fcbba1', '#fb6a4a', '#cb181d', '#67000d']
    };

    // Return the selected color ramp or a default one
    return colorRamps[name] || colorRamps.viridis;
  };

  // Generate SLD from style
  const generateSLD = async (style: any) => {
    try {
      // Convert MapBox style to GeoStyler style
      const mapboxParser = new MapboxStyleParser();
      const sldParser = new SldStyleParser();

      // Create a GeoStyler style from MapBox style
      const geostylerStyle = await mapboxParser.readStyle(style);

      // Convert GeoStyler style to SLD
      const sldStyle = await sldParser.writeStyle(geostylerStyle);

      // Set SLD output
      setSldOutput(sldStyle);
    } catch (error) {
      console.error('Error generating SLD:', error);
    }
  };

  // Publish style to GeoServer
  const publishToGeoServer = async () => {
    if (!layer || !styleConfig) return;

    try {
      // For GL JSON styles, we can directly use the current style
      const glStyle = generateSimpleStyle();

      // In a real implementation, you would make an API call to your backend
      // which would then publish the style to GeoServer

      // Mock API call
      /*
      const response = await axios.post('/api/v1/geoserver/styles', {
        name: `${layer.name}_style`,
        format: 'gl',
        style: glStyle
      });
      */

      // For now, just show an alert
      alert('Style would be published to GeoServer. This is a mock implementation.');

      // You could also generate and publish SLD if needed
      if (outputFormat === 'sld' && sldOutput) {
        /*
        const sldResponse = await axios.post('/api/v1/geoserver/styles', {
          name: `${layer.name}_style_sld`,
          format: 'sld',
          style: sldOutput
        });
        */
      }
    } catch (error) {
      console.error('Error publishing to GeoServer:', error);
      alert('Error publishing style to GeoServer');
    }
  };

  // Handle style property change
  const handleStyleChange = (property: string, value: any) => {
    setStyleConfig(prev => ({
      ...prev,
      [property]: value
    }));
  };

  // Handle classification property change
  const handleClassificationChange = (property: string, value: any) => {
    setClassificationConfig(prev => ({
      ...prev,
      [property]: value
    }));
  };

  // Handle tab change
  const handleTabChange = (tab: 'simple' | 'classified' | 'rule-based') => {
    setActiveTab(tab);
  };

  // Render color picker
  const renderColorPicker = (label: string, property: string, value: string) => (
    <div className="form-group">
      <label>{label}</label>
      <div className="color-picker">
        <input
          type="color"
          value={value}
          onChange={(e) => handleStyleChange(property, e.target.value)}
        />
        <input
          type="text"
          value={value}
          onChange={(e) => handleStyleChange(property, e.target.value)}
          className="color-text"
        />
      </div>
    </div>
  );

  // Render number input
  const renderNumberInput = (label: string, property: string, value: number, min: number = 0, max: number = 100, step: number = 1) => (
    <div className="form-group">
      <label>{label}</label>
      <div className="number-input">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => handleStyleChange(property, parseFloat(e.target.value))}
        />
        <input
          type="number"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => handleStyleChange(property, parseFloat(e.target.value))}
          className="number-text"
        />
      </div>
    </div>
  );

  // Render select input
  const renderSelectInput = (label: string, property: string, value: string, options: { value: string, label: string }[]) => (
    <div className="form-group">
      <label>{label}</label>
      <select
        value={value}
        onChange={(e) => handleStyleChange(property, e.target.value)}
      >
        {options.map(option => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );

  // Render field select
  const renderFieldSelect = (label: string, property: string, value: string) => (
    <div className="form-group">
      <label>{label}</label>
      <select
        value={value}
        onChange={(e) =>
          activeTab === 'classified'
            ? handleClassificationChange(property, e.target.value)
            : handleStyleChange(property, e.target.value)
        }
      >
        <option value="">Select a field</option>
        {availableFields.map(field => (
          <option key={field} value={field}>
            {field}
          </option>
        ))}
      </select>
    </div>
  );

  return (
    <div className="style-editor">
      <div className="tabs">
        <button
          className={`tab ${activeTab === 'simple' ? 'active' : ''}`}
          onClick={() => handleTabChange('simple')}
        >
          Simple
        </button>
        <button
          className={`tab ${activeTab === 'classified' ? 'active' : ''}`}
          onClick={() => handleTabChange('classified')}
        >
          Classified
        </button>
        <button
          className={`tab ${activeTab === 'rule-based' ? 'active' : ''}`}
          onClick={() => handleTabChange('rule-based')}
        >
          Rule-Based
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'simple' && (
          <div className="simple-style">
            <h3>Simple Style</h3>

            {getGeometryType(layer) === 'point' && (
              <>
                {renderNumberInput('Size', 'size', styleConfig.size, 1, 20, 1)}
                {renderColorPicker('Fill Color', 'color', styleConfig.color)}
                {renderNumberInput('Opacity', 'opacity', styleConfig.opacity, 0, 1, 0.1)}
                {renderColorPicker('Outline Color', 'outlineColor', styleConfig.outlineColor)}
                {renderNumberInput('Outline Width', 'outlineWidth', styleConfig.outlineWidth, 0, 5, 0.5)}
                {renderSelectInput('Symbol', 'symbol', styleConfig.symbol, [
                  { value: 'circle', label: 'Circle' },
                  { value: 'square', label: 'Square' },
                  { value: 'triangle', label: 'Triangle' },
                  { value: 'star', label: 'Star' }
                ])}
              </>
            )}

            {getGeometryType(layer) === 'line' && (
              <>
                {renderColorPicker('Line Color', 'color', styleConfig.color)}
                {renderNumberInput('Width', 'width', styleConfig.width, 0.5, 10, 0.5)}
                {renderNumberInput('Opacity', 'opacity', styleConfig.opacity, 0, 1, 0.1)}
                <div className="form-group">
                  <label>Dash Pattern (comma-separated)</label>
                  <input
                    type="text"
                    value={styleConfig.dashArray || ''}
                    onChange={(e) => handleStyleChange('dashArray', e.target.value)}
                    placeholder="e.g., 4,2"
                  />
                </div>
              </>
            )}

            {getGeometryType(layer) === 'polygon' && (
              <>
                {renderColorPicker('Fill Color', 'color', styleConfig.color)}
                {renderNumberInput('Opacity', 'opacity', styleConfig.opacity, 0, 1, 0.1)}
                {renderColorPicker('Outline Color', 'outlineColor', styleConfig.outlineColor)}
                {renderNumberInput('Outline Width', 'outlineWidth', styleConfig.outlineWidth, 0, 5, 0.5)}
              </>
            )}

            <h4>Labeling</h4>
            <div className="form-group">
              <label>Label Text</label>
              <input
                type="text"
                value={styleConfig.label}
                onChange={(e) => handleStyleChange('label', e.target.value)}
                placeholder="Enter static label text"
              />
            </div>

            {renderFieldSelect('Label Field', 'labelField', styleConfig.labelField)}
            {renderNumberInput('Label Size', 'labelSize', styleConfig.labelSize, 8, 24, 1)}
            {renderColorPicker('Label Color', 'labelColor', styleConfig.labelColor)}

            <div className="form-group">
              <label>Label Halo</label>
              <input
                type="checkbox"
                checked={styleConfig.labelHalo}
                onChange={(e) => handleStyleChange('labelHalo', e.target.checked)}
              />
            </div>

            {styleConfig.labelHalo && (
              <>
                {renderColorPicker('Halo Color', 'labelHaloColor', styleConfig.labelHaloColor)}
                {renderNumberInput('Halo Width', 'labelHaloWidth', styleConfig.labelHaloWidth, 0, 5, 0.5)}
              </>
            )}
          </div>
        )}

        {activeTab === 'classified' && (
          <div className="classified-style">
            <h3>Classified Style</h3>

            {renderFieldSelect('Classification Field', 'field', classificationConfig.field)}

            {renderSelectInput('Method', 'method', classificationConfig.method, [
              { value: 'equalInterval', label: 'Equal Interval' },
              { value: 'quantile', label: 'Quantile' },
              { value: 'jenks', label: 'Natural Breaks (Jenks)' }
            ])}

            {renderNumberInput('Number of Classes', 'classes', classificationConfig.classes, 2, 10, 1)}

            {renderSelectInput('Color Ramp', 'colorRamp', classificationConfig.colorRamp, [
              { value: 'viridis', label: 'Viridis' },
              { value: 'magma', label: 'Magma' },
              { value: 'plasma', label: 'Plasma' },
              { value: 'inferno', label: 'Inferno' },
              { value: 'blues', label: 'Blues' },
              { value: 'reds', label: 'Reds' }
            ])}

            <div className="color-ramp-preview">
              {generateColorRamp(classificationConfig.colorRamp, classificationConfig.classes).map((color, index) => (
                <div
                  key={index}
                  className="color-swatch"
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
          </div>
        )}

        {activeTab === 'rule-based' && (
          <div className="rule-based-style">
            <h3>Rule-Based Style</h3>
            <p>Rule-based styling is not yet implemented in this demo.</p>
          </div>
        )}
      </div>

      {outputFormat === 'sld' && sldOutput && (
        <div className="sld-output">
          <h3>SLD Output</h3>
          <pre>{sldOutput}</pre>
          <div className="sld-actions">
            <button
              className="copy-button"
              onClick={() => {
                navigator.clipboard.writeText(sldOutput);
                alert('SLD copied to clipboard!');
              }}
            >
              Copy SLD
            </button>
            <button
              className="export-button"
              onClick={() => {
                // Create a blob from the SLD content
                const blob = new Blob([sldOutput], { type: 'application/xml' });
                const url = URL.createObjectURL(blob);

                // Create a temporary link and trigger download
                const a = document.createElement('a');
                a.href = url;
                a.download = `${layer.name || 'style'}.sld`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
              }}
            >
              Export SLD File
            </button>
          </div>
        </div>
      )}

      <div className="geoserver-actions">
        <button
          className="geoserver-button"
          onClick={publishToGeoServer}
        >
          Publish to GeoServer
        </button>
        <p className="geoserver-note">
          Publishes the current style to GeoServer as a {outputFormat === 'sld' ? 'SLD' : 'GL JSON'} style.
          GeoServer's vector tile extension supports both formats.
        </p>
      </div>

      <style jsx>{`
        .style-editor {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 1rem;
          max-width: 100%;
          overflow: auto;
        }

        .tabs {
          display: flex;
          border-bottom: 1px solid #eee;
          margin-bottom: 1rem;
        }

        .tab {
          padding: 0.5rem 1rem;
          background: none;
          border: none;
          cursor: pointer;
          font-size: 0.9rem;
          opacity: 0.7;
        }

        .tab.active {
          border-bottom: 2px solid #0070f3;
          opacity: 1;
          font-weight: 500;
        }

        .tab-content {
          padding: 0.5rem 0;
        }

        h3 {
          margin-top: 0;
          margin-bottom: 1rem;
          font-size: 1.1rem;
        }

        h4 {
          margin-top: 1.5rem;
          margin-bottom: 0.5rem;
          font-size: 1rem;
        }

        .form-group {
          margin-bottom: 1rem;
        }

        label {
          display: block;
          margin-bottom: 0.5rem;
          font-size: 0.9rem;
          font-weight: 500;
        }

        input[type="text"],
        input[type="number"],
        select {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.9rem;
        }

        .color-picker {
          display: flex;
          align-items: center;
        }

        input[type="color"] {
          width: 40px;
          height: 40px;
          border: none;
          border-radius: 4px;
          margin-right: 0.5rem;
          cursor: pointer;
        }

        .color-text {
          flex: 1;
        }

        .number-input {
          display: flex;
          align-items: center;
        }

        input[type="range"] {
          flex: 1;
          margin-right: 0.5rem;
        }

        .number-text {
          width: 60px;
        }

        .color-ramp-preview {
          display: flex;
          height: 30px;
          margin-top: 0.5rem;
          border-radius: 4px;
          overflow: hidden;
        }

        .color-swatch {
          flex: 1;
        }

        .sld-output {
          margin-top: 1.5rem;
          padding-top: 1.5rem;
          border-top: 1px solid #eee;
        }

        pre {
          background-color: #f5f5f5;
          padding: 1rem;
          border-radius: 4px;
          overflow: auto;
          font-size: 0.8rem;
          max-height: 200px;
        }

        .sld-actions {
          display: flex;
          gap: 0.5rem;
          margin-top: 0.5rem;
        }

        .copy-button, .export-button {
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          padding: 0.5rem 1rem;
          font-size: 0.9rem;
          cursor: pointer;
          flex: 1;
        }

        .copy-button:hover, .export-button:hover {
          background-color: #0051a8;
        }

        .export-button {
          background-color: #28a745;
        }

        .export-button:hover {
          background-color: #218838;
        }

        .geoserver-actions {
          margin-top: 1.5rem;
          padding-top: 1.5rem;
          border-top: 1px solid #eee;
          display: flex;
          flex-direction: column;
          align-items: center;
        }

        .geoserver-button {
          background-color: #28a745;
          color: white;
          border: none;
          border-radius: 4px;
          padding: 0.75rem 1.5rem;
          font-size: 1rem;
          cursor: pointer;
          margin-bottom: 0.5rem;
        }

        .geoserver-button:hover {
          background-color: #218838;
        }

        .geoserver-note {
          font-size: 0.8rem;
          color: #666;
          text-align: center;
          max-width: 80%;
        }
      `}</style>
    </div>
  );
};

export default StyleEditor;
