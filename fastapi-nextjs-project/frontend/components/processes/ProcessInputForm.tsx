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
  Switch,
  Typography,
  Grid,
  Paper,
  Divider,
  Alert
} from '@mui/material';
import { useMap } from '../../hooks/useMap';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import MapIcon from '@mui/icons-material/Map';

interface ProcessInputFormProps {
  process: any;
  onSubmit: (inputs: any) => void;
}

const ProcessInputForm: React.FC<ProcessInputFormProps> = ({ process, onSubmit }) => {
  const { selectFeatureFromMap } = useMap();
  const [validationSchema, setValidationSchema] = useState<any>({});

  useEffect(() => {
    // Build Yup validation schema based on process inputs
    const schema: Record<string, any> = {};
    
    Object.entries(process.inputs || {}).forEach(([name, input]: [string, any]) => {
      const inputSchema = input.schema || {};
      const isRequired = input.required || false;
      
      let fieldSchema;
      
      switch (inputSchema.type) {
        case 'string':
          fieldSchema = Yup.string();
          break;
        case 'number':
          fieldSchema = Yup.number();
          if (inputSchema.minimum !== undefined) {
            fieldSchema = fieldSchema.min(inputSchema.minimum);
          }
          if (inputSchema.maximum !== undefined) {
            fieldSchema = fieldSchema.max(inputSchema.maximum);
          }
          break;
        case 'integer':
          fieldSchema = Yup.number().integer();
          if (inputSchema.minimum !== undefined) {
            fieldSchema = fieldSchema.min(inputSchema.minimum);
          }
          if (inputSchema.maximum !== undefined) {
            fieldSchema = fieldSchema.max(inputSchema.maximum);
          }
          break;
        case 'boolean':
          fieldSchema = Yup.boolean();
          break;
        case 'array':
          fieldSchema = Yup.array();
          break;
        case 'object':
          fieldSchema = Yup.object();
          break;
        default:
          fieldSchema = Yup.mixed();
      }
      
      if (isRequired) {
        fieldSchema = fieldSchema.required(`${input.title || name} is required`);
      }
      
      schema[name] = fieldSchema;
    });
    
    setValidationSchema(Yup.object().shape(schema));
  }, [process]);

  // Initialize form values
  const initialValues: Record<string, any> = {};
  Object.entries(process.inputs || {}).forEach(([name, input]: [string, any]) => {
    initialValues[name] = input.default !== undefined ? input.default : getDefaultValueForType(input.schema?.type);
  });

  const formik = useFormik({
    initialValues,
    validationSchema,
    enableReinitialize: true,
    onSubmit: (values) => {
      // Parse values based on input types
      const parsedValues: Record<string, any> = {};
      
      Object.entries(process.inputs || {}).forEach(([name, input]: [string, any]) => {
        const value = values[name];
        const type = input.schema?.type;
        
        if (value === undefined || value === '') {
          return;
        }
        
        if (type === 'object' && typeof value === 'string') {
          try {
            parsedValues[name] = JSON.parse(value);
          } catch (e) {
            parsedValues[name] = value;
          }
        } else if (type === 'array' && typeof value === 'string') {
          try {
            parsedValues[name] = JSON.parse(value);
          } catch (e) {
            parsedValues[name] = value.split(',').map(item => item.trim());
          }
        } else {
          parsedValues[name] = value;
        }
      });
      
      onSubmit(parsedValues);
    },
  });

  const handleSelectFromMap = async (inputName: string) => {
    try {
      const feature = await selectFeatureFromMap();
      if (feature && feature.geometry) {
        formik.setFieldValue(inputName, JSON.stringify(feature.geometry, null, 2));
      }
    } catch (error) {
      console.error('Error selecting feature from map:', error);
    }
  };

  return (
    <form onSubmit={formik.handleSubmit}>
      <Grid container spacing={3}>
        {Object.entries(process.inputs || {}).map(([name, input]: [string, any]) => {
          const inputSchema = input.schema || {};
          const isRequired = input.required || false;
          
          return (
            <Grid item xs={12} key={name}>
              <Paper variant="outlined" sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  {input.title || name}
                  {isRequired && <span style={{ color: 'red' }}> *</span>}
                </Typography>
                
                {input.description && (
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {input.description}
                  </Typography>
                )}
                
                {renderInputField(
                  name, 
                  inputSchema, 
                  formik, 
                  input.default,
                  () => handleSelectFromMap(name)
                )}
              </Paper>
            </Grid>
          );
        })}
      </Grid>
      
      <Box mt={3} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          color="primary"
          type="submit"
          startIcon={<PlayArrowIcon />}
          disabled={formik.isSubmitting}
        >
          Execute Process
        </Button>
      </Box>
    </form>
  );
};

