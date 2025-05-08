import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText, 
  ListItemSecondaryAction,
  IconButton, 
  Button, 
  Breadcrumbs,
  Link,
  CircularProgress,
  Divider,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Chip
} from '@mui/material';
import FolderIcon from '@mui/icons-material/Folder';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import DescriptionIcon from '@mui/icons-material/Description';
import ImageIcon from '@mui/icons-material/Image';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import CloudDownloadIcon from '@mui/icons-material/CloudDownload';
import InfoIcon from '@mui/icons-material/Info';
import ShareIcon from '@mui/icons-material/Share';
import SearchIcon from '@mui/icons-material/Search';
import { apiClient } from '../../lib/api';
import { formatFileSize, formatDate } from '../../utils/formatters';

interface BoxBrowserProps {
  onFileSelect?: (fileInfo: any) => void;
  onFileImport?: (fileInfo: any) => void;
  fileExtensionFilter?: string[];
}

const BoxBrowser: React.FC<BoxBrowserProps> = ({ 
  onFileSelect, 
  onFileImport,
  fileExtensionFilter 
}) => {
  const [isConfigured, setIsConfigured] = useState<boolean>(false);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  const [currentFolderId, setCurrentFolderId] = useState<string>("0");
  const [folderPath, setFolderPath] = useState<Array<{id: string, name: string}>>([{id: "0", name: "All Files"}]);
  const [folderContents, setFolderContents] = useState<any[]>([]);
  
  const [selectedFile, setSelectedFile] = useState<any | null>(null);
  const [fileDetailsOpen, setFileDetailsOpen] = useState<boolean>(false);
  const [shareLinkOpen, setShareLinkOpen] = useState<boolean>(false);
  const [shareLink, setShareLink] = useState<string>("");
  
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isSearching, setIsSearching] = useState<boolean>(false);

  useEffect(() => {
    checkBoxStatus();
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      loadFolderContents(currentFolderId);
    }
  }, [currentFolderId, isAuthenticated]);

  const checkBoxStatus = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.get('/box/status');
      setIsConfigured(response.data.configured);
      setIsAuthenticated(response.data.client_initialized);
      setLoading(false);
    } catch (err) {
      console.error('Error checking Box.com status:', err);
      setError('Failed to check Box.com integration status');
      setLoading(false);
    }
  };

  const handleAuthenticate = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.get('/box/auth/url');
      window.location.href = response.data.auth_url;
    } catch (err) {
      console.error('Error getting Box.com auth URL:', err);
      setError('Failed to get Box.com authentication URL');
      setLoading(false);
    }
  };

  const loadFolderContents = async (folderId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.get(`/box/folders/${folderId}`);
      
      // Filter items by file extension if specified
      let items = response.data.items;
      if (fileExtensionFilter && fileExtensionFilter.length > 0) {
        items = items.filter((item: any) => {
          if (item.type === 'folder') return true;
          const extension = item.name.split('.').pop()?.toLowerCase();
          return fileExtensionFilter.includes(extension);
        });
      }
      
      setFolderContents(items);
      setLoading(false);
    } catch (err) {
      console.error('Error loading folder contents:', err);
      setError('Failed to load folder contents');
      setLoading(false);
    }
  };

  const navigateToFolder = (folderId: string, folderName: string) => {
    // Update folder path
    const newPath = [...folderPath];
    const existingIndex = newPath.findIndex(item => item.id === folderId);
    
    if (existingIndex >= 0) {
      // If folder is already in path, truncate the path
      setFolderPath(newPath.slice(0, existingIndex + 1));
    } else {
      // Add folder to path
      setFolderPath([...newPath, { id: folderId, name: folderName }]);
    }
    
    setCurrentFolderId(folderId);
  };

  const navigateUp = () => {
    if (folderPath.length > 1) {
      const newPath = [...folderPath];
      newPath.pop();
      setFolderPath(newPath);
      setCurrentFolderId(newPath[newPath.length - 1].id);
    }
  };

  const handleFileClick = (file: any) => {
    setSelectedFile(file);
    if (onFileSelect) {
      onFileSelect(file);
    }
  };

  const handleFileDetails = (file: any) => {
    setSelectedFile(file);
    setFileDetailsOpen(true);
  };

  const handleDownloadFile = async (fileId: string) => {
    try {
      window.open(`${apiClient.defaults.baseURL}/box/files/${fileId}/download`, '_blank');
    } catch (err) {
      console.error('Error downloading file:', err);
      setError('Failed to download file');
    }
  };

  const handleImportFile = async (fileId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.post(`/box/files/${fileId}/import`);
      
      if (onFileImport) {
        onFileImport(response.data);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error importing file:', err);
      setError('Failed to import file');
      setLoading(false);
    }
  };

  const handleCreateShareLink = async (fileId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.post(`/box/files/${fileId}/share`);
      setShareLink(response.data.shared_link);
      setShareLinkOpen(true);
      setLoading(false);
    } catch (err) {
      console.error('Error creating share link:', err);
      setError('Failed to create share link');
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      return;
    }
    
    setIsSearching(true);
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.post('/box/search', {
        query: searchQuery,
        file_extensions: fileExtensionFilter,
        limit: 100
      });
      
      setFolderContents(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error searching files:', err);
      setError('Failed to search files');
      setLoading(false);
    }
  };

  const clearSearch = () => {
    setSearchQuery("");
    setIsSearching(false);
    loadFolderContents(currentFolderId);
  };

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    
    if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'].includes(extension)) {
      return <ImageIcon />;
    } else if (['pdf', 'doc', 'docx', 'txt', 'rtf', 'xls', 'xlsx', 'ppt', 'pptx'].includes(extension)) {
      return <DescriptionIcon />;
    } else {
      return <InsertDriveFileIcon />;
    }
  };

  if (loading && !isConfigured && !isAuthenticated) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
      </Box>
    );
  }

  if (!isConfigured) {
    return (
      <Paper elevation={2} sx={{ p: 3 }}>
        <Alert severity="warning">
          Box.com integration is not configured. Please configure the Box.com API credentials in the server settings.
        </Alert>
      </Paper>
    );
  }

  if (!isAuthenticated) {
    return (
      <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" gutterBottom>
          Connect to Box.com
        </Typography>
        <Typography variant="body1" paragraph>
          You need to authenticate with Box.com to access your files.
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={handleAuthenticate}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Connect to Box.com'}
        </Button>
      </Paper>
    );
  }

  return (
    <Paper elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box p={2} display="flex" alignItems="center">
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Box.com Files
        </Typography>
        
        <Box display="flex" alignItems="center">
          <TextField
            size="small"
            placeholder="Search files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            sx={{ mr: 1 }}
          />
          <Button
            variant="outlined"
            startIcon={<SearchIcon />}
            onClick={handleSearch}
            disabled={!searchQuery.trim()}
          >
            Search
          </Button>
        </Box>
      </Box>
      
      <Divider />
      
      <Box p={2} display="flex" alignItems="center">
        <IconButton 
          onClick={navigateUp} 
          disabled={folderPath.length <= 1 || isSearching}
          sx={{ mr: 1 }}
        >
          <ArrowBackIcon />
        </IconButton>
        
        <Breadcrumbs aria-label="breadcrumb" sx={{ flexGrow: 1 }}>
          {folderPath.map((folder, index) => (
            <Link
              key={folder.id}
              color="inherit"
              href="#"
              onClick={(e) => {
                e.preventDefault();
                if (!isSearching) {
                  navigateToFolder(folder.id, folder.name);
                }
              }}
              underline={index === folderPath.length - 1 ? "none" : "hover"}
              sx={{ 
                fontWeight: index === folderPath.length - 1 ? 'bold' : 'normal',
                cursor: isSearching ? 'default' : 'pointer'
              }}
            >
              {folder.name}
            </Link>
          ))}
        </Breadcrumbs>
        
        {isSearching && (
          <Button 
            variant="text" 
            color="primary" 
            onClick={clearSearch}
            size="small"
          >
            Clear Search
          </Button>
        )}
      </Box>
      
      <Divider />
      
      {error && (
        <Alert severity="error" sx={{ m: 2 }}>
          {error}
        </Alert>
      )}
      
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" height="100%">
            <CircularProgress />
          </Box>
        ) : folderContents.length === 0 ? (
          <Box display="flex" justifyContent="center" alignItems="center" height="100%" p={3}>
            <Typography variant="body1" color="text.secondary">
              {isSearching ? 'No files found matching your search.' : 'This folder is empty.'}
            </Typography>
          </Box>
        ) : (
          <List>
            {folderContents.map((item) => (
              <ListItem
                key={item.id}
                button
                onClick={() => item.type === 'folder' 
                  ? navigateToFolder(item.id, item.name) 
                  : handleFileClick(item)
                }
                selected={selectedFile && selectedFile.id === item.id}
              >
                <ListItemIcon>
                  {item.type === 'folder' 
                    ? <FolderIcon color="primary" /> 
                    : getFileIcon(item.name)
                  }
                </ListItemIcon>
                <ListItemText 
                  primary={item.name} 
                  secondary={
                    <React.Fragment>
                      {item.type === 'file' && (
                        <React.Fragment>
                          {formatFileSize(item.size)} • {formatDate(item.modified_at)}
                          {item.has_metadata && (
                            <Chip 
                              label="Metadata" 
                              size="small" 
                              color="primary" 
                              variant="outlined"
                              sx={{ ml: 1 }}
                            />
                          )}
                        </React.Fragment>
                      )}
                    </React.Fragment>
                  }
                />
                {item.type === 'file' && (
                  <ListItemSecondaryAction>
                    <Tooltip title="File Details">
                      <IconButton edge="end" onClick={() => handleFileDetails(item)}>
                        <InfoIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Download">
                      <IconButton edge="end" onClick={() => handleDownloadFile(item.id)}>
                        <CloudDownloadIcon />
                      </IconButton>
                    </Tooltip>
                    {onFileImport && (
                      <Button 
                        variant="outlined" 
                        size="small" 
                        onClick={() => handleImportFile(item.id)}
                        sx={{ ml: 1 }}
                      >
                        Import
                      </Button>
                    )}
                  </ListItemSecondaryAction>
                )}
              </ListItem>
            ))}
          </List>
        )}
      </Box>
      
      {/* File Details Dialog */}
      <Dialog open={fileDetailsOpen} onClose={() => setFileDetailsOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>File Details</DialogTitle>
        <DialogContent>
          {selectedFile && (
            <Box>
              <Typography variant="h6">{selectedFile.name}</Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {formatFileSize(selectedFile.size)} • Last modified: {formatDate(selectedFile.modified_at)}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              {selectedFile.has_metadata && selectedFile.metadata && (
                <Box>
                  <Typography variant="subtitle1" gutterBottom>Geospatial Metadata</Typography>
                  <Box sx={{ ml: 2 }}>
                    {selectedFile.metadata.crs && (
                      <Typography variant="body2">
                        <strong>CRS:</strong> {selectedFile.metadata.crs}
                      </Typography>
                    )}
                    {selectedFile.metadata.geometryType && (
                      <Typography variant="body2">
                        <strong>Geometry Type:</strong> {selectedFile.metadata.geometryType}
                      </Typography>
                    )}
                    {selectedFile.metadata.featureCount && (
                      <Typography variant="body2">
                        <strong>Feature Count:</strong> {selectedFile.metadata.featureCount}
                      </Typography>
                    )}
                    {selectedFile.metadata.boundingBox && (
                      <Typography variant="body2">
                        <strong>Bounding Box:</strong> {selectedFile.metadata.boundingBox}
                      </Typography>
                    )}
                    {selectedFile.metadata.attributes && (
                      <Typography variant="body2">
                        <strong>Attributes:</strong> {selectedFile.metadata.attributes}
                      </Typography>
                    )}
                    {selectedFile.metadata.dataFormat && (
                      <Typography variant="body2">
                        <strong>Data Format:</strong> {selectedFile.metadata.dataFormat}
                      </Typography>
                    )}
                  </Box>
                </Box>
              )}
              
              {!selectedFile.has_metadata && (
                <Alert severity="info">
                  No geospatial metadata available for this file.
                </Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => handleCreateShareLink(selectedFile.id)} startIcon={<ShareIcon />}>
            Create Share Link
          </Button>
          <Button onClick={() => handleDownloadFile(selectedFile.id)} startIcon={<CloudDownloadIcon />}>
            Download
          </Button>
          {onFileImport && (
            <Button 
              onClick={() => {
                handleImportFile(selectedFile.id);
                setFileDetailsOpen(false);
              }} 
              variant="contained"
            >
              Import
            </Button>
          )}
          <Button onClick={() => setFileDetailsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
      
      {/* Share Link Dialog */}
      <Dialog open={shareLinkOpen} onClose={() => setShareLinkOpen(false)}>
        <DialogTitle>Share Link</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            value={shareLink}
            InputProps={{
              readOnly: true,
            }}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => {
              navigator.clipboard.writeText(shareLink);
            }}
          >
            Copy Link
          </Button>
          <Button onClick={() => setShareLinkOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default BoxBrowser;
