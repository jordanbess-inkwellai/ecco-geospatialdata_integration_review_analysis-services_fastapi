import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Tabs,
  Tab,
  Button,
  Divider,
  Alert,
  Snackbar
} from '@mui/material';
import Layout from '../../components/layout/Layout';
import ERAlchemyDiagram from '../../components/eralchemy/ERAlchemyDiagram';
import PgModelerDiagram from '../../components/pgmodeler/PgModelerDiagram';

const DatabaseDiagramsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<number>(0);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleDiagramGenerated = (tool: string) => {
    setNotification({
      open: true,
      message: `${tool} diagram generated successfully!`,
      severity: 'success'
    });
  };

  const handleCloseNotification = () => {
    setNotification({
      ...notification,
      open: false
    });
  };

  return (
    <Layout title="Database Diagrams">
      <Container maxWidth={false} sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Database Diagrams
        </Typography>
        
        <Paper sx={{ mb: 3 }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="ERAlchemy" />
            <Tab label="PgModeler" />
          </Tabs>
        </Paper>
        
        <Box sx={{ mb: 3 }}>
          {activeTab === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                ERAlchemy - Entity Relation Diagrams
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                ERAlchemy generates Entity Relation (ER) diagrams from databases or from SQLAlchemy models.
                It can connect to various database types and generate diagrams in PNG, PDF, or SVG formats.
              </Typography>
              <ERAlchemyDiagram 
                onDiagramGenerated={() => handleDiagramGenerated('ERAlchemy')} 
              />
            </Box>
          )}
          
          {activeTab === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                PgModeler - PostgreSQL Database Modeler
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                PgModeler is a powerful PostgreSQL database modeling tool that allows you to design, generate, and export database models.
                It supports reverse engineering from existing databases and can export to various formats.
              </Typography>
              <PgModelerDiagram 
                onModelGenerated={() => handleDiagramGenerated('PgModeler model')}
                onDiagramGenerated={() => handleDiagramGenerated('PgModeler diagram')}
              />
            </Box>
          )}
        </Box>
        
        <Snackbar
          open={notification.open}
          autoHideDuration={6000}
          onClose={handleCloseNotification}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert 
            onClose={handleCloseNotification} 
            severity={notification.severity}
            sx={{ width: '100%' }}
          >
            {notification.message}
          </Alert>
        </Snackbar>
      </Container>
    </Layout>
  );
};

export default DatabaseDiagramsPage;
