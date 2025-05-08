import React, { useState, useCallback, useEffect, ChangeEvent } from 'react'
import ReactFlow, {
  Background,
  Controls,
  Edge,
  EdgeTypes,
  Node,
  Panel,
} from 'reactflow'
import PostgisConnectionForm from './PostgisConnectionForm';
import ArcgisLoginForm from './ArcgisLoginForm';

import { create } from 'zustand'

import { v4 as uuidv4 } from 'uuid'
import 'reactflow/dist/style.css'

type RFState = {
  nodes: Node[];
  edges: Edge[];
  addNode: (node: Node) => void
  addEdge: (edge: Edge) => void
};
type ConnectionState = {
  host: string
  database: string
  user: string
  password: string
  setPostgisHost: (host: string) => void;
  setPostgisDatabase: (database: string) => void;
  setPostgisUser: (user: string) => void;
  setPostgisPassword: (password: string) => void;
  username: string
  arcgisPassword: string
  setArcgisUsername: (username: string) => void;
  setArcgisPassword: (arcgisPassword: string) => void;
  fileGdbPath: string;
  setFileGdbPath: (fileGdbPath: string) => void;
  report: string;
  setReport: (report: string) => void;
};

const useStore = create<RFState & ConnectionState>((set) => ({
  nodes: [],
  edges: [],
  addNode: (node) => set((state) => ({ nodes: [...state.nodes, node] })),
  addEdge: (edge) => set((state) => ({ edges: [...state.edges, edge] })),  
  host: '', database: '', user: '', password: '',  
  setPostgisHost: (host) => set({ host }),
  setPostgisDatabase: (database) => set({ database }),
  setPostgisUser: (user) => set({ user }),
  setPostgisPassword: (password) => set({ password }),
  username: '', arcgisPassword: '',  
  setArcgisUsername: (username) => set({ username }),
  setArcgisPassword: (arcgisPassword) => set({ arcgisPassword }),
  fileGdbPath: 'test/data.gdb',
  setFileGdbPath: (fileGdbPath: string) => set({ fileGdbPath }),
  report: '',
  setReport: (report: string) => set({ report }),
}));

const getRandomPosition = () => {
  return {
    x: Math.random() * 500,
    y: Math.random() * 400,
  }
}

const nodeStyles = {
  borderRadius: '10px',
  backgroundColor: '#f0f0f0',
  border: '1px solid #ccc',
  color: 'black',
  minWidth: '150px',
  height: '50px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '5px'
}

const edgeStyles = {
  stroke: '#444',
  strokeWidth: 3,
  curve: 'smoothstep',
};

const defaultEdgeOptions = { type: 'smoothstep' };
const ErdEditor: React.FC = () => {
  const { nodes, edges, addNode, addEdge, host, database, user, password, username, arcgisPassword, fileGdbPath, setFileGdbPath, report, setReport } = useStore();

  
  useEffect(() => {
    addNode({
        id: 'table1',
        data: { label: 'table1' },        
        position: { x: 100, y: 100 },
        style: nodeStyles
    });
    addNode({
        id: 'table2',
        data: { label: 'table2' },
        position: { x: 400, y: 100 },
        style: nodeStyles
    });
    addNode({
        id: 'table3',
        style: nodeStyles,
        data: { label: 'table3' },
        position: { x: 400, y: 300 },
    });    
    addEdge({ id: 'e1-2', source: 'table1', target: 'table2', label: 'one-to-many', style: edgeStyles })
    addEdge({ id: 'e2-3', source: 'table2', target: 'table3', label: 'one-to-many', style: edgeStyles })
  }, [])

  const handleAddTable = useCallback(() => {
    const newTableId = uuidv4()
    const newTable = {
      id: `table-${newTableId}`,
      data: { label: `Table ${newTableId}` },
      position: {
        ...getRandomPosition()
      }, style: nodeStyles    }
    addNode(newTable)
  }, [])

    const onConnect = useCallback((connection: Edge) => {
        const newEdge = { ...connection, id: `e-${connection.source}-${connection.target}`, label: 'one-to-many', style: edgeStyles};
        addEdge(newEdge);
    }, [addEdge]);
    
    const handleCreateDatabase = useCallback(async () => {
      // Call to the client with the postgis agent data
      console.log('Sending create database request to client')
      const agent_name = "PostgisAgent";
      const method = "create_postgis_schema";
      const data = { host, database, user, password };
       // This is a dummy response for now, since we do not have the mcp server running
       //Dummy response
      const response = {"result": "Dummy response received", "report":"dummy report"};
      if (response.report) {
        setReport(response.report);
      }
      // This is a dummy response for now, since we do not have the mcp server running
      const response = "Dummy response from mcp server"
      console.log('Create Database Response:', response);
    }, [host, database, user, password]);

    const handleFileGdbConversion = useCallback(async () => {
      // Call to the client with the filegdb agent data
      console.log('Sending filegdb conversion request to client')
      const agent_name = "FileGDBAgent";
      const method = "handle_filegdb";
      const data = fileGdbPath
      //Dummy response
      const response = {"result": "Dummy response received", "report":"dummy report"};
      if (response.report) {
        setReport(response.report);
      }
      console.log('FileGDB Conversion Response:', response);
    }, [fileGdbPath]);

    const handleFileGdbPathChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
      if (event.target.value) {
        const newPath = event.target.value
        setFileGdbPath(newPath)
        console.log('FileGDB path:', newPath);
      } else {
        console.log('No FileGDB path');
      }
    }, [host, database, user, password]);
    useEffect(() => {
        console.log("Report:", report);
      }, [report]);

    const CustomNode: React.FC<any> = ({ data }) => {
        return (
          <div style={nodeStyles}>
            {data.label}
          </div>
        );
    }, [addEdge]);

    return (
    <div style={{ height: '600px' }}>
      <ReactFlow nodes={nodes} edges={edges} fitView onConnect={onConnect}>
        <Panel position="top-left">
          <p>ERD Editor</p>
          <button onClick={handleAddTable}>Add Table</button>
          <button onClick={handleCreateDatabase}>Create Database</button>
          <p>FileGDB path:</p>
          <input type='text' placeholder='path' id='filegdbpath' name='filegdbpath' value={fileGdbPath} onChange={handleFileGdbPathChange} />
          <button onClick={handleFileGdbConversion}>
            Convert filegdb
          </button>
        </Panel>
        <Controls />
        <Background />        
      </ReactFlow>
      <div>
        <p>Postgis Connection:</p>
        <PostgisConnectionForm/>
        <p>ArcGIS Online Login:</p>
        <ArcgisLoginForm />
      </div>
    </div>

  )
}

export default ErdEditor