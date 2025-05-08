import React, { useState } from 'react';
import Link from 'next/link';

interface Service {
  name: string;
  description: string;
  swaggerUrl: string;
  docsUrl?: string;
  githubUrl?: string;
}

const DeveloperDocs: React.FC = () => {
  // List of services with their documentation links
  const services: Service[] = [
    {
      name: 'FastGeospatial',
      description: 'Geospatial data processing and analysis service',
      swaggerUrl: '/api/v1/fast-geospatial/docs',
      docsUrl: '/docs/fast-geospatial',
      githubUrl: 'https://github.com/yourusername/fastgeospatial'
    },
    {
      name: 'FastImporter',
      description: 'Data import service for various geospatial formats',
      swaggerUrl: '/api/v1/fast-importer/docs',
      docsUrl: '/docs/fast-importer'
    },
    {
      name: 'FateGeoFeature',
      description: 'Feature management service for geospatial data',
      swaggerUrl: '/api/v1/fate-geo-feature/docs',
      docsUrl: '/docs/fate-geo-feature'
    },
    {
      name: 'FastGeoTable',
      description: 'Table management service for geospatial data',
      swaggerUrl: '/api/v1/fast-geo-table/docs',
      docsUrl: '/docs/fast-geo-table'
    },
    {
      name: 'FastGeoSuitability',
      description: 'Geospatial suitability analysis service',
      swaggerUrl: '/api/v1/fast-geo-suitability/docs',
      docsUrl: '/docs/fast-geo-suitability'
    },
    {
      name: 'Tile Services',
      description: 'Vector and raster tile management services',
      swaggerUrl: '/api/v1/tiles/docs',
      docsUrl: '/docs/tiles'
    },
    {
      name: 'Tippecanoe',
      description: 'Vector tile generation service using Tippecanoe',
      swaggerUrl: '/api/v1/tippecanoe/docs',
      docsUrl: '/docs/tippecanoe'
    },
    {
      name: 'Geospatial Processing',
      description: 'Advanced geospatial data processing with DuckDB',
      swaggerUrl: '/api/v1/geospatial-processing/docs',
      docsUrl: '/docs/geospatial-processing'
    },
    {
      name: 'ESRI Geodatabase',
      description: 'ESRI Mobile Geodatabase conversion service',
      swaggerUrl: '/api/v1/esri-geodatabase/docs',
      docsUrl: '/docs/esri-geodatabase'
    },
    {
      name: 'Integrated API',
      description: 'Combined API for all geospatial services',
      swaggerUrl: '/api/v1/docs',
      docsUrl: '/docs/integrated'
    }
  ];

  // State for search filter
  const [searchTerm, setSearchTerm] = useState('');
  
  // Filter services based on search term
  const filteredServices = services.filter(service => 
    service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    service.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="developer-docs">
      <div className="docs-header">
        <h1>Developer Documentation</h1>
        <p>
          Access API documentation and developer resources for all microservices
          in the PostGIS Microservices ecosystem.
        </p>
        
        <div className="search-container">
          <input
            type="text"
            placeholder="Search services..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
      </div>
      
      <div className="services-grid">
        {filteredServices.map((service, index) => (
          <div key={index} className="service-card">
            <h2>{service.name}</h2>
            <p className="service-description">{service.description}</p>
            
            <div className="service-links">
              <a 
                href={service.swaggerUrl} 
                target="_blank" 
                rel="noopener noreferrer"
                className="swagger-link"
              >
                OpenAPI / Swagger
              </a>
              
              {service.docsUrl && (
                <Link href={service.docsUrl}>
                  <a className="docs-link">Documentation</a>
                </Link>
              )}
              
              {service.githubUrl && (
                <a 
                  href={service.githubUrl} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="github-link"
                >
                  GitHub Repository
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
      
      <div className="additional-resources">
        <h2>Additional Resources</h2>
        
        <div className="resources-grid">
          <div className="resource-card">
            <h3>API Overview</h3>
            <p>
              Get a comprehensive overview of all available APIs and how they work together.
            </p>
            <Link href="/docs/api-overview">
              <a className="resource-link">View API Overview</a>
            </Link>
          </div>
          
          <div className="resource-card">
            <h3>Authentication</h3>
            <p>
              Learn how to authenticate with the APIs and manage access tokens.
            </p>
            <Link href="/docs/authentication">
              <a className="resource-link">Authentication Guide</a>
            </Link>
          </div>
          
          <div className="resource-card">
            <h3>Tutorials</h3>
            <p>
              Step-by-step tutorials for common workflows and use cases.
            </p>
            <Link href="/docs/tutorials">
              <a className="resource-link">Browse Tutorials</a>
            </Link>
          </div>
          
          <div className="resource-card">
            <h3>Code Examples</h3>
            <p>
              Sample code in various languages to help you get started quickly.
            </p>
            <Link href="/docs/examples">
              <a className="resource-link">View Code Examples</a>
            </Link>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .developer-docs {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem 1rem;
        }
        
        .docs-header {
          text-align: center;
          margin-bottom: 3rem;
        }
        
        .docs-header h1 {
          font-size: 2.5rem;
          margin-bottom: 1rem;
          color: #333;
        }
        
        .docs-header p {
          font-size: 1.2rem;
          color: #666;
          max-width: 800px;
          margin: 0 auto 2rem;
        }
        
        .search-container {
          max-width: 600px;
          margin: 0 auto;
        }
        
        .search-input {
          width: 100%;
          padding: 0.75rem 1rem;
          font-size: 1rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .services-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 2rem;
          margin-bottom: 4rem;
        }
        
        .service-card {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          padding: 1.5rem;
          transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .service-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        .service-card h2 {
          font-size: 1.5rem;
          margin-bottom: 0.75rem;
          color: #333;
        }
        
        .service-description {
          color: #666;
          margin-bottom: 1.5rem;
          min-height: 3em;
        }
        
        .service-links {
          display: flex;
          flex-wrap: wrap;
          gap: 0.75rem;
        }
        
        .swagger-link, .docs-link, .github-link {
          display: inline-block;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          text-decoration: none;
          font-weight: 500;
          font-size: 0.9rem;
          transition: background-color 0.2s;
        }
        
        .swagger-link {
          background-color: #85ea2d;
          color: #173647;
        }
        
        .swagger-link:hover {
          background-color: #78d728;
        }
        
        .docs-link {
          background-color: #0070f3;
          color: white;
        }
        
        .docs-link:hover {
          background-color: #0051a8;
        }
        
        .github-link {
          background-color: #333;
          color: white;
        }
        
        .github-link:hover {
          background-color: #000;
        }
        
        .additional-resources {
          margin-top: 4rem;
        }
        
        .additional-resources h2 {
          text-align: center;
          font-size: 2rem;
          margin-bottom: 2rem;
          color: #333;
        }
        
        .resources-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 2rem;
        }
        
        .resource-card {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          padding: 1.5rem;
          text-align: center;
        }
        
        .resource-card h3 {
          font-size: 1.25rem;
          margin-bottom: 0.75rem;
          color: #333;
        }
        
        .resource-card p {
          color: #666;
          margin-bottom: 1.5rem;
          min-height: 4em;
        }
        
        .resource-link {
          display: inline-block;
          padding: 0.5rem 1rem;
          background-color: #f0f0f0;
          color: #333;
          border-radius: 4px;
          text-decoration: none;
          font-weight: 500;
          transition: background-color 0.2s;
        }
        
        .resource-link:hover {
          background-color: #e0e0e0;
        }
        
        @media (max-width: 768px) {
          .services-grid, .resources-grid {
            grid-template-columns: 1fr;
          }
          
          .service-description, .resource-card p {
            min-height: auto;
          }
        }
      `}</style>
    </div>
  );
};

export default DeveloperDocs;
