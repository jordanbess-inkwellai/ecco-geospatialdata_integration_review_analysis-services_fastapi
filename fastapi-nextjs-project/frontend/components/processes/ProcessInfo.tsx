import React from 'react';
import { 
  Box, 
  Typography, 
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip
} from '@mui/material';

interface ProcessInfoProps {
  process: any;
}

const ProcessInfo: React.FC<ProcessInfoProps> = ({ process }) => {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>Description</Typography>
      <Typography paragraph>{process.description}</Typography>

      {/* Inputs */}
      <Typography variant="h6" gutterBottom>Inputs</Typography>
      <TableContainer component={Paper} variant="outlined" sx={{ mb: 3 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Required</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.entries(process.inputs || {}).map(([name, input]: [string, any]) => (
              <TableRow key={name}>
                <TableCell>{input.title || name}</TableCell>
                <TableCell>{input.description || '-'}</TableCell>
                <TableCell>
                  {input.schema?.type || 'any'}
                  {input.schema?.enum && (
                    <Box mt={1}>
                      {input.schema.enum.map((value: string) => (
                        <Chip 
                          key={value} 
                          label={value} 
                          size="small" 
                          variant="outlined" 
                          sx={{ mr: 0.5, mb: 0.5 }} 
                        />
                      ))}
                    </Box>
                  )}
                </TableCell>
                <TableCell>
                  <Chip 
                    label={input.required ? 'Required' : 'Optional'} 
                    color={input.required ? 'primary' : 'default'} 
                    size="small" 
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Outputs */}
      <Typography variant="h6" gutterBottom>Outputs</Typography>
      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Type</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.entries(process.outputs || {}).map(([name, output]: [string, any]) => (
              <TableRow key={name}>
                <TableCell>{output.title || name}</TableCell>
                <TableCell>{output.description || '-'}</TableCell>
                <TableCell>{output.schema?.type || 'any'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default ProcessInfo;
