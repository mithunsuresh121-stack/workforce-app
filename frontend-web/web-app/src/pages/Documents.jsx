import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Card,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Chip,
  Grid,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Switch,
  FormControlLabel
} from "@mui/material";
import {
  Upload as CloudArrowUpIcon,
  Download as CloudArrowDownIcon,
  Visibility as EyeIcon,
  Delete as TrashIcon,
  Search as MagnifyingGlassIcon,
  ViewList as ListBulletIcon,
  GridView as Squares2X2Icon,
  FilterList as FunnelIcon
} from '@mui/icons-material';
import { api, useAuth } from "../contexts/AuthContext";

export default function Documents() {
  const { user } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [viewMode, setViewMode] = useState('table'); // 'table' or 'cards'
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState(null);

  const isManager = user && ['Manager', 'CompanyAdmin', 'SuperAdmin'].includes(user.role);
  const canUpload = isManager || user?.role === 'Employee'; // Adjust based on RBAC
  const canDelete = isManager;

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get("/documents");
      setDocuments(response.data);
    } catch (error) {
      console.error("Error fetching documents:", error);
      setError('Failed to load documents. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.uploaded_by.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = !typeFilter || doc.type === typeFilter;
    return matchesSearch && matchesType;
  });

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      setUploadLoading(true);
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await api.post('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setDocuments([...documents, response.data]);
      setUploadDialogOpen(false);
      setSelectedFile(null);
    } catch (error) {
      console.error('Error uploading document:', error);
      setError('Failed to upload document. Please try again.');
    } finally {
      setUploadLoading(false);
    }
  };

  const handleDownload = async (doc) => {
    try {
      const response = await api.get(`/documents/${doc.id}/download`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', doc.name);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading document:', error);
      setError('Failed to download document. Please try again.');
    }
  };

  const handleView = (doc) => {
    // For now, just download. In a real app, you might open in a viewer
    handleDownload(doc);
  };

  const handleDelete = (doc) => {
    setDocumentToDelete(doc);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!documentToDelete) return;

    try {
      await api.delete(`/documents/${documentToDelete.id}`);
      setDocuments(documents.filter(d => d.id !== documentToDelete.id));
      setDeleteDialogOpen(false);
      setDocumentToDelete(null);
    } catch (error) {
      console.error('Error deleting document:', error);
      setError('Failed to delete document. Please try again.');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgress sx={{ mb: 2 }} />
            <Typography color="text.secondary">Loading documents...</Typography>
          </Box>
        </Box>
      </>
    );
  }

  return (
    <>
      <Box sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h4" fontWeight="bold">Documents</Typography>
            <Typography color="text.secondary">Manage and access company documents</Typography>
          </Box>
          {canUpload && (
            <Button
              variant="contained"
              startIcon={<CloudArrowUpIcon />}
              onClick={() => setUploadDialogOpen(true)}
            >
              Upload Document
            </Button>
          )}
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Filters and View Controls */}
        <Card sx={{ p: 3, mb: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <MagnifyingGlassIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  startAdornment={<FunnelIcon sx={{ mr: 1, color: 'text.secondary' }} />}
                >
                  <MenuItem value="">All Types</MenuItem>
                  <MenuItem value="pdf">PDF</MenuItem>
                  <MenuItem value="doc">DOC</MenuItem>
                  <MenuItem value="docx">DOCX</MenuItem>
                  <MenuItem value="xls">XLS</MenuItem>
                  <MenuItem value="xlsx">XLSX</MenuItem>
                  <MenuItem value="txt">TXT</MenuItem>
                  <MenuItem value="jpg">JPG</MenuItem>
                  <MenuItem value="png">PNG</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <IconButton
                  onClick={() => setViewMode('table')}
                  sx={{
                    border: 1,
                    borderColor: viewMode === 'table' ? 'primary.main' : 'grey.300',
                    bgcolor: viewMode === 'table' ? 'primary.light' : 'transparent',
                  }}
                >
                  <ListBulletIcon />
                </IconButton>
                <IconButton
                  onClick={() => setViewMode('cards')}
                  sx={{
                    border: 1,
                    borderColor: viewMode === 'cards' ? 'primary.main' : 'grey.300',
                    bgcolor: viewMode === 'cards' ? 'primary.light' : 'transparent',
                  }}
                >
                  <Squares2X2Icon />
                </IconButton>
                <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
                  {filteredDocuments.length} of {documents.length} documents
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Card>

        {/* Documents Display */}
        {viewMode === 'table' ? (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Size</TableCell>
                  <TableCell>Uploaded By</TableCell>
                  <TableCell>Upload Date</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredDocuments.map((doc) => (
                  <TableRow key={doc.id} hover>
                    <TableCell>
                      <Typography fontWeight="bold">{doc.name}</Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={doc.type.toUpperCase()} size="small" />
                    </TableCell>
                    <TableCell>{formatFileSize(doc.size)}</TableCell>
                    <TableCell>{doc.uploaded_by}</TableCell>
                    <TableCell>{new Date(doc.upload_date).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Tooltip title="View">
                        <IconButton onClick={() => handleView(doc)}>
                          <EyeIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Download">
                        <IconButton onClick={() => handleDownload(doc)}>
                          <CloudArrowDownIcon />
                        </IconButton>
                      </Tooltip>
                      {canDelete && (
                        <Tooltip title="Delete">
                          <IconButton onClick={() => handleDelete(doc)} color="error">
                            <TrashIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Grid container spacing={3}>
            {filteredDocuments.map((doc) => (
              <Grid item xs={12} sm={6} md={4} key={doc.id}>
                <Card sx={{ p: 2, cursor: 'pointer' }}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Typography variant="h6" fontWeight="bold" sx={{ wordBreak: 'break-word' }}>
                      {doc.name}
                    </Typography>
                    <Chip label={doc.type.toUpperCase()} size="small" />
                    <Typography variant="body2" color="text.secondary">
                      Size: {formatFileSize(doc.size)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      By: {doc.uploaded_by}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {new Date(doc.upload_date).toLocaleDateString()}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                      <IconButton size="small" onClick={() => handleView(doc)}>
                        <EyeIcon />
                      </IconButton>
                      <IconButton size="small" onClick={() => handleDownload(doc)}>
                        <CloudArrowDownIcon />
                      </IconButton>
                      {canDelete && (
                        <IconButton size="small" onClick={() => handleDelete(doc)} color="error">
                          <TrashIcon />
                        </IconButton>
                      )}
                    </Box>
                  </Box>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Upload Dialog */}
        <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Upload Document</DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 2 }}>
              <TextField
                fullWidth
                type="file"
                onChange={handleFileSelect}
                inputProps={{ accept: '.pdf,.doc,.docx,.xls,.xlsx,.txt,.jpg,.png' }}
              />
              {selectedFile && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Selected: {selectedFile.name} ({formatFileSize(selectedFile.size)})
                </Typography>
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setUploadDialogOpen(false)}>Cancel</Button>
            <Button
              onClick={handleUpload}
              variant="contained"
              disabled={!selectedFile || uploadLoading}
            >
              {uploadLoading ? <CircularProgress size={20} /> : 'Upload'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
          <DialogTitle>Delete Document</DialogTitle>
          <DialogContent>
            <Typography>
              Are you sure you want to delete "{documentToDelete?.name}"? This action cannot be undone.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
            <Button onClick={confirmDelete} color="error" variant="contained">
              Delete
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </>
  );
}
