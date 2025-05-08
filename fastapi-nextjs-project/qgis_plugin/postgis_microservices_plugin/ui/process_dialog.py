import os
import json
from typing import Dict, List, Any, Optional

from qgis.PyQt.QtCore import Qt, QSettings
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTabWidget, QWidget, QFormLayout,
    QSpinBox, QDoubleSpinBox, QCheckBox, QMessageBox, QGroupBox, 
    QDialogButtonBox, QTextEdit, QTreeWidget, QTreeWidgetItem,
    QSplitter, QStackedWidget, QListWidget, QListWidgetItem,
    QProgressBar
)
from qgis.core import (
    QgsMessageLog, Qgis, QgsVectorLayer, QgsProject,
    QgsGeometry, QgsFeature, QgsCoordinateReferenceSystem,
    QgsCoordinateTransform, QgsRectangle
)
from qgis.gui import QgsMapLayerComboBox, QgsMapLayerProxyModel

class ProcessDialog(QDialog):
    """Dialog for discovering and executing OGC API Processes."""
    
    def __init__(self, parent, api_client, iface):
        """Initialize the dialog.
        
        Args:
            parent: Parent widget
            api_client: API client instance
            iface: QGIS interface
        """
        super(ProcessDialog, self).__init__(parent)
        
        self.api_client = api_client
        self.iface = iface
        self.settings = QSettings()
        
        self.setWindowTitle("OGC API Processes")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        self.processes = []
        self.selected_process = None
        self.input_widgets = {}
        
        self.setup_ui()
        self.load_processes()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Process list panel
        process_panel = QWidget()
        process_layout = QVBoxLayout(process_panel)
        process_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.filter_processes)
        search_layout.addWidget(self.search_edit)
        process_layout.addLayout(search_layout)
        
        # Process list
        self.process_list = QListWidget()
        self.process_list.itemClicked.connect(self.on_process_selected)
        process_layout.addWidget(self.process_list)
        
        # Process details panel
        details_panel = QWidget()
        details_layout = QVBoxLayout(details_panel)
        details_layout.setContentsMargins(0, 0, 0, 0)
        
        # Process info
        self.info_group = QGroupBox("Process Information")
        info_layout = QVBoxLayout()
        self.info_edit = QTextEdit()
        self.info_edit.setReadOnly(True)
        info_layout.addWidget(self.info_edit)
        self.info_group.setLayout(info_layout)
        details_layout.addWidget(self.info_group)
        
        # Process inputs
        self.inputs_group = QGroupBox("Process Inputs")
        self.inputs_layout = QFormLayout()
        self.inputs_widget = QWidget()
        self.inputs_widget.setLayout(self.inputs_layout)
        
        inputs_scroll_layout = QVBoxLayout()
        inputs_scroll_layout.addWidget(self.inputs_widget)
        inputs_scroll_layout.addStretch()
        
        self.inputs_group.setLayout(inputs_scroll_layout)
        details_layout.addWidget(self.inputs_group)
        
        # Execute button
        execute_layout = QHBoxLayout()
        self.execute_btn = QPushButton("Execute Process")
        self.execute_btn.clicked.connect(self.execute_process)
        execute_layout.addStretch()
        execute_layout.addWidget(self.execute_btn)
        details_layout.addLayout(execute_layout)
        
        # Add panels to splitter
        splitter.addWidget(process_panel)
        splitter.addWidget(details_panel)
        splitter.setSizes([200, 600])
        
        layout.addWidget(splitter, 1)
        
        # Results panel
        self.results_group = QGroupBox("Process Results")
        results_layout = QVBoxLayout()
        
        self.results_tabs = QTabWidget()
        
        # Text results tab
        self.text_results = QTextEdit()
        self.text_results.setReadOnly(True)
        self.results_tabs.addTab(self.text_results, "Text Results")
        
        # Map results tab
        self.map_results = QTextEdit()
        self.map_results.setReadOnly(True)
        self.results_tabs.addTab(self.map_results, "Map Results")
        
        results_layout.addWidget(self.results_tabs)
        
        # Add to map button
        map_layout = QHBoxLayout()
        self.add_to_map_btn = QPushButton("Add to Map")
        self.add_to_map_btn.clicked.connect(self.add_results_to_map)
        map_layout.addStretch()
        map_layout.addWidget(self.add_to_map_btn)
        results_layout.addLayout(map_layout)
        
        self.results_group.setLayout(results_layout)
        layout.addWidget(self.results_group)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        layout.addLayout(status_layout)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def load_processes(self):
        """Load processes from the API."""
        self.set_status("Loading processes...")
        self.progress_bar.setVisible(True)
        
        try:
            # Get processes
            self.processes = self.api_client.get_processes().get('processes', [])
            
            # Update list widget
            self.process_list.clear()
            for process in self.processes:
                item = QListWidgetItem(process.get('title', process.get('id', 'Unknown')))
                item.setData(Qt.UserRole, process)
                self.process_list.addItem(item)
            
            self.set_status(f"Loaded {len(self.processes)} processes")
            self.progress_bar.setVisible(False)
        
        except Exception as e:
            self.set_status(f"Error loading processes: {str(e)}")
            self.progress_bar.setVisible(False)
            QgsMessageLog.logMessage(f"Error loading processes: {str(e)}", "PostGIS Microservices", Qgis.Critical)
    
    def filter_processes(self, text):
        """Filter processes by search text."""
        for i in range(self.process_list.count()):
            item = self.process_list.item(i)
            process = item.data(Qt.UserRole)
            
            # Check if text is in title, id, or description
            title = process.get('title', '').lower()
            process_id = process.get('id', '').lower()
            description = process.get('description', '').lower()
            
            if (text.lower() in title or 
                text.lower() in process_id or 
                text.lower() in description):
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def on_process_selected(self, item):
        """Handle process selection."""
        process_id = item.data(Qt.UserRole).get('id')
        
        self.set_status(f"Loading process details: {process_id}")
        self.progress_bar.setVisible(True)
        
        try:
            # Get process details
            self.selected_process = self.api_client.get_process(process_id)
            
            # Update info panel
            self.update_info_panel()
            
            # Update inputs panel
            self.update_inputs_panel()
            
            self.set_status(f"Loaded process details: {process_id}")
            self.progress_bar.setVisible(False)
        
        except Exception as e:
            self.set_status(f"Error loading process details: {str(e)}")
            self.progress_bar.setVisible(False)
            QgsMessageLog.logMessage(f"Error loading process details: {str(e)}", "PostGIS Microservices", Qgis.Critical)
    
    def update_info_panel(self):
        """Update the information panel with process details."""
        if not self.selected_process:
            return
        
        # Clear the info panel
        self.info_edit.clear()
        
        # Add process information
        self.info_edit.append(f"<h2>{self.selected_process.get('title', 'Unnamed Process')}</h2>")
        self.info_edit.append(f"<p><b>ID:</b> {self.selected_process.get('id', 'Unknown')}</p>")
        
        description = self.selected_process.get('description', '')
        if description:
            self.info_edit.append(f"<p>{description}</p>")
        
        # Add input information
        inputs = self.selected_process.get('inputs', {})
        if inputs:
            self.info_edit.append("<h3>Inputs</h3>")
            self.info_edit.append("<ul>")
            for name, input_def in inputs.items():
                required = input_def.get('required', False)
                self.info_edit.append(f"<li><b>{name}</b>{' (required)' if required else ''}: {input_def.get('description', '')}</li>")
            self.info_edit.append("</ul>")
        
        # Add output information
        outputs = self.selected_process.get('outputs', {})
        if outputs:
            self.info_edit.append("<h3>Outputs</h3>")
            self.info_edit.append("<ul>")
            for name, output_def in outputs.items():
                self.info_edit.append(f"<li><b>{name}</b>: {output_def.get('description', '')}</li>")
            self.info_edit.append("</ul>")
        
        # Add examples if available
        examples = self.selected_process.get('examples', [])
        if examples:
            self.info_edit.append("<h3>Examples</h3>")
            for example in examples:
                self.info_edit.append(f"<p><b>{example.get('title', 'Example')}:</b></p>")
                self.info_edit.append("<pre>" + json.dumps(example.get('inputs', {}), indent=2) + "</pre>")
    
    def update_inputs_panel(self):
        """Update the inputs panel with form fields for process inputs."""
        if not self.selected_process:
            return
        
        # Clear the inputs layout
        while self.inputs_layout.count():
            item = self.inputs_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Clear input widgets dictionary
        self.input_widgets = {}
        
        # Add input fields
        inputs = self.selected_process.get('inputs', {})
        for name, input_def in inputs.items():
            title = input_def.get('title', name)
            required = input_def.get('required', False)
            schema = input_def.get('schema', {})
            default = input_def.get('default')
            
            # Create label with required indicator
            label_text = f"{title}{'*' if required else ''}"
            
            # Create appropriate widget based on schema
            schema_type = schema.get('type', 'string')
            
            if schema_type == 'string':
                if 'enum' in schema:
                    # Create dropdown for enum
                    widget = QComboBox()
                    for option in schema['enum']:
                        widget.addItem(option)
                    if default:
                        index = widget.findText(default)
                        if index >= 0:
                            widget.setCurrentIndex(index)
                else:
                    # Create text field
                    widget = QLineEdit()
                    if default:
                        widget.setText(default)
            elif schema_type == 'number' or schema_type == 'integer':
                # Create number spinner
                if schema_type == 'number':
                    widget = QDoubleSpinBox()
                    widget.setDecimals(6)
                else:
                    widget = QSpinBox()
                
                # Set range if specified
                if 'minimum' in schema:
                    widget.setMinimum(schema['minimum'])
                else:
                    widget.setMinimum(-1000000)
                
                if 'maximum' in schema:
                    widget.setMaximum(schema['maximum'])
                else:
                    widget.setMaximum(1000000)
                
                if default is not None:
                    widget.setValue(default)
            elif schema_type == 'boolean':
                # Create checkbox
                widget = QCheckBox()
                if default is not None:
                    widget.setChecked(default)
            elif schema_type == 'array':
                # Create text field for now (could be improved)
                widget = QLineEdit()
                if default:
                    widget.setText(json.dumps(default))
            elif schema_type == 'object':
                # For geometry objects, add a layer selector
                if name.lower() in ['geometry', 'geometry_a', 'geometry_b', 'point', 'start_point', 'end_point']:
                    widget = QgsMapLayerComboBox()
                    widget.setFilters(QgsMapLayerProxyModel.VectorLayer)
                else:
                    # Create text field for JSON input
                    widget = QTextEdit()
                    widget.setMaximumHeight(100)
                    if default:
                        widget.setText(json.dumps(default, indent=2))
            else:
                # Default to text field
                widget = QLineEdit()
                if default:
                    widget.setText(str(default))
            
            # Add to layout
            self.inputs_layout.addRow(label_text, widget)
            
            # Store widget reference
            self.input_widgets[name] = (widget, schema_type)
    
    def get_input_values(self):
        """Get input values from the form fields."""
        inputs = {}
        
        for name, (widget, schema_type) in self.input_widgets.items():
            if schema_type == 'string':
                if isinstance(widget, QComboBox):
                    inputs[name] = widget.currentText()
                else:
                    inputs[name] = widget.text()
            elif schema_type == 'number' or schema_type == 'integer':
                inputs[name] = widget.value()
            elif schema_type == 'boolean':
                inputs[name] = widget.isChecked()
            elif schema_type == 'array':
                try:
                    inputs[name] = json.loads(widget.text())
                except:
                    # If not valid JSON, treat as comma-separated list
                    inputs[name] = [item.strip() for item in widget.text().split(',')]
            elif schema_type == 'object':
                if isinstance(widget, QgsMapLayerComboBox):
                    # Get geometry from selected layer
                    layer = widget.currentLayer()
                    if layer:
                        # Get the layer's CRS
                        layer_crs = layer.crs()
                        
                        # Get the canvas CRS
                        canvas_crs = self.iface.mapCanvas().mapSettings().destinationCrs()
                        
                        # Create a coordinate transform if needed
                        transform = QgsCoordinateTransform(
                            layer_crs, 
                            QgsCoordinateReferenceSystem("EPSG:4326"), 
                            QgsProject.instance()
                        )
                        
                        # Get the selected features or the extent
                        selected_features = layer.selectedFeatures()
                        
                        if selected_features:
                            # Use the first selected feature
                            feature = selected_features[0]
                            geom = feature.geometry()
                            
                            # Transform to EPSG:4326 if needed
                            if layer_crs.authid() != "EPSG:4326":
                                geom.transform(transform)
                            
                            # Convert to GeoJSON
                            inputs[name] = json.loads(geom.asJson())
                        else:
                            # Use the layer extent
                            extent = layer.extent()
                            
                            # Transform to EPSG:4326 if needed
                            if layer_crs.authid() != "EPSG:4326":
                                extent = transform.transformBoundingBox(extent)
                            
                            # Create a polygon from the extent
                            inputs[name] = {
                                "type": "Polygon",
                                "coordinates": [[
                                    [extent.xMinimum(), extent.yMinimum()],
                                    [extent.xMaximum(), extent.yMinimum()],
                                    [extent.xMaximum(), extent.yMaximum()],
                                    [extent.xMinimum(), extent.yMaximum()],
                                    [extent.xMinimum(), extent.yMinimum()]
                                ]]
                            }
                else:
                    try:
                        inputs[name] = json.loads(widget.toPlainText())
                    except:
                        # If not valid JSON, use as is
                        inputs[name] = widget.toPlainText()
        
        return inputs
    
    def execute_process(self):
        """Execute the selected process with the input values."""
        if not self.selected_process:
            return
        
        # Get process ID
        process_id = self.selected_process.get('id')
        
        # Get input values
        inputs = self.get_input_values()
        
        # Validate required inputs
        process_inputs = self.selected_process.get('inputs', {})
        missing_inputs = []
        
        for name, input_def in process_inputs.items():
            if input_def.get('required', False) and (name not in inputs or inputs[name] is None):
                missing_inputs.append(name)
        
        if missing_inputs:
            QMessageBox.warning(
                self,
                "Missing Inputs",
                f"The following required inputs are missing: {', '.join(missing_inputs)}"
            )
            return
        
        self.set_status(f"Executing process: {process_id}")
        self.progress_bar.setVisible(True)
        
        try:
            # Execute process
            result = self.api_client.execute_process(process_id, inputs)
            
            # Display results
            self.display_results(result)
            
            self.set_status(f"Process executed successfully: {process_id}")
            self.progress_bar.setVisible(False)
        
        except Exception as e:
            self.set_status(f"Error executing process: {str(e)}")
            self.progress_bar.setVisible(False)
            QgsMessageLog.logMessage(f"Error executing process: {str(e)}", "PostGIS Microservices", Qgis.Critical)
    
    def display_results(self, result):
        """Display process results."""
        # Clear result panels
        self.text_results.clear()
        self.map_results.clear()
        
        # Store result for later use
        self.process_result = result
        
        # Display as formatted JSON
        self.text_results.setText(json.dumps(result, indent=2))
        
        # Check if result contains GeoJSON
        if self.contains_geojson(result):
            self.map_results.setText("Result contains geographic data that can be added to the map.")
            self.add_to_map_btn.setEnabled(True)
        else:
            self.map_results.setText("Result does not contain geographic data.")
            self.add_to_map_btn.setEnabled(False)
    
    def contains_geojson(self, obj):
        """Check if an object contains GeoJSON data."""
        if isinstance(obj, dict):
            # Check if this is a GeoJSON object
            if 'type' in obj and 'coordinates' in obj:
                return True
            
            # Check if this is a GeoJSON FeatureCollection
            if obj.get('type') == 'FeatureCollection' and 'features' in obj:
                return True
            
            # Check if this is a GeoJSON Feature
            if obj.get('type') == 'Feature' and 'geometry' in obj:
                return True
            
            # Recursively check all values
            for value in obj.values():
                if self.contains_geojson(value):
                    return True
        
        elif isinstance(obj, list):
            # Recursively check all items
            for item in obj:
                if self.contains_geojson(item):
                    return True
        
        return False
    
    def add_results_to_map(self):
        """Add process results to the map."""
        if not hasattr(self, 'process_result') or not self.process_result:
            return
        
        # Extract GeoJSON from result
        geojson = self.extract_geojson(self.process_result)
        
        if not geojson:
            QMessageBox.warning(self, "No GeoJSON", "Could not extract GeoJSON from the result.")
            return
        
        # Create a temporary file
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(suffix='.geojson', delete=False)
        temp_file.close()
        
        # Write GeoJSON to file
        with open(temp_file.name, 'w') as f:
            json.dump(geojson, f)
        
        # Add to map
        layer_name = f"Process Result: {self.selected_process.get('title', 'Unnamed')}"
        layer = QgsVectorLayer(temp_file.name, layer_name, "ogr")
        
        if layer.isValid():
            QgsProject.instance().addMapLayer(layer)
            self.set_status(f"Added result to map as layer: {layer_name}")
        else:
            QMessageBox.warning(self, "Invalid Layer", "Could not create a valid layer from the result.")
            self.set_status("Failed to add result to map")
    
    def extract_geojson(self, obj):
        """Extract GeoJSON from a result object."""
        if isinstance(obj, dict):
            # Check if this is a GeoJSON object
            if 'type' in obj and 'coordinates' in obj:
                return obj
            
            # Check if this is a GeoJSON FeatureCollection
            if obj.get('type') == 'FeatureCollection' and 'features' in obj:
                return obj
            
            # Check if this is a GeoJSON Feature
            if obj.get('type') == 'Feature' and 'geometry' in obj:
                return obj
            
            # Check for result key
            if 'result' in obj:
                return self.extract_geojson(obj['result'])
            
            # Check for specific keys that might contain GeoJSON
            for key in ['geometry', 'geojson', 'features', 'buffered_geometry', 'intersection_geometry',
                       'convex_hull', 'simplified_geometry', 'voronoi_polygons', 'contours', 'path', 'service_area']:
                if key in obj:
                    extracted = self.extract_geojson(obj[key])
                    if extracted:
                        return extracted
            
            # Recursively check all values
            for value in obj.values():
                extracted = self.extract_geojson(value)
                if extracted:
                    return extracted
        
        elif isinstance(obj, list):
            # If this is a list of features, wrap in a FeatureCollection
            if all(isinstance(item, dict) and item.get('type') == 'Feature' for item in obj):
                return {
                    "type": "FeatureCollection",
                    "features": obj
                }
            
            # Recursively check all items
            for item in obj:
                extracted = self.extract_geojson(item)
                if extracted:
                    return extracted
        
        return None
    
    def set_status(self, message):
        """Set status message."""
        self.status_label.setText(message)
        QgsMessageLog.logMessage(message, "PostGIS Microservices", Qgis.Info)
