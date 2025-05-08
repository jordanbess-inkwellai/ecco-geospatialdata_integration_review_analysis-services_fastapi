from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union

class PivotTableRequest(BaseModel):
    """Schema for creating a pivot table."""
    
    query: str = Field(..., description="SQL query to execute that returns the data to pivot")
    pivot_column: str = Field(..., description="The column to use for new column names")
    row_identifier: str = Field(..., description="The column to use for row identifiers")
    value_column: Union[str, Dict[str, str]] = Field(..., description="The column to aggregate or a dictionary mapping column names to aggregation functions")
    column_names: Optional[Dict[str, str]] = Field(None, description="Optional dictionary mapping pivot values to column names")
    db_path: Optional[str] = Field(None, description="Path to the database file")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "SELECT category, product, sales FROM sales_data",
                "pivot_column": "category",
                "row_identifier": "product",
                "value_column": "sales",
                "column_names": {"1": "Category 1", "2": "Category 2"},
                "db_path": None
            }
        }

class PivotTableResponse(BaseModel):
    """Schema for pivot table response."""
    
    data: List[Dict[str, Any]] = Field(..., description="Pivot table data")
    columns: List[str] = Field(..., description="Column names in the pivot table")
