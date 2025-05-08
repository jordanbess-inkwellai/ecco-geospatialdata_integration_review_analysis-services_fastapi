import React, { useState, useEffect, useCallback, useRef } from 'react';
import ReactFlow, {
  ReactFlowProvider,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  NodeTypes,
  EdgeTypes,
  MarkerType,
  Panel
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Box,
  Typography,
  Paper,
  Button,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Tooltip,
  Alert,
  CircularProgress,
  Snackbar
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import CodeIcon from '@mui/icons-material/Code';
import SettingsIcon from '@mui/icons-material/Settings';
import DescriptionIcon from '@mui/icons-material/Description';
import StorageIcon from '@mui/icons-material/Storage';
import HttpIcon from '@mui/icons-material/Http';
import FolderIcon from '@mui/icons-material/Folder';
import TerminalIcon from '@mui/icons-material/Terminal';
import ScheduleIcon from '@mui/icons-material/Schedule';
import WebhookIcon from '@mui/icons-material/Webhook';

import TaskNode from './nodes/TaskNode';
import TriggerNode from './nodes/TriggerNode';
import TaskPropertiesPanel from './panels/TaskPropertiesPanel';
import TriggerPropertiesPanel from './panels/TriggerPropertiesPanel';
import FlowPropertiesPanel from './panels/FlowPropertiesPanel';
import { apiClient } from '../../lib/api';

// Define node types
const nodeTypes: NodeTypes = {
  task: TaskNode,
  trigger: TriggerNode
};

// Task type definitions
const taskTypes = [
  { id: 'io.kestra.plugin.scripts.python.Script', name: 'Python Script', icon: <CodeIcon /> },
  { id: 'io.kestra.plugin.scripts.shell.Script', name: 'Shell Script', icon: <TerminalIcon /> },
  { id: 'io.kestra.plugin.http.Request', name: 'HTTP Request', icon: <HttpIcon /> },
  { id: 'io.kestra.plugin.fs.http.Read', name: 'File Read', icon: <FolderIcon /> },
  { id: 'io.kestra.plugin.fs.http.Write', name: 'File Write', icon: <FolderIcon /> },
  { id: 'io.kestra.plugin.jdbc.Query', name: 'SQL Query', icon: <StorageIcon /> },
  { id: 'io.kestra.plugin.core.flow.Trigger', name: 'Flow Trigger', icon: <PlayArrowIcon /> }
];

// Trigger type definitions
const triggerTypes = [
  { id: 'io.kestra.plugin.webhook.Trigger', name: 'Webhook', icon: <WebhookIcon /> },
  { id: 'io.kestra.plugin.schedules.Schedule', name: 'Schedule', icon: <ScheduleIcon /> },
  { id: 'io.kestra.plugin.core.trigger.Flow', name: 'Flow', icon: <PlayArrowIcon /> }
];

interface WorkflowBuilderProps {
  initialFlow?: any;
  onSave?: (flow: any) => void;
  onExecute?: (flow: any) => void;
  readOnly?: boolean;
}

const WorkflowBuilder: React.FC<WorkflowBuilderProps> = ({
  initialFlow,
  onSave,
  onExecute,
  readOnly = false
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedElement, setSelectedElement] = useState<any>(null);
  const [selectedElementType, setSelectedElementType] = useState<'node' | 'edge' | 'flow' | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [flowProperties, setFlowProperties] = useState<any>({
    id: '',
    namespace: 'default',
    tasks: [],
    triggers: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });
  const [codeDialogOpen, setCodeDialogOpen] = useState(false);
  const [flowCode, setFlowCode] = useState('');
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);

  // Initialize the flow
  useEffect(() => {
    if (initialFlow) {
      setFlowProperties({
        id: initialFlow.id || '',
        namespace: initialFlow.namespace || 'default',
        description: initialFlow.description || '',
        revision: initialFlow.revision || 1,
        inputs: initialFlow.inputs || [],
        outputs: initialFlow.outputs || []
      });

      // Convert flow to nodes and edges
      const flowNodes: Node[] = [];
      const flowEdges: Edge[] = [];

      // Add trigger nodes
      if (initialFlow.triggers) {
        initialFlow.triggers.forEach((trigger: any, index: number) => {
          flowNodes.push({
            id: trigger.id,
            type: 'trigger',
            position: { x: 100, y: 100 + index * 150 },
            data: { ...trigger, label: trigger.id }
          });
        });
      }

      // Add task nodes
      if (initialFlow.tasks) {
        initialFlow.tasks.forEach((task: any, index: number) => {
          flowNodes.push({
            id: task.id,
            type: 'task',
            position: { x: 400, y: 100 + index * 150 },
            data: { ...task, label: task.id }
          });

          // Add edges for task dependencies
          if (task.dependsOn) {
            task.dependsOn.forEach((dep: string) => {
              flowEdges.push({
                id: `${dep}-${task.id}`,
                source: dep,
                target: task.id,
                type: 'default',
                markerEnd: {
                  type: MarkerType.ArrowClosed
                }
              });
            });
          }
        });
      }

      setNodes(flowNodes);
      setEdges(flowEdges);
    }
  }, [initialFlow, setNodes, setEdges]);

  // Handle connection between nodes
  const onConnect = useCallback(
    (params: Connection) => {
      // Create a new edge
      const newEdge = {
        ...params,
        id: `${params.source}-${params.target}`,
        markerEnd: {
          type: MarkerType.ArrowClosed
        }
      };

      // Add the edge
      setEdges((eds) => addEdge(newEdge, eds));

      // Update the target node's dependencies
      setNodes((nds) =>
        nds.map((node) => {
          if (node.id === params.target) {
            // Get the current dependencies
            const dependsOn = node.data.dependsOn || [];

            // Add the new dependency if it doesn't already exist
            if (!dependsOn.includes(params.source)) {
              return {
                ...node,
                data: {
                  ...node.data,
                  dependsOn: [...dependsOn, params.source]
                }
              };
            }
          }
          return node;
        })
      );
    },
    [setEdges, setNodes]
  );

  // Handle node selection
  const onNodeClick = useCallback(
    (event: React.MouseEvent, node: Node) => {
      setSelectedElement(node);
      setSelectedElementType('node');
    },
    [setSelectedElement]
  );

  // Handle edge selection
  const onEdgeClick = useCallback(
    (event: React.MouseEvent, edge: Edge) => {
      setSelectedElement(edge);
      setSelectedElementType('edge');
    },
    [setSelectedElement]
  );

  // Handle pane click (deselect elements)
  const onPaneClick = useCallback(() => {
    setSelectedElement(null);
    setSelectedElementType('flow');
  }, [setSelectedElement]);

  // Handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Add a new task node
  const addTaskNode = (taskType: string) => {
    const taskTypeInfo = taskTypes.find((type) => type.id === taskType);
    const taskId = `task_${Date.now()}`;
    const newNode: Node = {
      id: taskId,
      type: 'task',
      position: {
        x: 250,
        y: 100 + nodes.length * 50
      },
      data: {
        id: taskId,
        type: taskType,
        label: taskTypeInfo?.name || taskId
      }
    };

    setNodes((nds) => [...nds, newNode]);
    setDrawerOpen(false);
  };

  // Add a new trigger node
  const addTriggerNode = (triggerType: string) => {
    const triggerTypeInfo = triggerTypes.find((type) => type.id === triggerType);
    const triggerId = `trigger_${Date.now()}`;
    const newNode: Node = {
      id: triggerId,
      type: 'trigger',
      position: {
        x: 50,
        y: 100 + nodes.length * 50
      },
      data: {
        id: triggerId,
        type: triggerType,
        label: triggerTypeInfo?.name || triggerId
      }
    };

    setNodes((nds) => [...nds, newNode]);
    setDrawerOpen(false);
  };

  // Delete the selected element
  const deleteSelectedElement = () => {
    if (!selectedElement) return;

    if (selectedElementType === 'node') {
      // Remove the node
      setNodes((nds) => nds.filter((node) => node.id !== selectedElement.id));

      // Remove any edges connected to the node
      setEdges((eds) =>
        eds.filter(
          (edge) => edge.source !== selectedElement.id && edge.target !== selectedElement.id
        )
      );

      // Remove the node from any dependencies
      setNodes((nds) =>
        nds.map((node) => {
          if (node.data.dependsOn && node.data.dependsOn.includes(selectedElement.id)) {
            return {
              ...node,
              data: {
                ...node.data,
                dependsOn: node.data.dependsOn.filter((dep: string) => dep !== selectedElement.id)
              }
            };
          }
          return node;
        })
      );
    } else if (selectedElementType === 'edge') {
      // Remove the edge
      setEdges((eds) => eds.filter((edge) => edge.id !== selectedElement.id));

      // Remove the dependency from the target node
      const [source, target] = selectedElement.id.split('-');
      setNodes((nds) =>
        nds.map((node) => {
          if (node.id === target && node.data.dependsOn) {
            return {
              ...node,
              data: {
                ...node.data,
                dependsOn: node.data.dependsOn.filter((dep: string) => dep !== source)
              }
            };
          }
          return node;
        })
      );
    }

    setSelectedElement(null);
    setSelectedElementType(null);
  };

  // Update node data
  const updateNodeData = (nodeId: string, data: any) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            data: {
              ...node.data,
              ...data
            }
          };
        }
        return node;
      })
    );
  };

  // Update flow properties
  const updateFlowProperties = (properties: any) => {
    setFlowProperties((prev: any) => ({
      ...prev,
      ...properties
    }));
  };

  // Convert the workflow to a Kestra flow
  const buildFlow = () => {
    // Get all task nodes
    const taskNodes = nodes.filter((node) => node.type === 'task');
    const triggerNodes = nodes.filter((node) => node.type === 'trigger');

    // Build the flow object
    const flow = {
      id: flowProperties.id || `flow_${Date.now()}`,
      namespace: flowProperties.namespace || 'default',
      revision: flowProperties.revision || 1,
      tasks: taskNodes.map((node) => ({
        ...node.data,
        dependsOn: node.data.dependsOn || []
      })),
      triggers: triggerNodes.map((node) => ({
        ...node.data
      }))
    };

    // Add optional properties
    if (flowProperties.description) {
      flow.description = flowProperties.description;
    }

    if (flowProperties.inputs && flowProperties.inputs.length > 0) {
      flow.inputs = flowProperties.inputs;
    }

    if (flowProperties.outputs && flowProperties.outputs.length > 0) {
      flow.outputs = flowProperties.outputs;
    }

    return flow;
  };

  // Save the workflow
  const saveWorkflow = async () => {
    try {
      setLoading(true);
      setError(null);

      // Build the flow
      const flow = buildFlow();

      // Call the save callback if provided
      if (onSave) {
        onSave(flow);
      } else {
        // Otherwise, save the flow via the API
        const response = await apiClient.post('/workflows/flows', flow);
        
        setNotification({
          open: true,
          message: 'Workflow saved successfully',
          severity: 'success'
        });
      }

      setLoading(false);
    } catch (err) {
      console.error('Error saving workflow:', err);
      setError('Failed to save workflow');
      setLoading(false);
      
      setNotification({
        open: true,
        message: 'Failed to save workflow',
        severity: 'error'
      });
    }
  };

  // Execute the workflow
  const executeWorkflow = async () => {
    try {
      setLoading(true);
      setError(null);

      // Build the flow
      const flow = buildFlow();

      // Call the execute callback if provided
      if (onExecute) {
        onExecute(flow);
      } else {
        // Otherwise, execute the flow via the API
        const response = await apiClient.post('/workflows/flows/execute', {
          namespace: flow.namespace,
          flow_id: flow.id
        });
        
        setNotification({
          open: true,
          message: 'Workflow execution started',
          severity: 'success'
        });
      }

      setLoading(false);
    } catch (err) {
      console.error('Error executing workflow:', err);
      setError('Failed to execute workflow');
      setLoading(false);
      
      setNotification({
        open: true,
        message: 'Failed to execute workflow',
        severity: 'error'
      });
    }
  };

  // Show the flow code
  const showFlowCode = () => {
    const flow = buildFlow();
    setFlowCode(JSON.stringify(flow, null, 2));
    setCodeDialogOpen(true);
  };

  // Close the notification
  const handleCloseNotification = () => {
    setNotification({
      ...notification,
      open: false
    });
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 1, display: 'flex', alignItems: 'center', borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Workflow Builder
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => setDrawerOpen(true)}
            disabled={readOnly}
          >
            Add Node
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<CodeIcon />}
            onClick={showFlowCode}
          >
            View Code
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<PlayArrowIcon />}
            onClick={executeWorkflow}
            disabled={loading || nodes.length === 0}
            color="secondary"
          >
            Execute
          </Button>
          
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={saveWorkflow}
            disabled={loading || readOnly || nodes.length === 0}
          >
            Save
          </Button>
        </Box>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ m: 1 }}>
          {error}
        </Alert>
      )}
      
      <Box sx={{ flexGrow: 1, position: 'relative' }}>
        <ReactFlowProvider>
          <Box ref={reactFlowWrapper} sx={{ height: '100%' }}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onNodeClick={onNodeClick}
              onEdgeClick={onEdgeClick}
              onPaneClick={onPaneClick}
              nodeTypes={nodeTypes}
              fitView
              onInit={setReactFlowInstance}
              deleteKeyCode={null} // Disable default delete behavior
            >
              <Controls />
              <Background />
              
              {/* Properties Panel */}
              <Panel position="right" style={{ width: '300px', height: '100%', padding: 0 }}>
                <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <Tabs
                    value={selectedElementType === 'flow' ? 0 : 1}
                    onChange={(e, val) => {
                      if (val === 0) {
                        setSelectedElement(null);
                        setSelectedElementType('flow');
                      }
                    }}
                    sx={{ borderBottom: 1, borderColor: 'divider' }}
                  >
                    <Tab label="Flow Properties" />
                    <Tab label="Node Properties" disabled={!selectedElement} />
                  </Tabs>
                  
                  {selectedElementType === 'flow' && (
                    <FlowPropertiesPanel
                      flowProperties={flowProperties}
                      onChange={updateFlowProperties}
                      readOnly={readOnly}
                    />
                  )}
                  
                  {selectedElementType === 'node' && selectedElement && (
                    selectedElement.type === 'trigger' ? (
                      <TriggerPropertiesPanel
                        trigger={selectedElement.data}
                        onChange={(data) => updateNodeData(selectedElement.id, data)}
                        readOnly={readOnly}
                      />
                    ) : (
                      <TaskPropertiesPanel
                        task={selectedElement.data}
                        onChange={(data) => updateNodeData(selectedElement.id, data)}
                        readOnly={readOnly}
                      />
                    )
                  )}
                  
                  {selectedElementType === 'edge' && selectedElement && (
                    <Box p={2}>
                      <Typography variant="subtitle1" gutterBottom>
                        Edge Properties
                      </Typography>
                      <Typography variant="body2">
                        Source: {selectedElement.source}
                      </Typography>
                      <Typography variant="body2">
                        Target: {selectedElement.target}
                      </Typography>
                      
                      {!readOnly && (
                        <Button
                          variant="outlined"
                          color="error"
                          startIcon={<DeleteIcon />}
                          onClick={deleteSelectedElement}
                          sx={{ mt: 2 }}
                        >
                          Delete Edge
                        </Button>
                      )}
                    </Box>
                  )}
                </Paper>
              </Panel>
            </ReactFlow>
          </Box>
        </ReactFlowProvider>
      </Box>
      
      {/* Add Node Drawer */}
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Box sx={{ width: 300 }}>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h6">Add Node</Typography>
          </Box>
          
          <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tab label="Tasks" />
            <Tab label="Triggers" />
          </Tabs>
          
          {tabValue === 0 && (
            <List>
              {taskTypes.map((taskType) => (
                <ListItem
                  key={taskType.id}
                  button
                  onClick={() => addTaskNode(taskType.id)}
                >
                  <ListItemIcon>
                    {taskType.icon}
                  </ListItemIcon>
                  <ListItemText primary={taskType.name} />
                </ListItem>
              ))}
            </List>
          )}
          
          {tabValue === 1 && (
            <List>
              {triggerTypes.map((triggerType) => (
                <ListItem
                  key={triggerType.id}
                  button
                  onClick={() => addTriggerNode(triggerType.id)}
                >
                  <ListItemIcon>
                    {triggerType.icon}
                  </ListItemIcon>
                  <ListItemText primary={triggerType.name} />
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      </Drawer>
      
      {/* Flow Code Dialog */}
      <Dialog
        open={codeDialogOpen}
        onClose={() => setCodeDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Flow Code</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={20}
            value={flowCode}
            InputProps={{
              readOnly: true
            }}
            sx={{ fontFamily: 'monospace' }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCodeDialogOpen(false)}>Close</Button>
          <Button
            onClick={() => {
              navigator.clipboard.writeText(flowCode);
              setNotification({
                open: true,
                message: 'Code copied to clipboard',
                severity: 'success'
              });
            }}
          >
            Copy to Clipboard
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Notification */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleCloseNotification}
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
      
      {/* Loading Overlay */}
      {loading && (
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'rgba(255, 255, 255, 0.7)',
            zIndex: 9999
          }}
        >
          <CircularProgress />
        </Box>
      )}
    </Box>
  );
};

export default WorkflowBuilder;
