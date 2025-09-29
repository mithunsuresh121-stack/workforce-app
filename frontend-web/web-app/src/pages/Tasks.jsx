import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import {
  Card,
  Typography,
  Box,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Grid,
  Divider
} from '@mui/material';
import {
  Add as PlusIcon,
  Search as MagnifyingGlassIcon,
  GridView as Squares2X2Icon,
  List as ListBulletIcon,
  ViewKanban as QueueListIcon,
  Edit as PencilIcon,
  Visibility as EyeIcon,
  FilterList as FunnelIcon,
  Close as XMarkIcon,
  CalendarToday as CalendarDaysIcon,
  Person as UserIcon,
  Flag as FlagIcon
} from '@mui/icons-material';
import DashboardLayout from '../layouts/DashboardLayout';
import { api, useAuth } from '../contexts/AuthContext';

const Tasks = () => {
  const { user } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [viewMode, setViewMode] = useState('kanban'); // 'grid', 'list', or 'kanban'
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: 'Pending',
    assignee_id: '',
    priority: 'Medium',
    dueDate: ''
  });

  const isManager = user && ['Manager', 'CompanyAdmin', 'SuperAdmin'].includes(user.role);

  const fetchEmployees = async () => {
    if (!isManager) return;
    try {
      const response = await api.get('/users/employees');
      setEmployees(response.data);
    } catch (error) {
      console.error('Error fetching employees:', error);
    }
  };

  useEffect(() => {
    if (user && isManager) {
      fetchEmployees();
    }
  }, [user, isManager]);

  const getName = useCallback((id) => {
    if (!id) return 'Unassigned';
    const emp = employees.find(e => e.id === id);
    return emp ? emp.name : `Employee ${id}`;
  }, [employees]);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await api.get('/tasks');
        setTasks(response.data);
      } catch (error) {
        console.error('Error fetching tasks:', error);
        setError('Failed to load tasks. Using sample data.');
        // Fallback sample data
        setTasks([
          {
            id: 1,
            title: 'Complete quarterly report',
            description: 'Prepare and submit the Q4 financial report',
            status: 'In Progress',
            assignee_id: 1,
            priority: 'High',
            dueDate: '2024-01-15',
            createdAt: new Date().toISOString()
          },
          {
            id: 2,
            title: 'Review code changes',
            description: 'Review pull request #123 for the new feature',
            status: 'Pending',
            assignee_id: 2,
            priority: 'Medium',
            dueDate: '2024-01-10',
            createdAt: new Date().toISOString()
          },
          {
            id: 3,
            title: 'Update documentation',
            description: 'Update API documentation for version 2.0',
            status: 'Completed',
            assignee_id: 3,
            priority: 'Low',
            dueDate: '2024-01-05',
            createdAt: new Date().toISOString()
          },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, []);

  useEffect(() => {
    fetchEmployees();
  }, []);

  const filteredTasks = useMemo(() => {
    return tasks.filter(task => {
      const assigneeName = getName(task.assignee_id);
      const matchesSearch = task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           task.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           assigneeName.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = !statusFilter || task.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [tasks, searchTerm, statusFilter, getName]);



  const handleCreateTask = () => {
    setIsEditing(false);
    setFormData({
      title: '',
      description: '',
      status: 'Pending',
      assignee_id: '',
      priority: 'Medium',
      dueDate: ''
    });
    setDialogOpen(true);
  };

  const handleEditTask = (task) => {
    setIsEditing(true);
    setSelectedTask(task);
    setFormData({
      title: task.title,
      description: task.description,
      status: task.status,
      assignee_id: task.assignee_id || '',
      priority: task.priority,
      dueDate: task.dueDate
    });
    setDialogOpen(true);
  };

  const handleViewTask = (task) => {
    setSelectedTask(task);
    setIsEditing(false);
    setDialogOpen(true);
  };

  const handleSaveTask = async () => {
    if (isManager && !formData.assignee_id) {
      setError('Please select an assignee.');
      return;
    }

    try {
      if (isEditing) {
        // Update existing task
        const response = await api.put(`/tasks/${selectedTask.id}`, formData);
        setTasks(tasks.map(task => task.id === selectedTask.id ? response.data : task));
      } else {
        // Create new task
        const response = await api.post('/tasks', formData);
        setTasks([...tasks, response.data]);
      }
      setDialogOpen(false);
    } catch (error) {
      console.error('Error saving task:', error);
      setError('Failed to save task. Please try again.');
    }
  };

  const TaskCard = ({ task }) => (
    <Card
      sx={{
        p: 3,
        cursor: 'pointer',
        '&:hover': { boxShadow: 3 },
        transition: 'all 0.2s',
      }}
      onClick={() => handleViewTask(task)}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
        <Typography variant="h6" sx={{ flex: 1, mr: 2, '&:hover': { color: 'primary.main' } }}>
          {task.title}
        </Typography>
        <Chip
          label={task.priority}
          size="small"
          icon={<FlagIcon />}
          color={
            task.priority === 'High' ? 'error' :
            task.priority === 'Medium' ? 'warning' :
            'success'
          }
          variant="outlined"
        />
      </Box>

      <Typography color="text.secondary" sx={{ mb: 2, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
        {task.description}
      </Typography>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Chip
          label={task.status}
          size="small"
          color={
            task.status === 'Completed' ? 'success' :
            task.status === 'In Progress' ? 'primary' :
            task.status === 'Pending' ? 'warning' :
            'error'
          }
        />
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.secondary' }}>
          <CalendarDaysIcon fontSize="small" />
          <Typography variant="body2">{new Date(task.dueDate).toLocaleDateString()}</Typography>
        </Box>
      </Box>

      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'text.secondary' }}>
          <UserIcon fontSize="small" />
          <Typography variant="body2">{getName(task.assignee_id)}</Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1, opacity: 0, '&:hover': { opacity: 1 } }}>
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              handleViewTask(task);
            }}
          >
            <EyeIcon />
          </IconButton>
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              handleEditTask(task);
            }}
          >
            <PencilIcon />
          </IconButton>
        </Box>
      </Box>
    </Card>
  );

  if (loading) {
    return (
      <DashboardLayout>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgress sx={{ mb: 2 }} />
            <Typography color="text.secondary">Loading tasks...</Typography>
          </Box>
        </Box>
      </DashboardLayout>
    );
  }

  const onDragEnd = (result) => {
    if (!result.destination) return;
    const { source, destination, draggableId } = result;
    if (source.droppableId !== destination.droppableId) {
      const task = tasks.find(t => t.id.toString() === draggableId);
      if (task) {
        const updatedTask = { ...task, status: destination.droppableId };
        setTasks(tasks.map(t => t.id === task.id ? updatedTask : t));
        api.put(`/tasks/${task.id}`, { status: destination.droppableId }).catch(error => {
          console.error('Error updating task status:', error);
          // Revert on error
          setTasks(tasks.map(t => t.id === task.id ? task : t));
        });
      }
    }
  };

  return (
    <DashboardLayout>
      <Box sx={{ p: 3 }}>
        {/* Header Section */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h4" sx={{ color: 'text.primary' }}>Tasks</Typography>
            <Typography sx={{ color: 'text.secondary' }}>Manage and track your team's tasks</Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<PlusIcon />}
            onClick={handleCreateTask}
          >
            New Task
          </Button>
        </Box>

        {/* Main Content */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} action={
            <IconButton size="small" onClick={() => setError('')}>
              <XMarkIcon />
            </IconButton>
          }>
            {error}
          </Alert>
        )}

        {/* Filters and View Controls */}
        <Card sx={{ p: 3, mb: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                placeholder="Search tasks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <MagnifyingGlassIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  startAdornment={<FunnelIcon sx={{ mr: 1, color: 'text.secondary' }} />}
                >
                  <MenuItem value="">All Statuses</MenuItem>
                  <MenuItem value="Pending">Pending</MenuItem>
                  <MenuItem value="In Progress">In Progress</MenuItem>
                  <MenuItem value="Completed">Completed</MenuItem>
                  <MenuItem value="Overdue">Overdue</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <IconButton
                  onClick={() => setViewMode('grid')}
                  sx={{
                    border: 1,
                    borderColor: viewMode === 'grid' ? 'primary.main' : 'grey.300',
                    bgcolor: viewMode === 'grid' ? 'primary.light' : 'transparent',
                  }}
                >
                  <Squares2X2Icon />
                </IconButton>
                <IconButton
                  onClick={() => setViewMode('list')}
                  sx={{
                    border: 1,
                    borderColor: viewMode === 'list' ? 'primary.main' : 'grey.300',
                    bgcolor: viewMode === 'list' ? 'primary.light' : 'transparent',
                  }}
                >
                  <ListBulletIcon />
                </IconButton>
                <IconButton
                  onClick={() => setViewMode('kanban')}
                  sx={{
                    border: 1,
                    borderColor: viewMode === 'kanban' ? 'primary.main' : 'grey.300',
                    bgcolor: viewMode === 'kanban' ? 'primary.light' : 'transparent',
                  }}
                >
                  <QueueListIcon />
                </IconButton>
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Button
                fullWidth
                variant="outlined"
                onClick={() => {
                  setSearchTerm('');
                  setStatusFilter('');
                }}
              >
                Clear Filters
              </Button>
            </Grid>
          </Grid>
        </Card>

        {/* Results Summary */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography color="text.secondary">
            Showing {filteredTasks.length} of {tasks.length} tasks
          </Typography>
          {(searchTerm || statusFilter) && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">Filtered by:</Typography>
              {searchTerm && <Chip label={`"${searchTerm}"`} size="small" />}
              {statusFilter && <Chip label={statusFilter} size="small" />}
            </Box>
          )}
        </Box>

        {/* Tasks Display */}
        <DragDropContext onDragEnd={onDragEnd}>
          {viewMode === 'kanban' ? (
            <Box sx={{ display: 'flex', gap: 2, overflowX: 'auto', p: 2 }}>
              {['Pending', 'In Progress', 'Completed', 'Overdue'].map(status => (
                <Card key={status} sx={{ minWidth: 320, p: 2 }}>
                  <Typography variant="h6" fontWeight="bold" mb={2}>{status}</Typography>
                  <Droppable droppableId={status}>
                    {(provided) => (
                      <Box ref={provided.innerRef} {...provided.droppableProps} sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                        {filteredTasks.filter(task => task.status === status).map((task, index) => (
                          <Draggable key={task.id} draggableId={task.id.toString()} index={index}>
                            {(provided) => (
                              <Box ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps}>
                                <TaskCard task={task} />
                              </Box>
                            )}
                          </Draggable>
                        ))}
                        {provided.placeholder}
                      </Box>
                    )}
                  </Droppable>
                </Card>
              ))}
            </Box>
          ) : viewMode === 'grid' ? (
            <Grid container spacing={3}>
              {filteredTasks.map((task) => (
                <Grid item xs={12} md={6} lg={4} key={task.id}>
                  <TaskCard task={task} />
                </Grid>
              ))}
            </Grid>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Title</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Assignee</TableCell>
                    <TableCell>Due Date</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredTasks.map((task) => (
                    <TableRow key={task.id} hover>
                      <TableCell>
                        <Typography fontWeight="bold">{task.title}</Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {task.description}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={task.status}
                          size="small"
                          color={
                            task.status === 'Completed' ? 'success' :
                            task.status === 'In Progress' ? 'primary' :
                            task.status === 'Pending' ? 'warning' :
                            'error'
                          }
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={task.priority}
                          size="small"
                          icon={<FlagIcon />}
                          color={
                            task.priority === 'High' ? 'error' :
                            task.priority === 'Medium' ? 'warning' :
                            'success'
                          }
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <UserIcon fontSize="small" color="disabled" />
                          <Typography variant="body2">{getName(task.assignee_id)}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <CalendarDaysIcon fontSize="small" color="disabled" />
                          <Typography variant="body2">{new Date(task.dueDate).toLocaleDateString()}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <IconButton size="small" onClick={() => handleViewTask(task)}>
                            <EyeIcon />
                          </IconButton>
                          <IconButton size="small" onClick={() => handleEditTask(task)}>
                            <PencilIcon />
                          </IconButton>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </DragDropContext>

        {filteredTasks.length === 0 && (
          <Card sx={{ p: 6, textAlign: 'center' }}>
            <Box sx={{ width: 64, height: 64, bgcolor: 'grey.100', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 2 }}>
              <Box sx={{ width: 32, height: 32, color: 'grey.400' }}>
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </Box>
            </Box>
            <Typography variant="h6" fontWeight="bold" mb={1}>
              No tasks found
            </Typography>
            <Typography color="text.secondary">
              {searchTerm || statusFilter
                ? "No tasks match your current filters. Try adjusting your search criteria."
                : "Get started by creating your first task."
              }
            </Typography>
          </Card>
        )}

        {/* Task Dialog */}
        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {isEditing ? 'Edit Task' : selectedTask ? 'Task Details' : 'Create New Task'}
        </DialogTitle>
        <DialogContent>
          {selectedTask && !isEditing ? (
            // View mode
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <Box>
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>Title</Typography>
                <Typography variant="h5">{selectedTask.title}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>Description</Typography>
                <Box sx={{ bgcolor: 'grey.50', p: 2, borderRadius: 1 }}>
                  <Typography color="text.secondary">{selectedTask.description}</Typography>
                </Box>
              </Box>
              <Grid container spacing={3}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>Status</Typography>
                  <Chip
                    label={selectedTask.status}
                    color={
                      selectedTask.status === 'Completed' ? 'success' :
                      selectedTask.status === 'In Progress' ? 'primary' :
                      selectedTask.status === 'Pending' ? 'warning' :
                      'error'
                    }
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>Priority</Typography>
                  <Chip
                    label={selectedTask.priority}
                    icon={<FlagIcon />}
                    color={
                      selectedTask.priority === 'High' ? 'error' :
                      selectedTask.priority === 'Medium' ? 'warning' :
                      'success'
                    }
                    variant="outlined"
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>Assignee</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <UserIcon color="disabled" />
                    <Typography>{getName(selectedTask.assignee_id)}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>Due Date</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CalendarDaysIcon color="disabled" />
                    <Typography>{new Date(selectedTask.dueDate).toLocaleDateString()}</Typography>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          ) : (
            // Edit/Create mode
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <Box>
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>Title *</Typography>
                <TextField
                  fullWidth
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  placeholder="Enter task title"
                  required
                />
              </Box>
              <Box>
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>Description</Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  placeholder="Enter task description"
                />
              </Box>
              <Grid container spacing={3}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>Status</Typography>
                  <FormControl fullWidth>
                    <Select
                      value={formData.status}
                      onChange={(e) => setFormData({...formData, status: e.target.value})}
                    >
                      <MenuItem value="Pending">Pending</MenuItem>
                      <MenuItem value="In Progress">In Progress</MenuItem>
                      <MenuItem value="Completed">Completed</MenuItem>
                      <MenuItem value="Overdue">Overdue</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>Priority</Typography>
                  <FormControl fullWidth>
                    <Select
                      value={formData.priority}
                      onChange={(e) => setFormData({...formData, priority: e.target.value})}
                    >
                      <MenuItem value="Low">Low</MenuItem>
                      <MenuItem value="Medium">Medium</MenuItem>
                      <MenuItem value="High">High</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
              <Grid container spacing={3}>
                {isManager && (
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>Assignee *</Typography>
                    <FormControl fullWidth>
                      <Select
                        value={formData.assignee_id}
                        onChange={(e) => setFormData({...formData, assignee_id: e.target.value})}
                      >
                        <MenuItem value="">Select Employee</MenuItem>
                        {employees.map(emp => (
                          <MenuItem key={emp.id} value={emp.id}>
                            {emp.name}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                )}
                <Grid item xs={isManager ? 6 : 12}>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>Due Date</Typography>
                  <TextField
                    fullWidth
                    type="date"
                    value={formData.dueDate}
                    onChange={(e) => setFormData({...formData, dueDate: e.target.value})}
                  />
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>
            {selectedTask && !isEditing ? 'Close' : 'Cancel'}
          </Button>
          {(!selectedTask || isEditing) && (
            <Button variant="contained" onClick={handleSaveTask}>
              {isEditing ? 'Update Task' : 'Create Task'}
            </Button>
          )}
          {selectedTask && !isEditing && (
            <Button variant="outlined" onClick={() => setIsEditing(true)}>
              Edit Task
            </Button>
          )}
        </DialogActions>
      </Dialog>
      </Box>
    </DashboardLayout>
  );
};

export default Tasks;
