import React, { useState, useRef, useCallback, useEffect } from 'react';
import ReactFlow, {
  ReactFlowProvider,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  Panel,
  Connection,
  Edge,
  Node,
  NodeTypes,
  EdgeTypes,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';

import ReaderNode from './nodes/ReaderNode';
import TransformerNode from './nodes/TransformerNode';
import WriterNode from './nodes/WriterNode';
import TriggerNode from './nodes/TriggerNode';
import NodeSelector from './NodeSelector';
import WorkflowProperties from './WorkflowProperties';
import NodeConfigPanel from './NodeConfigPanel';
import axios from 'axios';

// Define custom node types
const nodeTypes: NodeTypes = {
  reader: ReaderNode,
  transformer: TransformerNode,
  writer: WriterNode,
  trigger: TriggerNode
};

interface WorkflowBuilderProps {
  initialWorkflow?: any;
  onSave?: (workflow: any) => void;
}

const WorkflowBuilder: React.FC<WorkflowBuilderProps> = ({ initialWorkflow, onSave }) => {
  // Workflow metadata
  const [workflowName, setWorkflowName] = useState<string>(initialWorkflow?.name || 'New Workflow');
  const [workflowNamespace, setWorkflowNamespace] = useState<string>(initialWorkflow?.namespace || 'default');
  const [workflowDescription, setWorkflowDescription] = useState<string>(initialWorkflow?.description || '');
  
  // Flow state
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<Edge | null>(null);
  const [showNodeSelector, setShowNodeSelector] = useState<boolean>(false);
  const [nodeSelectorPosition, setNodeSelectorPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [isValidating, setIsValidating] = useState<boolean>(false);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  
  // Refs
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const reactFlowInstance = useRef<any>(null);
  
  // Initialize workflow if provided
  useEffect(() => {
    if (initialWorkflow) {
      // Convert initialWorkflow to nodes and edges
      try {
        const { nodes: initialNodes, edges: initialEdges } = convertWorkflowToFlow(initialWorkflow);
        setNodes(initialNodes);
        setEdges(initialEdges);
      } catch (error) {
        console.error('Error initializing workflow:', error);
      }
    }
  }, [initialWorkflow, setNodes, setEdges]);
  
  // Handle flow initialization
  const onInit = useCallback((instance: any) => {
    reactFlowInstance.current = instance;
  }, []);
  
  // Handle node click
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
    setSelectedEdge(null);
  }, []);
  
  // Handle edge click
  const onEdgeClick = useCallback((event: React.MouseEvent, edge: Edge) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
  }, []);
  
  // Handle pane click (background)
  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
    setSelectedEdge(null);
    setShowNodeSelector(false);
  }, []);
  
  // Handle connection between nodes
  const onConnect = useCallback(
    (connection: Connection) => {
      // Check if connection is valid
      const sourceNode = nodes.find(node => node.id === connection.source);
      const targetNode = nodes.find(node => node.id === connection.target);
      
      if (!sourceNode || !targetNode) return;
      
      // Prevent connecting to a trigger node
      if (targetNode.type === 'trigger') {
        return;
      }
      
      // Prevent connecting from a writer node
      if (sourceNode.type === 'writer') {
        return;
      }
      
      // Add the edge with a marker
      const newEdge = {
        ...connection,
        animated: true,
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 20,
          height: 20
        },
        style: { stroke: '#0041d0' }
      };
      
      setEdges(eds => addEdge(newEdge, eds));
    },
    [nodes, setEdges]
  );
  
  // Handle node drag
  const onNodeDragStart = useCallback(() => {
    setIsDragging(true);
  }, []);
  
  const onNodeDragStop = useCallback(() => {
    setIsDragging(false);
  }, []);
  
  // Handle right-click to add node
  const onPaneContextMenu = useCallback(
    (event: React.MouseEvent) => {
      event.preventDefault();
      
      if (!reactFlowWrapper.current) return;
      
      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const position = reactFlowInstance.current.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top
      });
      
      setNodeSelectorPosition(position);
      setShowNodeSelector(true);
    },
    [reactFlowInstance]
  );
  
  // Add a new node
  const addNode = useCallback(
    (type: string, data: any = {}) => {
      const newNode = {
        id: `${type}_${Date.now()}`,
        type,
        position: nodeSelectorPosition,
        data: {
          label: `New ${type.charAt(0).toUpperCase() + type.slice(1)}`,
          ...data
        }
      };
      
      setNodes(nds => [...nds, newNode]);
      setShowNodeSelector(false);
      setSelectedNode(newNode);
    },
    [nodeSelectorPosition, setNodes]
  );
  
  // Update node data
  const updateNodeData = useCallback(
    (nodeId: string, newData: any) => {
      setNodes(nds =>
        nds.map(node => {
          if (node.id === nodeId) {
            return {
              ...node,
              data: {
                ...node.data,
                ...newData
              }
            };
          }
          return node;
        })
      );
      
      // Update selected node if it's the one being edited
      if (selectedNode && selectedNode.id === nodeId) {
        setSelectedNode({
          ...selectedNode,
          data: {
            ...selectedNode.data,
            ...newData
          }
        });
      }
    },
    [selectedNode, setNodes]
  );
  
  // Delete selected element
  const deleteSelected = useCallback(() => {
    if (selectedNode) {
      setNodes(nodes => nodes.filter(node => node.id !== selectedNode.id));
      setSelectedNode(null);
    }
    
    if (selectedEdge) {
      setEdges(edges => edges.filter(edge => edge.id !== selectedEdge.id));
      setSelectedEdge(null);
    }
  }, [selectedNode, selectedEdge, setNodes, setEdges]);
  
  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Delete' || event.key === 'Backspace') {
        deleteSelected();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [deleteSelected]);
  
  // Validate workflow
  const validateWorkflow = useCallback(() => {
    setIsValidating(true);
    setValidationErrors([]);
    
    const errors = [];
    
    // Check if workflow has a name
    if (!workflowName.trim()) {
      errors.push('Workflow must have a name');
    }
    
    // Check if workflow has at least one node
    if (nodes.length === 0) {
      errors.push('Workflow must have at least one node');
    }
    
    // Check if workflow has at least one reader and one writer
    const hasReader = nodes.some(node => node.type === 'reader');
    const hasWriter = nodes.some(node => node.type === 'writer');
    
    if (!hasReader) {
      errors.push('Workflow must have at least one reader node');
    }
    
    if (!hasWriter) {
      errors.push('Workflow must have at least one writer node');
    }
    
    // Check if all nodes are connected
    const connectedNodeIds = new Set<string>();
    
    // Add all source and target nodes from edges
    edges.forEach(edge => {
      connectedNodeIds.add(edge.source);
      connectedNodeIds.add(edge.target);
    });
    
    // Check for isolated nodes (except triggers)
    nodes.forEach(node => {
      if (node.type !== 'trigger' && !connectedNodeIds.has(node.id)) {
        errors.push(`Node "${node.data.label}" is not connected to any other node`);
      }
    });
    
    // Check if all nodes have required configuration
    nodes.forEach(node => {
      if (node.type === 'reader' && (!node.data.sourceType || !node.data.sourceConfig)) {
        errors.push(`Reader node "${node.data.label}" is missing configuration`);
      }
      
      if (node.type === 'writer' && (!node.data.destinationType || !node.data.destinationConfig)) {
        errors.push(`Writer node "${node.data.label}" is missing configuration`);
      }
      
      if (node.type === 'transformer' && !node.data.transformationType) {
        errors.push(`Transformer node "${node.data.label}" is missing configuration`);
      }
    });
    
    setValidationErrors(errors);
    setIsValidating(false);
    
    return errors.length === 0;
  }, [workflowName, nodes, edges]);
  
  // Convert flow to Kestra workflow
  const convertFlowToWorkflow = useCallback(() => {
    // Create workflow object
    const workflow = {
      id: workflowName.toLowerCase().replace(/[^a-z0-9]/g, '_'),
      namespace: workflowNamespace,
      tasks: [],
      inputs: []
    };
    
    if (workflowDescription) {
      workflow.description = workflowDescription;
    }
    
    // Add triggers if any
    const triggerNodes = nodes.filter(node => node.type === 'trigger');
    if (triggerNodes.length > 0) {
      workflow.triggers = triggerNodes.map(node => {
        const { triggerType, ...triggerConfig } = node.data.triggerConfig || {};
        return {
          type: triggerType,
          ...triggerConfig
        };
      });
    }
    
    // Process nodes to create tasks
    // This is a simplified version - in a real implementation, you'd need to handle the DAG properly
    const readerNodes = nodes.filter(node => node.type === 'reader');
    const transformerNodes = nodes.filter(node => node.type === 'transformer');
    const writerNodes = nodes.filter(node => node.type === 'writer');
    
    // Add reader tasks
    readerNodes.forEach(node => {
      const task = {
        id: node.id,
        type: getTaskTypeForSource(node.data.sourceType),
        name: node.data.label,
        ...node.data.sourceConfig
      };
      
      workflow.tasks.push(task);
    });
    
    // Add transformer tasks with dependencies
    transformerNodes.forEach(node => {
      // Find incoming edges to determine dependencies
      const incomingEdges = edges.filter(edge => edge.target === node.id);
      const dependencies = incomingEdges.map(edge => edge.source);
      
      const task = {
        id: node.id,
        type: getTaskTypeForTransformation(node.data.transformationType),
        name: node.data.label,
        ...node.data.transformationConfig,
        dependsOn: dependencies
      };
      
      workflow.tasks.push(task);
    });
    
    // Add writer tasks with dependencies
    writerNodes.forEach(node => {
      // Find incoming edges to determine dependencies
      const incomingEdges = edges.filter(edge => edge.target === node.id);
      const dependencies = incomingEdges.map(edge => edge.source);
      
      const task = {
        id: node.id,
        type: getTaskTypeForDestination(node.data.destinationType),
        name: node.data.label,
        ...node.data.destinationConfig,
        dependsOn: dependencies
      };
      
      workflow.tasks.push(task);
    });
    
    return workflow;
  }, [workflowName, workflowNamespace, workflowDescription, nodes, edges]);
  
  // Helper function to get task type for source
  const getTaskTypeForSource = (sourceType: string) => {
    switch (sourceType) {
      case 'postgres':
        return 'io.kestra.plugin.jdbc.postgresql.Query';
      case 'mysql':
        return 'io.kestra.plugin.jdbc.mysql.Query';
      case 'http':
        return 'io.kestra.plugin.core.http.Request';
      case 'file':
        return 'io.kestra.plugin.core.fs.Read';
      case 'duckdb':
        return 'io.kestra.plugin.jdbc.duckdb.Query';
      default:
        return 'io.kestra.plugin.core.flow.Task';
    }
  };
  
  // Helper function to get task type for transformation
  const getTaskTypeForTransformation = (transformationType: string) => {
    switch (transformationType) {
      case 'python':
        return 'io.kestra.plugin.scripts.python.Python';
      case 'javascript':
        return 'io.kestra.plugin.scripts.js.EvalJs';
      case 'groovy':
        return 'io.kestra.plugin.scripts.groovy.Eval';
      case 'jq':
        return 'io.kestra.plugin.core.json.Jq';
      default:
        return 'io.kestra.plugin.core.flow.Task';
    }
  };
  
  // Helper function to get task type for destination
  const getTaskTypeForDestination = (destinationType: string) => {
    switch (destinationType) {
      case 'postgres':
        return 'io.kestra.plugin.jdbc.postgresql.Insert';
      case 'mysql':
        return 'io.kestra.plugin.jdbc.mysql.Insert';
      case 'file':
        return 'io.kestra.plugin.core.fs.Write';
      case 'duckdb':
        return 'io.kestra.plugin.jdbc.duckdb.Insert';
      case 's3':
        return 'io.kestra.plugin.aws.s3.Upload';
      default:
        return 'io.kestra.plugin.core.flow.Task';
    }
  };
  
  // Helper function to convert Kestra workflow to flow
  const convertWorkflowToFlow = (workflow: any) => {
    const nodes: Node[] = [];
    const edges: Edge[] = [];
    
    // Process tasks
    if (workflow.tasks && Array.isArray(workflow.tasks)) {
      workflow.tasks.forEach((task: any, index: number) => {
        // Determine node type based on task type
        let nodeType = 'transformer';
        if (task.type.includes('Query') || task.type.includes('Read') || task.type.includes('Request')) {
          nodeType = 'reader';
        } else if (task.type.includes('Insert') || task.type.includes('Write') || task.type.includes('Upload')) {
          nodeType = 'writer';
        }
        
        // Create node
        const node: Node = {
          id: task.id || `task_${index}`,
          type: nodeType,
          position: { x: 100 + (index % 3) * 250, y: 100 + Math.floor(index / 3) * 150 },
          data: {
            label: task.name || task.id || `Task ${index + 1}`
          }
        };
        
        // Add specific configuration based on node type
        if (nodeType === 'reader') {
          node.data.sourceType = getSourceTypeFromTask(task.type);
          node.data.sourceConfig = { ...task };
          delete node.data.sourceConfig.id;
          delete node.data.sourceConfig.type;
          delete node.data.sourceConfig.name;
        } else if (nodeType === 'writer') {
          node.data.destinationType = getDestinationTypeFromTask(task.type);
          node.data.destinationConfig = { ...task };
          delete node.data.destinationConfig.id;
          delete node.data.destinationConfig.type;
          delete node.data.destinationConfig.name;
          delete node.data.destinationConfig.dependsOn;
        } else {
          node.data.transformationType = getTransformationTypeFromTask(task.type);
          node.data.transformationConfig = { ...task };
          delete node.data.transformationConfig.id;
          delete node.data.transformationConfig.type;
          delete node.data.transformationConfig.name;
          delete node.data.transformationConfig.dependsOn;
        }
        
        nodes.push(node);
        
        // Create edges for dependencies
        if (task.dependsOn && Array.isArray(task.dependsOn)) {
          task.dependsOn.forEach((sourceId: string) => {
            edges.push({
              id: `edge_${sourceId}_${task.id}`,
              source: sourceId,
              target: task.id,
              animated: true,
              markerEnd: {
                type: MarkerType.ArrowClosed,
                width: 20,
                height: 20
              },
              style: { stroke: '#0041d0' }
            });
          });
        }
      });
    }
    
    // Process triggers
    if (workflow.triggers && Array.isArray(workflow.triggers)) {
      workflow.triggers.forEach((trigger: any, index: number) => {
        const node: Node = {
          id: `trigger_${index}`,
          type: 'trigger',
          position: { x: 100 + index * 250, y: 20 },
          data: {
            label: `Trigger ${index + 1}`,
            triggerConfig: {
              triggerType: trigger.type,
              ...trigger
            }
          }
        };
        
        delete node.data.triggerConfig.type;
        
        nodes.push(node);
      });
    }
    
    return { nodes, edges };
  };
  
  // Helper function to get source type from task type
  const getSourceTypeFromTask = (taskType: string) => {
    if (taskType.includes('postgresql')) return 'postgres';
    if (taskType.includes('mysql')) return 'mysql';
    if (taskType.includes('http')) return 'http';
    if (taskType.includes('fs.Read')) return 'file';
    if (taskType.includes('duckdb')) return 'duckdb';
    return 'unknown';
  };
  
  // Helper function to get transformation type from task type
  const getTransformationTypeFromTask = (taskType: string) => {
    if (taskType.includes('python')) return 'python';
    if (taskType.includes('js')) return 'javascript';
    if (taskType.includes('groovy')) return 'groovy';
    if (taskType.includes('json.Jq')) return 'jq';
    return 'unknown';
  };
  
  // Helper function to get destination type from task type
  const getDestinationTypeFromTask = (taskType: string) => {
    if (taskType.includes('postgresql')) return 'postgres';
    if (taskType.includes('mysql')) return 'mysql';
    if (taskType.includes('fs.Write')) return 'file';
    if (taskType.includes('duckdb')) return 'duckdb';
    if (taskType.includes('s3')) return 's3';
    return 'unknown';
  };
  
  // Save workflow
  const saveWorkflow = useCallback(async () => {
    // Validate workflow first
    const isValid = validateWorkflow();
    if (!isValid) {
      return;
    }
    
    setIsSaving(true);
    setSaveSuccess(false);
    setSaveError(null);
    
    try {
      // Convert flow to workflow
      const workflow = convertFlowToWorkflow();
      
      // If onSave callback is provided, use it
      if (onSave) {
        onSave(workflow);
        setSaveSuccess(true);
      } else {
        // Otherwise, save via API
        const response = await axios.post('/api/v1/kestra/workflows', workflow);
        setSaveSuccess(true);
      }
    } catch (error) {
      console.error('Error saving workflow:', error);
      setSaveError('Failed to save workflow. Please try again.');
    } finally {
      setIsSaving(false);
    }
  }, [validateWorkflow, convertFlowToWorkflow, onSave]);
  
  return (
    <div className="workflow-builder">
      <div className="workflow-header">
        <div className="workflow-title">
          <h2>Visual Workflow Builder</h2>
          <div className="workflow-actions">
            <button 
              className="validate-button"
              onClick={validateWorkflow}
              disabled={isValidating}
            >
              {isValidating ? 'Validating...' : 'Validate'}
            </button>
            <button 
              className="save-button"
              onClick={saveWorkflow}
              disabled={isSaving}
            >
              {isSaving ? 'Saving...' : 'Save Workflow'}
            </button>
          </div>
        </div>
        
        {validationErrors.length > 0 && (
          <div className="validation-errors">
            <h4>Validation Errors:</h4>
            <ul>
              {validationErrors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </div>
        )}
        
        {saveSuccess && (
          <div className="save-success">
            Workflow saved successfully!
          </div>
        )}
        
        {saveError && (
          <div className="save-error">
            {saveError}
          </div>
        )}
      </div>
      
      <div className="workflow-content">
        <div className="flow-container" ref={reactFlowWrapper}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={onInit}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
            onPaneClick={onPaneClick}
            onNodeDragStart={onNodeDragStart}
            onNodeDragStop={onNodeDragStop}
            onContextMenu={onPaneContextMenu}
            nodeTypes={nodeTypes}
            fitView
            snapToGrid
            snapGrid={[15, 15]}
          >
            <Controls />
            <Background color="#aaa" gap={16} />
            
            <Panel position="top-left">
              <WorkflowProperties
                name={workflowName}
                namespace={workflowNamespace}
                description={workflowDescription}
                onNameChange={setWorkflowName}
                onNamespaceChange={setWorkflowNamespace}
                onDescriptionChange={setWorkflowDescription}
              />
            </Panel>
            
            {showNodeSelector && (
              <NodeSelector
                position={nodeSelectorPosition}
                onSelect={addNode}
                onClose={() => setShowNodeSelector(false)}
              />
            )}
          </ReactFlow>
        </div>
        
        {selectedNode && (
          <NodeConfigPanel
            node={selectedNode}
            onUpdate={updateNodeData}
            onDelete={deleteSelected}
          />
        )}
      </div>
      
      <style jsx>{`
        .workflow-builder {
          display: flex;
          flex-direction: column;
          height: calc(100vh - 100px);
          width: 100%;
        }
        
        .workflow-header {
          padding: 1rem;
          background-color: #f8f9fa;
          border-bottom: 1px solid #ddd;
        }
        
        .workflow-title {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .workflow-title h2 {
          margin: 0;
          font-size: 1.5rem;
          color: #333;
        }
        
        .workflow-actions {
          display: flex;
          gap: 1rem;
        }
        
        .validate-button, .save-button {
          padding: 0.5rem 1rem;
          border-radius: 4px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .validate-button {
          background-color: #f8f9fa;
          color: #333;
          border: 1px solid #ddd;
        }
        
        .validate-button:hover {
          background-color: #e9ecef;
        }
        
        .save-button {
          background-color: #0070f3;
          color: white;
          border: none;
        }
        
        .save-button:hover {
          background-color: #0051a8;
        }
        
        .save-button:disabled, .validate-button:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }
        
        .validation-errors {
          margin-top: 1rem;
          padding: 0.75rem;
          background-color: #f8d7da;
          color: #721c24;
          border-radius: 4px;
        }
        
        .validation-errors h4 {
          margin: 0 0 0.5rem;
          font-size: 1rem;
        }
        
        .validation-errors ul {
          margin: 0;
          padding-left: 1.5rem;
        }
        
        .save-success {
          margin-top: 1rem;
          padding: 0.75rem;
          background-color: #d1e7dd;
          color: #0f5132;
          border-radius: 4px;
        }
        
        .save-error {
          margin-top: 1rem;
          padding: 0.75rem;
          background-color: #f8d7da;
          color: #721c24;
          border-radius: 4px;
        }
        
        .workflow-content {
          display: flex;
          flex: 1;
          overflow: hidden;
        }
        
        .flow-container {
          flex: 1;
          height: 100%;
        }
      `}</style>
    </div>
  );
};

// Wrap with ReactFlowProvider
const WorkflowBuilderWithProvider: React.FC<WorkflowBuilderProps> = (props) => {
  return (
    <ReactFlowProvider>
      <WorkflowBuilder {...props} />
    </ReactFlowProvider>
  );
};

export default WorkflowBuilderWithProvider;
