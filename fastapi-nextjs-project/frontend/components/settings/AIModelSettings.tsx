import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  FormControl, 
  FormControlLabel, 
  FormGroup,
  Switch,
  RadioGroup,
  Radio,
  Button,
  Alert,
  CircularProgress,
  Divider,
  Card,
  CardContent,
  CardHeader,
  Grid
} from '@mui/material';
import { apiClient } from '../../lib/api';

interface AIModelSettingsProps {
  onSettingsChange?: (settings: any) => void;
}

const AIModelSettings: React.FC<AIModelSettingsProps> = ({ onSettingsChange }) => {
  const [aiEnabled, setAiEnabled] = useState<boolean>(false);
  const [selectedModel, setSelectedModel] = useState<string>('jellyfish');
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [aiStatus, setAiStatus] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);

  useEffect(() => {
    fetchAIStatus();
  }, []);

  const fetchAIStatus = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.get('/ai/status');
      const status = response.data;
      
      setAiStatus(status);
      setAiEnabled(status.enabled);
      setSelectedModel(status.model_type || 'jellyfish');
      setAvailableModels(status.available_models || []);
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching AI status:', err);
      setError('Failed to fetch AI status. AI features may not be enabled on the server.');
      setLoading(false);
    }
  };

  const handleEnableChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setAiEnabled(event.target.checked);
    
    if (onSettingsChange) {
      onSettingsChange({
        enabled: event.target.checked,
        model_type: selectedModel
      });
    }
  };

  const handleModelChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedModel(event.target.value);
    
    if (onSettingsChange) {
      onSettingsChange({
        enabled: aiEnabled,
        model_type: event.target.value
      });
    }
  };

  const handleSaveSettings = async () => {
    setLoading(true);
    setError(null);
    setSaveSuccess(false);
    
    try {
      // In a real implementation, this would save the settings to the server
      // For now, we'll just simulate a successful save
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSaveSuccess(true);
      setLoading(false);
      
      // Refresh the AI status
      fetchAIStatus();
    } catch (err) {
      console.error('Error saving AI settings:', err);
      setError('Failed to save AI settings.');
      setLoading(false);
    }
  };

  const getModelDescription = (modelType: string): string => {
    switch (modelType) {
      case 'jellyfish':
        return 'Jellyfish-13B is a powerful large language model optimized for data understanding and schema matching.';
      case 'xlnet':
        return 'XLNet excels at understanding the context and relationships in sequential data.';
      case 't5':
        return 'T5 (Text-to-Text Transfer Transformer) is designed for various text transformation tasks.';
      case 'bert':
        return 'BERT provides deep bidirectional representations and is excellent for understanding context.';
      default:
        return 'Select a model to see its description.';
    }
  };

  const getModelCapabilities = (modelType: string): string[] => {
    switch (modelType) {
      case 'jellyfish':
        return [
          'Advanced schema matching and data validation',
          'Detailed data transformation suggestions',
          'Entity extraction from text fields',
          'Semantic understanding of data relationships'
        ];
      case 'xlnet':
        return [
          'Sequential data pattern recognition',
          'Context-aware data validation',
          'Advanced text embeddings',
          'Time series data analysis'
        ];
      case 't5':
        return [
          'Text summarization and transformation',
          'Data format conversion',
          'Translation between schemas',
          'Question answering about data'
        ];
      case 'bert':
        return [
          'Semantic analysis of text fields',
          'Sentiment classification',
          'Named entity recognition',
          'Context-aware data validation'
        ];
      default:
        return [];
    }
  };

  if (loading && !aiStatus) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        AI Model Settings
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Settings saved successfully!
        </Alert>
      )}
      
      <FormGroup>
        <FormControlLabel
          control={
            <Switch
              checked={aiEnabled}
              onChange={handleEnableChange}
              name="enableAI"
            />
          }
          label="Enable AI Features"
        />
      </FormGroup>
      
      <Box mt={3}>
        <Typography variant="h6" gutterBottom>
          Select AI Model
        </Typography>
        
        <FormControl component="fieldset" disabled={!aiEnabled}>
          <RadioGroup
            aria-label="ai-model"
            name="ai-model"
            value={selectedModel}
            onChange={handleModelChange}
          >
            {availableModels.map((model) => (
              <FormControlLabel
                key={model}
                value={model}
                control={<Radio />}
                label={model.charAt(0).toUpperCase() + model.slice(1)}
              />
            ))}
          </RadioGroup>
        </FormControl>
      </Box>
      
      <Divider sx={{ my: 3 }} />
      
      <Box mt={3}>
        <Typography variant="h6" gutterBottom>
          Model Information
        </Typography>
        
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardHeader
            title={selectedModel.charAt(0).toUpperCase() + selectedModel.slice(1)}
            subheader={aiEnabled ? 'Active' : 'Inactive'}
          />
          <CardContent>
            <Typography variant="body1" paragraph>
              {getModelDescription(selectedModel)}
            </Typography>
            
            <Typography variant="subtitle1" gutterBottom>
              Capabilities:
            </Typography>
            
            <ul>
              {getModelCapabilities(selectedModel).map((capability, index) => (
                <li key={index}>
                  <Typography variant="body2">{capability}</Typography>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </Box>
      
      <Box mt={3} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          color="primary"
          onClick={handleSaveSettings}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Save Settings'}
        </Button>
      </Box>
    </Paper>
  );
};

export default AIModelSettings;
