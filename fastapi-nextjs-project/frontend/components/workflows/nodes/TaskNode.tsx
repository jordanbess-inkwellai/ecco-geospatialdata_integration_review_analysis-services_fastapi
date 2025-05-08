import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Box, Typography, Paper, Tooltip } from '@mui/material';
import CodeIcon from '@mui/icons-material/Code';
import TerminalIcon from '@mui/icons-material/Terminal';
import HttpIcon from '@mui/icons-material/Http';
import FolderIcon from '@mui/icons-material/Folder';
import StorageIcon from '@mui/icons-material/Storage';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

const TaskNode: React.FC<NodeProps> = ({ data, isConnectable, selected }) => {
  // Get the appropriate icon based on the task type
  const getTaskIcon = () => {
    switch (data.type) {
      case 'io.kestra.plugin.scripts.python.Script':
        return <CodeIcon />;
      case 'io.kestra.plugin.scripts.shell.Script':
        return <TerminalIcon />;
      case 'io.kestra.plugin.http.Request':
        return <HttpIcon />;
      case 'io.kestra.plugin.fs.http.Read':
      case 'io.kestra.plugin.fs.http.Write':
        return <FolderIcon />;
      case 'io.kestra.plugin.jdbc.Query':
        return <StorageIcon />;
      case 'io.kestra.plugin.core.flow.Trigger':
        return <PlayArrowIcon />;
      default:
        return null;
    }
  };

  // Get a short name for the task type
  const getTaskTypeName = () => {
    switch (data.type) {
      case 'io.kestra.plugin.scripts.python.Script':
        return 'Python Script';
      case 'io.kestra.plugin.scripts.shell.Script':
        return 'Shell Script';
      case 'io.kestra.plugin.http.Request':
        return 'HTTP Request';
      case 'io.kestra.plugin.fs.http.Read':
        return 'File Read';
      case 'io.kestra.plugin.fs.http.Write':
        return 'File Write';
      case 'io.kestra.plugin.jdbc.Query':
        return 'SQL Query';
      case 'io.kestra.plugin.core.flow.Trigger':
        return 'Flow Trigger';
      default:
        return 'Task';
    }
  };

  return (
    <Paper
      elevation={selected ? 8 : 3}
      sx={{
        padding: 1,
        borderRadius: 1,
        width: 200,
        height: 'auto',
        backgroundColor: selected ? '#f0f7ff' : 'white',
        border: selected ? '2px solid #1976d2' : '1px solid #e0e0e0'
      }}
    >
      <Handle
        type="target"
        position={Position.Left}
        isConnectable={isConnectable}
        style={{ background: '#555' }}
      />
      
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Box sx={{ mr: 1, color: 'primary.main' }}>
          {getTaskIcon()}
        </Box>
        <Tooltip title={data.type}>
          <Typography variant="subtitle2" noWrap>
            {getTaskTypeName()}
          </Typography>
        </Tooltip>
      </Box>
      
      <Typography variant="body1" fontWeight="bold" noWrap>
        {data.label || data.id}
      </Typography>
      
      {data.description && (
        <Typography variant="body2" color="text.secondary" noWrap>
          {data.description}
        </Typography>
      )}
      
      <Handle
        type="source"
        position={Position.Right}
        isConnectable={isConnectable}
        style={{ background: '#555' }}
      />
    </Paper>
  );
};

export default memo(TaskNode);
