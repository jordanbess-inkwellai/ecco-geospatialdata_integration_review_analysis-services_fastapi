import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from qgis.PyQt.QtCore import Qt, QSettings, QTimer
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import (
    QDockWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTabWidget, QWidget, QFormLayout,
    QSpinBox, QCheckBox, QMessageBox, QGroupBox, QRadioButton,
    QDialogButtonBox, QFileDialog, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QToolButton,
    QMenu, QAction, QProgressBar
)
from qgis.core import QgsMessageLog, Qgis

class MonitoringDock(QDockWidget):
    """Dock widget for database monitoring."""
    
    def __init__(self, title, parent, api_client):
        """Initialize the dock widget.
        
        Args:
            title: Dock widget title
            parent: Parent widget
            api_client: API client instance
        """
        super(MonitoringDock, self).__init__(title, parent)
        
        self.api_client = api_client
        self.settings = QSettings()
        
        self.monitored_databases = []
        self.current_database = None
        
        self.setup_ui()
        self.load_monitored_databases()
        
        # Set up refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_status)
        
        # Start with auto-refresh disabled
        self.auto_refresh_check.setChecked(False)
        self.on_auto_refresh_changed(False)
    
    def setup_ui(self):
        """Set up the user interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Database selection
        db_layout = QHBoxLayout()
        db_layout.addWidget(QLabel("Database:"))
        
        self.db_combo = QComboBox()
        self.db_combo.currentIndexChanged.connect(self.on_database_selected)
        db_layout.addWidget(self.db_combo, 1)
        
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_database)
        db_layout.addWidget(self.add_btn)
        
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self.remove_database)
        db_layout.addWidget(self.remove_btn)
        
        layout.addLayout(db_layout)
        
        # Refresh controls
        refresh_layout = QHBoxLayout()
        
        self.auto_refresh_check = QCheckBox("Auto-refresh")
        self.auto_refresh_check.stateChanged.connect(self.on_auto_refresh_changed)
        refresh_layout.addWidget(self.auto_refresh_check)
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 3600)
        self.interval_spin.setValue(30)
        self.interval_spin.setSuffix(" sec")
        refresh_layout.addWidget(self.interval_spin)
        
        self.refresh_btn = QPushButton("Refresh Now")
        self.refresh_btn.clicked.connect(self.refresh_status)
        refresh_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(refresh_layout)
        
        # Status tabs
        self.tabs = QTabWidget()
        
        # Overview tab
        overview_widget = QWidget()
        overview_layout = QVBoxLayout(overview_widget)
        
        self.status_table = QTableWidget()
        self.status_table.setColumnCount(2)
        self.status_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        overview_layout.addWidget(self.status_table)
        
        self.tabs.addTab(overview_widget, "Overview")
        
        # Connections tab
        connections_widget = QWidget()
        connections_layout = QVBoxLayout(connections_widget)
        
        self.connections_table = QTableWidget()
        self.connections_table.setColumnCount(4)
        self.connections_table.setHorizontalHeaderLabels(["PID", "User", "Database", "Client"])
        self.connections_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        connections_layout.addWidget(self.connections_table)
        
        self.tabs.addTab(connections_widget, "Connections")
        
        # Performance tab
        performance_widget = QWidget()
        performance_layout = QVBoxLayout(performance_widget)
        
        self.performance_table = QTableWidget()
        self.performance_table.setColumnCount(2)
        self.performance_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.performance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        performance_layout.addWidget(self.performance_table)
        
        self.tabs.addTab(performance_widget, "Performance")
        
        # PostGIS tab
        postgis_widget = QWidget()
        postgis_layout = QVBoxLayout(postgis_widget)
        
        self.postgis_table = QTableWidget()
        self.postgis_table.setColumnCount(3)
        self.postgis_table.setHorizontalHeaderLabels(["Table", "Geometry Type", "Count"])
        self.postgis_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        postgis_layout.addWidget(self.postgis_table)
        
        self.tabs.addTab(postgis_widget, "PostGIS")
        
        layout.addWidget(self.tabs, 1)
        
        # Status bar
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label, 1)
        
        self.last_update_label = QLabel("Last update: Never")
        status_layout.addWidget(self.last_update_label)
        
        layout.addLayout(status_layout)
        
        self.setWidget(widget)
    
    def load_monitored_databases(self):
        """Load monitored databases from settings."""
        self.monitored_databases = self.settings.value('PostGISMicroservices/monitored_databases', [])
        if not isinstance(self.monitored_databases, list):
            self.monitored_databases = []
        
        self.db_combo.clear()
        for db in self.monitored_databases:
            self.db_combo.addItem(db.get('name', 'Unknown'), db)
    
    def save_monitored_databases(self):
        """Save monitored databases to settings."""
        self.settings.setValue('PostGISMicroservices/monitored_databases', self.monitored_databases)
    
    def on_database_selected(self, index):
        """Handle database selection change."""
        if index < 0:
            self.current_database = None
            return
        
        self.current_database = self.db_combo.itemData(index)
        self.refresh_status()
    
    def add_database(self):
        """Add a database to monitor."""
        # Get PostgreSQL connections
        connections = self.settings.value('PostGISMicroservices/postgres_connections', {})
        if not isinstance(connections, dict) or not connections:
            QMessageBox.warning(self, "Warning", "No PostgreSQL connections available. Please create a connection first.")
            return
        
        # Show connection selection dialog
        dialog = DatabaseSelectionDialog(self, connections)
        if dialog.exec_() != dialog.Accepted:
            return
        
        # Get selected connection
        connection_name = dialog.get_selected_connection()
        if not connection_name or connection_name not in connections:
            return
        
        connection = connections[connection_name]
        
        # Create database config
        db_config = {
            'name': connection_name,
            'host': connection.get('host', ''),
            'port': connection.get('port', 5432),
            'database': connection.get('database', ''),
            'user': connection.get('username', ''),
            'password': connection.get('password', '')
        }
        
        # Check if already monitored
        for db in self.monitored_databases:
            if db.get('name') == connection_name:
                QMessageBox.information(self, "Information", f"Database '{connection_name}' is already being monitored.")
                return
        
        # Add to monitored databases
        self.monitored_databases.append(db_config)
        self.save_monitored_databases()
        
        # Update combo box
        self.db_combo.addItem(connection_name, db_config)
        self.db_combo.setCurrentIndex(self.db_combo.count() - 1)
    
    def remove_database(self):
        """Remove the current database from monitoring."""
        if not self.current_database:
            return
        
        name = self.current_database.get('name', 'Unknown')
        
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to stop monitoring '{name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Remove from monitored databases
        self.monitored_databases = [db for db in self.monitored_databases if db.get('name') != name]
        self.save_monitored_databases()
        
        # Update combo box
        current_index = self.db_combo.currentIndex()
        self.db_combo.removeItem(current_index)
        
        # Clear current database
        self.current_database = None
        
        # Clear tables
        self.clear_tables()
    
    def on_auto_refresh_changed(self, state):
        """Handle auto-refresh state change."""
        if state:
            # Start timer with current interval
            interval = self.interval_spin.value() * 1000  # Convert to milliseconds
            self.refresh_timer.start(interval)
            self.set_status(f"Auto-refresh enabled ({self.interval_spin.value()} seconds)")
        else:
            # Stop timer
            self.refresh_timer.stop()
            self.set_status("Auto-refresh disabled")
        
        # Enable/disable interval spin box
        self.interval_spin.setEnabled(state)
    
    def refresh_status(self):
        """Refresh database status."""
        if not self.current_database:
            return
        
        self.set_status(f"Refreshing status for {self.current_database.get('name')}...")
        
        try:
            # Get database status
            status = self.api_client.get_database_status(self.current_database)
            
            # Update overview tab
            self.update_overview(status)
            
            # Update connections tab
            self.update_connections(status.get('connections', []))
            
            # Get performance metrics
            metrics = self.api_client.get_performance_metrics(self.current_database)
            
            # Update performance tab
            self.update_performance(metrics)
            
            # Get PostGIS stats
            postgis_stats = self.api_client.get_postgis_stats(self.current_database)
            
            # Update PostGIS tab
            self.update_postgis(postgis_stats)
            
            # Update last update time
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.last_update_label.setText(f"Last update: {now}")
            
            self.set_status(f"Status refreshed for {self.current_database.get('name')}")
        
        except Exception as e:
            self.set_status(f"Error refreshing status: {str(e)}")
            QgsMessageLog.logMessage(f"Error refreshing status: {str(e)}", "PostGIS Microservices", Qgis.Critical)
    
    def update_overview(self, status):
        """Update overview tab with database status.
        
        Args:
            status: Database status dictionary
        """
        self.status_table.setRowCount(0)
        
        # Add general info
        self.add_status_row("Database", status.get('database_name', 'Unknown'))
        self.add_status_row("Version", status.get('version', 'Unknown'))
        self.add_status_row("Status", status.get('status', 'Unknown'))
        self.add_status_row("Uptime", status.get('uptime', 'Unknown'))
        
        # Add connection info
        self.add_status_row("Active Connections", str(status.get('active_connections', 0)))
        self.add_status_row("Max Connections", str(status.get('max_connections', 0)))
        
        # Add size info
        self.add_status_row("Database Size", status.get('database_size', 'Unknown'))
        
        # Add PostGIS info
        if 'postgis_version' in status:
            self.add_status_row("PostGIS Version", status.get('postgis_version', 'Unknown'))
    
    def update_connections(self, connections):
        """Update connections tab with active connections.
        
        Args:
            connections: List of active connections
        """
        self.connections_table.setRowCount(len(connections))
        
        for i, conn in enumerate(connections):
            self.connections_table.setItem(i, 0, QTableWidgetItem(str(conn.get('pid', ''))))
            self.connections_table.setItem(i, 1, QTableWidgetItem(conn.get('user', '')))
            self.connections_table.setItem(i, 2, QTableWidgetItem(conn.get('database', '')))
            self.connections_table.setItem(i, 3, QTableWidgetItem(conn.get('client', '')))
    
    def update_performance(self, metrics):
        """Update performance tab with performance metrics.
        
        Args:
            metrics: Performance metrics dictionary
        """
        self.performance_table.setRowCount(0)
        
        # Add CPU metrics
        self.add_performance_row("CPU Usage", f"{metrics.get('cpu_usage', 0):.2f}%")
        
        # Add memory metrics
        self.add_performance_row("Memory Usage", f"{metrics.get('memory_usage', 0):.2f}%")
        self.add_performance_row("Memory Used", metrics.get('memory_used', 'Unknown'))
        self.add_performance_row("Memory Total", metrics.get('memory_total', 'Unknown'))
        
        # Add disk metrics
        self.add_performance_row("Disk Usage", f"{metrics.get('disk_usage', 0):.2f}%")
        self.add_performance_row("Disk Used", metrics.get('disk_used', 'Unknown'))
        self.add_performance_row("Disk Total", metrics.get('disk_total', 'Unknown'))
        
        # Add query metrics
        self.add_performance_row("Queries Per Second", str(metrics.get('queries_per_second', 0)))
        self.add_performance_row("Slow Queries", str(metrics.get('slow_queries', 0)))
        
        # Add transaction metrics
        self.add_performance_row("Transactions Per Second", str(metrics.get('transactions_per_second', 0)))
    
    def update_postgis(self, postgis_stats):
        """Update PostGIS tab with PostGIS statistics.
        
        Args:
            postgis_stats: PostGIS statistics dictionary
        """
        tables = postgis_stats.get('tables', [])
        self.postgis_table.setRowCount(len(tables))
        
        for i, table in enumerate(tables):
            self.postgis_table.setItem(i, 0, QTableWidgetItem(table.get('table_name', '')))
            self.postgis_table.setItem(i, 1, QTableWidgetItem(table.get('geometry_type', '')))
            self.postgis_table.setItem(i, 2, QTableWidgetItem(str(table.get('count', 0))))
    
    def add_status_row(self, metric, value):
        """Add a row to the status table.
        
        Args:
            metric: Metric name
            value: Metric value
        """
        row = self.status_table.rowCount()
        self.status_table.insertRow(row)
        self.status_table.setItem(row, 0, QTableWidgetItem(metric))
        self.status_table.setItem(row, 1, QTableWidgetItem(value))
    
    def add_performance_row(self, metric, value):
        """Add a row to the performance table.
        
        Args:
            metric: Metric name
            value: Metric value
        """
        row = self.performance_table.rowCount()
        self.performance_table.insertRow(row)
        self.performance_table.setItem(row, 0, QTableWidgetItem(metric))
        self.performance_table.setItem(row, 1, QTableWidgetItem(value))
    
    def clear_tables(self):
        """Clear all tables."""
        self.status_table.setRowCount(0)
        self.connections_table.setRowCount(0)
        self.performance_table.setRowCount(0)
        self.postgis_table.setRowCount(0)
    
    def set_status(self, message):
        """Set status message."""
        self.status_label.setText(message)
        QgsMessageLog.logMessage(message, "PostGIS Microservices", Qgis.Info)


class DatabaseSelectionDialog(QDialog):
    """Dialog for selecting a database to monitor."""
    
    def __init__(self, parent, connections):
        """Initialize the dialog.
        
        Args:
            parent: Parent widget
            connections: Dictionary of available connections
        """
        super(DatabaseSelectionDialog, self).__init__(parent)
        
        self.connections = connections
        self.selected_connection = None
        
        self.setWindowTitle("Select Database to Monitor")
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Select a PostgreSQL connection to monitor:"))
        
        self.connections_combo = QComboBox()
        for name in self.connections.keys():
            self.connections_combo.addItem(name)
        
        layout.addWidget(self.connections_combo)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_selected_connection(self):
        """Get the selected connection name.
        
        Returns:
            Selected connection name
        """
        return self.connections_combo.currentText()