function renderInputField(
  name: string, 
  schema: any, 
  formik: any, 
  defaultValue: any,
  onSelectFromMap: () => void
) {
  const { values, errors, touched, handleChange, handleBlur, setFieldValue } = formik;
  const hasError = touched[name] && Boolean(errors[name]);
  const errorMessage = touched[name] ? errors[name] : '';
  
  switch (schema.type) {
    case 'string':
      if (schema.enum) {
        return (
          <FormControl fullWidth error={hasError}>
            <InputLabel id={`${name}-label`}>{name}</InputLabel>
            <Select
              labelId={`${name}-label`}
              id={name}
              name={name}
              value={values[name] || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              label={name}
            >
              {schema.enum.map((option: string) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </Select>
            {hasError && <FormHelperText>{errorMessage}</FormHelperText>}
          </FormControl>
        );
      } else {
        return (
          <TextField
            fullWidth
            id={name}
            name={name}
            label={name}
            value={values[name] || ''}
            onChange={handleChange}
            onBlur={handleBlur}
            error={hasError}
            helperText={errorMessage}
          />
        );
      }
    
    case 'number':
    case 'integer':
      return (
        <TextField
          fullWidth
          id={name}
          name={name}
          label={name}
          type="number"
          value={values[name] || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          error={hasError}
          helperText={errorMessage}
          inputProps={{
            min: schema.minimum,
            max: schema.maximum,
            step: schema.type === 'integer' ? 1 : 'any'
          }}
        />
      );
    
    case 'boolean':
      return (
        <FormControl fullWidth error={hasError}>
          <FormControlLabel
            control={
              <Switch
                id={name}
                name={name}
                checked={Boolean(values[name])}
                onChange={handleChange}
                onBlur={handleBlur}
              />
            }
            label={name}
          />
          {hasError && <FormHelperText>{errorMessage}</FormHelperText>}
        </FormControl>
      );
    
    case 'array':
      return (
        <TextField
          fullWidth
          id={name}
          name={name}
          label={`${name} (comma-separated or JSON array)`}
          value={values[name] || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          error={hasError}
          helperText={errorMessage || 'Enter values separated by commas or as a JSON array'}
          multiline
          rows={3}
        />
      );
    
    case 'object':
      // For geometry objects, add a button to select from map
      const isGeometry = name.toLowerCase().includes('geometry') || 
                         name.toLowerCase().includes('point') ||
                         name.toLowerCase().includes('polygon') ||
                         name.toLowerCase().includes('line');
      
      return (
        <Box>
          <TextField
            fullWidth
            id={name}
            name={name}
            label={`${name} (JSON object)`}
            value={values[name] || ''}
            onChange={handleChange}
            onBlur={handleBlur}
            error={hasError}
            helperText={errorMessage || 'Enter a valid JSON object'}
            multiline
            rows={5}
          />
          {isGeometry && (
            <Button
              variant="outlined"
              startIcon={<MapIcon />}
              onClick={onSelectFromMap}
              sx={{ mt: 1 }}
            >
              Select from Map
            </Button>
          )}
        </Box>
      );
    
    default:
      return (
        <TextField
          fullWidth
          id={name}
          name={name}
          label={name}
          value={values[name] || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          error={hasError}
          helperText={errorMessage}
        />
      );
  }
}

function getDefaultValueForType(type: string | undefined): any {
  switch (type) {
    case 'string':
      return '';
    case 'number':
    case 'integer':
      return '';
    case 'boolean':
      return false;
    case 'array':
      return '';
    case 'object':
      return '';
    default:
      return '';
  }
}

export default ProcessInputForm;
