import React, { useState } from 'react';
import Layout from '../components/Layout';
import { connectDatabase } from '../utils/api';

interface DatabaseSettings {
    host: string;
    port: number;
    username: string;
    password: string;
    database: string;
}

const Settings: React.FC = () => {
    const [settings, setSettings] = useState<DatabaseSettings>({
        host: 'localhost',
        port: 5432,
        username: 'postgres',
        password: 'postgres',
        database: 'geospatial',
    });

    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' | '' }>({
        text: '',
        type: '',
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setSettings({
            ...settings,
            [name]: name === 'port' ? parseInt(value, 10) : value,
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setMessage({ text: '', type: '' });

        try {
            const response = await connectDatabase(settings);
            setMessage({
                text: response.message,
                type: response.success ? 'success' : 'error',
            });
        } catch (error) {
            setMessage({
                text: 'Failed to connect to the database. Please check your settings and try again.',
                type: 'error',
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <Layout>
            <div className="settings-page">
                <h1>Database Settings</h1>
                <p>Configure your PostgreSQL database connection settings.</p>

                {message.text && (
                    <div className={`message ${message.type}`}>
                        {message.text}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="host">Host</label>
                        <input
                            type="text"
                            id="host"
                            name="host"
                            value={settings.host}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="port">Port</label>
                        <input
                            type="number"
                            id="port"
                            name="port"
                            value={settings.port}
                            onChange={handleChange}
                            min="1"
                            max="65535"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={settings.username}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={settings.password}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="database">Database</label>
                        <input
                            type="text"
                            id="database"
                            name="database"
                            value={settings.database}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <button type="submit" className="button" disabled={loading}>
                        {loading ? 'Connecting...' : 'Connect'}
                    </button>
                </form>

                <div className="info-box">
                    <h3>PostGIS Requirements</h3>
                    <p>
                        Make sure your PostgreSQL database has the PostGIS extension installed.
                        The application will attempt to create the extension if it doesn't exist.
                    </p>
                    <p>
                        To manually install PostGIS, connect to your database and run:
                        <code>CREATE EXTENSION postgis;</code>
                    </p>
                </div>
            </div>

            <style jsx>{`
                .settings-page {
                    max-width: 600px;
                    margin: 0 auto;
                }

                .form-group {
                    margin-bottom: 1rem;
                }

                label {
                    display: block;
                    margin-bottom: 0.5rem;
                    font-weight: bold;
                }

                input {
                    width: 100%;
                    padding: 0.5rem;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }

                .button {
                    background-color: #0070f3;
                    color: white;
                    border: none;
                    padding: 0.5rem 1rem;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 1rem;
                }

                .button:disabled {
                    background-color: #ccc;
                    cursor: not-allowed;
                }

                .message {
                    padding: 1rem;
                    margin: 1rem 0;
                    border-radius: 4px;
                }

                .success {
                    background-color: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }

                .error {
                    background-color: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }

                .info-box {
                    background-color: #e3f2fd;
                    border: 1px solid #b3e5fc;
                    border-radius: 4px;
                    padding: 1rem;
                    margin-top: 2rem;
                }

                code {
                    display: block;
                    background-color: #f8f9fa;
                    padding: 0.5rem;
                    margin: 0.5rem 0;
                    border-radius: 4px;
                    font-family: monospace;
                }
            `}</style>
        </Layout>
    );
};

export default Settings;
