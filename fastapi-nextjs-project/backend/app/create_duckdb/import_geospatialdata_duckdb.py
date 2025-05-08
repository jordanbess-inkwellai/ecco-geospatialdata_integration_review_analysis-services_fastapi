import os
import sys
import duckdb
import geopandas as gpd

# Script: import_geojson.py
# Purpose: This script imports all GeoJSON files from a specified folder into a DuckDB database 
#          using the spatial extension capabilities of DuckDB.
# Usage:
#   python import_geojson.py <input_folder> <output_db>
# Where:
#   <input_folder> is the path to the folder containing GeoJSON files.
#   <output_db> is the path to the DuckDB database file that will be created or modified.
# Dependencies:
#   - duckdb
#   - geopandas

def import_geojson_to_duckdb(input_folder, output_db):
    # Connect to DuckDB (this will create the database if it doesn't exist)
    conn = duckdb.connect(output_db)
    
    # Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        # Check if the file is a GeoJSON file
        if filename.endswith('.geojson'):
            file_path = os.path.join(input_folder, filename)  # Construct full file path
            print(f"Importing {file_path}...")  # Notify user about the import process
            # Read the GeoJSON file using GeoPandas
            gdf = gpd.read_file(file_path)
            # Create a table name based on the filename without extension
            table_name = os.path.splitext(filename)[0]
            # Convert the GeoDataFrame to Parquet format for optimal performance
            gdf.to_parquet('temp.parquet')  
            # Import the Parquet data into DuckDB as a new table
            conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_parquet('temp.parquet')")
    
    # Close the database connection
    conn.close()
    print("Import completed.")  # Notify user of the completion

if __name__ == "__main__":
    # Check for the correct number of command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python import_geojson.py <input_folder> <output_db>")
        sys.exit(1)
    
    # Capture command-line arguments for input folder and output database
    input_folder = sys.argv[1]
    output_db = sys.argv[2]
    
    # Call the import function with the specified paths
    import_geojson_to_duckdb(input_folder, output_db)