import React, { useState, useEffect, useCallback, useRef } from 'react';
import ReactFlow, {
  ReactFlowProvider,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Panel,
  MarkerType,
  Node,
  Edge,
  ConnectionLineType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from 'dagre';
import axios from 'axios';

// Custom node types
import TableNode from './nodes/TableNode';

// Define node types
const nodeTypes = {
  table: TableNode,
};

// Define layout direction
const LAYOUT_DIRECTION = 'LR'; // LR = Left to Right, TB = Top to Bottom

interface ERDViewerProps {
  dataSourceId?: number;
  schemaData?: any;
  height?: string;
  width?: string;
  onNodeClick?: (node: Node) => void;
  onEdgeClick?: (edge: Edge) => void;
  readOnly?: boolean;
}

const ERDViewer: React.FC<ERDViewerProps> = ({
  dataSourceId,
  schemaData,
  height = '600px',
  width = '100%',
  onNodeClick,
  onEdgeClick,
  readOnly = true,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const reactFlowWrapper = useRef<HTMLDivElement>(null);

  // Function to fetch schema data from API
  const fetchSchemaData = useCallback(async () => {
    if (!dataSourceId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`/api/v1/erd/schema/${dataSourceId}`);
      const data = response.data;
      
      // Process nodes and edges
      setNodes(data.nodes || []);
      setEdges(data.edges || []);
      
      // Apply layout
      setTimeout(() => {
        getLayoutedElements(data.nodes || [], data.edges || []);
      }, 100);
    } catch (err) {
      console.error('Error fetching schema data:', err);
      setError('Failed to fetch schema data. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [dataSourceId, setNodes, setEdges]);

  // Use schema data if provided directly
  useEffect(() => {
    if (schemaData) {
      setNodes(schemaData.nodes || []);
      setEdges(schemaData.edges || []);
      
      // Apply layout
      setTimeout(() => {
        getLayoutedElements(schemaData.nodes || [], schemaData.edges || []);
      }, 100);
    }
  }, [schemaData, setNodes, setEdges]);

  // Fetch schema data if dataSourceId is provided
  useEffect(() => {
    if (dataSourceId && !schemaData) {
      fetchSchemaData();
    }
  }, [dataSourceId, schemaData, fetchSchemaData]);

  // Function to layout nodes and edges using dagre
  const getLayoutedElements = useCallback(
    (nodes: Node[], edges: Edge[]) => {
      if (!nodes.length) return { nodes, edges };

      const dagreGraph = new dagre.graphlib.Graph();
      dagreGraph.setDefaultEdgeLabel(() => ({}));
      dagreGraph.setGraph({ rankdir: LAYOUT_DIRECTION });

      // Add nodes to dagre graph
      nodes.forEach((node) => {
        dagreGraph.setNode(node.id, { width: 250, height: 200 });
      });

      // Add edges to dagre graph
      edges.forEach((edge) => {
        dagreGraph.setEdge(edge.source, edge.target);
      });

      // Calculate layout
      dagre.layout(dagreGraph);

      // Apply layout to nodes
      const layoutedNodes = nodes.map((node) => {
        const nodeWithPosition = dagreGraph.node(node.id);
        return {
          ...node,
          position: {
            x: nodeWithPosition.x - 125, // Center node
            y: nodeWithPosition.y - 100, // Center node
          },
        };
      });

      setNodes(layoutedNodes);
      return { nodes: layoutedNodes, edges };
    },
    [setNodes]
  );

  // Handle node click
  const handleNodeClick = useCallback(
    (event: React.MouseEvent, node: Node) => {
      if (onNodeClick) {
        onNodeClick(node);
      }
    },
    [onNodeClick]
  );

  // Handle edge click
  const handleEdgeClick = useCallback(
    (event: React.MouseEvent, edge: Edge) => {
      if (onEdgeClick) {
        onEdgeClick(edge);
      }
    },
    [onEdgeClick]
  );

  // Export diagram as image
  const exportAsPNG = useCallback(() => {
    if (reactFlowWrapper.current) {
      const dataUrl = (reactFlowWrapper.current as any).toDataURL('image/png');
      const link = document.createElement('a');
      link.download = `erd-${dataSourceId || 'diagram'}.png`;
      link.href = dataUrl;
      link.click();
    }
  }, [dataSourceId]);

  return (
    <div style={{ height, width }} ref={reactFlowWrapper}>
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>Loading schema...</p>
        </div>
      )}
      
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={fetchSchemaData}>Retry</button>
        </div>
      )}
      
      <ReactFlowProvider>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          onNodeClick={handleNodeClick}
          onEdgeClick={handleEdgeClick}
          fitView
          attributionPosition="bottom-right"
          connectionLineType={ConnectionLineType.SmoothStep}
          defaultEdgeOptions={{
            type: 'smoothstep',
            markerEnd: {
              type: MarkerType.ArrowClosed,
            },
            style: { stroke: '#555', strokeWidth: 1.5 },
          }}
          proOptions={{ hideAttribution: true }}
          nodesDraggable={!readOnly}
          nodesConnectable={!readOnly}
          elementsSelectable={true}
        >
          <Controls />
          <Background color="#f0f0f0" gap={16} />
          
          <Panel position="top-right">
            <div className="erd-controls">
              <button onClick={exportAsPNG} className="export-button">
                Export as PNG
              </button>
              <button onClick={() => getLayoutedElements(nodes, edges)} className="layout-button">
                Reset Layout
              </button>
            </div>
          </Panel>
        </ReactFlow>
      </ReactFlowProvider>
      
      <style jsx>{`
        .loading-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(255, 255, 255, 0.8);
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          z-index: 10;
        }
        
        .loading-spinner {
          border: 4px solid #f3f3f3;
          border-top: 4px solid #3498db;
          border-radius: 50%;
          width: 40px;
          height: 40px;
          animation: spin 2s linear infinite;
          margin-bottom: 1rem;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .error-message {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          background-color: #f8d7da;
          color: #721c24;
          padding: 1rem;
          border-radius: 4px;
          text-align: center;
          z-index: 10;
        }
        
        .error-message button {
          background-color: #dc3545;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          cursor: pointer;
          margin-top: 0.5rem;
        }
        
        .erd-controls {
          display: flex;
          gap: 0.5rem;
        }
        
        .export-button,
        .layout-button {
          background-color: white;
          border: 1px solid #ccc;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.875rem;
          display: flex;
          align-items: center;
          gap: 0.25rem;
        }
        
        .export-button:hover,
        .layout-button:hover {
          background-color: #f0f0f0;
        }
      `}</style>
    </div>
  );
};

export default ERDViewer;
