import React, { useState, useEffect } from 'react';
import { 
  Box, 
  List, 
  ListItem, 
  ListItemButton, 
  ListItemText, 
  Typography, 
  TextField, 
  InputAdornment,
  CircularProgress,
  Paper,
  Divider,
  Collapse,
  ListItemIcon
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import VectorIcon from '@mui/icons-material/Category';
import RasterIcon from '@mui/icons-material/Grid4x4';
import InfoIcon from '@mui/icons-material/Info';
import { useDataProcessingOperations } from '../../hooks/useDataProcessingOperations';

interface Operation {
  id: string;
  name: string;
  description: string;
  inputs: Array<{
    name: string;
    type: string;
    description: string;
    options?: string[];
    required?: boolean;
  }>;
}

interface DataProcessingMenuProps {
  onSelectOperation: (operation: Operation) => void;
  selectedOperationId?: string;
}

const DataProcessingMenu: React.FC<DataProcessingMenuProps> = ({ 
  onSelectOperation, 
  selectedOperationId 
}) => {
  const { operations, loading, error } = useDataProcessingOperations();
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>({
    vector: true,
    raster: true,
    info: true
  });

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const toggleCategory = (category: string) => {
    setExpandedCategories({
      ...expandedCategories,
      [category]: !expandedCategories[category]
    });
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'vector':
        return <VectorIcon />;
      case 'raster':
        return <RasterIcon />;
      case 'info':
        return <InfoIcon />;
      default:
        return null;
    }
  };

  const filterOperations = (category: string, ops: Operation[]) => {
    if (!searchTerm) return ops;
    
    return ops.filter(op => 
      op.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      op.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      op.id.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={2}>
        <Typography color="error">Error loading operations: {error}</Typography>
      </Box>
    );
  }

  return (
    <Paper elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box p={2}>
        <Typography variant="h6" gutterBottom>
          Data Processing Tools
        </Typography>
        <TextField
          fullWidth
          placeholder="Search tools..."
          value={searchTerm}
          onChange={handleSearchChange}
          variant="outlined"
          size="small"
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Box>
      <Divider />
      <Box sx={{ overflow: 'auto', flexGrow: 1 }}>
        <List disablePadding>
          {Object.entries(operations).map(([category, ops]) => {
            const filteredOps = filterOperations(category, ops);
            
            // Skip empty categories after filtering
            if (filteredOps.length === 0) return null;
            
            return (
              <React.Fragment key={category}>
                <ListItemButton onClick={() => toggleCategory(category)}>
                  <ListItemIcon>
                    {getCategoryIcon(category)}
                  </ListItemIcon>
                  <ListItemText 
                    primary={category.charAt(0).toUpperCase() + category.slice(1)} 
                  />
                  {expandedCategories[category] ? <ExpandLess /> : <ExpandMore />}
                </ListItemButton>
                <Collapse in={expandedCategories[category]} timeout="auto" unmountOnExit>
                  <List component="div" disablePadding>
                    {filteredOps.map((operation) => (
                      <ListItemButton 
                        key={operation.id}
                        selected={selectedOperationId === operation.id}
                        onClick={() => onSelectOperation(operation)}
                        sx={{ pl: 4 }}
                      >
                        <ListItemText 
                          primary={operation.name} 
                          secondary={operation.description.length > 60 
                            ? `${operation.description.substring(0, 60)}...` 
                            : operation.description
                          } 
                        />
                      </ListItemButton>
                    ))}
                  </List>
                </Collapse>
              </React.Fragment>
            );
          })}
        </List>
      </Box>
    </Paper>
  );
};

export default DataProcessingMenu;
