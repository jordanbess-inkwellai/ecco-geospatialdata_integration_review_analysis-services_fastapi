import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import geopandas as gpd
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered data validation and schema matching."""
    
    def __init__(self):
        """Initialize the AI service."""
        self.model = None
        self.tokenizer = None
        self.is_initialized = False
        
        # Only initialize if AI features are enabled
        if settings.ENABLE_AI_FEATURES:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the AI model."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            logger.info(f"Initializing AI model from {settings.AI_MODEL_PATH}")
            
            # Configure quantization if specified
            if settings.AI_MODEL_QUANTIZATION:
                if settings.AI_MODEL_QUANTIZATION == "4bit":
                    quantization_config = {"load_in_4bit": True}
                elif settings.AI_MODEL_QUANTIZATION == "8bit":
                    quantization_config = {"load_in_8bit": True}
                else:
                    quantization_config = None
            else:
                quantization_config = None
            
            # Load the model and tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(settings.AI_MODEL_PATH)
            
            # Load the model with appropriate quantization
            if quantization_config:
                self.model = AutoModelForCausalLM.from_pretrained(
                    settings.AI_MODEL_PATH,
                    device_map=settings.AI_MODEL_DEVICE,
                    **quantization_config
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    settings.AI_MODEL_PATH,
                    device_map=settings.AI_MODEL_DEVICE
                )
            
            self.is_initialized = True
            logger.info("AI model initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing AI model: {str(e)}")
            self.is_initialized = False
    
    def validate_data(self, data_path: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate data against a schema or infer data quality issues.
        
        Args:
            data_path: Path to the data file
            schema: Optional schema to validate against
            
        Returns:
            Validation results
        """
        if not settings.ENABLE_AI_FEATURES or not self.is_initialized:
            return self._fallback_validate_data(data_path, schema)
        
        try:
            # Read the data
            file_ext = os.path.splitext(data_path)[1].lower()
            
            if file_ext in ['.csv', '.xlsx', '.xls']:
                df = pd.read_csv(data_path) if file_ext == '.csv' else pd.read_excel(data_path)
                data_sample = df.head(10).to_dict(orient='records')
                column_info = {col: str(df[col].dtype) for col in df.columns}
            elif file_ext in ['.shp', '.geojson', '.json', '.gpkg']:
                gdf = gpd.read_file(data_path)
                data_sample = json.loads(gdf.head(10).to_json())
                column_info = {col: str(gdf[col].dtype) for col in gdf.columns if col != 'geometry'}
                if 'geometry' in gdf.columns:
                    column_info['geometry'] = 'geometry'
            else:
                return {
                    "valid": False,
                    "errors": [f"Unsupported file format: {file_ext}"]
                }
            
            # Prepare the prompt for the model
            prompt = self._create_validation_prompt(data_sample, column_info, schema)
            
            # Generate validation results
            validation_results = self._generate_text(prompt)
            
            # Parse the validation results
            try:
                # Try to extract JSON from the response
                json_start = validation_results.find('{')
                json_end = validation_results.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = validation_results[json_start:json_end]
                    results = json.loads(json_str)
                else:
                    # If no JSON found, create a simple result
                    results = {
                        "valid": "invalid" not in validation_results.lower(),
                        "analysis": validation_results.strip()
                    }
            except json.JSONDecodeError:
                results = {
                    "valid": "invalid" not in validation_results.lower(),
                    "analysis": validation_results.strip()
                }
            
            return results
        except Exception as e:
            logger.error(f"Error in AI data validation: {str(e)}")
            return self._fallback_validate_data(data_path, schema)
    
    def match_schema(self, source_schema: Dict[str, Any], target_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match source schema to target schema.
        
        Args:
            source_schema: Source schema
            target_schema: Target schema
            
        Returns:
            Schema mapping
        """
        if not settings.ENABLE_AI_FEATURES or not self.is_initialized:
            return self._fallback_match_schema(source_schema, target_schema)
        
        try:
            # Prepare the prompt for the model
            prompt = self._create_schema_matching_prompt(source_schema, target_schema)
            
            # Generate schema mapping
            mapping_results = self._generate_text(prompt)
            
            # Parse the mapping results
            try:
                # Try to extract JSON from the response
                json_start = mapping_results.find('{')
                json_end = mapping_results.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = mapping_results[json_start:json_end]
                    mapping = json.loads(json_str)
                else:
                    # If no JSON found, create a simple result
                    mapping = {
                        "mapping": mapping_results.strip(),
                        "confidence": "low"
                    }
            except json.JSONDecodeError:
                mapping = {
                    "mapping": mapping_results.strip(),
                    "confidence": "low"
                }
            
            return mapping
        except Exception as e:
            logger.error(f"Error in AI schema matching: {str(e)}")
            return self._fallback_match_schema(source_schema, target_schema)
    
    def suggest_data_transformations(self, data_path: str, target_schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Suggest data transformations to match a target schema or improve data quality.
        
        Args:
            data_path: Path to the data file
            target_schema: Optional target schema
            
        Returns:
            Suggested transformations
        """
        if not settings.ENABLE_AI_FEATURES or not self.is_initialized:
            return self._fallback_suggest_transformations(data_path, target_schema)
        
        try:
            # Read the data
            file_ext = os.path.splitext(data_path)[1].lower()
            
            if file_ext in ['.csv', '.xlsx', '.xls']:
                df = pd.read_csv(data_path) if file_ext == '.csv' else pd.read_excel(data_path)
                data_sample = df.head(10).to_dict(orient='records')
                column_info = {col: str(df[col].dtype) for col in df.columns}
            elif file_ext in ['.shp', '.geojson', '.json', '.gpkg']:
                gdf = gpd.read_file(data_path)
                data_sample = json.loads(gdf.head(10).to_json())
                column_info = {col: str(gdf[col].dtype) for col in gdf.columns if col != 'geometry'}
                if 'geometry' in gdf.columns:
                    column_info['geometry'] = 'geometry'
            else:
                return {
                    "error": f"Unsupported file format: {file_ext}"
                }
            
            # Prepare the prompt for the model
            prompt = self._create_transformation_prompt(data_sample, column_info, target_schema)
            
            # Generate transformation suggestions
            transformation_results = self._generate_text(prompt)
            
            # Parse the transformation results
            try:
                # Try to extract JSON from the response
                json_start = transformation_results.find('{')
                json_end = transformation_results.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = transformation_results[json_start:json_end]
                    transformations = json.loads(json_str)
                else:
                    # If no JSON found, create a simple result
                    transformations = {
                        "transformations": transformation_results.strip()
                    }
            except json.JSONDecodeError:
                transformations = {
                    "transformations": transformation_results.strip()
                }
            
            return transformations
        except Exception as e:
            logger.error(f"Error in AI transformation suggestions: {str(e)}")
            return self._fallback_suggest_transformations(data_path, target_schema)
    
    def _generate_text(self, prompt: str) -> str:
        """
        Generate text using the AI model.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text
        """
        try:
            # Tokenize the prompt
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            
            # Generate text
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    temperature=0.1,
                    top_p=0.95,
                    do_sample=True
                )
            
            # Decode the generated text
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract the response (remove the prompt)
            response = generated_text[len(prompt):].strip()
            
            return response
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return f"Error generating text: {str(e)}"
    
    def _create_validation_prompt(self, data_sample: List[Dict[str, Any]], column_info: Dict[str, str], schema: Optional[Dict[str, Any]]) -> str:
        """
        Create a prompt for data validation.
        
        Args:
            data_sample: Sample of the data
            column_info: Information about the columns
            schema: Optional schema to validate against
            
        Returns:
            Validation prompt
        """
        prompt = "You are a data validation expert. Analyze the following data sample and provide a detailed validation report.\n\n"
        
        # Add data sample
        prompt += "Data Sample:\n"
        prompt += json.dumps(data_sample, indent=2)
        prompt += "\n\n"
        
        # Add column information
        prompt += "Column Information:\n"
        prompt += json.dumps(column_info, indent=2)
        prompt += "\n\n"
        
        # Add schema if provided
        if schema:
            prompt += "Target Schema:\n"
            prompt += json.dumps(schema, indent=2)
            prompt += "\n\n"
            prompt += "Validate the data against the target schema and identify any issues or discrepancies.\n"
        else:
            prompt += "Analyze the data quality and identify any potential issues or anomalies.\n"
        
        # Request specific output format
        prompt += "Provide your analysis in JSON format with the following structure:\n"
        prompt += "{\n"
        prompt += '  "valid": true/false,\n'
        prompt += '  "issues": [{"column": "column_name", "issue": "description", "severity": "high/medium/low"}],\n'
        prompt += '  "recommendations": ["recommendation1", "recommendation2", ...],\n'
        prompt += '  "summary": "Overall assessment of the data quality"\n'
        prompt += "}\n\n"
        
        return prompt
    
    def _create_schema_matching_prompt(self, source_schema: Dict[str, Any], target_schema: Dict[str, Any]) -> str:
        """
        Create a prompt for schema matching.
        
        Args:
            source_schema: Source schema
            target_schema: Target schema
            
        Returns:
            Schema matching prompt
        """
        prompt = "You are a data integration expert. Match the source schema to the target schema.\n\n"
        
        # Add source schema
        prompt += "Source Schema:\n"
        prompt += json.dumps(source_schema, indent=2)
        prompt += "\n\n"
        
        # Add target schema
        prompt += "Target Schema:\n"
        prompt += json.dumps(target_schema, indent=2)
        prompt += "\n\n"
        
        # Request specific output format
        prompt += "Provide a mapping from source schema to target schema in JSON format with the following structure:\n"
        prompt += "{\n"
        prompt += '  "mapping": {\n'
        prompt += '    "source_field1": {"target_field": "target_field1", "transformation": "transformation_needed", "confidence": 0.9},\n'
        prompt += '    "source_field2": {"target_field": "target_field2", "transformation": null, "confidence": 1.0},\n'
        prompt += '    ...\n'
        prompt += '  },\n'
        prompt += '  "unmapped_source_fields": ["source_field3", ...],\n'
        prompt += '  "unmapped_target_fields": ["target_field3", ...],\n'
        prompt += '  "confidence": 0.85\n'
        prompt += "}\n\n"
        
        return prompt
    
    def _create_transformation_prompt(self, data_sample: List[Dict[str, Any]], column_info: Dict[str, str], target_schema: Optional[Dict[str, Any]]) -> str:
        """
        Create a prompt for suggesting data transformations.
        
        Args:
            data_sample: Sample of the data
            column_info: Information about the columns
            target_schema: Optional target schema
            
        Returns:
            Transformation prompt
        """
        prompt = "You are a data transformation expert. Suggest transformations for the following data.\n\n"
        
        # Add data sample
        prompt += "Data Sample:\n"
        prompt += json.dumps(data_sample, indent=2)
        prompt += "\n\n"
        
        # Add column information
        prompt += "Column Information:\n"
        prompt += json.dumps(column_info, indent=2)
        prompt += "\n\n"
        
        # Add target schema if provided
        if target_schema:
            prompt += "Target Schema:\n"
            prompt += json.dumps(target_schema, indent=2)
            prompt += "\n\n"
            prompt += "Suggest transformations to convert the data to match the target schema.\n"
        else:
            prompt += "Suggest transformations to improve the data quality and usability.\n"
        
        # Request specific output format
        prompt += "Provide your suggestions in JSON format with the following structure:\n"
        prompt += "{\n"
        prompt += '  "transformations": [\n'
        prompt += '    {"column": "column_name", "transformation": "description", "code": "python_code_example"},\n'
        prompt += '    ...\n'
        prompt += '  ],\n'
        prompt += '  "new_columns": [\n'
        prompt += '    {"name": "new_column_name", "derived_from": ["source_column1", ...], "transformation": "description", "code": "python_code_example"},\n'
        prompt += '    ...\n'
        prompt += '  ],\n'
        prompt += '  "recommendations": ["recommendation1", ...]\n'
        prompt += "}\n\n"
        
        return prompt
    
    def _fallback_validate_data(self, data_path: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fallback method for data validation when AI is not available.
        
        Args:
            data_path: Path to the data file
            schema: Optional schema to validate against
            
        Returns:
            Validation results
        """
        try:
            # Read the data
            file_ext = os.path.splitext(data_path)[1].lower()
            
            if file_ext in ['.csv', '.xlsx', '.xls']:
                df = pd.read_csv(data_path) if file_ext == '.csv' else pd.read_excel(data_path)
                
                # Basic validation
                issues = []
                
                # Check for missing values
                missing_values = df.isnull().sum()
                for column, count in missing_values.items():
                    if count > 0:
                        issues.append({
                            "column": column,
                            "issue": f"Contains {count} missing values",
                            "severity": "medium" if count / len(df) > 0.1 else "low"
                        })
                
                # Check for duplicate rows
                duplicate_count = df.duplicated().sum()
                if duplicate_count > 0:
                    issues.append({
                        "column": "entire_dataset",
                        "issue": f"Contains {duplicate_count} duplicate rows",
                        "severity": "medium"
                    })
                
                return {
                    "valid": len(issues) == 0,
                    "issues": issues,
                    "recommendations": ["Consider handling missing values", "Remove duplicate rows if not intended"],
                    "summary": f"Found {len(issues)} potential issues in the data"
                }
            
            elif file_ext in ['.shp', '.geojson', '.json', '.gpkg']:
                gdf = gpd.read_file(data_path)
                
                # Basic validation
                issues = []
                
                # Check for missing values
                missing_values = gdf.drop(columns=['geometry']).isnull().sum()
                for column, count in missing_values.items():
                    if count > 0:
                        issues.append({
                            "column": column,
                            "issue": f"Contains {count} missing values",
                            "severity": "medium" if count / len(gdf) > 0.1 else "low"
                        })
                
                # Check for invalid geometries
                invalid_geom_count = (~gdf.geometry.is_valid).sum()
                if invalid_geom_count > 0:
                    issues.append({
                        "column": "geometry",
                        "issue": f"Contains {invalid_geom_count} invalid geometries",
                        "severity": "high"
                    })
                
                return {
                    "valid": len(issues) == 0,
                    "issues": issues,
                    "recommendations": ["Consider handling missing values", "Fix invalid geometries"],
                    "summary": f"Found {len(issues)} potential issues in the data"
                }
            
            else:
                return {
                    "valid": False,
                    "issues": [{"column": "file_format", "issue": f"Unsupported file format: {file_ext}", "severity": "high"}],
                    "recommendations": ["Convert to a supported format (CSV, Excel, Shapefile, GeoJSON, GeoPackage)"],
                    "summary": "Unsupported file format"
                }
        
        except Exception as e:
            return {
                "valid": False,
                "issues": [{"column": "entire_dataset", "issue": f"Error validating data: {str(e)}", "severity": "high"}],
                "recommendations": ["Check file format and content"],
                "summary": f"Error validating data: {str(e)}"
            }
    
    def _fallback_match_schema(self, source_schema: Dict[str, Any], target_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback method for schema matching when AI is not available.
        
        Args:
            source_schema: Source schema
            target_schema: Target schema
            
        Returns:
            Schema mapping
        """
        # Simple name-based matching
        mapping = {}
        unmapped_source_fields = []
        unmapped_target_fields = list(target_schema.keys())
        
        for source_field, source_info in source_schema.items():
            # Try exact match
            if source_field in target_schema:
                mapping[source_field] = {
                    "target_field": source_field,
                    "transformation": None,
                    "confidence": 1.0
                }
                unmapped_target_fields.remove(source_field)
            # Try case-insensitive match
            elif source_field.lower() in [field.lower() for field in target_schema.keys()]:
                target_field = next(field for field in target_schema.keys() if field.lower() == source_field.lower())
                mapping[source_field] = {
                    "target_field": target_field,
                    "transformation": None,
                    "confidence": 0.9
                }
                unmapped_target_fields.remove(target_field)
            # Try substring match
            else:
                matches = []
                for target_field in target_schema.keys():
                    if source_field in target_field or target_field in source_field:
                        matches.append(target_field)
                
                if matches:
                    # Use the shortest match (likely the most specific)
                    target_field = min(matches, key=len)
                    mapping[source_field] = {
                        "target_field": target_field,
                        "transformation": None,
                        "confidence": 0.7
                    }
                    if target_field in unmapped_target_fields:
                        unmapped_target_fields.remove(target_field)
                else:
                    unmapped_source_fields.append(source_field)
        
        # Calculate overall confidence
        if not mapping:
            confidence = 0.0
        else:
            confidence = sum(m["confidence"] for m in mapping.values()) / len(mapping)
        
        return {
            "mapping": mapping,
            "unmapped_source_fields": unmapped_source_fields,
            "unmapped_target_fields": unmapped_target_fields,
            "confidence": confidence
        }
    
    def _fallback_suggest_transformations(self, data_path: str, target_schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fallback method for suggesting transformations when AI is not available.
        
        Args:
            data_path: Path to the data file
            target_schema: Optional target schema
            
        Returns:
            Suggested transformations
        """
        try:
            # Read the data
            file_ext = os.path.splitext(data_path)[1].lower()
            
            if file_ext in ['.csv', '.xlsx', '.xls']:
                df = pd.read_csv(data_path) if file_ext == '.csv' else pd.read_excel(data_path)
                
                # Basic transformation suggestions
                transformations = []
                
                # Check for missing values
                missing_values = df.isnull().sum()
                for column, count in missing_values.items():
                    if count > 0:
                        transformations.append({
                            "column": column,
                            "transformation": "Fill missing values",
                            "code": f"df['{column}'].fillna(df['{column}'].mean())  # For numeric columns\n# or\ndf['{column}'].fillna(df['{column}'].mode()[0])  # For categorical columns"
                        })
                
                # Check for duplicate rows
                duplicate_count = df.duplicated().sum()
                if duplicate_count > 0:
                    transformations.append({
                        "column": "entire_dataset",
                        "transformation": "Remove duplicate rows",
                        "code": "df.drop_duplicates(inplace=True)"
                    })
                
                return {
                    "transformations": transformations,
                    "new_columns": [],
                    "recommendations": ["Consider normalizing numeric columns", "Convert categorical columns to appropriate types"]
                }
            
            elif file_ext in ['.shp', '.geojson', '.json', '.gpkg']:
                gdf = gpd.read_file(data_path)
                
                # Basic transformation suggestions
                transformations = []
                
                # Check for missing values
                missing_values = gdf.drop(columns=['geometry']).isnull().sum()
                for column, count in missing_values.items():
                    if count > 0:
                        transformations.append({
                            "column": column,
                            "transformation": "Fill missing values",
                            "code": f"gdf['{column}'].fillna(gdf['{column}'].mean())  # For numeric columns\n# or\ngdf['{column}'].fillna(gdf['{column}'].mode()[0])  # For categorical columns"
                        })
                
                # Check for invalid geometries
                invalid_geom_count = (~gdf.geometry.is_valid).sum()
                if invalid_geom_count > 0:
                    transformations.append({
                        "column": "geometry",
                        "transformation": "Fix invalid geometries",
                        "code": "gdf['geometry'] = gdf.geometry.buffer(0)  # Simple fix for most issues"
                    })
                
                return {
                    "transformations": transformations,
                    "new_columns": [],
                    "recommendations": ["Consider reprojecting to an appropriate CRS", "Simplify geometries if needed"]
                }
            
            else:
                return {
                    "error": f"Unsupported file format: {file_ext}"
                }
        
        except Exception as e:
            return {
                "error": f"Error suggesting transformations: {str(e)}"
            }
