import os
import json
from typing import Dict, List, Any, Optional

from qgis.PyQt.QtCore import Qt, QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QAction, QMenu, QToolButton, QDockWidget, QMessageBox,
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTabWidget, QWidget, QFormLayout,
    QSpinBox, QDoubleSpinBox, QCheckBox, QFileDialog, QTextEdit
)
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsRasterLayer, QgsFeature, 
    QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform,
    QgsMessageLog, Qgis, QgsApplication, QgsTask, QgsTaskManager
)
from qgis.gui import QgsMapToolEmitPoint, QgsMapCanvas, QgsRubberBand

# Import the API client
from .api_client import APIClient

# Import UI components
from .ui.connection_dialog import ConnectionDialog
from .ui.workflow_dialog import WorkflowDialog
from .ui.duckdb_dialog import DuckDBDialog
from .ui.tippecanoe_dialog import TippecanoeDialog
from .ui.monitoring_dock import MonitoringDock

class PostGISMicroservices:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.
        
        Args:
            iface: An interface instance that will be passed to this class
                which provides the hook by which you can manipulate the QGIS
                application at run time.
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        
        # Initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        
        # Initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PostGISMicroservices_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)
        
        # Initialize API client
        self.api_client = APIClient()
        
        # Initialize UI components
        self.actions = []
        self.menu = self.tr('&PostGIS Microservices')
        self.toolbar = self.iface.addToolBar('PostGIS Microservices')
        self.toolbar.setObjectName('PostGISMicroservices')
        
        # Initialize dock widgets
        self.monitoring_dock = None
        
        # Initialize dialogs
        self.connection_dialog = None
        self.workflow_dialog = None
        self.duckdb_dialog = None
        self.tippecanoe_dialog = None
        
        # Initialize settings
        self.settings = QSettings()
        self.load_settings()
    
    def tr(self, message):
        """Get the translation for a string using Qt translation API.
        
        Args:
            message: String for translation.
            
        Returns:
            Translated version of message.
        """
        return QCoreApplication.translate('PostGISMicroservices', message)
    
    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.
        
        Args:
            icon_path: Path to the icon for this action. Can be a resource
                path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
            text: Text that should be shown in menu items for this action.
            callback: Function to be called when the action is triggered.
            enabled_flag: A flag indicating if the action should be enabled
                by default. Defaults to True.
            add_to_menu: Flag indicating whether the action should also
                be added to the menu. Defaults to True.
            add_to_toolbar: Flag indicating whether the action should also
                be added to the toolbar. Defaults to True.
            status_tip: Optional text to show in a popup when mouse pointer
                hovers over the action.
            whats_this: Optional text to show in the status bar when the
                mouse pointer hovers over the action.
            parent: Parent widget for the new action. Defaults None.
            
        Returns:
            The action that was created. Note that the action is also
            added to self.actions list.
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action
    
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Main plugin icon
        icon_path = os.path.join(self.plugin_dir, 'icons', 'icon.png')
        
        # Add main menu button
        self.add_action(
            icon_path,
            text=self.tr('PostGIS Microservices'),
            callback=self.show_menu,
            parent=self.iface.mainWindow())
        
        # Create menu actions
        self.connection_action = QAction(
            QIcon(os.path.join(self.plugin_dir, 'icons', 'database.png')),
            self.tr('Database Connection'),
            self.iface.mainWindow())
        self.connection_action.triggered.connect(self.show_connection_dialog)
        
        self.workflow_action = QAction(
            QIcon(os.path.join(self.plugin_dir, 'icons', 'workflow.png')),
            self.tr('Workflow Management'),
            self.iface.mainWindow())
        self.workflow_action.triggered.connect(self.show_workflow_dialog)
        
        self.duckdb_action = QAction(
            QIcon(os.path.join(self.plugin_dir, 'icons', 'duckdb.png')),
            self.tr('DuckDB Operations'),
            self.iface.mainWindow())
        self.duckdb_action.triggered.connect(self.show_duckdb_dialog)
        
        self.tippecanoe_action = QAction(
            QIcon(os.path.join(self.plugin_dir, 'icons', 'tippecanoe.png')),
            self.tr('Tippecanoe Vector Tiles'),
            self.iface.mainWindow())
        self.tippecanoe_action.triggered.connect(self.show_tippecanoe_dialog)
        
        self.monitoring_action = QAction(
            QIcon(os.path.join(self.plugin_dir, 'icons', 'monitoring.png')),
            self.tr('Database Monitoring'),
            self.iface.mainWindow())
        self.monitoring_action.triggered.connect(self.toggle_monitoring_dock)
        
        # Create monitoring dock widget
        self.create_monitoring_dock()
    
    def show_menu(self):
        """Show the plugin menu."""
        menu = QMenu()
        menu.addAction(self.connection_action)
        menu.addAction(self.workflow_action)
        menu.addAction(self.duckdb_action)
        menu.addAction(self.tippecanoe_action)
        menu.addAction(self.monitoring_action)
        
        # Show the menu at the toolbar button position
        button = self.toolbar.widgetForAction(self.actions[0])
        menu.exec_(button.mapToGlobal(button.rect().bottomLeft()))
    
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr('&PostGIS Microservices'),
                action)
            self.iface.removeToolBarIcon(action)
        
        # Remove the toolbar
        del self.toolbar
        
        # Remove dock widgets
        if self.monitoring_dock:
            self.iface.removeDockWidget(self.monitoring_dock)
            self.monitoring_dock = None
    
    def load_settings(self):
        """Load plugin settings."""
        self.api_url = self.settings.value('PostGISMicroservices/api_url', 'http://localhost:8000/api/v1')
        self.api_client.base_url = self.api_url
    
    def save_settings(self):
        """Save plugin settings."""
        self.settings.setValue('PostGISMicroservices/api_url', self.api_client.base_url)
    
    def show_connection_dialog(self):
        """Show the database connection dialog."""
        if not self.connection_dialog:
            self.connection_dialog = ConnectionDialog(self.iface.mainWindow(), self.api_client)
        
        self.connection_dialog.show()
    
    def show_workflow_dialog(self):
        """Show the workflow management dialog."""
        if not self.workflow_dialog:
            self.workflow_dialog = WorkflowDialog(self.iface.mainWindow(), self.api_client)
        
        self.workflow_dialog.show()
    
    def show_duckdb_dialog(self):
        """Show the DuckDB operations dialog."""
        if not self.duckdb_dialog:
            self.duckdb_dialog = DuckDBDialog(self.iface.mainWindow(), self.api_client, self.iface)
        
        self.duckdb_dialog.show()
    
    def show_tippecanoe_dialog(self):
        """Show the Tippecanoe vector tiles dialog."""
        if not self.tippecanoe_dialog:
            self.tippecanoe_dialog = TippecanoeDialog(self.iface.mainWindow(), self.api_client, self.iface)
        
        self.tippecanoe_dialog.show()
    
    def create_monitoring_dock(self):
        """Create the database monitoring dock widget."""
        self.monitoring_dock = MonitoringDock(self.tr('Database Monitoring'), self.iface.mainWindow(), self.api_client)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.monitoring_dock)
        self.monitoring_dock.hide()
    
    def toggle_monitoring_dock(self):
        """Toggle the database monitoring dock widget."""
        if self.monitoring_dock.isVisible():
            self.monitoring_dock.hide()
        else:
            self.monitoring_dock.show()
    
    def run(self):
        """Run method that performs all the real work."""
        # Show the dialog
        self.show_menu()
