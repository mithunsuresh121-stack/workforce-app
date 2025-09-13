import React, { useEffect, useState, useMemo } from 'react';
import axios from 'axios';
import {
  Card,
  CardBody,
  CardHeader,
  Typography,
  Button,
  Chip,
  Dialog,
  DialogHeader,
  DialogBody,
  DialogFooter,
  Input,
  Textarea,
  Select,
  Option,
  Spinner,
  Alert,
  IconButton
} from '@material-tailwind/react';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  Squares2X2Icon,
  ListBulletIcon,
  PencilIcon,
  EyeIcon
} from '@heroicons/react/24/outline';

const Tasks = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: 'Pending',
    assignee: '',
    priority: 'Medium',
    dueDate: ''
  });

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await axios.get('/api/tasks');
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
            assignee: 'John Doe',
            priority: 'High',
            dueDate: '2024-01-15',
            createdAt: new Date().toISOString()
          },
          {
            id: 2,
            title: 'Review code changes',
            description: 'Review pull request #123 for the new feature',
            status: 'Pending',
            assignee: 'Jane Smith',
            priority: 'Medium',
            dueDate: '2024-01-10',
            createdAt: new Date().toISOString()
          },
          {
            id: 3,
            title: 'Update documentation',
            description: 'Update API documentation for version 2.0',
            status: 'Completed',
            assignee: 'Bob Johnson',
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

  const filteredTasks = useMemo(() => {
    return tasks.filter(task => {
      const matchesSearch = task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           task.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           task.assignee.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = !statusFilter || task.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [tasks, searchTerm, statusFilter]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'Completed': return 'green';
      case 'In Progress': return 'blue';
      case 'Pending': return 'orange';
      case 'Overdue': return 'red';
      default: return 'gray';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'High': return 'red';
      case 'Medium': return 'yellow';
      case 'Low': return 'green';
      default: return 'gray';
    }
  };

  const handleCreateTask = () => {
    setIsEditing(false);
    setFormData({
      title: '',
      description: '',
      status: 'Pending',
      assignee: '',
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
      assignee: task.assignee,
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
    try {
      if (isEditing) {
        // Update existing task
        const response = await axios.put(`/api/tasks/${selectedTask.id}`, formData);
        setTasks(tasks.map(task => task.id === selectedTask.id ? response.data : task));
      } else {
        // Create new task
        const response = await axios.post('/api/tasks', formData);
        setTasks([...tasks, response.data]);
      }
      setDialogOpen(false);
    } catch (error) {
      console.error('Error saving task:', error);
      setError('Failed to save task. Please try again.');
    }
  };

  const TaskCard = ({ task }) => (
    <Card className="hover:shadow-lg transition-shadow">
      <CardBody>
        <div className="flex justify-between items-start mb-3">
          <Typography variant="h6" color="blue-gray" className="flex-1 mr-2">
            {task.title}
          </Typography>
          <Chip
            color={getPriorityColor(task.priority)}
            value={task.priority}
            size="sm"
            variant="outlined"
          />
        </div>

        <Typography variant="small" color="gray" className="mb-3 line-clamp-2">
          {task.description}
        </Typography>

        <div className="flex justify-between items-center mb-3">
          <Chip
            color={getStatusColor(task.status)}
            value={task.status}
            size="sm"
          />
          <Typography variant="small" color="gray">
            Due: {new Date(task.dueDate).toLocaleDateString()}
          </Typography>
        </div>

        <Typography variant="small" color="gray" className="mb-4">
          Assigned to: {task.assignee}
        </Typography>

        <div className="flex gap-2">
          <IconButton
            size="sm"
            variant="outlined"
            onClick={() => handleViewTask(task)}
          >
            <EyeIcon className="h-4 w-4" />
          </IconButton>
          <IconButton
            size="sm"
            variant="outlined"
            onClick={() => handleEditTask(task)}
          >
            <PencilIcon className="h-4 w-4" />
          </IconButton>
        </div>
      </CardBody>
    </Card>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-6">
        <Typography variant="h3" color="blue-gray">
          Tasks
        </Typography>
        <Button
          onClick={handleCreateTask}
          className="flex items-center gap-2"
        >
          <PlusIcon className="h-4 w-4" />
          New Task
        </Button>
      </div>

      {error && (
        <Alert color="red" className="mb-6">
          {error}
        </Alert>
      )}

      {/* Filters and View Controls */}
      <Card className="mb-6">
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Input
                type="text"
                label="Search tasks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                icon={<MagnifyingGlassIcon className="h-5 w-5" />}
              />
            </div>
            <div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Statuses</option>
                <option value="Pending">Pending</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
                <option value="Overdue">Overdue</option>
              </select>
            </div>
            <div className="flex gap-2">
              <IconButton
                variant={viewMode === 'grid' ? 'filled' : 'outlined'}
                onClick={() => setViewMode('grid')}
              >
                <Squares2X2Icon className="h-4 w-4" />
              </IconButton>
              <IconButton
                variant={viewMode === 'list' ? 'filled' : 'outlined'}
                onClick={() => setViewMode('list')}
              >
                <ListBulletIcon className="h-4 w-4" />
              </IconButton>
            </div>
            <div className="flex items-end">
              <Button
                variant="outlined"
                onClick={() => {
                  setSearchTerm('');
                  setStatusFilter('');
                }}
                className="w-full"
              >
                Clear Filters
              </Button>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Results Summary */}
      <Typography variant="small" color="gray" className="mb-4">
        Showing {filteredTasks.length} of {tasks.length} tasks
      </Typography>

      {/* Tasks Display */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTasks.map((task) => (
            <TaskCard key={task.id} task={task} />
          ))}
        </div>
      ) : (
        <Card>
          <CardBody className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full min-w-max table-auto text-left">
                <thead>
                  <tr>
                    <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                      <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
                        Title
                      </Typography>
                    </th>
                    <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                      <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
                        Status
                      </Typography>
                    </th>
                    <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                      <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
                        Assignee
                      </Typography>
                    </th>
                    <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                      <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
                        Due Date
                      </Typography>
                    </th>
                    <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                      <Typography variant="small" color="blue-gray" className="font-normal leading-none opacity-70">
                        Actions
                      </Typography>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTasks.map((task) => (
                    <tr key={task.id}>
                      <td className="p-4 border-b border-blue-gray-50">
                        <Typography variant="small" color="blue-gray" className="font-normal">
                          {task.title}
                        </Typography>
                      </td>
                      <td className="p-4 border-b border-blue-gray-50">
                        <Chip
                          color={getStatusColor(task.status)}
                          value={task.status}
                          size="sm"
                        />
                      </td>
                      <td className="p-4 border-b border-blue-gray-50">
                        <Typography variant="small" color="blue-gray" className="font-normal">
                          {task.assignee}
                        </Typography>
                      </td>
                      <td className="p-4 border-b border-blue-gray-50">
                        <Typography variant="small" color="blue-gray" className="font-normal">
                          {new Date(task.dueDate).toLocaleDateString()}
                        </Typography>
                      </td>
                      <td className="p-4 border-b border-blue-gray-50">
                        <div className="flex gap-2">
                          <IconButton
                            size="sm"
                            variant="text"
                            onClick={() => handleViewTask(task)}
                          >
                            <EyeIcon className="h-4 w-4" />
                          </IconButton>
                          <IconButton
                            size="sm"
                            variant="text"
                            onClick={() => handleEditTask(task)}
                          >
                            <PencilIcon className="h-4 w-4" />
                          </IconButton>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardBody>
        </Card>
      )}

      {filteredTasks.length === 0 && (
        <Card>
          <CardBody className="text-center py-12">
            <Typography variant="h6" color="gray">
              No tasks found matching your criteria.
            </Typography>
          </CardBody>
        </Card>
      )}

      {/* Task Dialog */}
      <Dialog open={dialogOpen} handler={setDialogOpen} size="lg">
        <DialogHeader>
          {isEditing ? 'Edit Task' : selectedTask ? 'Task Details' : 'Create New Task'}
        </DialogHeader>
        <DialogBody divider className="space-y-4">
          {selectedTask && !isEditing ? (
            // View mode
            <div className="space-y-4">
              <div>
                <Typography variant="small" color="blue-gray" className="font-medium">
                  Title
                </Typography>
                <Typography variant="h6" color="blue-gray">
                  {selectedTask.title}
                </Typography>
              </div>
              <div>
                <Typography variant="small" color="blue-gray" className="font-medium">
                  Description
                </Typography>
                <Typography variant="small" color="gray">
                  {selectedTask.description}
                </Typography>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Typography variant="small" color="blue-gray" className="font-medium">
                    Status
                  </Typography>
                  <Chip
                    color={getStatusColor(selectedTask.status)}
                    value={selectedTask.status}
                    size="sm"
                  />
                </div>
                <div>
                  <Typography variant="small" color="blue-gray" className="font-medium">
                    Priority
                  </Typography>
                  <Chip
                    color={getPriorityColor(selectedTask.priority)}
                    value={selectedTask.priority}
                    size="sm"
                    variant="outlined"
                  />
                </div>
                <div>
                  <Typography variant="small" color="blue-gray" className="font-medium">
                    Assignee
                  </Typography>
                  <Typography variant="small" color="gray">
                    {selectedTask.assignee}
                  </Typography>
                </div>
                <div>
                  <Typography variant="small" color="blue-gray" className="font-medium">
                    Due Date
                  </Typography>
                  <Typography variant="small" color="gray">
                    {new Date(selectedTask.dueDate).toLocaleDateString()}
                  </Typography>
                </div>
              </div>
            </div>
          ) : (
            // Edit/Create mode
            <div className="space-y-4">
              <Input
                label="Title"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                required
              />
              <Textarea
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
              />
              <div className="grid grid-cols-2 gap-4">
                <Select
                  label="Status"
                  value={formData.status}
                  onChange={(value) => setFormData({...formData, status: value})}
                >
                  <Option value="Pending">Pending</Option>
                  <Option value="In Progress">In Progress</Option>
                  <Option value="Completed">Completed</Option>
                  <Option value="Overdue">Overdue</Option>
                </Select>
                <Select
                  label="Priority"
                  value={formData.priority}
                  onChange={(value) => setFormData({...formData, priority: value})}
                >
                  <Option value="Low">Low</Option>
                  <Option value="Medium">Medium</Option>
                  <Option value="High">High</Option>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Assignee"
                  value={formData.assignee}
                  onChange={(e) => setFormData({...formData, assignee: e.target.value})}
                />
                <Input
                  type="date"
                  label="Due Date"
                  value={formData.dueDate}
                  onChange={(e) => setFormData({...formData, dueDate: e.target.value})}
                />
              </div>
            </div>
          )}
        </DialogBody>
        <DialogFooter>
          <Button variant="text" color="red" onClick={() => setDialogOpen(false)}>
            {selectedTask && !isEditing ? 'Close' : 'Cancel'}
          </Button>
          {(!selectedTask || isEditing) && (
            <Button variant="gradient" color="green" onClick={handleSaveTask}>
              {isEditing ? 'Update Task' : 'Create Task'}
            </Button>
          )}
          {selectedTask && !isEditing && (
            <Button variant="gradient" color="blue" onClick={() => { setIsEditing(true); }}>
              Edit Task
            </Button>
          )}
        </DialogFooter>
      </Dialog>
    </div>
  );
};

export default Tasks;
