from qgis.core import QgsPluginLayerRegistry
from qgis.gui import QgsGui, QgsAction
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
import os

class MCPPlugin(QgsPluginLayerRegistry):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.button = None
        self.action = None

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.svg')
        icon = QIcon(icon_path)
        self.action = QAction(icon, "MCP plugin", self.iface.mainWindow())
        self.button = self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)