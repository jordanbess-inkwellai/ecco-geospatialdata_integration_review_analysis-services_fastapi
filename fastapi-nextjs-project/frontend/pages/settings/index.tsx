import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Container,
  Grid,
  Paper,
  Tabs,
  Tab,
  Divider,
  CircularProgress
} from '@mui/material';
import Layout from '../../components/layout/Layout';
import AIModelSettings from '../../components/settings/AIModelSettings';
import { useAIFeatures } from '../../hooks/useAIFeatures';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const SettingsPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const { aiEnabled, aiStatus, loading: aiLoading } = useAIFeatures();

  // Adjust tab value if AI tab is removed and we were on a higher tab
  useEffect(() => {
    if (!aiEnabled && tabValue > 0) {
      // If AI is disabled, we need to adjust the tab index since the AI tab is removed
      setTabValue(tabValue > 1 ? tabValue - 1 : tabValue);
    }
  }, [aiEnabled, tabValue]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleAISettingsChange = (settings: any) => {
    console.log('AI Settings changed:', settings);
    // In a real implementation, this would save the settings to the server or local storage
  };

  // Get tab index based on whether AI is enabled
  const getTabIndex = (baseIndex: number) => {
    // If AI is enabled, indices stay the same
    // If AI is disabled, indices after the AI tab (index 1) are reduced by 1
    if (aiEnabled) {
      return baseIndex;
    } else {
      return baseIndex < 1 ? baseIndex : baseIndex - 1;
    }
  };

  if (aiLoading) {
    return (
      <Layout title="Settings">
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <CircularProgress />
        </Container>
      </Layout>
    );
  }

  return (
    <Layout title="Settings">
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Settings
        </Typography>
        <Typography variant="body1" paragraph>
          Configure application settings and preferences.
        </Typography>

        <Paper sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              aria-label="settings tabs"
            >
              <Tab label="General" id="settings-tab-0" aria-controls="settings-tabpanel-0" />
              {aiEnabled && (
                <Tab label="AI Models" id="settings-tab-1" aria-controls="settings-tabpanel-1" />
              )}
              <Tab
                label="Database"
                id={`settings-tab-${aiEnabled ? 2 : 1}`}
                aria-controls={`settings-tabpanel-${aiEnabled ? 2 : 1}`}
              />
              <Tab
                label="Map"
                id={`settings-tab-${aiEnabled ? 3 : 2}`}
                aria-controls={`settings-tabpanel-${aiEnabled ? 3 : 2}`}
              />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            <Typography variant="h6" gutterBottom>
              General Settings
            </Typography>
            <Typography variant="body1">
              General application settings will be displayed here.
            </Typography>
          </TabPanel>

          {aiEnabled && (
            <TabPanel value={tabValue} index={1}>
              <AIModelSettings onSettingsChange={handleAISettingsChange} />
            </TabPanel>
          )}

          <TabPanel value={tabValue} index={getTabIndex(2)}>
            <Typography variant="h6" gutterBottom>
              Database Settings
            </Typography>
            <Typography variant="body1">
              Database connection settings will be displayed here.
            </Typography>
          </TabPanel>

          <TabPanel value={tabValue} index={getTabIndex(3)}>
            <Typography variant="h6" gutterBottom>
              Map Settings
            </Typography>
            <Typography variant="body1">
              Map configuration settings will be displayed here.
            </Typography>
          </TabPanel>
        </Paper>
      </Container>
    </Layout>
  );
};

export default SettingsPage;
