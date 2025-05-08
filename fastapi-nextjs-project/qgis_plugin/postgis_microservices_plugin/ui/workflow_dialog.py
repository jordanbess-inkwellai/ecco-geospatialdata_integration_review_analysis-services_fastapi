import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from qgis.PyQt.QtCore import Qt, QSettings, QTimer
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTabWidget, QWidget, QFormLayout,
    QSpinBox, QCheckBox, QMessageBox, QGroupBox, QRadioButton,
    QDialogButtonBox, QFileDialog, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QTreeWidget,
    QTreeWidgetItem, QProgressBar, QMenu, QAction
)
from qgis.core import QgsMessageLog, Qgis

class WorkflowDialog(QDialog):
    """Dialog for managing Kestra workflows."""
    
    def __init__(self, parent, api_client):
        """Initialize the dialog.
        
        Args:
            parent: Parent widget
            api_client: API client instance
        """
        super(WorkflowDialog, self).__init__(parent)
        
        self.api_client = api_client
        self.settings = QSettings()
        
        self.setWindowTitle("Workflow Management")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        self.workflows = []
        self.executions = []
        self.selected_workflow = None
        self.selected_execution = None
        
        self.setup_ui()
        self.load_namespaces()
        
        # Set up refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_executions)
        self.refresh_timer.start(10000)  # Refresh every 10 seconds
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        # Namespace selection
        namespace_layout = QHBoxLayout()
        namespace_layout.addWidget(QLabel("Namespace:"))
        self.namespace_combo = QComboBox()
        self.namespace_combo.currentIndexChanged.connect(self.on_namespace_changed)
        namespace_layout.addWidget(self.namespace_combo)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_workflows)
        namespace_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(namespace_layout)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Workflows panel
        workflows_widget = QWidget()
        workflows_layout = QVBoxLayout(workflows_widget)
        workflows_layout.setContentsMargins(0, 0, 0, 0)
        
        workflows_label = QLabel("Workflows")
        workflows_layout.addWidget(workflows_label)
        
        self.workflows_tree = QTreeWidget()
        self.workflows_tree.setHeaderLabels(["Name", "ID", "Status"])
        self.workflows_tree.setColumnWidth(0, 200)
        self.workflows_tree.setColumnWidth(1, 150)
        self.workflows_tree.itemClicked.connect(self.on_workflow_selected)
        self.workflows_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.workflows_tree.customContextMenuRequested.connect(self.show_workflow_context_menu)
        workflows_layout.addWidget(self.workflows_tree)
        
        # Executions panel
        executions_widget = QWidget()
        executions_layout = QVBoxLayout(executions_widget)
        executions_layout.setContentsMargins(0, 0, 0, 0)
        
        executions_label = QLabel("Executions")
        executions_layout.addWidget(executions_label)
        
        self.executions_table = QTableWidget()
        self.executions_table.setColumnCount(5)
        self.executions_table.setHorizontalHeaderLabels(["ID", "Status", "Started", "Duration", "Trigger"])
        self.executions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.executions_table.itemClicked.connect(self.on_execution_selected)
        self.executions_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.executions_table.customContextMenuRequested.connect(self.show_execution_context_menu)
        executions_layout.addWidget(self.executions_table)
        
        # Add widgets to splitter
        splitter.addWidget(workflows_widget)
        splitter.addWidget(executions_widget)
        splitter.setSizes([300, 500])
        
        layout.addWidget(splitter, 1)
        
        # Details panel
        details_group = QGroupBox("Details")
        details_layout = QVBoxLayout()
        
        self.details_edit = QTextEdit()
        self.details_edit.setReadOnly(True)
        details_layout.addWidget(self.details_edit)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
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
    
    def load_namespaces(self):
        """Load namespaces from the API."""
        self.set_status("Loading namespaces...")
        self.progress_bar.setVisible(True)
        
        try:
            # Get all workflows to extract namespaces
            workflows = self.api_client.get_workflows()
            
            # Extract unique namespaces
            namespaces = sorted(set(workflow.get('namespace', 'default') for workflow in workflows))
            
            # Update combo box
            self.namespace_combo.clear()
            self.namespace_combo.addItem("All Namespaces", None)
            for namespace in namespaces:
                self.namespace_combo.addItem(namespace, namespace)
            
            self.set_status("Namespaces loaded")
            self.progress_bar.setVisible(False)
            
            # Load workflows for the selected namespace
            self.refresh_workflows()
        
        except Exception as e:
            self.set_status(f"Error loading namespaces: {str(e)}")
            self.progress_bar.setVisible(False)
            QgsMessageLog.logMessage(f"Error loading namespaces: {str(e)}", "PostGIS Microservices", Qgis.Critical)
    
    def on_namespace_changed(self, index):
        """Handle namespace selection change."""
        self.refresh_workflows()
    
    def refresh_workflows(self):
        """Refresh workflows from the API."""
        self.set_status("Loading workflows...")
        self.progress_bar.setVisible(True)
        
        try:
            # Get namespace
            namespace = self.namespace_combo.currentData()
            
            # Get workflows
            self.workflows = self.api_client.get_workflows(namespace)
            
            # Update tree widget
            self.workflows_tree.clear()
            
            for workflow in self.workflows:
                item = QTreeWidgetItem(self.workflows_tree)
                item.setText(0, workflow.get('name', 'Unnamed'))
                item.setText(1, workflow.get('id', ''))
                item.setText(2, 'Enabled' if workflow.get('enabled', True) else 'Disabled')
                item.setData(0, Qt.UserRole, workflow)
            
            self.set_status(f"Loaded {len(self.workflows)} workflows")
            self.progress_bar.setVisible(False)
        
        except Exception as e:
            self.set_status(f"Error loading workflows: {str(e)}")
            self.progress_bar.setVisible(False)
            QgsMessageLog.logMessage(f"Error loading workflows: {str(e)}", "PostGIS Microservices", Qgis.Critical)
    
    def on_workflow_selected(self, item, column):
        """Handle workflow selection."""
        self.selected_workflow = item.data(0, Qt.UserRole)
        self.refresh_executions()
        self.update_details()
    
    def refresh_executions(self):
        """Refresh executions for the selected workflow."""
        if not self.selected_workflow:
            return
        
        self.set_status("Loading executions...")
        
        try:
            # Get executions
            namespace = self.selected_workflow.get('namespace')
            flow_id = self.selected_workflow.get('id')
            
            self.executions = self.api_client.get_executions(namespace, flow_id)
            
            # Update table widget
            self.executions_table.setRowCount(len(self.executions))
            
            for i, execution in enumerate(self.executions):
                # ID
                id_item = QTableWidgetItem(execution.get('id', ''))
                id_item.setData(Qt.UserRole, execution)
                self.executions_table.setItem(i, 0, id_item)
                
                # Status
                status = execution.get('state', {}).get('current', 'UNKNOWN')
                status_item = QTableWidgetItem(status)
                
                # Set color based on status
                if status in ['RUNNING', 'CREATED']:
                    status_item.setBackground(Qt.yellow)
                elif status == 'SUCCESS':
                    status_item.setBackground(Qt.green)
                elif status in ['FAILED', 'KILLED']:
                    status_item.setBackground(Qt.red)
                
                self.executions_table.setItem(i, 1, status_item)
                
                # Started
                start_date = execution.get('state', {}).get('startDate')
                if start_date:
                    try:
                        dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                        started = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        started = start_date
                else:
                    started = 'N/A'
                
                self.executions_table.setItem(i, 2, QTableWidgetItem(started))
                
                # Duration
                duration = 'N/A'
                start = execution.get('state', {}).get('startDate')
                end = execution.get('state', {}).get('endDate')
                
                if start and end:
                    try:
                        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                        delta = end_dt - start_dt
                        duration = str(delta)
                    except:
                        duration = 'Error'
                elif start and status in ['RUNNING', 'CREATED']:
                    try:
                        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        now = datetime.now()
                        delta = now - start_dt
                        duration = f"{str(delta)} (running)"
                    except:
                        duration = 'Running'
                
                self.executions_table.setItem(i, 3, QTableWidgetItem(duration))
                
                # Trigger
                trigger_type = execution.get('trigger', {}).get('type', 'Manual')
                self.executions_table.setItem(i, 4, QTableWidgetItem(trigger_type))
            
            self.set_status(f"Loaded {len(self.executions)} executions")
        
        except Exception as e:
            self.set_status(f"Error loading executions: {str(e)}")
            QgsMessageLog.logMessage(f"Error loading executions: {str(e)}", "PostGIS Microservices", Qgis.Critical)
    
    def on_execution_selected(self, item):
        """Handle execution selection."""
        row = item.row()
        self.selected_execution = self.executions_table.item(row, 0).data(Qt.UserRole)
        self.update_details()
    
    def update_details(self):
        """Update details panel with selected item information."""
        self.details_edit.clear()
        
        if self.selected_execution:
            # Show execution details
            self.details_edit.append("<h2>Execution Details</h2>")
            self.details_edit.append(f"<p><b>ID:</b> {self.selected_execution.get('id', 'N/A')}</p>")
            self.details_edit.append(f"<p><b>Workflow:</b> {self.selected_workflow.get('name', 'N/A')}</p>")
            
            status = self.selected_execution.get('state', {}).get('current', 'UNKNOWN')
            self.details_edit.append(f"<p><b>Status:</b> {status}</p>")
            
            start_date = self.selected_execution.get('state', {}).get('startDate')
            if start_date:
                try:
                    dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    started = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    started = start_date
                self.details_edit.append(f"<p><b>Started:</b> {started}</p>")
            
            end_date = self.selected_execution.get('state', {}).get('endDate')
            if end_date:
                try:
                    dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    ended = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    ended = end_date
                self.details_edit.append(f"<p><b>Ended:</b> {ended}</p>")
            
            # Inputs
            inputs = self.selected_execution.get('inputs', {})
            if inputs:
                self.details_edit.append("<h3>Inputs</h3>")
                self.details_edit.append("<ul>")
                for key, value in inputs.items():
                    self.details_edit.append(f"<li><b>{key}:</b> {value}</li>")
                self.details_edit.append("</ul>")
            
            # Outputs
            outputs = self.selected_execution.get('outputs', {})
            if outputs:
                self.details_edit.append("<h3>Outputs</h3>")
                self.details_edit.append("<ul>")
                for key, value in outputs.items():
                    self.details_edit.append(f"<li><b>{key}:</b> {value}</li>")
                self.details_edit.append("</ul>")
            
            # Task runs
            task_runs = self.selected_execution.get('taskRunList', [])
            if task_runs:
                self.details_edit.append("<h3>Tasks</h3>")
                self.details_edit.append("<ul>")
                for task in task_runs:
                    task_id = task.get('taskId', 'Unknown')
                    task_status = task.get('state', {}).get('current', 'UNKNOWN')
                    self.details_edit.append(f"<li><b>{task_id}:</b> {task_status}</li>")
                self.details_edit.append("</ul>")
        
        elif self.selected_workflow:
            # Show workflow details
            self.details_edit.append("<h2>Workflow Details</h2>")
            self.details_edit.append(f"<p><b>Name:</b> {self.selected_workflow.get('name', 'N/A')}</p>")
            self.details_edit.append(f"<p><b>ID:</b> {self.selected_workflow.get('id', 'N/A')}</p>")
            self.details_edit.append(f"<p><b>Namespace:</b> {self.selected_workflow.get('namespace', 'N/A')}</p>")
            
            description = self.selected_workflow.get('description', '')
            if description:
                self.details_edit.append(f"<p><b>Description:</b> {description}</p>")
            
            # Tags
            tags = self.selected_workflow.get('tags', [])
            if tags:
                self.details_edit.append("<p><b>Tags:</b> " + ", ".join(tags) + "</p>")
            
            # Inputs
            inputs = self.selected_workflow.get('inputs', [])
            if inputs:
                self.details_edit.append("<h3>Inputs</h3>")
                self.details_edit.append("<ul>")
                for input_def in inputs:
                    name = input_def.get('name', 'Unknown')
                    type_name = input_def.get('type', 'Unknown')
                    required = input_def.get('required', False)
                    self.details_edit.append(f"<li><b>{name}</b> ({type_name}){' (required)' if required else ''}</li>")
                self.details_edit.append("</ul>")
            
            # Tasks
            tasks = self.selected_workflow.get('tasks', [])
            if tasks:
                self.details_edit.append("<h3>Tasks</h3>")
                self.details_edit.append("<ul>")
                for task in tasks:
                    task_id = task.get('id', 'Unknown')
                    task_type = task.get('type', 'Unknown')
                    self.details_edit.append(f"<li><b>{task_id}</b> ({task_type})</li>")
                self.details_edit.append("</ul>")
    
    def show_workflow_context_menu(self, position):
        """Show context menu for workflows."""
        item = self.workflows_tree.itemAt(position)
        if not item:
            return
        
        self.selected_workflow = item.data(0, Qt.UserRole)
        
        menu = QMenu()
        
        run_action = QAction("Run Workflow", self)
        run_action.triggered.connect(self.run_workflow)
        menu.addAction(run_action)
        
        menu.exec_(self.workflows_tree.mapToGlobal(position))
    
    def show_execution_context_menu(self, position):
        """Show context menu for executions."""
        item = self.executions_table.itemAt(position)
        if not item:
            return
        
        row = item.row()
        self.selected_execution = self.executions_table.item(row, 0).data(Qt.UserRole)
        
        menu = QMenu()
        
        status = self.selected_execution.get('state', {}).get('current', '')
        
        if status in ['FAILED', 'KILLED']:
            restart_action = QAction("Restart Execution", self)
            restart_action.triggered.connect(self.restart_execution)
            menu.addAction(restart_action)
        
        if status in ['RUNNING', 'CREATED']:
            stop_action = QAction("Stop Execution", self)
            stop_action.triggered.connect(self.stop_execution)
            menu.addAction(stop_action)
        
        menu.exec_(self.executions_table.mapToGlobal(position))
    
    def run_workflow(self):
        """Run the selected workflow."""
        if not self.selected_workflow:
            return
        
        # Check if workflow has inputs
        inputs = self.selected_workflow.get('inputs', [])
        if inputs:
            # Show input dialog
            input_dialog = WorkflowInputDialog(self, self.selected_workflow)
            if input_dialog.exec_() != QDialog.Accepted:
                return
            
            workflow_inputs = input_dialog.get_inputs()
        else:
            workflow_inputs = {}
        
        self.set_status(f"Running workflow {self.selected_workflow.get('name')}...")
        self.progress_bar.setVisible(True)
        
        try:
            # Trigger workflow
            namespace = self.selected_workflow.get('namespace')
            flow_id = self.selected_workflow.get('id')
            
            result = self.api_client.trigger_workflow(namespace, flow_id, workflow_inputs)
            
            self.set_status(f"Workflow triggered: {result.get('id', 'Unknown')}")
            self.progress_bar.setVisible(False)
            
            # Refresh executions
            self.refresh_executions()
        
        except Exception as e:
            self.set_status(f"Error running workflow: {str(e)}")
            self.progress_bar.setVisible(False)
            QgsMessageLog.logMessage(f"Error running workflow: {str(e)}", "PostGIS Microservices", Qgis.Critical)
    
    def restart_execution(self):
        """Restart the selected execution."""
        if not self.selected_execution:
            return
        
        self.set_status(f"Restarting execution {self.selected_execution.get('id')}...")
        self.progress_bar.setVisible(True)
        
        try:
            # Restart execution
            execution_id = self.selected_execution.get('id')
            
            result = self.api_client.restart_execution(execution_id)
            
            self.set_status(f"Execution restarted: {result.get('id', 'Unknown')}")
            self.progress_bar.setVisible(False)
            
            # Refresh executions
            self.refresh_executions()
        
        except Exception as e:
            self.set_status(f"Error restarting execution: {str(e)}")
            self.progress_bar.setVisible(False)
            QgsMessageLog.logMessage(f"Error restarting execution: {str(e)}", "PostGIS Microservices", Qgis.Critical)
    
    def stop_execution(self):
        """Stop the selected execution."""
        if not self.selected_execution:
            return
        
        self.set_status(f"Stopping execution {self.selected_execution.get('id')}...")
        self.progress_bar.setVisible(True)
        
        try:
            # Stop execution
            execution_id = self.selected_execution.get('id')
            
            result = self.api_client.stop_execution(execution_id)
            
            self.set_status(f"Execution stopped: {result.get('id', 'Unknown')}")
            self.progress_bar.setVisible(False)
            
            # Refresh executions
            self.refresh_executions()
        
        except Exception as e:
            self.set_status(f"Error stopping execution: {str(e)}")
            self.progress_bar.setVisible(False)
            QgsMessageLog.logMessage(f"Error stopping execution: {str(e)}", "PostGIS Microservices", Qgis.Critical)
    
    def set_status(self, message):
        """Set status message."""
        self.status_label.setText(message)
        QgsMessageLog.logMessage(message, "PostGIS Microservices", Qgis.Info)


