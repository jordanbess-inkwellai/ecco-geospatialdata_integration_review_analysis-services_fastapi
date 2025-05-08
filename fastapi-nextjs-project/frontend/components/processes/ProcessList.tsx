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
  Divider
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { useProcesses } from '../../hooks/useProcesses';

interface Process {
  id: string;
  title: string;
  description: string;
}

interface ProcessListProps {
  onSelectProcess: (processId: string) => void;
  selectedProcessId?: string;
}

const ProcessList: React.FC<ProcessListProps> = ({ onSelectProcess, selectedProcessId }) => {
  const { processes, loading, error } = useProcesses();
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredProcesses, setFilteredProcesses] = useState<Process[]>([]);

  useEffect(() => {
    if (processes) {
      setFilteredProcesses(
        processes.filter((process) => 
          process.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          process.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
          process.description.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }
  }, [processes, searchTerm]);

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
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
        <Typography color="error">Error loading processes: {error}</Typography>
      </Box>
    );
  }

  return (
    <Paper elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box p={2}>
        <Typography variant="h6" gutterBottom>
          OGC API Processes
        </Typography>
        <TextField
          fullWidth
          placeholder="Search processes..."
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
          {filteredProcesses.length > 0 ? (
            filteredProcesses.map((process) => (
              <ListItem key={process.id} disablePadding>
                <ListItemButton 
                  selected={selectedProcessId === process.id}
                  onClick={() => onSelectProcess(process.id)}
                >
                  <ListItemText 
                    primary={process.title} 
                    secondary={process.description.length > 60 
                      ? `${process.description.substring(0, 60)}...` 
                      : process.description
                    } 
                  />
                </ListItemButton>
              </ListItem>
            ))
          ) : (
            <ListItem>
              <ListItemText 
                primary={searchTerm ? "No matching processes found" : "No processes available"} 
              />
            </ListItem>
          )}
        </List>
      </Box>
    </Paper>
  );
};

export default ProcessList;
