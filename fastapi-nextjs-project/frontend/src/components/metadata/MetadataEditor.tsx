import React, { useState, useEffect } from 'react';
import { useForm, Controller, useFieldArray } from 'react-hook-form';
import axios from 'axios';
import { DatePicker } from '../ui/DatePicker';
import { MapSelector } from '../map/MapSelector';
import { TagInput } from '../ui/TagInput';
import { ContactSelector } from './ContactSelector';

interface MetadataEditorProps {
  datasetId?: number;
  initialData?: any;
  onSave?: (data: any) => void;
  onCancel?: () => void;
}

const MetadataEditor: React.FC<MetadataEditorProps> = ({
  datasetId,
  initialData,
  onSave,
  onCancel
}) => {
  // Form state
  const { control, handleSubmit, setValue, watch, formState: { errors } } = useForm({
    defaultValues: initialData || {
      title: '',
      description: '',
      abstract: '',
      resource_type: 'dataset',
      resource_format: '',
      keywords: [],
      contacts: [],
      bbox: [0, 0, 0, 0],
      temporal_start: null,
      temporal_end: null,
      metadata_language: 'en',
      is_published: false,
      attributes: []
    }
  });
  
  // Field array for attributes
  const { fields: attributeFields, append: appendAttribute, remove: removeAttribute } = useFieldArray({
    control,
    name: 'attributes'
  });
  
  // State for loading and errors
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // State for available keywords and contacts
  const [availableKeywords, setAvailableKeywords] = useState<any[]>([]);
  const [availableContacts, setAvailableContacts] = useState<any[]>([]);
  
  // Watch values for conditional rendering
  const resourceType = watch('resource_type');
  
  // Load dataset if datasetId is provided
  useEffect(() => {
    if (datasetId && !initialData) {
      loadDataset();
    }
    
    // Load available keywords and contacts
    loadKeywords();
    loadContacts();
  }, [datasetId]);
  
  // Load dataset
  const loadDataset = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`/api/v1/metadata/datasets/${datasetId}`);
      
      // Set form values
      Object.entries(response.data).forEach(([key, value]) => {
        setValue(key, value);
      });
    } catch (error: any) {
      console.error('Error loading dataset:', error);
      setError(error.response?.data?.detail || 'Error loading dataset');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Load available keywords
  const loadKeywords = async () => {
    try {
      const response = await axios.get('/api/v1/metadata/keywords');
      setAvailableKeywords(response.data);
    } catch (error) {
      console.error('Error loading keywords:', error);
    }
  };
  
  // Load available contacts
  const loadContacts = async () => {
    try {
      const response = await axios.get('/api/v1/metadata/contacts');
      setAvailableContacts(response.data);
    } catch (error) {
      console.error('Error loading contacts:', error);
    }
  };
  
  // Handle form submission
  const onSubmit = async (data: any) => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      let response;
      
      if (datasetId) {
        // Update existing dataset
        response = await axios.put(`/api/v1/metadata/datasets/${datasetId}`, data);
        setSuccess('Metadata updated successfully');
      } else {
        // Create new dataset
        response = await axios.post('/api/v1/metadata/datasets', data);
        setSuccess('Metadata created successfully');
      }
      
      // Call onSave callback if provided
      if (onSave) {
        onSave(response.data);
      }
    } catch (error: any) {
      console.error('Error saving metadata:', error);
      setError(error.response?.data?.detail || 'Error saving metadata');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle adding a new attribute
  const handleAddAttribute = () => {
    appendAttribute({
      name: '',
      description: '',
      data_type: 'string',
      unit: '',
      domain: null
    });
  };
  
  // Render resource type specific fields
  const renderResourceTypeFields = () => {
    switch (resourceType) {
      case 'dataset':
        return (
          <>
            <div className="form-group">
              <label>Resource Format</label>
              <Controller
                name="resource_format"
                control={control}
                rules={{ required: 'Resource format is required' }}
                render={({ field }) => (
                  <select {...field} className="form-control">
                    <option value="">Select format</option>
                    <option value="GeoJSON">GeoJSON</option>
                    <option value="Shapefile">Shapefile</option>
                    <option value="GeoPackage">GeoPackage</option>
                    <option value="GeoTIFF">GeoTIFF</option>
                    <option value="CSV">CSV</option>
                    <option value="KML">KML</option>
                    <option value="DXF">DXF</option>
                    <option value="Other">Other</option>
                  </select>
                )}
              />
              {errors.resource_format && (
                <div className="error-message">{errors.resource_format.message as string}</div>
              )}
            </div>
            
            <div className="form-section">
              <h3>Attributes</h3>
              
              {attributeFields.map((field, index) => (
                <div key={field.id} className="attribute-item">
                  <div className="attribute-header">
                    <h4>Attribute {index + 1}</h4>
                    <button
                      type="button"
                      className="remove-button"
                      onClick={() => removeAttribute(index)}
                    >
                      Remove
                    </button>
                  </div>
                  
                  <div className="form-row">
                    <div className="form-group">
                      <label>Name</label>
                      <Controller
                        name={`attributes.${index}.name`}
                        control={control}
                        rules={{ required: 'Name is required' }}
                        render={({ field }) => (
                          <input {...field} type="text" className="form-control" />
                        )}
                      />
                    </div>
                    
                    <div className="form-group">
                      <label>Data Type</label>
                      <Controller
                        name={`attributes.${index}.data_type`}
                        control={control}
                        render={({ field }) => (
                          <select {...field} className="form-control">
                            <option value="string">String</option>
                            <option value="integer">Integer</option>
                            <option value="float">Float</option>
                            <option value="boolean">Boolean</option>
                            <option value="date">Date</option>
                            <option value="datetime">DateTime</option>
                            <option value="geometry">Geometry</option>
                            <option value="other">Other</option>
                          </select>
                        )}
                      />
                    </div>
                  </div>
                  
                  <div className="form-group">
                    <label>Description</label>
                    <Controller
                      name={`attributes.${index}.description`}
                      control={control}
                      render={({ field }) => (
                        <textarea {...field} className="form-control" rows={2} />
                      )}
                    />
                  </div>
                  
                  <div className="form-row">
                    <div className="form-group">
                      <label>Unit</label>
                      <Controller
                        name={`attributes.${index}.unit`}
                        control={control}
                        render={({ field }) => (
                          <input {...field} type="text" className="form-control" />
                        )}
                      />
                    </div>
                    
                    <div className="form-group">
                      <label>Domain (comma-separated values or range)</label>
                      <Controller
                        name={`attributes.${index}.domain`}
                        control={control}
                        render={({ field }) => (
                          <input
                            type="text"
                            className="form-control"
                            value={field.value ? (Array.isArray(field.value) ? field.value.join(',') : field.value) : ''}
                            onChange={(e) => {
                              const value = e.target.value;
                              if (value.includes('-') && value.split('-').length === 2) {
                                // Range format (e.g., "0-100")
                                const [min, max] = value.split('-').map(Number);
                                field.onChange([min, max]);
                              } else if (value.includes(',')) {
                                // List format (e.g., "red,green,blue")
                                field.onChange(value.split(',').map(v => v.trim()));
                              } else {
                                field.onChange(value);
                              }
                            }}
                          />
                        )}
                      />
                    </div>
                  </div>
                </div>
              ))}
              
              <button
                type="button"
                className="add-button"
                onClick={handleAddAttribute}
              >
                Add Attribute
              </button>
            </div>
          </>
        );
        
      case 'service':
        return (
          <>
            <div className="form-group">
              <label>Service Type</label>
              <Controller
                name="service_type"
                control={control}
                rules={{ required: 'Service type is required' }}
                render={({ field }) => (
                  <select {...field} className="form-control">
                    <option value="">Select service type</option>
                    <option value="WMS">WMS</option>
                    <option value="WFS">WFS</option>
                    <option value="WCS">WCS</option>
                    <option value="WMTS">WMTS</option>
                    <option value="CSW">CSW</option>
                    <option value="OGC API">OGC API</option>
                    <option value="Other">Other</option>
                  </select>
                )}
              />
              {errors.service_type && (
                <div className="error-message">{errors.service_type.message as string}</div>
              )}
            </div>
            
            <div className="form-group">
              <label>Service URL</label>
              <Controller
                name="service_url"
                control={control}
                rules={{ required: 'Service URL is required' }}
                render={({ field }) => (
                  <input {...field} type="url" className="form-control" />
                )}
              />
              {errors.service_url && (
                <div className="error-message">{errors.service_url.message as string}</div>
              )}
            </div>
          </>
        );
        
      default:
        return null;
    }
  };
  
  return (
    <div className="metadata-editor">
      <h2>{datasetId ? 'Edit Metadata' : 'Create Metadata'}</h2>
      
      {isLoading && <div className="loading">Loading...</div>}
      
      {error && (
        <div className="error-message">{error}</div>
      )}
      
      {success && (
        <div className="success-message">{success}</div>
      )}
      
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="form-section">
          <h3>Basic Information</h3>
          
          <div className="form-group">
            <label>Title</label>
            <Controller
              name="title"
              control={control}
              rules={{ required: 'Title is required' }}
              render={({ field }) => (
                <input {...field} type="text" className="form-control" />
              )}
            />
            {errors.title && (
              <div className="error-message">{errors.title.message as string}</div>
            )}
          </div>
          
          <div className="form-group">
            <label>Description</label>
            <Controller
              name="description"
              control={control}
              render={({ field }) => (
                <textarea {...field} className="form-control" rows={3} />
              )}
            />
          </div>
          
          <div className="form-group">
            <label>Abstract</label>
            <Controller
              name="abstract"
              control={control}
              render={({ field }) => (
                <textarea {...field} className="form-control" rows={5} />
              )}
            />
          </div>
          
          <div className="form-group">
            <label>Resource Type</label>
            <Controller
              name="resource_type"
              control={control}
              rules={{ required: 'Resource type is required' }}
              render={({ field }) => (
                <select {...field} className="form-control">
                  <option value="dataset">Dataset</option>
                  <option value="service">Service</option>
                  <option value="application">Application</option>
                  <option value="map">Map</option>
                  <option value="other">Other</option>
                </select>
              )}
            />
            {errors.resource_type && (
              <div className="error-message">{errors.resource_type.message as string}</div>
            )}
          </div>
          
          {renderResourceTypeFields()}
          
          <div className="form-group">
            <label>Keywords</label>
            <Controller
              name="keywords"
              control={control}
              render={({ field }) => (
                <TagInput
                  value={field.value}
                  onChange={field.onChange}
                  suggestions={availableKeywords.map(k => k.name)}
                  placeholder="Add keywords..."
                />
              )}
            />
          </div>
        </div>
        
        <div className="form-section">
          <h3>Spatial Information</h3>
          
          <div className="form-group">
            <label>Bounding Box</label>
            <Controller
              name="bbox"
              control={control}
              render={({ field }) => (
                <MapSelector
                  bbox={field.value}
                  onChange={field.onChange}
                  height="300px"
                />
              )}
            />
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label>SRID</label>
              <Controller
                name="srid"
                control={control}
                render={({ field }) => (
                  <input {...field} type="number" className="form-control" />
                )}
              />
            </div>
          </div>
        </div>
        
        <div className="form-section">
          <h3>Temporal Information</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label>Start Date</label>
              <Controller
                name="temporal_start"
                control={control}
                render={({ field }) => (
                  <DatePicker
                    selected={field.value ? new Date(field.value) : null}
                    onChange={field.onChange}
                    className="form-control"
                  />
                )}
              />
            </div>
            
            <div className="form-group">
              <label>End Date</label>
              <Controller
                name="temporal_end"
                control={control}
                render={({ field }) => (
                  <DatePicker
                    selected={field.value ? new Date(field.value) : null}
                    onChange={field.onChange}
                    className="form-control"
                  />
                )}
              />
            </div>
          </div>
        </div>
        
        <div className="form-section">
          <h3>Contact Information</h3>
          
          <Controller
            name="contacts"
            control={control}
            render={({ field }) => (
              <ContactSelector
                contacts={field.value}
                availableContacts={availableContacts}
                onChange={field.onChange}
              />
            )}
          />
        </div>
        
        <div className="form-section">
          <h3>Administrative Information</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label>Metadata Language</label>
              <Controller
                name="metadata_language"
                control={control}
                render={({ field }) => (
                  <select {...field} className="form-control">
                    <option value="en">English</option>
                    <option value="es">Spanish</option>
                    <option value="fr">French</option>
                    <option value="de">German</option>
                    <option value="it">Italian</option>
                    <option value="pt">Portuguese</option>
                    <option value="zh">Chinese</option>
                    <option value="ja">Japanese</option>
                    <option value="ru">Russian</option>
                  </select>
                )}
              />
            </div>
            
            <div className="form-group checkbox-group">
              <Controller
                name="is_published"
                control={control}
                render={({ field }) => (
                  <label>
                    <input
                      type="checkbox"
                      checked={field.value}
                      onChange={(e) => field.onChange(e.target.checked)}
                    />
                    Publish Metadata
                  </label>
                )}
              />
            </div>
          </div>
        </div>
        
        <div className="form-actions">
          <button
            type="button"
            className="cancel-button"
            onClick={onCancel}
          >
            Cancel
          </button>
          
          <button
            type="submit"
            className="save-button"
            disabled={isLoading}
          >
            {isLoading ? 'Saving...' : 'Save Metadata'}
          </button>
        </div>
      </form>
      
      <style jsx>{`
        .metadata-editor {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 1.5rem;
          max-width: 100%;
        }
        
        h2 {
          margin-top: 0;
          margin-bottom: 1.5rem;
          font-size: 1.5rem;
        }
        
        .form-section {
          margin-bottom: 2rem;
          padding-bottom: 1.5rem;
          border-bottom: 1px solid #eee;
        }
        
        .form-section h3 {
          margin-top: 0;
          margin-bottom: 1rem;
          font-size: 1.2rem;
          color: #333;
        }
        
        .form-group {
          margin-bottom: 1rem;
        }
        
        .form-row {
          display: flex;
          gap: 1rem;
          margin-bottom: 1rem;
        }
        
        .form-row .form-group {
          flex: 1;
          margin-bottom: 0;
        }
        
        label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
        }
        
        .form-control {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 1rem;
        }
        
        textarea.form-control {
          resize: vertical;
        }
        
        .checkbox-group {
          display: flex;
          align-items: center;
          margin-top: 2rem;
        }
        
        .checkbox-group label {
          display: flex;
          align-items: center;
          margin-bottom: 0;
          cursor: pointer;
        }
        
        .checkbox-group input {
          margin-right: 0.5rem;
        }
        
        .attribute-item {
          margin-bottom: 1.5rem;
          padding: 1rem;
          background-color: #f8f9fa;
          border-radius: 4px;
        }
        
        .attribute-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }
        
        .attribute-header h4 {
          margin: 0;
          font-size: 1rem;
        }
        
        .add-button, .remove-button {
          padding: 0.5rem 1rem;
          border-radius: 4px;
          font-size: 0.9rem;
          cursor: pointer;
        }
        
        .add-button {
          background-color: #e9ecef;
          color: #333;
          border: 1px solid #ddd;
        }
        
        .remove-button {
          background-color: #f8d7da;
          color: #721c24;
          border: 1px solid #f5c6cb;
        }
        
        .form-actions {
          display: flex;
          justify-content: flex-end;
          gap: 1rem;
          margin-top: 2rem;
        }
        
        .cancel-button, .save-button {
          padding: 0.75rem 1.5rem;
          border-radius: 4px;
          font-size: 1rem;
          cursor: pointer;
        }
        
        .cancel-button {
          background-color: #f8f9fa;
          color: #333;
          border: 1px solid #ddd;
        }
        
        .save-button {
          background-color: #0070f3;
          color: white;
          border: none;
        }
        
        .save-button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }
        
        .loading {
          text-align: center;
          margin: 1rem 0;
          color: #666;
        }
        
        .error-message {
          background-color: #f8d7da;
          color: #721c24;
          padding: 0.75rem;
          border-radius: 4px;
          margin: 1rem 0;
        }
        
        .success-message {
          background-color: #d4edda;
          color: #155724;
          padding: 0.75rem;
          border-radius: 4px;
          margin: 1rem 0;
        }
        
        @media (max-width: 768px) {
          .form-row {
            flex-direction: column;
            gap: 1rem;
          }
          
          .form-row .form-group {
            margin-bottom: 0;
          }
        }
      `}</style>
    </div>
  );
};

export default MetadataEditor;
