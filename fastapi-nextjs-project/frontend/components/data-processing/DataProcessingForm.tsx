import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  TextField, 
  FormControl, 
  FormControlLabel,
  FormHelperText,
  InputLabel, 
  MenuItem, 
  Select, 
  Typography,
  Grid,
  Paper,
  Divider,
  Alert,
  CircularProgress
} from '@mui/material';
import { useMap } from '../../hooks/useMap';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import MapIcon from '@mui/icons-material/Map';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import { apiClient } from '../../lib/api';

interface Operation {
  id: string;
  name: string;
  description: string;
  inputs: Array<{
    name: string;
    type: string;
    description: string;
    options?: string[];
    required?: boolean;
  }>;
}

interface DataProcessingFormProps {
  operation: Operation | null;
  onProcessingComplete: (result: any) => void;
}

const DataProcessingForm: React.FC<DataProcessingFormProps> = ({ 
  operation, 
  onProcessingComplete 
}) => {
  const { selectFeatureFromMap } = useMap();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<Record<string, any>>({});

  const formik = useFormik({
    initialValues: {},
    validationSchema: Yup.object({}),
    enableReinitialize: true,
    onSubmit: async (values) => {
      if (!operation) return;
      
      setLoading(true);
      setError(null);
      
      try {
        // Create a FormData object for the API request
        const formData = new FormData();
        
        // Add all form values to the FormData
        for (const [key, value] of Object.entries(values)) {
          if (value !== undefined && value !== null && value !== '') {
            formData.append(key, value as string);
          }
        }
        
        // Make the API request
        const response = await apiClient.post(`/data-processing/${operation.id}`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        // Call the onProcessingComplete callback with the result
        onProcessingComplete(response.data);
      } catch (err) {
        console.error('Error processing data:', err);
        setError(err instanceof Error ? err.message : 'An error occurred during processing');
      } finally {
        setLoading(false);
      }
    }
  });

  // Update form validation schema when operation changes
  useEffect(() => {
    if (!operation) return;
    
    const schemaFields: Record<string, any> = {};
    
    operation.inputs.forEach(input => {
      let fieldSchema;
      
      switch (input.type) {
        case 'file':
          fieldSchema = Yup.mixed();
          break;
        case 'text':
          fieldSchema = Yup.string();
          break;
        case 'number':
          fieldSchema = Yup.number();
          break;
        case 'select':
          fieldSchema = Yup.string();
          break;
        case 'geometry':
          fieldSchema = Yup.string();
          break;
        default:
          fieldSchema = Yup.mixed();
      }
      
      if (input.required !== false) {
        fieldSchema = fieldSchema.required(`${input.name} is required`);
      }
      
      schemaFields[input.name] = fieldSchema;
    });
    
    formik.setValidationSchema(Yup.object().shape(schemaFields));
    
    // Reset form values
    const initialValues: Record<string, any> = {};
    operation.inputs.forEach(input => {
      initialValues[input.name] = '';
    });
    
    formik.resetForm({ values: initialValues });
  }, [operation]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>, inputName: string) => {
    if (!event.target.files || event.target.files.length === 0) return;
    
    const file = event.target.files[0];
    
    setLoading(true);
    setError(null);
    
    try {
      // Create a FormData object for the file upload
      const formData = new FormData();
      formData.append('file', file);
      
      // Upload the file
      const response = await apiClient.post('/data-processing/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      // Store the uploaded file info
      setUploadedFiles({
        ...uploadedFiles,
        [inputName]: response.data
      });
      
      // Set the file path in the form
      formik.setFieldValue(inputName, response.data.file_path);
    } catch (err) {
      console.error('Error uploading file:', err);
      setError(err instanceof Error ? err.message : 'An error occurred during file upload');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectFromMap = async (inputName: string) => {
    try {
      const feature = await selectFeatureFromMap();
      if (feature && feature.geometry) {
        formik.setFieldValue(inputName, JSON.stringify(feature.geometry));
      }
    } catch (error) {
      console.error('Error selecting feature from map:', error);
    }
  };

  if (!operation) {
    return (
      <Paper elevation={2} sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Box p={3} textAlign="center">
          <Typography variant="h6" gutterBottom>
            Select an Operation
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Choose a data processing operation from the menu to get started.
          </Typography>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box p={2}>
        <Typography variant="h6">{operation.name}</Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          {operation.description}
        </Typography>
      </Box>
      <Divider />
      <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <form onSubmit={formik.handleSubmit}>
          <Grid container spacing={3}>
            {operation.inputs.map((input) => (
              <Grid item xs={12} key={input.name}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    {input.name}
                    {input.required !== false && <span style={{ color: 'red' }}> *</span>}
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {input.description}
                  </Typography>
                  
                  {renderInputField(
                    input,
                    formik,
                    handleFileUpload,
                    handleSelectFromMap,
                    uploadedFiles
                  )}
                </Paper>
              </Grid>
            ))}
          </Grid>
          
          <Box mt={3} display="flex" justifyContent="flex-end">
            <Button
              variant="contained"
              color="primary"
              type="submit"
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
              disabled={loading || !formik.isValid}
            >
              {loading ? 'Processing...' : 'Process Data'}
            </Button>
          </Box>
        </form>
      </Box>
    </Paper>
  );
};

function renderInputField(
  input: {
    name: string;
    type: string;
    description: string;
    options?: string[];
    required?: boolean;
  },
  formik: any,
  handleFileUpload: (event: React.ChangeEvent<HTMLInputElement>, inputName: string) => void,
  handleSelectFromMap: (inputName: string) => void,
  uploadedFiles: Record<string, any>
) {
  const { values, errors, touched, handleChange, handleBlur, setFieldValue } = formik;
  const hasError = touched[input.name] && Boolean(errors[input.name]);
  const errorMessage = touched[input.name] ? errors[input.name] : '';
  
  switch (input.type) {
    case 'file':
      return (
        <Box>
          <input
            type="file"
            id={`file-upload-${input.name}`}
            style={{ display: 'none' }}
            onChange={(e) => handleFileUpload(e, input.name)}
          />
          <label htmlFor={`file-upload-${input.name}`}>
            <Button
              variant="outlined"
              component="span"
              startIcon={<UploadFileIcon />}
              sx={{ mb: 1 }}
            >
              Upload File
            </Button>
          </label>
          
          {values[input.name] && uploadedFiles[input.name] && (
            <Box mt={1}>
              <Typography variant="body2">
                File: {uploadedFiles[input.name].file_name}
              </Typography>
              {uploadedFiles[input.name].type && (
                <Typography variant="body2">
                  Type: {uploadedFiles[input.name].type}
                </Typography>
              )}
              {uploadedFiles[input.name].crs && (
                <Typography variant="body2">
                  CRS: {uploadedFiles[input.name].crs}
                </Typography>
              )}
            </Box>
          )}
          
          {hasError && (
            <FormHelperText error>{errorMessage}</FormHelperText>
          )}
        </Box>
      );
    
    case 'text':
      return (
        <TextField
          fullWidth
          id={input.name}
          name={input.name}
          value={values[input.name] || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          error={hasError}
          helperText={errorMessage}
        />
      );
    
    case 'number':
      return (
        <TextField
          fullWidth
          id={input.name}
          name={input.name}
          type="number"
          value={values[input.name] || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          error={hasError}
          helperText={errorMessage}
        />
      );
    
    case 'select':
      return (
        <FormControl fullWidth error={hasError}>
          <InputLabel id={`${input.name}-label`}>{input.name}</InputLabel>
          <Select
            labelId={`${input.name}-label`}
            id={input.name}
            name={input.name}
            value={values[input.name] || ''}
            onChange={handleChange}
            onBlur={handleBlur}
            label={input.name}
          >
            {input.options?.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </Select>
          {hasError && <FormHelperText>{errorMessage}</FormHelperText>}
        </FormControl>
      );
    
    case 'geometry':
      return (
        <Box>
          <TextField
            fullWidth
            id={input.name}
            name={input.name}
            multiline
            rows={5}
            value={values[input.name] || ''}
            onChange={handleChange}
            onBlur={handleBlur}
            error={hasError}
            helperText={errorMessage || 'Enter a GeoJSON geometry or select from map'}
            sx={{ mb: 1 }}
          />
          <Button
            variant="outlined"
            startIcon={<MapIcon />}
            onClick={() => handleSelectFromMap(input.name)}
          >
            Select from Map
          </Button>
        </Box>
      );
    
    default:
      return (
        <TextField
          fullWidth
          id={input.name}
          name={input.name}
          value={values[input.name] || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          error={hasError}
          helperText={errorMessage}
        />
      );
  }
}

export default DataProcessingForm;
