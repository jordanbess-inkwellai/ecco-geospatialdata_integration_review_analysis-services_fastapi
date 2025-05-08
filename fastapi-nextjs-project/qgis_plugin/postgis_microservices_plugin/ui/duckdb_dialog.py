import os
from typing import Dict, List, Any, Optional

from qgis.PyQt.QtCore import Qt, QSettings
from qgis.PyQt.QtGui import QIcon, QTextCursor
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTabWidget, QWidget, QFormLayout,
    QSpinBox, QCheckBox, QMessageBox, QGroupBox, QRadioButton,
    QDialogButtonBox, QFileDialog, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QToolButton,
    QMenu, QAction
)
from qgis.core import (
    QgsMessageLog, Qgis, QgsVectorLayer, QgsProject,
    QgsTask, QgsApplication
)

class DuckDBDialog(QDialog):
    """Dialog for DuckDB operations."""
    
    def __init__(self, parent, api_client, iface):
        """Initialize the dialog.
        
        Args:
            parent: Parent widget
            api_client: API client instance
            iface: QGIS interface
        """
        super(DuckDBDialog, self).__init__(parent)
        
        self.api_client = api_client
        self.iface = iface
        self.settings = QSettings()
        
        self.setWindowTitle("DuckDB Operations")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        self.current_db = None
        self.query_results = None
        
        self.setup_ui()
        self.load_recent_databases()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        # Database selection
        db_layout = QHBoxLayout()
        db_layout.addWidget(QLabel("Database:"))
        
        self.db_combo = QComboBox()
        self.db_combo.setEditable(True)
        self.db_combo.currentTextChanged.connect(self.on_database_changed)
        db_layout.addWidget(self.db_combo, 1)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_database)
        db_layout.addWidget(self.browse_btn)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_database)
        db_layout.addWidget(self.connect_btn)
        
        layout.addLayout(db_layout)
        
        # Main splitter
        splitter = QSplitter(Qt.Vertical)
        
        # Query editor
        editor_group = QGroupBox("SQL Query")
        editor_layout = QVBoxLayout()
        
        self.query_edit = QTextEdit()
        self.query_edit.setPlaceholderText("Enter SQL query here...")
        editor_layout.addWidget(self.query_edit)
        
        query_buttons = QHBoxLayout()
        
        self.run_btn = QPushButton("Run Query")
        self.run_btn.clicked.connect(self.run_query)
        query_buttons.addWidget(self.run_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_query)
        query_buttons.addWidget(self.clear_btn)
        
        self.load_btn = QPushButton("Load Query")
        self.load_btn.clicked.connect(self.load_query)
        query_buttons.addWidget(self.load_btn)
        
        self.save_btn = QPushButton("Save Query")
        self.save_btn.clicked.connect(self.save_query)
        query_buttons.addWidget(self.save_btn)
        
        editor_layout.addLayout(query_buttons)
        editor_group.setLayout(editor_layout)
        
        # Results
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        
        self.results_tabs = QTabWidget()
        
        # Data tab
        self.data_table = QTableWidget()
        self.results_tabs.addTab(self.data_table, "Data")
        
        # Messages tab
        self.messages_edit = QTextEdit()
        self.messages_edit.setReadOnly(True)
        self.results_tabs.addTab(self.messages_edit, "Messages")
        
        results_layout.addWidget(self.results_tabs)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("Export Results")
        self.export_btn.clicked.connect(self.show_export_menu)
        export_layout.addWidget(self.export_btn)
        
        self.add_to_map_btn = QPushButton("Add to Map")
        self.add_to_map_btn.clicked.connect(self.add_to_map)
        export_layout.addWidget(self.add_to_map_btn)
        
        export_layout.addStretch()
        
        results_layout.addLayout(export_layout)
        results_group.setLayout(results_layout)
        
        # Add widgets to splitter
        splitter.addWidget(editor_group)
        splitter.addWidget(results_group)
        splitter.setSizes([200, 400])
        
        layout.addWidget(splitter, 1)
        
        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Set up export menu
        self.export_menu = QMenu(self)
        self.export_csv_action = QAction("Export as CSV", self)
        self.export_csv_action.triggered.connect(lambda: self.export_results("csv"))
        self.export_menu.addAction(self.export_csv_action)
        
        self.export_geojson_action = QAction("Export as GeoJSON", self)
        self.export_geojson_action.triggered.connect(lambda: self.export_results("geojson"))
        self.export_menu.addAction(self.export_geojson_action)
        
        self.export_shapefile_action = QAction("Export as Shapefile", self)
        self.export_shapefile_action.triggered.connect(lambda: self.export_results("shapefile"))
        self.export_menu.addAction(self.export_shapefile_action)
        
        self.export_geoparquet_action = QAction("Export as GeoParquet", self)
        self.export_geoparquet_action.triggered.connect(lambda: self.export_results("geoparquet"))
        self.export_menu.addAction(self.export_geoparquet_action)
    
    def load_recent_databases(self):
        """Load recent databases from settings."""
        recent_dbs = self.settings.value('PostGISMicroservices/recent_duckdb', [])
        if isinstance(recent_dbs, list):
            self.db_combo.clear()
            for db in recent_dbs:
                self.db_combo.addItem(db)
    
    def save_recent_databases(self):
        """Save recent databases to settings."""
        current_db = self.db_combo.currentText()
        if not current_db:
            return
        
        recent_dbs = self.settings.value('PostGISMicroservices/recent_duckdb', [])
        if not isinstance(recent_dbs, list):
            recent_dbs = []
        
        # Add current DB to the list if not already present
        if current_db not in recent_dbs:
            recent_dbs.insert(0, current_db)
            
            # Limit to 10 recent databases
            if len(recent_dbs) > 10:
                recent_dbs = recent_dbs[:10]
            
            self.settings.setValue('PostGISMicroservices/recent_duckdb', recent_dbs)
    
    def on_database_changed(self, text):
        """Handle database selection change."""
        self.current_db = text
    
    def browse_database(self):
        """Browse for a DuckDB file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select DuckDB File", "", "DuckDB Files (*.duckdb);;All Files (*.*)"
        )
        
        if file_path:
            self.db_combo.setCurrentText(file_path)
            self.current_db = file_path
    
    def connect_database(self):
        """Connect to the selected database."""
        if not self.current_db:
            QMessageBox.warning(self, "Warning", "Please select a database file.")
            return
        
        self.set_status(f"Connecting to {self.current_db}...")
        
        try:
            # Test connection with a simple query
            db_name = os.path.basename(self.current_db)
            result = self.api_client.query_duckdb(
                db_name=db_name,
                query="SELECT 1 AS test"
            )
            
            if "data" in result:
                self.set_status(f"Connected to {self.current_db}")
                self.save_recent_databases()
                
                # Show tables
                self.query_edit.setText("SELECT name FROM sqlite_master WHERE type='table';")
                self.run_query()
            else:
                self.set_status(f"Connection failed: {result.get('detail', 'Unknown error')}")
        
        except Exception as e:
            self.set_status(f"Error connecting to database: {str(e)}")
            QgsMessageLog.logMessage(f"Error connecting to database: {str(e)}", "PostGIS Microservices", Qgis.Critical)
    
    def run_query(self):
        """Run the current SQL query."""
        if not self.current_db:
            QMessageBox.warning(self, "Warning", "Please connect to a database first.")
            return
        
        query = self.query_edit.toPlainText().strip()
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a SQL query.")
            return
        
        self.set_status(f"Running query...")
        
        try:
            # Run query
            db_name = os.path.basename(self.current_db)
            result = self.api_client.query_duckdb(
                db_name=db_name,
                query=query
            )
            
            # Store results
            self.query_results = result
            
            # Update data table
            self.update_results_table(result)
            
            # Update messages
            self.messages_edit.clear()
            self.messages_edit.append(f"Query executed successfully.")
            self.messages_edit.append(f"Rows returned: {len(result.get('data', []))}")
            
            # Switch to data tab
            self.results_tabs.setCurrentIndex(0)
            
            self.set_status(f"Query completed. {len(result.get('data', []))} rows returned.")
        
        except Exception as e:
            self.set_status(f"Error running query: {str(e)}")
            self.messages_edit.clear()
            self.messages_edit.append(f"Error running query: {str(e)}")
            self.results_tabs.setCurrentIndex(1)
            QgsMessageLog.logMessage(f"Error running query: {str(e)}", "PostGIS Microservices", Qgis.Critical)
    
    def update_results_table(self, result):
        """Update the results table with query results.
        
        Args:
            result: Query result dictionary
        """
        self.data_table.clear()
        
        # Get columns and data
        columns = result.get('columns', [])
        data = result.get('data', [])
        
        if not columns or not data:
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            return
        
        # Set up table
        self.data_table.setRowCount(len(data))
        self.data_table.setColumnCount(len(columns))
        self.data_table.setHorizontalHeaderLabels(columns)
        
        # Fill data
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value) if value is not None else "NULL")
                self.data_table.setItem(row_idx, col_idx, item)
        
        # Resize columns to content
        self.data_table.resizeColumnsToContents()
    
    def clear_query(self):
        """Clear the query editor."""
        self.query_edit.clear()
    
    def load_query(self):
        """Load a SQL query from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load SQL Query", "", "SQL Files (*.sql);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    query = f.read()
                
                self.query_edit.setText(query)
                self.set_status(f"Loaded query from {file_path}")
            
            except Exception as e:
                self.set_status(f"Error loading query: {str(e)}")
                QgsMessageLog.logMessage(f"Error loading query: {str(e)}", "PostGIS Microservices", Qgis.Critical)
    
    def save_query(self):
        """Save the current SQL query to file."""
        query = self.query_edit.toPlainText().strip()
        if not query:
            QMessageBox.warning(self, "Warning", "No query to save.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save SQL Query", "", "SQL Files (*.sql);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(query)
                
                self.set_status(f"Saved query to {file_path}")
            
            except Exception as e:
                self.set_status(f"Error saving query: {str(e)}")
                QgsMessageLog.logMessage(f"Error saving query: {str(e)}", "PostGIS Microservices", Qgis.Critical)
    
    def show_export_menu(self):
        """Show the export menu."""
        if not self.query_results or not self.query_results.get('data'):
            QMessageBox.warning(self, "Warning", "No results to export.")
            return
        
        # Check if results have geometry
        columns = self.query_results.get('columns', [])
        has_geometry = any(col.lower() in ['geometry', 'geom', 'shape', 'wkt', 'the_geom'] for col in columns)
        
        # Enable/disable geometry-specific formats
        self.export_geojson_action.setEnabled(has_geometry)
        self.export_shapefile_action.setEnabled(has_geometry)
        self.export_geoparquet_action.setEnabled(has_geometry)
        
        # Show menu at button position
        self.export_menu.exec_(self.export_btn.mapToGlobal(self.export_btn.rect().bottomLeft()))
    
    def export_results(self, format_type):
        """Export query results to file.
        
        Args:
            format_type: Export format (csv, geojson, shapefile, geoparquet)
        """
        if not self.query_results or not self.query_results.get('data'):
            QMessageBox.warning(self, "Warning", "No results to export.")
            return
        
        # Determine file extension and filter
        if format_type == 'csv':
            extension = 'csv'
            filter_str = "CSV Files (*.csv);;All Files (*.*)"
        elif format_type == 'geojson':
            extension = 'geojson'
            filter_str = "GeoJSON Files (*.geojson);;All Files (*.*)"
        elif format_type == 'shapefile':
            extension = 'shp'
            filter_str = "Shapefile (*.shp);;All Files (*.*)"
        elif format_type == 'geoparquet':
            extension = 'parquet'
            filter_str = "Parquet Files (*.parquet);;All Files (*.*)"
        else:
            QMessageBox.warning(self, "Warning", f"Unsupported export format: {format_type}")
            return
        
        # Get save file path
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Export as {format_type.upper()}", "", filter_str
        )
        
        if not file_path:
            return
        
        self.set_status(f"Exporting to {file_path}...")
        
        try:
            # Run query with export
            db_name = os.path.basename(self.current_db)
            query = self.query_edit.toPlainText().strip()
            
            result = self.api_client.query_duckdb(
                db_name=db_name,
                query=query,
                export_format=format_type,
                export_path=file_path
            )
            
            if result.get('status') == 'success':
                self.set_status(f"Exported to {file_path}")
                
                # Ask if user wants to add to map
                if format_type in ['geojson', 'shapefile', 'geoparquet']:
                    reply = QMessageBox.question(
                        self, "Add to Map",
                        "Do you want to add the exported file to the map?",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                    )
                    
                    if reply == QMessageBox.Yes:
                        self.add_layer_to_map(file_path, format_type)
            else:
                self.set_status(f"Export failed: {result.get('detail', 'Unknown error')}")
        
        except Exception as e:
            self.set_status(f"Error exporting results: {str(e)}")
            QgsMessageLog.logMessage(f"Error exporting results: {str(e)}", "PostGIS Microservices", Qgis.Critical)
    
    def add_to_map(self):
        """Add query results directly to the map."""
        if not self.query_results or not self.query_results.get('data'):
            QMessageBox.warning(self, "Warning", "No results to add to map.")
            return
        
        # Check if results have geometry
        columns = self.query_results.get('columns', [])
        geom_column = None
        for col in columns:
            if col.lower() in ['geometry', 'geom', 'shape', 'wkt', 'the_geom']:
                geom_column = col
                break
        
        if not geom_column:
            QMessageBox.warning(self, "Warning", "Results do not contain geometry column.")
            return
        
        # Export to temporary GeoJSON
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(suffix='.geojson', delete=False)
        temp_file.close()
        
        self.set_status(f"Exporting to temporary file...")
        
        try:
            # Run query with export
            db_name = os.path.basename(self.current_db)
            query = self.query_edit.toPlainText().strip()
            
            result = self.api_client.query_duckdb(
                db_name=db_name,
                query=query,
                export_format='geojson',
                export_path=temp_file.name
            )
            
            if result.get('status') == 'success':
                self.set_status(f"Adding to map...")
                self.add_layer_to_map(temp_file.name, 'geojson')
            else:
                self.set_status(f"Export failed: {result.get('detail', 'Unknown error')}")
        
        except Exception as e:
            self.set_status(f"Error adding to map: {str(e)}")
            QgsMessageLog.logMessage(f"Error adding to map: {str(e)}", "PostGIS Microservices", Qgis.Critical)
    
    def add_layer_to_map(self, file_path, format_type):
        """Add a layer to the map.
        
        Args:
            file_path: Path to the file
            format_type: File format
        """
        layer_name = os.path.basename(file_path)
        
        if format_type == 'geojson':
            layer = QgsVectorLayer(file_path, layer_name, "ogr")
        elif format_type == 'shapefile':
            layer = QgsVectorLayer(file_path, layer_name, "ogr")
        elif format_type == 'geoparquet':
            # Use GDAL/OGR provider for GeoParquet
            layer = QgsVectorLayer(f"GPKG:{file_path}", layer_name, "ogr")
        else:
            QMessageBox.warning(self, "Warning", f"Unsupported layer format: {format_type}")
            return
        
        if layer.isValid():
            QgsProject.instance().addMapLayer(layer)
            self.set_status(f"Added layer to map: {layer_name}")
        else:
            self.set_status(f"Error adding layer to map: Invalid layer")
            QgsMessageLog.logMessage(f"Error adding layer to map: Invalid layer", "PostGIS Microservices", Qgis.Critical)
    
    def set_status(self, message):
        """Set status message."""
        self.status_label.setText(message)
        QgsMessageLog.logMessage(message, "PostGIS Microservices", Qgis.Info)
