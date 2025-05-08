import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { fetchGeospatialData, createGeospatialData, deleteGeospatialData } from '../utils/api';

interface GeospatialItem {
    id: number;
    name: string;
    description: string;
    geometry: any;
    properties: any;
    created_at: string;
}

const Geospatial: React.FC = () => {
    const [geospatialData, setGeospatialData] = useState<GeospatialItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showForm, setShowForm] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        geometry: {
            type: 'Point',
            coordinates: [0, 0]
        },
        properties: {}
    });

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setLoading(true);
        setError('');
        try {
            const data = await fetchGeospatialData();
            setGeospatialData(data);
        } catch (err) {
            setError('Failed to fetch geospatial data. Please check your database connection.');
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData({
            ...formData,
            [name]: value
        });
    };

    const handleGeometryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const geometryType = e.target.value;
        let coordinates;

        switch (geometryType) {
            case 'Point':
                coordinates = [0, 0];
                break;
            case 'LineString':
                coordinates = [[0, 0], [1, 1]];
                break;
            case 'Polygon':
                coordinates = [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]];
                break;
            default:
                coordinates = [0, 0];
        }

        setFormData({
            ...formData,
            geometry: {
                type: geometryType,
                coordinates
            }
        });
    };

    const handleCoordinatesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        try {
            const coordinates = JSON.parse(e.target.value);
            setFormData({
                ...formData,
                geometry: {
                    ...formData.geometry,
                    coordinates
                }
            });
        } catch (err) {
            // Invalid JSON, ignore
        }
    };

    const handlePropertiesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        try {
            const properties = JSON.parse(e.target.value);
            setFormData({
                ...formData,
                properties
            });
        } catch (err) {
            // Invalid JSON, ignore
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await createGeospatialData(formData);
            setShowForm(false);
            setFormData({
                name: '',
                description: '',
                geometry: {
                    type: 'Point',
                    coordinates: [0, 0]
                },
                properties: {}
            });
            fetchData();
        } catch (err) {
            setError('Failed to create geospatial data.');
        }
    };

    const handleDelete = async (id: number) => {
        if (confirm('Are you sure you want to delete this item?')) {
            try {
                await deleteGeospatialData(id);
                fetchData();
            } catch (err) {
                setError('Failed to delete geospatial data.');
            }
        }
    };

    return (
        <Layout>
            <div className="geospatial-page">
                <div className="page-header">
                    <h1>Geospatial Data</h1>
                    <button className="button" onClick={() => setShowForm(!showForm)}>
                        {showForm ? 'Cancel' : 'Add New Data'}
                    </button>
                </div>

                {error && <div className="error-message">{error}</div>}

                {showForm && (
                    <div className="form-container">
                        <h2>Add New Geospatial Data</h2>
                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label htmlFor="name">Name</label>
                                <input
                                    type="text"
                                    id="name"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="description">Description</label>
                                <textarea
                                    id="description"
                                    name="description"
                                    value={formData.description}
                                    onChange={handleInputChange}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="geometryType">Geometry Type</label>
                                <select
                                    id="geometryType"
                                    value={formData.geometry.type}
                                    onChange={handleGeometryChange}
                                >
                                    <option value="Point">Point</option>
                                    <option value="LineString">LineString</option>
                                    <option value="Polygon">Polygon</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label htmlFor="coordinates">Coordinates (JSON)</label>
                                <textarea
                                    id="coordinates"
                                    value={JSON.stringify(formData.geometry.coordinates, null, 2)}
                                    onChange={handleCoordinatesChange}
                                    rows={5}
                                />
                                <small>
                                    Format: [lon, lat] for Point, [[lon1, lat1], [lon2, lat2], ...] for LineString,
                                    [[[lon1, lat1], [lon2, lat2], ...]] for Polygon
                                </small>
                            </div>

                            <div className="form-group">
                                <label htmlFor="properties">Properties (JSON)</label>
                                <textarea
                                    id="properties"
                                    value={JSON.stringify(formData.properties, null, 2)}
                                    onChange={handlePropertiesChange}
                                    rows={5}
                                />
                            </div>

                            <button type="submit" className="button">
                                Save
                            </button>
                        </form>
                    </div>
                )}

                {loading ? (
                    <div className="loading">Loading...</div>
                ) : (
                    <div className="data-container">
                        {geospatialData.length === 0 ? (
                            <div className="empty-state">
                                <p>No geospatial data found. Add some data to get started.</p>
                            </div>
                        ) : (
                            <div className="data-grid">
                                {geospatialData.map((item) => (
                                    <div key={item.id} className="data-card">
                                        <div className="data-header">
                                            <h3>{item.name}</h3>
                                            <button
                                                className="delete-button"
                                                onClick={() => handleDelete(item.id)}
                                            >
                                                <span className="material-icons">delete</span>
                                            </button>
                                        </div>
                                        <p className="description">{item.description}</p>
                                        <div className="data-details">
                                            <p>
                                                <strong>Type:</strong> {item.geometry.type}
                                            </p>
                                            <p>
                                                <strong>Created:</strong>{' '}
                                                {new Date(item.created_at).toLocaleDateString()}
                                            </p>
                                        </div>
                                        <div className="data-actions">
                                            <button className="view-button">
                                                <span className="material-icons">visibility</span>
                                                View
                                            </button>
                                            <button className="edit-button">
                                                <span className="material-icons">edit</span>
                                                Edit
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>

            <style jsx>{`
                .geospatial-page {
                    padding: 1rem 0;
                }

                .page-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 2rem;
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

                .error-message {
                    background-color: #f8d7da;
                    color: #721c24;
                    padding: 1rem;
                    border-radius: 4px;
                    margin-bottom: 1rem;
                }

                .form-container {
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                }

                .form-group {
                    margin-bottom: 1rem;
                }

                label {
                    display: block;
                    margin-bottom: 0.5rem;
                    font-weight: bold;
                }

                input,
                textarea,
                select {
                    width: 100%;
                    padding: 0.5rem;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-family: inherit;
                    font-size: inherit;
                }

                textarea {
                    font-family: monospace;
                }

                small {
                    display: block;
                    margin-top: 0.25rem;
                    color: #6c757d;
                }

                .loading {
                    text-align: center;
                    padding: 2rem;
                    font-size: 1.2rem;
                    color: #6c757d;
                }

                .empty-state {
                    text-align: center;
                    padding: 2rem;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }

                .data-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 1.5rem;
                }

                .data-card {
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    padding: 1.5rem;
                }

                .data-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin-bottom: 1rem;
                }

                .data-header h3 {
                    margin: 0;
                }

                .delete-button {
                    background: none;
                    border: none;
                    color: #dc3545;
                    cursor: pointer;
                    padding: 0;
                }

                .description {
                    color: #6c757d;
                    margin-bottom: 1rem;
                }

                .data-details {
                    margin-bottom: 1rem;
                }

                .data-details p {
                    margin: 0.25rem 0;
                }

                .data-actions {
                    display: flex;
                    gap: 0.5rem;
                }

                .view-button,
                .edit-button {
                    display: flex;
                    align-items: center;
                    gap: 0.25rem;
                    background: none;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 0.25rem 0.5rem;
                    cursor: pointer;
                    font-size: 0.875rem;
                }

                .view-button {
                    color: #0070f3;
                }

                .edit-button {
                    color: #28a745;
                }

                .view-button:hover,
                .edit-button:hover {
                    background-color: #f8f9fa;
                }
            `}</style>
        </Layout>
    );
};

export default Geospatial;
