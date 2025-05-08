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
  LinearProgress
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
import { apiClient } from '../../lib/api';

interface FileItem {
  Path: string;
  Name: string;
  Size: number;
  MimeType: string;
  ModTime: string;
  IsDir: boolean;
}

const RcloneFileBrowser: React.FC = () => {
  const [remotes, setRemotes] = useState<string[]>([]);
  const [currentPath, setCurrentPath] = useState<string>('');
  const [pathHistory, setPathHistory] = useState<string[]>([]);
  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);
  const [uploadDialogOpen, setUploadDialogOpen] = useState<boolean>(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [downloadProgress, setDownloadProgress] = useState<{[key: string]: number}>({});

  useEffect(() => {
    fetchRemotes();
  }, []);

  useEffect(() => {
    if (currentPath) {
      fetchFiles();
    }
  }, [currentPath]);

  const fetchRemotes = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get('/api/v1/rclone/remotes');
      setRemotes(response.data.remotes || []);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching remotes:', err);
      setError('Failed to load remotes. Please try again.');
      setLoading(false);
    }
  };

  const fetchFiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get('/api/v1/rclone/files', {
        params: { path: currentPath, recursive: false }
      });
      setFiles(response.data.files || []);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching files:', err);
      setError('Failed to load files. Please try again.');
      setLoading(false);
    }
  };

  const handleRemoteClick = (remote: string) => {
    setCurrentPath(`${remote}:`);
    setPathHistory([]);
  };

  const handleFileClick = (file: FileItem) => {
    if (file.IsDir) {
      setPathHistory([...pathHistory, currentPath]);
      setCurrentPath(`${currentPath}${currentPath.endsWith(':') ? '' : '/'}${file.Path}`);
    }
  };

  const handleBackClick = () => {
    if (pathHistory.length > 0) {
      const previousPath = pathHistory[pathHistory.length - 1];
      setCurrentPath(previousPath);
      setPathHistory(pathHistory.slice(0, -1));
    } else if (currentPath.includes(':')) {
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
      const filePath = `${currentPath}${currentPath.endsWith(':') ? '' : '/'}${selectedFile.Path}`;

      // For small files, just open in a new tab
      if (selectedFile.Size < 10 * 1024 * 1024) { // Less than 10MB
        window.open(`/api/v1/rclone/download?path=${encodeURIComponent(filePath)}`, '_blank');
        setSuccess(`Downloading ${selectedFile.Name}`);
        return;
      }

      // For larger files, show progress
      setDownloadProgress({
        ...downloadProgress,
        [selectedFile.Path]: 0
      });

      // Start a download with progress tracking
      const response = await apiClient.post('/api/v1/rclone/download-with-progress', {
        path: filePath
      }, {
        onDownloadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setDownloadProgress({
              ...downloadProgress,
              [selectedFile.Path]: progress
            });
          }
        },
        responseType: 'blob'
      });

      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', selectedFile.Name);
      document.body.appendChild(link);
      link.click();
      link.remove();

      // Clean up
      setDownloadProgress({
        ...downloadProgress,
        [selectedFile.Path]: 100
      });

      setTimeout(() => {
        setDownloadProgress({
          ...downloadProgress,
          [selectedFile.Path]: undefined
        });
      }, 2000);

      setSuccess(`Downloaded ${selectedFile.Name}`);
    } catch (err) {
      console.error('Error downloading file:', err);
      setError('Failed to download file. Please try again.');

      // Clean up progress on error
      setDownloadProgress({
        ...downloadProgress,
        [selectedFile.Path]: undefined
      });
    }
  };

  const handleUploadDialogOpen = () => {
    setUploadDialogOpen(true);
  };

  const handleUploadDialogClose = () => {
    setUploadDialogOpen(false);
    setUploadFile(null);
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
      formData.append('remote_path', `${currentPath}${currentPath.endsWith(':') ? '' : '/'}${uploadFile.name}`);

      // Determine if we should use chunked upload
      const useChunks = uploadFile.size > 100 * 1024 * 1024; // > 100MB

      if (useChunks) {
        formData.append('chunk_size', '10'); // 10MB chunks
      }

      await apiClient.post('/api/v1/rclone/upload', formData, {
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
      fetchFiles();
    } catch (err) {
      console.error('Error uploading file:', err);
      setError('Failed to upload file. Please try again.');
    } finally {
      setUploading(false);
      // Reset progress after a delay
      setTimeout(() => setUploadProgress(0), 2000);
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

    const parts = currentPath.split('/');
    const remote = parts[0];

    return (
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
        <Link
          component="button"
          variant="body1"
          onClick={() => setCurrentPath('')}
          underline="hover"
          color="inherit"
        >
          Remotes
        </Link>
        {parts.map((part, index) => {
          const path = parts.slice(0, index + 1).join('/');
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
                setPathHistory(parts.slice(0, index).map((_, i) => parts.slice(0, i + 1).join('/')));
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
        Rclone File Browser
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
            {renderBreadcrumbs() || <Typography variant="h6">Select a Remote</Typography>}
          </Box>
          <Box>
            <Button
              startIcon={<RefreshIcon />}
              onClick={currentPath ? fetchFiles : fetchRemotes}
              disabled={loading}
              sx={{ mr: 1 }}
            >
              Refresh
            </Button>
            {currentPath && (
              <Button
                variant="contained"
                startIcon={<CloudUploadIcon />}
                onClick={handleUploadDialogOpen}
                disabled={loading}
              >
                Upload
              </Button>
            )}
          </Box>
        </Box>

        <Divider sx={{ mb: 2 }} />

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : !currentPath ? (
          // Show remotes
          <List>
            {remotes.length === 0 ? (
              <Typography variant="body1" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
                No remotes configured. Please add a remote in the configuration section.
              </Typography>
            ) : (
              remotes.map((remote) => (
                <ListItem
                  key={remote}
                  button
                  onClick={() => handleRemoteClick(remote)}
                >
                  <ListItemIcon>
                    <FolderIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={remote}
                    secondary="Remote storage"
                  />
                </ListItem>
              ))
            )}
          </List>
        ) : (
          // Show files
          <List>
            {files.length === 0 ? (
              <Typography variant="body1" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
                This directory is empty.
              </Typography>
            ) : (
              files.map((file) => (
                <ListItem
                  key={file.Path}
                  button
                  onClick={() => handleFileClick(file)}
                >
                  <ListItemIcon>
                    {file.IsDir ? <FolderIcon /> : <InsertDriveFileIcon />}
                  </ListItemIcon>
                  <ListItemText
                    primary={file.Name}
                    secondary={
                      <>
                        {file.IsDir ? 'Directory' : `${formatFileSize(file.Size)} • ${new Date(file.ModTime).toLocaleString()}`}
                        {downloadProgress[file.Path] !== undefined && !file.IsDir && (
                          <Box sx={{ width: '100%', mt: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={downloadProgress[file.Path]}
                              color="primary"
                            />
                            <Typography variant="caption" color="text.secondary">
                              Downloading: {downloadProgress[file.Path]}%
                            </Typography>
                          </Box>
                        )}
                      </>
                    }
                  />
                  <ListItemSecondaryAction>
                    {downloadProgress[file.Path] !== undefined && !file.IsDir ? (
                      <CircularProgress size={24} />
                    ) : (
                      <IconButton
                        edge="end"
                        aria-label="more"
                        onClick={(e) => handleMenuOpen(e, file)}
                      >
                        <MoreVertIcon />
                      </IconButton>
                    )}
                  </ListItemSecondaryAction>
                </ListItem>
              ))
            )}
          </List>
        )}
      </Paper>

      {/* File Actions Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        {selectedFile && !selectedFile.IsDir && (
          <MenuItem onClick={handleDownload}>
            <ListItemIcon>
              <CloudDownloadIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Download</ListItemText>
          </MenuItem>
        )}
        <MenuItem onClick={handleMenuClose}>
          <ListItemIcon>
            <InfoIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Properties</ListItemText>
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
          <Box sx={{ width: '100%' }}>
            {uploading && uploadProgress > 0 && (
              <Box sx={{ mb: 2 }}>
                <LinearProgress variant="determinate" value={uploadProgress} />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                  {uploadProgress}% Complete
                </Typography>
              </Box>
            )}
            <Button
              onClick={handleUpload}
              variant="contained"
              disabled={!uploadFile || uploading}
              startIcon={uploading ? <CircularProgress size={20} /> : null}
              fullWidth
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </Button>
          </Box>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RcloneFileBrowser;
