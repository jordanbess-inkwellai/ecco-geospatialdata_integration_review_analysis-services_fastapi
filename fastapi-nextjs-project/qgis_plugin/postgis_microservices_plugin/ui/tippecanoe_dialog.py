import os
from typing import Dict, List, Any, Optional

from qgis.PyQt.QtCore import Qt, QSettings
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTabWidget, QWidget, QFormLayout,
    QSpinBox, QCheckBox, QMessageBox, QGroupBox, QRadioButton,
    QDialogButtonBox, QFileDialog, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QToolButton,
    QMenu, QAction, QProgressBar, QListWidget, QListWidgetItem,
    QDoubleSpinBox
)
from qgis.core import (
    QgsMessageLog, Qgis, QgsVectorLayer, QgsProject,
    QgsTask, QgsApplication, QgsMapLayerProxyModel, QgsMapLayerComboBox
)

class TippecanoeDialog(QDialog):
    """Dialog for Tippecanoe vector tile generation."""
    
    def __init__(self, parent, api_client, iface):
        """Initialize the dialog.
        
        Args:
            parent: Parent widget
            api_client: API client instance
            iface: QGIS interface
        """
        super(TippecanoeDialog, self).__init__(parent)
        
        self.api_client = api_client
        self.iface = iface
        self.settings = QSettings()
        
        self.setWindowTitle("Tippecanoe Vector Tiles")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        self.input_files = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        # Input files
        input_group = QGroupBox("Input Files")
        input_layout = QVBoxLayout()
        
        # Layer selection
        layer_layout = QHBoxLayout()
        layer_layout.addWidget(QLabel("Layer:"))
        
        self.layer_combo = QgsMapLayerComboBox()
        self.layer_combo.setFilters(QgsMapLayerProxyModel.VectorLayer)
        layer_layout.addWidget(self.layer_combo, 1)
        
        self.add_layer_btn = QPushButton("Add Layer")
        self.add_layer_btn.clicked.connect(self.add_layer)
        layer_layout.addWidget(self.add_layer_btn)
        
        input_layout.addLayout(layer_layout)
        
        # File selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("File:"))
        
        self.file_edit = QLineEdit()
        file_layout.addWidget(self.file_edit, 1)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_btn)
        
        self.add_file_btn = QPushButton("Add File")
        self.add_file_btn.clicked.connect(self.add_file)
        file_layout.addWidget(self.add_file_btn)
        
        input_layout.addLayout(file_layout)
        
        # Input files list
        self.files_list = QListWidget()
        self.files_list.setSelectionMode(QListWidget.ExtendedSelection)
        input_layout.addWidget(self.files_list, 1)
        
        # List buttons
        list_buttons = QHBoxLayout()
        
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self.remove_selected)
        list_buttons.addWidget(self.remove_btn)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_all)
        list_buttons.addWidget(self.clear_btn)
        
        input_layout.addLayout(list_buttons)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Output options
        output_group = QGroupBox("Output Options")
        output_layout = QFormLayout()
        
        # Output format
        self.format_combo = QComboBox()
        self.format_combo.addItem("PMTiles", "pmtiles")
        self.format_combo.addItem("MBTiles", "mbtiles")
        output_layout.addRow("Output Format:", self.format_combo)
        
        # Output name
        self.output_name_edit = QLineEdit()
        output_layout.addRow("Output Name:", self.output_name_edit)
        
        # Layer name
        self.layer_name_edit = QLineEdit()
        output_layout.addRow("Layer Name:", self.layer_name_edit)
        
        # Zoom levels
        zoom_layout = QHBoxLayout()
        
        self.min_zoom_spin = QSpinBox()
        self.min_zoom_spin.setRange(0, 22)
        self.min_zoom_spin.setValue(0)
        zoom_layout.addWidget(QLabel("Min:"))
        zoom_layout.addWidget(self.min_zoom_spin)
        
        self.max_zoom_spin = QSpinBox()
        self.max_zoom_spin.setRange(0, 22)
        self.max_zoom_spin.setValue(14)
        zoom_layout.addWidget(QLabel("Max:"))
        zoom_layout.addWidget(self.max_zoom_spin)
        
        output_layout.addRow("Zoom Levels:", zoom_layout)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Advanced options
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QFormLayout()
        
        # Simplification
        self.simplification_spin = QDoubleSpinBox()
        self.simplification_spin.setRange(0, 10)
        self.simplification_spin.setValue(1)
        self.simplification_spin.setSingleStep(0.1)
        advanced_layout.addRow("Simplification:", self.simplification_spin)
        
        # Drop rate
        self.drop_rate_spin = QDoubleSpinBox()
        self.drop_rate_spin.setRange(0, 1)
        self.drop_rate_spin.setValue(0)
        self.drop_rate_spin.setSingleStep(0.01)
        advanced_layout.addRow("Drop Rate:", self.drop_rate_spin)
        
        # Buffer size
        self.buffer_spin = QSpinBox()
        self.buffer_spin.setRange(0, 10)
        self.buffer_spin.setValue(5)
        advanced_layout.addRow("Buffer Size:", self.buffer_spin)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        # Progress
        progress_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.status_label, 1)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addLayout(progress_layout)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        
        self.generate_btn = QPushButton("Generate Tiles")
        self.generate_btn.clicked.connect(self.generate_tiles)
        button_box.addButton(self.generate_btn, QDialogButtonBox.ActionRole)
        
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def add_layer(self):
        """Add the selected layer to the input files list."""
        layer = self.layer_combo.currentLayer()
        if not layer:
            QMessageBox.warning(self, "Warning", "No layer selected.")
            return
        
        # Check if layer is valid
        if not layer.isValid():
            QMessageBox.warning(self, "Warning", "Selected layer is not valid.")
            return
        
        # Get layer source
        source = layer.source()
        
        # For memory layers, we need to save to a file first
        if source.startswith('memory'):
            # Ask for file path
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Layer to File", "", "GeoJSON Files (*.geojson);;All Files (*.*)"
            )
            
            if not file_path:
                return
            
            # Save layer to file
            error = QgsVectorFileWriter.writeAsVectorFormat(
                layer, file_path, "UTF-8", layer.crs(), "GeoJSON"
            )
            
            if error[0] != QgsVectorFileWriter.NoError:
                QMessageBox.warning(self, "Warning", f"Error saving layer to file: {error[1]}")
                return
            
            source = file_path
        
        # Add to input files
        self.add_input_file(source, layer.name())
    
    def browse_file(self):
        """Browse for an input file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Input File", "", "GeoJSON Files (*.geojson);;Shapefile (*.shp);;All Files (*.*)"
        )
        
        if file_path:
            self.file_edit.setText(file_path)
    
    def add_file(self):
        """Add the file from the file edit to the input files list."""
        file_path = self.file_edit.text().strip()
        if not file_path:
            QMessageBox.warning(self, "Warning", "No file specified.")
            return
        
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Warning", f"File does not exist: {file_path}")
            return
        
        # Add to input files
        self.add_input_file(file_path)
        
        # Clear file edit
        self.file_edit.clear()
    
    def add_input_file(self, file_path, name=None):
        """Add an input file to the list.
        
        Args:
            file_path: Path to the input file
            name: Optional name for the file
        """
        # Check if file already in list
        for i in range(self.files_list.count()):
            item = self.files_list.item(i)
            if item.data(Qt.UserRole) == file_path:
                QMessageBox.information(self, "Information", f"File already in list: {file_path}")
                return
        
        # Create list item
        if not name:
            name = os.path.basename(file_path)
        
        item = QListWidgetItem(f"{name} ({file_path})")
        item.setData(Qt.UserRole, file_path)
        
        # Add to list
        self.files_list.addItem(item)
        
        # Add to input files
        self.input_files.append(file_path)
        
        # Update status
        self.set_status(f"Added file: {file_path}")
    
    def remove_selected(self):
        """Remove selected files from the list."""
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            return
        
        for item in selected_items:
            file_path = item.data(Qt.UserRole)
            
            # Remove from input files
            if file_path in self.input_files:
                self.input_files.remove(file_path)
            
            # Remove from list
            self.files_list.takeItem(self.files_list.row(item))
        
        self.set_status(f"Removed {len(selected_items)} file(s)")
    
    def clear_all(self):
        """Clear all files from the list."""
        if self.files_list.count() == 0:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Clear",
            "Are you sure you want to clear all files from the list?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Clear list
        self.files_list.clear()
        
        # Clear input files
        self.input_files = []
        
        self.set_status("Cleared all files")
    
    def generate_tiles(self):
        """Generate vector tiles using Tippecanoe."""
        if not self.input_files:
            QMessageBox.warning(self, "Warning", "No input files specified.")
            return
        
        # Get output format
        output_format = self.format_combo.currentData()
        
        # Get output name
        output_name = self.output_name_edit.text().strip()
        if not output_name:
            QMessageBox.warning(self, "Warning", "Output name is required.")
            return
        
        # Get layer name
        layer_name = self.layer_name_edit.text().strip()
        
        # Get zoom levels
        min_zoom = self.min_zoom_spin.value()
        max_zoom = self.max_zoom_spin.value()
        
        if min_zoom > max_zoom:
            QMessageBox.warning(self, "Warning", "Minimum zoom level cannot be greater than maximum zoom level.")
            return
        
        # Get advanced options
        simplification = self.simplification_spin.value()
        drop_rate = self.drop_rate_spin.value()
        buffer_size = self.buffer_spin.value()
        
        self.set_status(f"Generating {output_format} tiles...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Disable generate button
        self.generate_btn.setEnabled(False)
        
        try:
            # Run Tippecanoe
            result = self.api_client.run_tippecanoe(
                input_files=self.input_files,
                output_format=output_format,
                output_name=output_name,
                min_zoom=min_zoom,
                max_zoom=max_zoom,
                layer_name=layer_name if layer_name else None,
                simplification=simplification,
                drop_rate=drop_rate,
                buffer_size=buffer_size
            )
            
            if result.get('status') == 'success':
                self.set_status(f"Tiles generated successfully: {result.get('output_path')}")
                self.progress_bar.setValue(100)
                
                # Ask if user wants to add to map
                reply = QMessageBox.question(
                    self, "Add to Map",
                    "Do you want to add the generated tiles to the map?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    self.add_tiles_to_map(result.get('output_path'), output_format)
            else:
                self.set_status(f"Error generating tiles: {result.get('message', 'Unknown error')}")
                self.progress_bar.setVisible(False)
        
        except Exception as e:
            self.set_status(f"Error generating tiles: {str(e)}")
            self.progress_bar.setVisible(False)
            QgsMessageLog.logMessage(f"Error generating tiles: {str(e)}", "PostGIS Microservices", Qgis.Critical)
        
        finally:
            # Re-enable generate button
            self.generate_btn.setEnabled(True)
    
    def add_tiles_to_map(self, file_path, format_type):
        """Add generated tiles to the map.
        
        Args:
            file_path: Path to the tiles file
            format_type: Tiles format (pmtiles, mbtiles)
        """
        # For now, we'll just show a message since QGIS doesn't natively support vector tiles
        QMessageBox.information(
            self, "Vector Tiles",
            f"Vector tiles generated at: {file_path}\n\n"
            f"To view these tiles, you can use the Vector Tiles Reader plugin or "
            f"load them into a web map using MapLibre GL JS."
        )
    
    def set_status(self, message):
        """Set status message."""
        self.status_label.setText(message)
        QgsMessageLog.logMessage(message, "PostGIS Microservices", Qgis.Info)