class WorkflowInputDialog(QDialog):
    """Dialog for entering workflow inputs."""
    
    def __init__(self, parent, workflow):
        """Initialize the dialog.
        
        Args:
            parent: Parent widget
            workflow: Workflow definition
        """
        super(WorkflowInputDialog, self).__init__(parent)
        
        self.workflow = workflow
        self.input_widgets = {}
        
        self.setWindowTitle(f"Inputs for {workflow.get('name', 'Workflow')}")
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Add input fields
        inputs = self.workflow.get('inputs', [])
        for input_def in inputs:
            name = input_def.get('name', '')
            type_name = input_def.get('type', 'STRING')
            description = input_def.get('description', '')
            required = input_def.get('required', False)
            default = input_def.get('defaults')
            
            # Create label with required indicator
            label_text = f"{name}{'*' if required else ''}"
            if description:
                label_text += f" ({description})"
            
            # Create appropriate widget based on type
            if type_name == 'STRING':
                widget = QLineEdit()
                if default:
                    widget.setText(str(default))
            elif type_name == 'INTEGER':
                widget = QSpinBox()
                widget.setRange(-1000000, 1000000)
                if default is not None:
                    widget.setValue(int(default))
            elif type_name == 'FLOAT':
                widget = QDoubleSpinBox()
                widget.setRange(-1000000, 1000000)
                widget.setDecimals(6)
                if default is not None:
                    widget.setValue(float(default))
            elif type_name == 'BOOLEAN':
                widget = QCheckBox()
                if default is not None:
                    widget.setChecked(bool(default))
            elif type_name == 'JSON':
                widget = QTextEdit()
                if default:
                    widget.setText(str(default))
            else:
                widget = QLineEdit()
                if default:
                    widget.setText(str(default))
            
            form_layout.addRow(label_text, widget)
            self.input_widgets[name] = (widget, type_name)
        
        layout.addLayout(form_layout)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_inputs(self):
        """Get input values.
        
        Returns:
            Dictionary of input values
        """
        inputs = {}
        
        for name, (widget, type_name) in self.input_widgets.items():
            if type_name == 'STRING':
                inputs[name] = widget.text()
            elif type_name == 'INTEGER':
                inputs[name] = widget.value()
            elif type_name == 'FLOAT':
                inputs[name] = widget.value()
            elif type_name == 'BOOLEAN':
                inputs[name] = widget.isChecked()
            elif type_name == 'JSON':
                try:
                    # Try to parse as JSON
                    import json
                    inputs[name] = json.loads(widget.toPlainText())
                except:
                    # Fall back to string
                    inputs[name] = widget.toPlainText()
            else:
                inputs[name] = widget.text()
        
        return inputs
