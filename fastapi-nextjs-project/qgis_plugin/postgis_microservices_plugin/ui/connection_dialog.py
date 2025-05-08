import os
from typing import Dict, List, Any, Optional

from qgis.PyQt.QtCore import Qt, QSettings
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTabWidget, QWidget, QFormLayout,
    QSpinBox, QCheckBox, QMessageBox, QGroupBox, QRadioButton,
    QDialogButtonBox, QFileDialog, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from qgis.core import QgsMessageLog, Qgis

class ConnectionDialog(QDialog):
    """Dialog for managing database connections."""
    
    def __init__(self, parent, api_client):
        """Initialize the dialog.
        
        Args:
            parent: Parent widget
            api_client: API client instance
        """
        super(ConnectionDialog, self).__init__(parent)
        
        self.api_client = api_client
        self.settings = QSettings()
        
        self.setWindowTitle("Database Connection")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.setup_ui()
        self.load_saved_connections()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        # Connection type selection
        type_group = QGroupBox("Connection Type")
        type_layout = QHBoxLayout()
        
        self.postgres_radio = QRadioButton("PostgreSQL/PostGIS")
        self.postgres_radio.setChecked(True)
        self.postgres_radio.toggled.connect(self.on_connection_type_changed)
        
        self.duckdb_radio = QRadioButton("DuckDB")
        self.duckdb_radio.toggled.connect(self.on_connection_type_changed)
        
        type_layout.addWidget(self.postgres_radio)
        type_layout.addWidget(self.duckdb_radio)
        type_group.setLayout(type_layout)
        
        layout.addWidget(type_group)
        
        # Saved connections
        saved_group = QGroupBox("Saved Connections")
        saved_layout = QHBoxLayout()
        
        self.connections_combo = QComboBox()
        self.connections_combo.currentIndexChanged.connect(self.on_connection_selected)
        
        self.load_btn = QPushButton("Load")
        self.load_btn.clicked.connect(self.load_connection)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_connection)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_connection)
        
        saved_layout.addWidget(QLabel("Connection:"))
        saved_layout.addWidget(self.connections_combo, 1)
        saved_layout.addWidget(self.load_btn)
        saved_layout.addWidget(self.save_btn)
        saved_layout.addWidget(self.delete_btn)
        
        saved_group.setLayout(saved_layout)
        layout.addWidget(saved_group)
        
        # Connection parameters
        self.stack_widget = QTabWidget()
        
        # PostgreSQL connection
        pg_widget = QWidget()
        pg_layout = QFormLayout()
        
        self.pg_name_edit = QLineEdit()
        self.pg_host_edit = QLineEdit()
        self.pg_port_spin = QSpinBox()
        self.pg_port_spin.setRange(1, 65535)
        self.pg_port_spin.setValue(5432)
        self.pg_database_edit = QLineEdit()
        self.pg_schema_edit = QLineEdit()
        self.pg_schema_edit.setText("public")
        self.pg_user_edit = QLineEdit()
        self.pg_password_edit = QLineEdit()
        self.pg_password_edit.setEchoMode(QLineEdit.Password)
        self.pg_save_password_check = QCheckBox("Save Password")
        
        pg_layout.addRow("Connection Name:", self.pg_name_edit)
        pg_layout.addRow("Host:", self.pg_host_edit)
        pg_layout.addRow("Port:", self.pg_port_spin)
        pg_layout.addRow("Database:", self.pg_database_edit)
        pg_layout.addRow("Schema:", self.pg_schema_edit)
        pg_layout.addRow("Username:", self.pg_user_edit)
        pg_layout.addRow("Password:", self.pg_password_edit)
        pg_layout.addRow("", self.pg_save_password_check)
        
        pg_widget.setLayout(pg_layout)
        
        # DuckDB connection
        duck_widget = QWidget()
        duck_layout = QFormLayout()
        
        self.duck_name_edit = QLineEdit()
        self.duck_file_edit = QLineEdit()
        self.duck_browse_btn = QPushButton("Browse...")
        self.duck_browse_btn.clicked.connect(self.browse_duckdb_file)
        
        duck_file_layout = QHBoxLayout()
        duck_file_layout.addWidget(self.duck_file_edit)
        duck_file_layout.addWidget(self.duck_browse_btn)
        
        duck_layout.addRow("Connection Name:", self.duck_name_edit)
        duck_layout.addRow("Database File:", duck_file_layout)
        
        duck_widget.setLayout(duck_layout)
        
        # Add tabs
        self.stack_widget.addTab(pg_widget, "PostgreSQL")
        self.stack_widget.addTab(duck_widget, "DuckDB")
        
        layout.addWidget(self.stack_widget)
        
        # Test connection
        test_layout = QHBoxLayout()
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        test_layout.addStretch()
        test_layout.addWidget(self.test_btn)
        layout.addLayout(test_layout)
        
        # Connection status
        self.status_edit = QTextEdit()
        self.status_edit.setReadOnly(True)
        self.status_edit.setMaximumHeight(100)
        layout.addWidget(self.status_edit)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def on_connection_type_changed(self):
        """Handle connection type change."""
        if self.postgres_radio.isChecked():
            self.stack_widget.setCurrentIndex(0)
        else:
            self.stack_widget.setCurrentIndex(1)
        
        self.load_saved_connections()
    
    def load_saved_connections(self):
        """Load saved connections from settings."""
        self.connections_combo.clear()
        
        if self.postgres_radio.isChecked():
            connections = self.settings.value('PostGISMicroservices/postgres_connections', {})
            if isinstance(connections, dict):
                for name in connections.keys():
                    self.connections_combo.addItem(name)
        else:
            connections = self.settings.value('PostGISMicroservices/duckdb_connections', {})
            if isinstance(connections, dict):
                for name in connections.keys():
                    self.connections_combo.addItem(name)
    
    def on_connection_selected(self, index):
        """Handle connection selection."""
        if index < 0:
            return
        
        name = self.connections_combo.currentText()
        
        if self.postgres_radio.isChecked():
            connections = self.settings.value('PostGISMicroservices/postgres_connections', {})
            if isinstance(connections, dict) and name in connections:
                conn = connections[name]
                self.pg_name_edit.setText(name)
                self.pg_host_edit.setText(conn.get('host', ''))
                self.pg_port_spin.setValue(int(conn.get('port', 5432)))
                self.pg_database_edit.setText(conn.get('database', ''))
                self.pg_schema_edit.setText(conn.get('schema', 'public'))
                self.pg_user_edit.setText(conn.get('username', ''))
                self.pg_password_edit.setText(conn.get('password', ''))
                self.pg_save_password_check.setChecked(conn.get('save_password', False))
        else:
            connections = self.settings.value('PostGISMicroservices/duckdb_connections', {})
            if isinstance(connections, dict) and name in connections:
                conn = connections[name]
                self.duck_name_edit.setText(name)
                self.duck_file_edit.setText(conn.get('file', ''))
    
    def load_connection(self):
        """Load the selected connection."""
        self.on_connection_selected(self.connections_combo.currentIndex())
    
    def save_connection(self):
        """Save the current connection."""
        if self.postgres_radio.isChecked():
            name = self.pg_name_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Please enter a connection name.")
                return
            
            connections = self.settings.value('PostGISMicroservices/postgres_connections', {})
            if not isinstance(connections, dict):
                connections = {}
            
            connections[name] = {
                'host': self.pg_host_edit.text(),
                'port': self.pg_port_spin.value(),
                'database': self.pg_database_edit.text(),
                'schema': self.pg_schema_edit.text(),
                'username': self.pg_user_edit.text(),
                'save_password': self.pg_save_password_check.isChecked()
            }
            
            if self.pg_save_password_check.isChecked():
                connections[name]['password'] = self.pg_password_edit.text()
            
            self.settings.setValue('PostGISMicroservices/postgres_connections', connections)
        else:
            name = self.duck_name_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Please enter a connection name.")
                return
            
            connections = self.settings.value('PostGISMicroservices/duckdb_connections', {})
            if not isinstance(connections, dict):
                connections = {}
            
            connections[name] = {
                'file': self.duck_file_edit.text()
            }
            
            self.settings.setValue('PostGISMicroservices/duckdb_connections', connections)
        
        self.load_saved_connections()
        
        # Select the saved connection
        index = self.connections_combo.findText(name)
        if index >= 0:
            self.connections_combo.setCurrentIndex(index)
    
    def delete_connection(self):
        """Delete the selected connection."""
        name = self.connections_combo.currentText()
        if not name:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete the connection '{name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        if self.postgres_radio.isChecked():
            connections = self.settings.value('PostGISMicroservices/postgres_connections', {})
            if isinstance(connections, dict) and name in connections:
                del connections[name]
                self.settings.setValue('PostGISMicroservices/postgres_connections', connections)
        else:
            connections = self.settings.value('PostGISMicroservices/duckdb_connections', {})
            if isinstance(connections, dict) and name in connections:
                del connections[name]
                self.settings.setValue('PostGISMicroservices/duckdb_connections', connections)
        
        self.load_saved_connections()
    
    def browse_duckdb_file(self):
        """Browse for a DuckDB file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select DuckDB File", "", "DuckDB Files (*.duckdb);;All Files (*.*)"
        )
        
        if file_path:
            self.duck_file_edit.setText(file_path)
    
    def test_connection(self):
        """Test the current connection."""
        self.status_edit.clear()
        self.status_edit.append("Testing connection...")
        
        try:
            if self.postgres_radio.isChecked():
                # Build connection settings
                connection_settings = {
                    "host": self.pg_host_edit.text(),
                    "port": self.pg_port_spin.value(),
                    "database": self.pg_database_edit.text(),
                    "user": self.pg_user_edit.text(),
                    "password": self.pg_password_edit.text(),
                    "schema": self.pg_schema_edit.text()
                }
                
                # Test connection
                result = self.api_client.connect_database(connection_settings)
                
                if result.get("status") == "success":
                    self.status_edit.append("Connection successful!")
                    self.status_edit.append(f"Connected to: {result.get('database_info', {}).get('version', 'Unknown')}")
                    
                    # Check for PostGIS
                    if "postgis_version" in result.get("database_info", {}):
                        self.status_edit.append(f"PostGIS version: {result['database_info']['postgis_version']}")
                else:
                    self.status_edit.append(f"Connection failed: {result.get('message', 'Unknown error')}")
            else:
                # For DuckDB, we'll use the geospatial processing API to test
                db_name = os.path.basename(self.duck_file_edit.text())
                if not db_name:
                    self.status_edit.append("Please select a DuckDB file.")
                    return
                
                # Test with a simple query
                result = self.api_client.query_duckdb(
                    db_name=db_name,
                    query="SELECT 1 AS test"
                )
                
                if "data" in result:
                    self.status_edit.append("Connection successful!")
                    self.status_edit.append(f"DuckDB file: {self.duck_file_edit.text()}")
                else:
                    self.status_edit.append(f"Connection failed: {result.get('detail', 'Unknown error')}")
        
        except Exception as e:
            self.status_edit.append(f"Error: {str(e)}")
    
    def accept(self):
        """Handle dialog acceptance."""
        # Save the current connection before closing
        self.save_connection()
        super(ConnectionDialog, self).accept()
