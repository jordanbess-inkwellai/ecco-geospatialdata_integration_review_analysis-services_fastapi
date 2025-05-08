import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Box, Typography, Paper, Tooltip } from '@mui/material';
import WebhookIcon from '@mui/icons-material/Webhook';
import ScheduleIcon from '@mui/icons-material/Schedule';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

const TriggerNode: React.FC<NodeProps> = ({ data, isConnectable, selected }) => {
  // Get the appropriate icon based on the trigger type
  const getTriggerIcon = () => {
    switch (data.type) {
      case 'io.kestra.plugin.webhook.Trigger':
        return <WebhookIcon />;
      case 'io.kestra.plugin.schedules.Schedule':
        return <ScheduleIcon />;
      case 'io.kestra.plugin.core.trigger.Flow':
        return <PlayArrowIcon />;
      default:
        return null;
    }
  };

  // Get a short name for the trigger type
  const getTriggerTypeName = () => {
    switch (data.type) {
      case 'io.kestra.plugin.webhook.Trigger':
        return 'Webhook';
      case 'io.kestra.plugin.schedules.Schedule':
        return 'Schedule';
      case 'io.kestra.plugin.core.trigger.Flow':
        return 'Flow';
      default:
        return 'Trigger';
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
        backgroundColor: selected ? '#fff8e1' : '#fffde7',
        border: selected ? '2px solid #ffc107' : '1px solid #e0e0e0'
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Box sx={{ mr: 1, color: 'warning.main' }}>
          {getTriggerIcon()}
        </Box>
        <Tooltip title={data.type}>
          <Typography variant="subtitle2" noWrap>
            {getTriggerTypeName()}
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
        style={{ background: '#ffc107' }}
      />
    </Paper>
  );
};

export default memo(TriggerNode);
