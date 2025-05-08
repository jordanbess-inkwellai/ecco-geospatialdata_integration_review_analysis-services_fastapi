import React from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Grid, 
  Paper, 
  Button,
  Card,
  CardContent,
  CardActions,
  CardMedia
} from '@mui/material';
import Link from 'next/link';
import Layout from '../components/layout/Layout';
import MapIcon from '@mui/icons-material/Map';
import LayersIcon from '@mui/icons-material/Layers';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import TransformIcon from '@mui/icons-material/Transform';
import StorageIcon from '@mui/icons-material/Storage';
import CodeIcon from '@mui/icons-material/Code';

const HomePage: React.FC = () => {
  const features = [
    {
      title: 'Interactive Mapping',
      description: 'Visualize geospatial data with an interactive map interface powered by MapLibre.',
      icon: <MapIcon fontSize="large" color="primary" />,
      link: '/map'
    },
    {
      title: 'Layer Management',
      description: 'Manage and style vector and raster layers with advanced visualization options.',
      icon: <LayersIcon fontSize="large" color="primary" />,
      link: '/layers'
    },
    {
      title: 'Spatial Analysis',
      description: 'Perform spatial analysis using OGC API Processes with PostGIS.',
      icon: <AnalyticsIcon fontSize="large" color="primary" />,
      link: '/processes'
    },
    {
      title: 'Data Processing',
      description: 'Process and transform geospatial data with powerful tools.',
      icon: <TransformIcon fontSize="large" color="primary" />,
      link: '/data-processing'
    },
    {
      title: 'Database Connections',
      description: 'Connect to various databases and data sources using OGR_FDW and PG_Analytics.',
      icon: <StorageIcon fontSize="large" color="primary" />,
      link: '/database'
    },
    {
      title: 'Marimo Notebooks',
      description: 'Create and run Marimo notebooks for data engineering workflows.',
      icon: <CodeIcon fontSize="large" color="primary" />,
      link: '/notebooks'
    }
  ];

  return (
    <Layout title="MCP Server - Home">
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ mb: 6, textAlign: 'center' }}>
          <Typography variant="h3" component="h1" gutterBottom>
            MCP Server
          </Typography>
          <Typography variant="h5" color="text.secondary" paragraph>
            PostGIS Microservices Analysis Platform
          </Typography>
          <Box sx={{ mt: 3 }}>
            <Button variant="contained" size="large" startIcon={<MapIcon />} component={Link} href="/map">
              Open Map
            </Button>
          </Box>
        </Box>

        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                    {feature.icon}
                  </Box>
                  <Typography gutterBottom variant="h5" component="h2" align="center">
                    {feature.title}
                  </Typography>
                  <Typography align="center">
                    {feature.description}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small" component={Link} href={feature.link} fullWidth>
                    Explore
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

export default HomePage;
