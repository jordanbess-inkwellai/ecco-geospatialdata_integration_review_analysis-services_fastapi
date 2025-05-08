import React, { useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Grid, 
  Paper, 
  Card,
  CardContent,
  CardActions,
  Button,
  Alert,
  CircularProgress
} from '@mui/material';
import { useRouter } from 'next/router';
import Layout from '../../components/layout/Layout';
import { useAIFeatures } from '../../hooks/useAIFeatures';

const AIToolsPage: React.FC = () => {
  const router = useRouter();
  const { aiEnabled, aiStatus, loading, error } = useAIFeatures();
  
  // Redirect to home if AI features are not enabled
  useEffect(() => {
    if (!loading && !aiEnabled) {
      router.push('/');
    }
  }, [aiEnabled, loading, router]);
  
  if (loading) {
    return (
      <Layout title="AI Tools">
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <CircularProgress />
        </Container>
      </Layout>
    );
  }
  
  // If AI is not enabled, show a message while redirecting
  if (!aiEnabled) {
    return (
      <Layout title="AI Tools">
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Alert severity="warning">
            AI features are not enabled in this build. Redirecting to home page...
          </Alert>
        </Container>
      </Layout>
    );
  }
  
  const aiTools = [
    {
      title: 'Data Validation',
      description: 'Validate data quality and identify issues using AI models.',
      modelSpecific: {
        jellyfish: 'Detailed semantic analysis of data quality issues.',
        xlnet: 'Sequential pattern recognition for data validation.',
        t5: 'Text transformation suggestions for data cleaning.',
        bert: 'Contextual understanding of data semantics.'
      }
    },
    {
      title: 'Schema Matching',
      description: 'Match source schema to target schema with AI assistance.',
      modelSpecific: {
        jellyfish: 'Advanced semantic matching of complex schemas.',
        xlnet: 'Context-aware field mapping suggestions.',
        t5: 'Translation between different schema formats.',
        bert: 'Field similarity analysis based on semantic meaning.'
      }
    },
    {
      title: 'Transformation Suggestions',
      description: 'Get AI-powered suggestions for data transformations.',
      modelSpecific: {
        jellyfish: 'Complex multi-step transformation pipelines.',
        xlnet: 'Sequential transformation suggestions for time-series data.',
        t5: 'Text-based field transformations and normalization.',
        bert: 'Context-aware field value standardization.'
      }
    }
  ];
  
  // Get model-specific description based on current model
  const getModelSpecificDescription = (tool: any) => {
    const modelType = aiStatus?.model_type || 'jellyfish';
    return tool.modelSpecific[modelType] || tool.description;
  };

  return (
    <Layout title="AI Tools">
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          AI Tools
        </Typography>
        <Typography variant="body1" paragraph>
          Leverage AI capabilities to enhance your geospatial data workflows.
          {aiStatus?.model_type && (
            <strong> Currently using {aiStatus.model_type.toUpperCase()} model.</strong>
          )}
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        
        <Grid container spacing={4}>
          {aiTools.map((tool, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography gutterBottom variant="h5" component="h2">
                    {tool.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {tool.description}
                  </Typography>
                  <Typography variant="body2" color="primary">
                    {getModelSpecificDescription(tool)}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small" color="primary">
                    Open Tool
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Layout>
  );
};

export default AIToolsPage;
