import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useRouter } from 'next/router';
import DatabaseStatus from './DatabaseStatus';
import PerformanceMetrics from './PerformanceMetrics';
import TableSizes from './TableSizes';
import PostGISStats from './PostGISStats';
import CustomQuery from './CustomQuery';
import DatabaseSelector from './DatabaseSelector';
import AlertsPanel from './AlertsPanel';

interface DatabaseDashboardProps {
  initialInstanceConfig?: any;
}

const DatabaseDashboard: React.FC<DatabaseDashboardProps> = ({ initialInstanceConfig }) => {
  // State for instance configuration
  const [instanceConfig, setInstanceConfig] = useState<any>(initialInstanceConfig || null);
  const [savedConfigs, setSavedConfigs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // State for active tab
  const [activeTab, setActiveTab] = useState<string>('status');

  // State for data
  const [statusData, setStatusData] = useState<any>(null);
  const [metricsData, setMetricsData] = useState<any>(null);
  const [tableSizesData, setTableSizesData] = useState<any[]>([]);
  const [postgisData, setPostgisData] = useState<any>(null);

  // Router
  const router = useRouter();

  // Load saved configurations on component mount
  useEffect(() => {
    loadSavedConfigs();
  }, []);

  // Load data when instance configuration changes
  useEffect(() => {
    if (instanceConfig) {
      loadData();
    }
  }, [instanceConfig]);

  // Load saved configurations
  const loadSavedConfigs = async () => {
    try {
      const response = await axios.get('/api/v1/cloudsql/instances/configs');
      setSavedConfigs(response.data);
    } catch (error) {
      console.error('Error loading saved configurations:', error);
      setError('Error loading saved configurations');
    }
  };

  // Load data for the selected instance
  const loadData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Load status data
      const statusResponse = await axios.post('/api/v1/cloudsql/instances/status', instanceConfig);
      setStatusData(statusResponse.data);

      // Load metrics data
      const metricsResponse = await axios.post('/api/v1/cloudsql/instances/metrics', instanceConfig);
      setMetricsData(metricsResponse.data);

      // Load table sizes data
      const tableSizesResponse = await axios.post('/api/v1/cloudsql/instances/table-sizes', instanceConfig);
      setTableSizesData(tableSizesResponse.data);

      // Load PostGIS data
      const postgisResponse = await axios.post('/api/v1/cloudsql/instances/postgis-stats', instanceConfig);
      setPostgisData(postgisResponse.data);
    } catch (error) {
      console.error('Error loading data:', error);
      setError('Error loading data');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle instance selection
  const handleInstanceSelect = (config: any) => {
    setInstanceConfig(config);
  };

  // Handle save configuration
  const handleSaveConfig = async (name: string) => {
    try {
      await axios.post('/api/v1/cloudsql/instances/save-config', {
        instance_config: instanceConfig,
        name
      });

      // Reload saved configurations
      loadSavedConfigs();
    } catch (error) {
      console.error('Error saving configuration:', error);
      setError('Error saving configuration');
    }
  };

  // Handle refresh data
  const handleRefresh = () => {
    loadData();
  };

  // Render content based on active tab
  const renderTabContent = () => {
    if (!instanceConfig) {
      return (
        <div className="no-instance-selected">
          <p>Select a database instance to monitor</p>
        </div>
      );
    }

    if (isLoading) {
      return (
        <div className="loading">
          <p>Loading data...</p>
        </div>
      );
    }

    switch (activeTab) {
      case 'status':
        return <DatabaseStatus data={statusData} onRefresh={handleRefresh} />;
      case 'metrics':
        return <PerformanceMetrics data={metricsData} onRefresh={handleRefresh} />;
      case 'tables':
        return <TableSizes data={tableSizesData} onRefresh={handleRefresh} />;
      case 'postgis':
        return <PostGISStats data={postgisData} onRefresh={handleRefresh} />;
      case 'alerts':
        return <AlertsPanel databaseId={instanceConfig.pocketbase_id} />;
      case 'query':
        return <CustomQuery instanceConfig={instanceConfig} />;
      default:
        return <DatabaseStatus data={statusData} onRefresh={handleRefresh} />;
    }
  };

  return (
    <div className="database-dashboard">
      <div className="dashboard-header">
        <h1>Cloud SQL Monitor</h1>
        <p>Monitor and analyze your Google Cloud SQL PostgreSQL instances</p>
      </div>

      <div className="dashboard-content">
        <div className="sidebar">
          <DatabaseSelector
            savedConfigs={savedConfigs}
            onSelect={handleInstanceSelect}
            onSave={handleSaveConfig}
            selectedConfig={instanceConfig}
          />
        </div>

        <div className="main-content">
          {error && (
            <div className="error-message">{error}</div>
          )}

          {instanceConfig && (
            <div className="instance-info">
              <h2>{instanceConfig.database}@{instanceConfig.instance_connection_name}</h2>
              <div className="connection-type">
                Connection: {instanceConfig.ip_type || 'PUBLIC'}
              </div>
            </div>
          )}

          <div className="tabs">
            <button
              className={`tab-button ${activeTab === 'status' ? 'active' : ''}`}
              onClick={() => setActiveTab('status')}
            >
              Status
            </button>
            <button
              className={`tab-button ${activeTab === 'metrics' ? 'active' : ''}`}
              onClick={() => setActiveTab('metrics')}
            >
              Performance
            </button>
            <button
              className={`tab-button ${activeTab === 'tables' ? 'active' : ''}`}
              onClick={() => setActiveTab('tables')}
            >
              Tables
            </button>
            <button
              className={`tab-button ${activeTab === 'postgis' ? 'active' : ''}`}
              onClick={() => setActiveTab('postgis')}
            >
              PostGIS
            </button>
            <button
              className={`tab-button ${activeTab === 'alerts' ? 'active' : ''}`}
              onClick={() => setActiveTab('alerts')}
            >
              Alerts
            </button>
            <button
              className={`tab-button ${activeTab === 'query' ? 'active' : ''}`}
              onClick={() => setActiveTab('query')}
            >
              Custom Query
            </button>
          </div>

          <div className="tab-content">
            {renderTabContent()}
          </div>
        </div>
      </div>

      <style jsx>{`
        .database-dashboard {
          display: flex;
          flex-direction: column;
          height: 100%;
        }

        .dashboard-header {
          padding: 1.5rem 0;
        }

        .dashboard-header h1 {
          margin: 0;
          font-size: 1.8rem;
          color: #333;
        }

        .dashboard-header p {
          margin: 0.5rem 0 0;
          color: #666;
        }

        .dashboard-content {
          display: flex;
          flex: 1;
          background-color: #f8f9fa;
          border-radius: 8px;
          overflow: hidden;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .sidebar {
          width: 300px;
          background-color: white;
          border-right: 1px solid #eee;
          overflow-y: auto;
        }

        .main-content {
          flex: 1;
          padding: 1.5rem;
          overflow-y: auto;
        }

        .instance-info {
          margin-bottom: 1.5rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid #eee;
        }

        .instance-info h2 {
          margin: 0;
          font-size: 1.2rem;
          color: #333;
        }

        .connection-type {
          margin-top: 0.25rem;
          font-size: 0.9rem;
          color: #666;
        }

        .tabs {
          display: flex;
          border-bottom: 1px solid #eee;
          margin-bottom: 1.5rem;
        }

        .tab-button {
          padding: 0.75rem 1.5rem;
          background: none;
          border: none;
          border-bottom: 2px solid transparent;
          font-size: 1rem;
          color: #666;
          cursor: pointer;
          transition: all 0.2s;
        }

        .tab-button:hover {
          color: #333;
        }

        .tab-button.active {
          color: #0070f3;
          border-bottom-color: #0070f3;
        }

        .tab-content {
          background-color: white;
          border-radius: 4px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }

        .no-instance-selected, .loading {
          padding: 3rem;
          text-align: center;
          color: #666;
        }

        .error-message {
          background-color: #f8d7da;
          color: #721c24;
          padding: 0.75rem;
          border-radius: 4px;
          margin-bottom: 1.5rem;
        }

        @media (max-width: 768px) {
          .dashboard-content {
            flex-direction: column;
          }

          .sidebar {
            width: 100%;
            border-right: none;
            border-bottom: 1px solid #eee;
          }
        }
      `}</style>
    </div>
  );
};

export default DatabaseDashboard;
