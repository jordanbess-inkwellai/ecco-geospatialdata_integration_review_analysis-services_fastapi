import React, { useState } from 'react';
import Layout from '../components/Layout';
import TileConverter from '../components/TileConverter';
import MapConfiguration from '../components/MapConfiguration';

const TileConverterPage: React.FC = () => {
  const [convertedGpkg, setConvertedGpkg] = useState<any | null>(null);
  const [showMap, setShowMap] = useState(false);
  
  const handleConversionComplete = (result: any) => {
    setConvertedGpkg(result);
    setShowMap(true);
  };
  
  return (
    <Layout>
      <div className="tile-converter-page">
        <div className="page-header">
          <h1>Tile Converter</h1>
          <p>
            Convert GeoJSON to vector tiles (PMTiles/MBTiles) using Tippecanoe and then to GeoPackage.
            This tool allows you to optimize and visualize your geospatial data before importing it into PostGIS.
          </p>
        </div>
        
        <div className="converter-container">
          <TileConverter onConversionComplete={handleConversionComplete} />
        </div>
        
        {showMap && (
          <div className="map-container">
            <h2>Preview Converted Data</h2>
            <p>
              Your GeoPackage has been successfully created. You can now preview it on the map
              or download it for use in other applications.
            </p>
            
            <MapConfiguration
              height="500px"
              width="100%"
              initialCenter={[0, 0]}
              initialZoom={2}
            />
          </div>
        )}
      </div>
      
      <style jsx>{`
        .tile-converter-page {
          padding: 1rem 0;
        }
        
        .page-header {
          margin-bottom: 2rem;
        }
        
        .page-header h1 {
          margin-bottom: 0.5rem;
        }
        
        .page-header p {
          color: #666;
          max-width: 800px;
        }
        
        .converter-container {
          margin-bottom: 2rem;
        }
        
        .map-container {
          margin-top: 3rem;
          padding-top: 2rem;
          border-top: 1px solid #eee;
        }
        
        .map-container h2 {
          margin-bottom: 0.5rem;
        }
        
        .map-container p {
          margin-bottom: 1.5rem;
          color: #666;
        }
      `}</style>
    </Layout>
  );
};

export default TileConverterPage;
