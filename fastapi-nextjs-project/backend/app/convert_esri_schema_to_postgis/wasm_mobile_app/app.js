// Import the gpkg_utils.js file
import { createGpkg, createTiles, downloadGpkg } from './gpkg/gpkg_utils.js';

const createGpkgButton = document.querySelector('button:nth-child(1)');
const createTilesButton = document.querySelector('button:nth-child(2)');
const downloadGpkgButton = document.querySelector('button:nth-child(3)');

// Add event listener to the "Create GPKG" button
createGpkgButton.addEventListener('click', () => {
  createGpkg();
});

// Add event listener to the "Create Tiles" button
createTilesButton.addEventListener('click', () => {
  createTiles();
});

// Add event listener to the "Download GPKG" button
downloadGpkgButton.addEventListener('click', () => {
  downloadGpkg();
});

// Here will be the code to register the service worker



// Here will be the code to register the service worker
