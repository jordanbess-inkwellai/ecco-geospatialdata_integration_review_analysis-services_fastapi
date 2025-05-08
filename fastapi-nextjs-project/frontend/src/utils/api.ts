import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';
const INTEGRATED_API_URL = `${API_BASE_URL}/integrated`;

// Create axios instance with default config
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add request interceptor for handling errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

// Database connection
export const connectDatabase = async (connectionSettings) => {
    try {
        const response = await api.post(`${INTEGRATED_API_URL}/database/connect`, connectionSettings);
        return response.data;
    } catch (error) {
        console.error('Error connecting to database:', error);
        throw error;
    }
};

// Geospatial data
export const fetchGeospatialData = async (params = {}) => {
    try {
        const response = await api.get(`${INTEGRATED_API_URL}/geospatial/data`, { params });
        return response.data;
    } catch (error) {
        console.error('Error fetching geospatial data:', error);
        throw error;
    }
};

export const getGeospatialDataById = async (id) => {
    try {
        const response = await api.get(`${INTEGRATED_API_URL}/geospatial/data/${id}`);
        return response.data;
    } catch (error) {
        console.error(`Error fetching geospatial data with ID ${id}:`, error);
        throw error;
    }
};

export const createGeospatialData = async (data) => {
    try {
        const response = await api.post(`${INTEGRATED_API_URL}/geospatial/data`, data);
        return response.data;
    } catch (error) {
        console.error('Error creating geospatial data:', error);
        throw error;
    }
};

export const updateGeospatialData = async (id, data) => {
    try {
        const response = await api.put(`${INTEGRATED_API_URL}/geospatial/data/${id}`, data);
        return response.data;
    } catch (error) {
        console.error(`Error updating geospatial data with ID ${id}:`, error);
        throw error;
    }
};

export const deleteGeospatialData = async (id) => {
    try {
        const response = await api.delete(`${INTEGRATED_API_URL}/geospatial/data/${id}`);
        return response.data;
    } catch (error) {
        console.error(`Error deleting geospatial data with ID ${id}:`, error);
        throw error;
    }
};

// Spatial queries
export const queryDataWithinGeometry = async (geometry) => {
    try {
        const response = await api.get(`${INTEGRATED_API_URL}/spatial/within`, {
            params: { geometry: JSON.stringify(geometry) }
        });
        return response.data;
    } catch (error) {
        console.error('Error querying data within geometry:', error);
        throw error;
    }
};

export const bufferGeometry = async (geometry, distance) => {
    try {
        const response = await api.get(`${INTEGRATED_API_URL}/spatial/buffer`, {
            params: {
                geometry: JSON.stringify(geometry),
                distance
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error buffering geometry:', error);
        throw error;
    }
};

// Legacy API endpoints (for backward compatibility)
export const importData = async (data) => {
    try {
        const response = await api.post(`${API_BASE_URL}/importer/import`, data);
        return response.data;
    } catch (error) {
        console.error('Error importing data:', error);
        throw error;
    }
};

export const getGeoFeatures = async (params = {}) => {
    try {
        const response = await api.get(`${API_BASE_URL}/geo-feature/geo_features`, { params });
        return response.data;
    } catch (error) {
        console.error('Error fetching geo features:', error);
        throw error;
    }
};

export const getGeoTable = async (params = {}) => {
    try {
        const response = await api.get(`${API_BASE_URL}/geo-table/tables`, { params });
        return response.data;
    } catch (error) {
        console.error('Error fetching geo table:', error);
        throw error;
    }
};

export const assessGeoSuitability = async (locationId) => {
    try {
        const response = await api.get(`${API_BASE_URL}/geo-suitability/suitability/${locationId}`);
        return response.data;
    } catch (error) {
        console.error('Error assessing geo suitability:', error);
        throw error;
    }
};