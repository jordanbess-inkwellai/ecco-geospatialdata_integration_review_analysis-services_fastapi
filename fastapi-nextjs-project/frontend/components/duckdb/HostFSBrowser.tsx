import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Breadcrumbs,
  Link,
  Divider,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Tooltip,
  Chip
} from '@mui/material';
import FolderIcon from '@mui/icons-material/Folder';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import CloudDownloadIcon from '@mui/icons-material/CloudDownload';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import RefreshIcon from '@mui/icons-material/Refresh';
import CreateNewFolderIcon from '@mui/icons-material/CreateNewFolder';
import TableViewIcon from '@mui/icons-material/TableView';
import CodeIcon from '@mui/icons-material/Code';
import { apiClient } from '../../lib/api';

interface FileItem {
  name: string;
  path: string;
  size: number;
  is_dir: boolean;
  last_modified: string;
  extension?: string;
}

interface DirectoryInfo {
  path: string;
  allowed: boolean;
  files: FileItem[];
}

interface FileInfoDialog {
  open: boolean;
  file: FileItem | null;
}

const HostFSBrowser: React.FC = () => {
  const [currentPath, setCurrentPath] = useState<string>('');
  const [pathHistory, setPathHistory] = useState<string[]>([]);
  const [directoryInfo, setDirectoryInfo] = useState<DirectoryInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);
  const [uploadDialogOpen, setUploadDialogOpen] = useState<boolean>(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [newFolderDialogOpen, setNewFolderDialogOpen] = useState<boolean>(false);
  const [newFolderName, setNewFolderName] = useState<string>('');
  const [fileInfoDialog, setFileInfoDialog] = useState<FileInfoDialog>({
    open: false,
    file: null
  });
  const [allowedDirectories, setAllowedDirectories] = useState<string[]>([]);

  useEffect(() => {
    fetchAllowedDirectories();
  }, []);

  useEffect(() => {
    if (currentPath) {
      fetchDirectoryContents(currentPath);
    } else {
      fetchAllowedDirectories();
    }
  }, [currentPath]);

  const fetchAllowedDirectories = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get('/api/v1/duckdb/hostfs/allowed-directories');
      setAllowedDirectories(response.data.directories || []);
      setDirectoryInfo({
        path: '',
        allowed: true,
        files: response.data.directories.map((dir: string) => ({
          name: dir.split('/').pop() || dir,
          path: dir,
          size: 0,
          is_dir: true,
          last_modified: ''
        }))
      });
      setLoading(false);
    } catch (err) {
      console.error('Error fetching allowed directories:', err);
      setError('Failed to load allowed directories. Please try again.');
      setLoading(false);
    }
  };

  const fetchDirectoryContents = async (path: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get('/api/v1/duckdb/hostfs/list', {
        params: { path }
      });
      setDirectoryInfo(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching directory contents:', err);
      setError('Failed to load directory contents. Please try again.');
      setLoading(false);
    }
  };

  const handleDirectoryClick = (directory: FileItem) => {
    setPathHistory([...pathHistory, currentPath]);
    setCurrentPath(directory.path);
  };

  const handleBackClick = () => {
    if (pathHistory.length > 0) {
      const previousPath = pathHistory[pathHistory.length - 1];
      setCurrentPath(previousPath);
      setPathHistory(pathHistory.slice(0, -1));
    } else {
      setCurrentPath('');
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, file: FileItem) => {
    setMenuAnchorEl(event.currentTarget);
    setSelectedFile(file);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
    setSelectedFile(null);
  };

  const handleDownload = async () => {
    if (!selectedFile) return;
    
    handleMenuClose();
    
    try {
      window.open(`/api/v1/duckdb/hostfs/download?path=${encodeURIComponent(selectedFile.path)}`, '_blank');
      setSuccess(`Downloading ${selectedFile.name}`);
    } catch (err) {
      console.error('Error downloading file:', err);
      setError('Failed to download file. Please try again.');
    }
  };

  const handleDelete = async () => {
    if (!selectedFile) return;
    
    handleMenuClose();
    
    if (!confirm(`Are you sure you want to delete ${selectedFile.name}?`)) {
      return;
    }
    
    try {
      if (selectedFile.is_dir) {
        await apiClient.delete('/api/v1/duckdb/hostfs/directory', {
          params: { path: selectedFile.path }
        });
      } else {
        await apiClient.delete('/api/v1/duckdb/hostfs/file', {
          params: { path: selectedFile.path }
        });
      }
      
      setSuccess(`${selectedFile.is_dir ? 'Directory' : 'File'} "${selectedFile.name}" deleted successfully`);
      fetchDirectoryContents(currentPath);
    } catch (err) {
      console.error('Error deleting:', err);
      setError(`Failed to delete ${selectedFile.is_dir ? 'directory' : 'file'}. Please try again.`);
    }
  };

  const handleFileInfo = () => {
    if (!selectedFile) return;
    
    handleMenuClose();
    setFileInfoDialog({
      open: true,
      file: selectedFile
    });
  };

  const handleCreateTable = async () => {
    if (!selectedFile || selectedFile.is_dir) return;
    
    handleMenuClose();
    
    try {
      // Determine table name from file name
      const tableName = selectedFile.name.split('.')[0].replace(/[^a-zA-Z0-9_]/g, '_');
      
      await apiClient.post('/api/v1/duckdb/tables', {
        file_path: selectedFile.path,
        table_name: tableName,
        use_hostfs: true
      });
      
      setSuccess(`Table "${tableName}" created successfully from ${selectedFile.name}`);
    } catch (err) {
      console.error('Error creating table:', err);
      setError('Failed to create table. Please try again.');
    }
  };

  const handleViewSql = () => {
    if (!selectedFile || selectedFile.is_dir) return;
    
    handleMenuClose();
    
    // Determine file type and generate SQL
    const extension = selectedFile.name.split('.').pop()?.toLowerCase();
    let sql = '';
    
    if (extension === 'csv') {
      sql = `-- View CSV file\nSELECT * FROM read_csv_auto(hostfs_file_path('${selectedFile.path}'));\n\n-- Create table from CSV\nCREATE TABLE ${selectedFile.name.split('.')[0]} AS SELECT * FROM read_csv_auto(hostfs_file_path('${selectedFile.path}'));`;
    } else if (extension === 'parquet') {
      sql = `-- View Parquet file\nSELECT * FROM read_parquet(hostfs_file_path('${selectedFile.path}'));\n\n-- Create table from Parquet\nCREATE TABLE ${selectedFile.name.split('.')[0]} AS SELECT * FROM read_parquet(hostfs_file_path('${selectedFile.path}'));`;
    } else if (extension === 'json') {
      sql = `-- View JSON file\nSELECT * FROM read_json_auto(hostfs_file_path('${selectedFile.path}'));\n\n-- Create table from JSON\nCREATE TABLE ${selectedFile.name.split('.')[0]} AS SELECT * FROM read_json_auto(hostfs_file_path('${selectedFile.path}'));`;
    } else if (['shp', 'gpkg', 'geojson'].includes(extension || '')) {
      sql = `-- View spatial file\nSELECT * FROM ST_Read(hostfs_file_path('${selectedFile.path}'));\n\n-- Create table from spatial file\nCREATE TABLE ${selectedFile.name.split('.')[0]} AS SELECT * FROM ST_Read(hostfs_file_path('${selectedFile.path}'));`;
    } else if (['xls', 'xlsx'].includes(extension || '')) {
      sql = `-- View Excel file\nSELECT * FROM read_excel(hostfs_file_path('${selectedFile.path}'));\n\n-- Create table from Excel\nCREATE TABLE ${selectedFile.name.split('.')[0]} AS SELECT * FROM read_excel(hostfs_file_path('${selectedFile.path}'));`;
    } else {
      sql = `-- View file info\nSELECT * FROM hostfs_file_info('${selectedFile.path}');\n\n-- Read text file (if applicable)\nSELECT * FROM hostfs_read_text('${selectedFile.path}');`;
    }
    
    // Copy to clipboard
    navigator.clipboard.writeText(sql);
    setSuccess('SQL copied to clipboard');
  };

  const handleUploadDialogOpen = () => {
    setUploadDialogOpen(true);
  };

  const handleUploadDialogClose = () => {
    setUploadDialogOpen(false);
    setUploadFile(null);
    setUploadProgress(0);
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setUploadFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!uploadFile) return;
    
    setUploading(true);
    setUploadProgress(0);
    
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('directory', currentPath);
      
      await apiClient.post('/api/v1/duckdb/hostfs/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(progress);
          }
        }
      });
      
      setSuccess(`File "${uploadFile.name}" uploaded successfully`);
      handleUploadDialogClose();
      fetchDirectoryContents(currentPath);
    } catch (err) {
      console.error('Error uploading file:', err);
      setError('Failed to upload file. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleNewFolderDialogOpen = () => {
    setNewFolderDialogOpen(true);
  };

  const handleNewFolderDialogClose = () => {
    setNewFolderDialogOpen(false);
    setNewFolderName('');
  };

  const handleCreateFolder = async () => {
    if (!newFolderName) return;
    
    try {
      await apiClient.post('/api/v1/duckdb/hostfs/directory', {
        path: `${currentPath}/${newFolderName}`
      });
      
      setSuccess(`Directory "${newFolderName}" created successfully`);
      handleNewFolderDialogClose();
      fetchDirectoryContents(currentPath);
    } catch (err) {
      console.error('Error creating directory:', err);
      setError('Failed to create directory. Please try again.');
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const renderBreadcrumbs = () => {
    if (!currentPath) return null;
    
    const parts = currentPath.split('/').filter(Boolean);
    
    return (
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
        <Link 
          component="button" 
          variant="body1" 
          onClick={() => setCurrentPath('')}
          underline="hover"
          color="inherit"
        >
          Home
        </Link>
        {parts.map((part, index) => {
          const path = '/' + parts.slice(0, index + 1).join('/');
          const isLast = index === parts.length - 1;
          
          return isLast ? (
            <Typography key={path} color="text.primary">
              {part}
            </Typography>
          ) : (
            <Link
              key={path}
              component="button"
              variant="body1"
              onClick={() => {
                setCurrentPath(path);
                setPathHistory(parts.slice(0, index).map((_, i) => '/' + parts.slice(0, i + 1).join('/')));
              }}
              underline="hover"
              color="inherit"
            >
              {part}
            </Link>
          );
        })}
      </Breadcrumbs>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Local File Browser (HostFS)
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {currentPath && (
              <IconButton onClick={handleBackClick} sx={{ mr: 1 }}>
                <ArrowBackIcon />
              </IconButton>
            )}
            {renderBreadcrumbs() || <Typography variant="h6">Allowed Directories</Typography>}
          </Box>
          <Box>
            <Button 
              startIcon={<RefreshIcon />} 
              onClick={() => currentPath ? fetchDirectoryContents(currentPath) : fetchAllowedDirectories()}
              disabled={loading}
              sx={{ mr: 1 }}
            >
              Refresh
            </Button>
            {currentPath && directoryInfo?.allowed && (
              <>
                <Button 
                  variant="outlined" 
                  startIcon={<CreateNewFolderIcon />} 
                  onClick={handleNewFolderDialogOpen}
                  disabled={loading}
                  sx={{ mr: 1 }}
                >
                  New Folder
                </Button>
                <Button 
                  variant="contained" 
                  startIcon={<CloudUploadIcon />} 
                  onClick={handleUploadDialogOpen}
                  disabled={loading}
                >
                  Upload
                </Button>
              </>
            )}
          </Box>
        </Box>
        
        <Divider sx={{ mb: 2 }} />
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : !directoryInfo ? (
          <Typography variant="body1" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
            No directories available. Please configure allowed directories.
          </Typography>
        ) : !directoryInfo.allowed ? (
          <Alert severity="warning" sx={{ mb: 2 }}>
            This directory is not allowed. Please select an allowed directory.
          </Alert>
        ) : directoryInfo.files.length === 0 ? (
          <Typography variant="body1" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
            This directory is empty.
          </Typography>
        ) : (
          <List>
            {directoryInfo.files.map((file) => (
              <ListItem 
                key={file.path} 
                button 
                onClick={file.is_dir ? () => handleDirectoryClick(file) : undefined}
              >
                <ListItemIcon>
                  {file.is_dir ? <FolderIcon /> : <InsertDriveFileIcon />}
                </ListItemIcon>
                <ListItemText 
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {file.name}
                      {file.extension && (
                        <Chip 
                          label={file.extension} 
                          size="small" 
                          sx={{ ml: 1, height: 20, fontSize: '0.7rem' }} 
                        />
                      )}
                    </Box>
                  }
                  secondary={file.is_dir ? 'Directory' : `${formatFileSize(file.size)} • ${new Date(file.last_modified).toLocaleString()}`} 
                />
                <ListItemSecondaryAction>
                  <IconButton 
                    edge="end" 
                    aria-label="more" 
                    onClick={(e) => handleMenuOpen(e, file)}
                  >
                    <MoreVertIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        )}
      </Paper>
      
      {/* File Actions Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        {selectedFile && !selectedFile.is_dir && (
          <MenuItem onClick={handleDownload}>
            <ListItemIcon>
              <CloudDownloadIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Download</ListItemText>
          </MenuItem>
        )}
        {selectedFile && !selectedFile.is_dir && (
          <MenuItem onClick={handleCreateTable}>
            <ListItemIcon>
              <TableViewIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Create DuckDB Table</ListItemText>
          </MenuItem>
        )}
        {selectedFile && !selectedFile.is_dir && (
          <MenuItem onClick={handleViewSql}>
            <ListItemIcon>
              <CodeIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Copy SQL</ListItemText>
          </MenuItem>
        )}
        <MenuItem onClick={handleFileInfo}>
          <ListItemIcon>
            <InfoIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Properties</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleDelete}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Delete</ListItemText>
        </MenuItem>
      </Menu>
      
      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onClose={handleUploadDialogClose}>
        <DialogTitle>Upload File</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <input
              accept="*/*"
              style={{ display: 'none' }}
              id="upload-file-button"
              type="file"
              onChange={handleFileChange}
            />
            <label htmlFor="upload-file-button">
              <Button
                variant="outlined"
                component="span"
                startIcon={<CloudUploadIcon />}
                fullWidth
              >
                Select File
              </Button>
            </label>
            
            {uploadFile && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle1">Selected File:</Typography>
                <Typography variant="body2">{uploadFile.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {formatFileSize(uploadFile.size)}
                </Typography>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleUploadDialogClose} disabled={uploading}>
            Cancel
          </Button>
          <Button 
            onClick={handleUpload} 
            variant="contained" 
            disabled={!uploadFile || uploading}
            startIcon={uploading ? <CircularProgress size={20} /> : null}
          >
            {uploading ? `Uploading (${uploadProgress}%)` : 'Upload'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* New Folder Dialog */}
      <Dialog open={newFolderDialogOpen} onClose={handleNewFolderDialogClose}>
        <DialogTitle>Create New Folder</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Folder Name"
            type="text"
            fullWidth
            value={newFolderName}
            onChange={(e) => setNewFolderName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleNewFolderDialogClose}>
            Cancel
          </Button>
          <Button 
            onClick={handleCreateFolder} 
            variant="contained" 
            disabled={!newFolderName}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* File Info Dialog */}
      <Dialog open={fileInfoDialog.open} onClose={() => setFileInfoDialog({ open: false, file: null })}>
        <DialogTitle>File Properties</DialogTitle>
        <DialogContent>
          {fileInfoDialog.file && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1">Name:</Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>{fileInfoDialog.file.name}</Typography>
              
              <Typography variant="subtitle1">Path:</Typography>
              <Typography variant="body2" sx={{ mb: 2, wordBreak: 'break-all' }}>{fileInfoDialog.file.path}</Typography>
              
              <Typography variant="subtitle1">Type:</Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {fileInfoDialog.file.is_dir ? 'Directory' : `File${fileInfoDialog.file.extension ? ` (${fileInfoDialog.file.extension})` : ''}`}
              </Typography>
              
              {!fileInfoDialog.file.is_dir && (
                <>
                  <Typography variant="subtitle1">Size:</Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>{formatFileSize(fileInfoDialog.file.size)}</Typography>
                </>
              )}
              
              <Typography variant="subtitle1">Last Modified:</Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {fileInfoDialog.file.last_modified ? new Date(fileInfoDialog.file.last_modified).toLocaleString() : 'Unknown'}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFileInfoDialog({ open: false, file: null })}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default HostFSBrowser;
