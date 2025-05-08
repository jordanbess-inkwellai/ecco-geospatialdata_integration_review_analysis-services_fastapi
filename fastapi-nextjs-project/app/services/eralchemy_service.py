import os
import tempfile
from typing import Dict, List, Optional, Union
from eralchemy import render_er
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.automap import automap_base

class ERAlchemyService:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def generate_diagram_from_db(self, 
                                connection_string: str, 
                                output_format: str = 'png',
                                exclude_tables: List[str] = None,
                                exclude_columns: List[str] = None) -> str:
        """
        Generate an ER diagram from a database connection
        
        Args:
            connection_string: SQLAlchemy connection string
            output_format: Output format (png, pdf, svg)
            exclude_tables: List of tables to exclude
            exclude_columns: List of columns to exclude
            
        Returns:
            Path to the generated diagram
        """
        try:
            # Create a unique filename
            output_file = os.path.join(self.temp_dir, f"diagram_{os.urandom(8).hex()}.{output_format}")
            
            # Generate the diagram
            render_er(connection_string, output_file, exclude_tables=exclude_tables or [], 
                     exclude_columns=exclude_columns or [])
            
            return output_file
        except Exception as e:
            raise Exception(f"Error generating diagram: {str(e)}")
    
    def generate_diagram_from_models(self, 
                                    models, 
                                    output_format: str = 'png') -> str:
        """
        Generate an ER diagram from SQLAlchemy models
        
        Args:
            models: SQLAlchemy models
            output_format: Output format (png, pdf, svg)
            
        Returns:
            Path to the generated diagram
        """
        try:
            # Create a unique filename
            output_file = os.path.join(self.temp_dir, f"diagram_{os.urandom(8).hex()}.{output_format}")
            
            # Generate the diagram
            render_er(models, output_file)
            
            return output_file
        except Exception as e:
            raise Exception(f"Error generating diagram: {str(e)}")

eralchemy_service = ERAlchemyService()
