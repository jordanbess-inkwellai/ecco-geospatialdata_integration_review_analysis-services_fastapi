import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import Link from 'next/link';
import { fetchGeospatialData, getGeoFeatures, getGeoTable } from '../utils/api';

const Home: React.FC = () => {
    const [stats, setStats] = useState({
        geospatialCount: 0,
        featuresCount: 0,
        tablesCount: 0,
        loading: true,
        error: ''
    });

    useEffect(() => {
        const fetchStats = async () => {
            try {
                // Fetch counts from API
                const [geospatialData, geoFeatures, geoTables] = await Promise.allSettled([
                    fetchGeospatialData(),
                    getGeoFeatures(),
                    getGeoTable()
                ]);

                setStats({
                    geospatialCount: geospatialData.status === 'fulfilled' ? geospatialData.value.length : 0,
                    featuresCount: geoFeatures.status === 'fulfilled' ? geoFeatures.value.length : 0,
                    tablesCount: geoTables.status === 'fulfilled' ? geoTables.value.length : 0,
                    loading: false,
                    error: ''
                });
            } catch (error) {
                setStats({
                    ...stats,
                    loading: false,
                    error: 'Failed to fetch statistics. Please check your database connection.'
                });
            }
        };

        fetchStats();
    }, []);

    return (
        <Layout>
            <div className="dashboard">
                <div className="dashboard-header">
                    <h1>Integrated Geospatial API Dashboard</h1>
                    <p>Welcome to the Integrated Geospatial API. Use the navigation menu to access different features.</p>
                </div>

                {stats.error && (
                    <div className="error-message">
                        <p>{stats.error}</p>
                        <Link href="/settings">
                            <a className="button">Configure Database</a>
                        </Link>
                    </div>
                )}

                <div className="stats-container">
                    <div className="stat-card">
                        <div className="stat-icon">
                            <span className="material-icons">map</span>
                        </div>
                        <div className="stat-content">
                            <h3>Geospatial Data</h3>
                            <p className="stat-value">{stats.loading ? '...' : stats.geospatialCount}</p>
                            <Link href="/geospatial">
                                <a className="stat-link">View Data</a>
                            </Link>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon">
                            <span className="material-icons">layers</span>
                        </div>
                        <div className="stat-content">
                            <h3>Geo Features</h3>
                            <p className="stat-value">{stats.loading ? '...' : stats.featuresCount}</p>
                            <Link href="/geo-feature">
                                <a className="stat-link">View Features</a>
                            </Link>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon">
                            <span className="material-icons">table_chart</span>
                        </div>
                        <div className="stat-content">
                            <h3>Geo Tables</h3>
                            <p className="stat-value">{stats.loading ? '...' : stats.tablesCount}</p>
                            <Link href="/geo-table">
                                <a className="stat-link">View Tables</a>
                            </Link>
                        </div>
                    </div>
                </div>

                <div className="quick-actions">
                    <h2>Quick Actions</h2>
                    <div className="action-buttons">
                        <Link href="/geospatial">
                            <a className="action-button">
                                <span className="material-icons">add_location</span>
                                Add Geospatial Data
                            </a>
                        </Link>
                        <Link href="/importer">
                            <a className="action-button">
                                <span className="material-icons">upload_file</span>
                                Import Data
                            </a>
                        </Link>
                        <Link href="/geo-suitability">
                            <a className="action-button">
                                <span className="material-icons">analytics</span>
                                Run Suitability Analysis
                            </a>
                        </Link>
                        <Link href="/settings">
                            <a className="action-button">
                                <span className="material-icons">settings</span>
                                Configure Database
                            </a>
                        </Link>
                    </div>
                </div>
            </div>

            <style jsx>{`
                .dashboard {
                    padding: 1rem 0;
                }

                .dashboard-header {
                    margin-bottom: 2rem;
                }

                .error-message {
                    background-color: #f8d7da;
                    color: #721c24;
                    padding: 1rem;
                    border-radius: 4px;
                    margin-bottom: 2rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }

                .error-message .button {
                    background-color: #dc3545;
                    color: white;
                    padding: 0.5rem 1rem;
                    border-radius: 4px;
                    text-decoration: none;
                }

                .stats-container {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 1.5rem;
                    margin-bottom: 2rem;
                }

                .stat-card {
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    padding: 1.5rem;
                    display: flex;
                    align-items: center;
                }

                .stat-icon {
                    background-color: #e3f2fd;
                    color: #0070f3;
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-right: 1rem;
                }

                .stat-icon .material-icons {
                    font-size: 2rem;
                }

                .stat-content {
                    flex: 1;
                }

                .stat-content h3 {
                    margin: 0 0 0.5rem 0;
                    font-size: 1.2rem;
                }

                .stat-value {
                    font-size: 2rem;
                    font-weight: bold;
                    margin: 0.5rem 0;
                    color: #0070f3;
                }

                .stat-link {
                    color: #0070f3;
                    text-decoration: none;
                    font-weight: 500;
                }

                .quick-actions {
                    margin-top: 2rem;
                }

                .action-buttons {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                    gap: 1rem;
                    margin-top: 1rem;
                }

                .action-button {
                    background-color: white;
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                    padding: 1rem;
                    text-align: center;
                    text-decoration: none;
                    color: #333;
                    transition: all 0.3s ease;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                }

                .action-button:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    border-color: #0070f3;
                    color: #0070f3;
                }

                .action-button .material-icons {
                    font-size: 2rem;
                    margin-bottom: 0.5rem;
                }

                @media (max-width: 768px) {
                    .stats-container {
                        grid-template-columns: 1fr;
                    }

                    .action-buttons {
                        grid-template-columns: 1fr 1fr;
                    }
                }

                @media (max-width: 480px) {
                    .action-buttons {
                        grid-template-columns: 1fr;
                    }
                }
            `}</style>
        </Layout>
    );
};

export default Home;