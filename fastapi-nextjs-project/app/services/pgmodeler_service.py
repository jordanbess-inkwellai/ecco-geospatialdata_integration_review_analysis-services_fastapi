import os
import subprocess
import tempfile
from typing import Dict, List, Optional, Union

class PgModelerService:
    def __init__(self, pgmodeler_bin_path: str = None):
        """
        Initialize PgModeler service
        
        Args:
            pgmodeler_bin_path: Path to PgModeler binaries
        """
        self.pgmodeler_bin_path = pgmodeler_bin_path or self._find_pgmodeler_path()
        self.temp_dir = tempfile.mkdtemp()
        
    def _find_pgmodeler_path(self) -> str:
        """Find PgModeler binary path"""
        # Try common installation paths
        common_paths = [
            "/usr/bin/pgmodeler",
            "/usr/local/bin/pgmodeler",
            "C:\\Program Files\\pgModeler\\pgmodeler.exe",
            "C:\\Program Files (x86)\\pgModeler\\pgmodeler.exe",
            "/Applications/pgModeler.app/Contents/MacOS/pgmodeler"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
                
        # If not found, assume it's in PATH
        return "pgmodeler"
    
    def import_database(self, 
                       connection_string: str, 
                       output_file: str = None,
                       import_system_objects: bool = False,
                       import_extension_objects: bool = True) -> str:
        """
        Import a database schema using PgModeler
        
        Args:
            connection_string: PostgreSQL connection string
            output_file: Output file path
            import_system_objects: Import system objects
            import_extension_objects: Import extension objects
            
        Returns:
            Path to the generated model file
        """
        try:
            # Parse connection string to extract components
            # Example: postgresql://username:password@hostname:5432/dbname
            conn_parts = connection_string.replace("postgresql://", "").split("@")
            user_pass = conn_parts[0].split(":")
            host_port_db = conn_parts[1].split("/")
            host_port = host_port_db[0].split(":")
            
            username = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            hostname = host_port[0]
            port = host_port[1] if len(host_port) > 1 else "5432"
            dbname = host_port_db[1]
            
            # Create output file if not provided
            if not output_file:
                output_file = os.path.join(self.temp_dir, f"model_{os.urandom(8).hex()}.dbm")
            
            # Build command
            cmd = [
                self.pgmodeler_bin_path,
                "--import-db",
                "--input-db", dbname,
                "--host", hostname,
                "--port", port,
                "--user", username,
                "--output", output_file
            ]
            
            # Add password if provided
            if password:
                cmd.extend(["--passwd", password])
                
            # Add import options
            if import_system_objects:
                cmd.append("--import-sys-objs")
                
            if import_extension_objects:
                cmd.append("--import-ext-objs")
            
            # Execute command
            subprocess.run(cmd, check=True)
            
            return output_file
        except Exception as e:
            raise Exception(f"Error importing database: {str(e)}")
    
    def export_model(self, 
                    model_file: str, 
                    output_format: str = 'png',
                    output_file: str = None) -> str:
        """
        Export a PgModeler model to different formats
        
        Args:
            model_file: Path to PgModeler model file (.dbm)
            output_format: Output format (png, svg, sql, data-dict)
            output_file: Output file path
            
        Returns:
            Path to the exported file
        """
        try:
            # Create output file if not provided
            if not output_file:
                output_file = os.path.join(self.temp_dir, f"export_{os.urandom(8).hex()}.{output_format}")
            
            # Build command
            cmd = [
                self.pgmodeler_bin_path,
                "--export-to-" + output_format,
                "--input", model_file,
                "--output", output_file
            ]
            
            # Execute command
            subprocess.run(cmd, check=True)
            
            return output_file
        except Exception as e:
            raise Exception(f"Error exporting model: {str(e)}")

pgmodeler_service = PgModelerService()
