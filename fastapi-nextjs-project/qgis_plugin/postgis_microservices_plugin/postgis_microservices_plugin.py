import os
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.core import QgsMessageLog, Qgis

# Import the API client
from .api_client import APIClient

# Import the dialogs
from .ui.connection_dialog import ConnectionDialog
from .ui.process_dialog import ProcessDialog

class PostGISMicroservicesPlugin:
    """QGIS Plugin for PostGIS Microservices"""
    
    def __init__(self, iface):
        """Constructor.
        
        Args:
            iface: QGIS interface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        
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
        
        # Initialize dialogs
        self.connection_dialog = None
        self.process_dialog = None
        
        # Initialize actions
        self.actions = []
    
    def tr(self, message):
        """Get the translation for a string.
        
        Args:
            message: String to translate
            
        Returns:
            Translated string
        """
        return QCoreApplication.translate('PostGISMicroservicesPlugin', message)
    
    def add_action(self, icon_path, text, callback, enabled_flag=True,
                  add_to_menu=True, add_to_toolbar=True, status_tip=None,
                  whats_this=None, parent=None):
        """Add a toolbar icon to the toolbar.
        
        Args:
            icon_path: Path to the icon for this action
            text: Text that should be shown in menu items for this action
            callback: Function to be called when the action is triggered
            enabled_flag: A flag indicating if the action should be enabled
            add_to_menu: Flag indicating whether the action should also be added to the menu
            add_to_toolbar: Flag indicating whether the action should also be added to the toolbar
            status_tip: Optional text to show in a popup when mouse pointer hovers over the action
            whats_this: Optional text to show in the status bar when the mouse pointer hovers over the action
            parent: Parent widget for the new action
            
        Returns:
            The action that was created
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
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)
        
        if add_to_menu:
            self.iface.addPluginToMenu(
                self.tr('&PostGIS Microservices'),
                action)
        
        self.actions.append(action)
        
        return action
    
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Create menu
        menu = QMenu(self.tr('&PostGIS Microservices'))
        self.iface.pluginMenu().addMenu(menu)
        
        # Add connection action
        self.connection_action = QAction(
            QIcon(os.path.join(self.plugin_dir, 'icons', 'connection.svg')),
            self.tr('Database Connection'),
            self.iface.mainWindow())
        self.connection_action.triggered.connect(self.show_connection_dialog)
        
        # Add process action
        self.process_action = QAction(
            QIcon(os.path.join(self.plugin_dir, 'icons', 'process.svg')),
            self.tr('OGC API Processes'),
            self.iface.mainWindow())
        self.process_action.triggered.connect(self.show_process_dialog)
        
        # Add actions to menu
        menu.addAction(self.connection_action)
        menu.addAction(self.process_action)
        
        # Add actions to toolbar
        self.iface.addToolBarIcon(self.connection_action)
        self.iface.addToolBarIcon(self.process_action)
        
        # Store actions
        self.actions.append(self.connection_action)
        self.actions.append(self.process_action)
    
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr('&PostGIS Microservices'),
                action)
            self.iface.removeToolBarIcon(action)
    
    def show_connection_dialog(self):
        """Show the database connection dialog."""
        if not self.connection_dialog:
            self.connection_dialog = ConnectionDialog(self.iface.mainWindow(), self.api_client)
        
        self.connection_dialog.show()
    
    def show_process_dialog(self):
        """Show the OGC API Processes dialog."""
        if not self.process_dialog:
            self.process_dialog = ProcessDialog(self.iface.mainWindow(), self.api_client, self.iface)
        
        self.process_dialog.show()
