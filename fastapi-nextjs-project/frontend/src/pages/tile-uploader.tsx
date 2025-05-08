import React, { useState } from 'react';
import Layout from '../components/Layout';
import TileUploader from '../components/TileUploader';
import MapConfiguration from '../components/MapConfiguration';

const TileUploaderPage: React.FC = () => {
  const [uploadedTile, setUploadedTile] = useState<any | null>(null);
  const [showMap, setShowMap] = useState(false);
  
  const handleUploadComplete = (result: any) => {
    setUploadedTile(result);
    setShowMap(true);
  };
  
  return (
    <Layout>
      <div className="tile-uploader-page">
        <div className="page-header">
          <h1>Tile Uploader</h1>
          <p>
            Upload and manage PMTiles and MBTiles files. These files can be used directly with Martin
            for serving vector and raster tiles, or converted to GeoPackage format.
          </p>
        </div>
        
        <div className="uploader-container">
          <TileUploader onUploadComplete={handleUploadComplete} />
        </div>
        
        {showMap && (
          <div className="map-container">
            <h2>Preview Uploaded Tile</h2>
            <p>
              Your tile file has been successfully uploaded. You can now preview it on the map
              or use it in your applications.
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
        .tile-uploader-page {
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
        
        .uploader-container {
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

export default TileUploaderPage;
