import React, { useEffect, useState, useMemo } from 'react';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  Squares2X2Icon,
  ListBulletIcon,
  PencilIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import {
  Card,
  CardBody,
  Typography,
  Button,
  Input,
  IconButton,
  Chip,
  Alert,
  Spinner
} from '@material-tailwind/react';
import { api } from '../contexts/AuthContext';

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
    <div className="bg-white p-6 rounded-lg shadow-md border hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <h6 className="text-lg font-semibold text-gray-800 flex-1 mr-2">
          {task.title}
        </h6>
        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${
          task.priority === 'High' ? 'bg-red-100 text-red-800 border-red-200' :
          task.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800 border-yellow-200' :
          'bg-green-100 text-green-800 border-green-200'
        }`}>
          {task.priority}
        </span>
      </div>

      <p className="text-sm text-gray-600 mb-3 line-clamp-2">
        {task.description}
      </p>

      <div className="flex justify-between items-center mb-3">
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          task.status === 'Completed' ? 'bg-green-100 text-green-800' :
          task.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
          task.status === 'Pending' ? 'bg-orange-100 text-orange-800' :
          'bg-red-100 text-red-800'
        }`}>
          {task.status}
        </span>
        <p className="text-sm text-gray-600">
          Due: {new Date(task.dueDate).toLocaleDateString()}
        </p>
      </div>

      <p className="text-sm text-gray-600 mb-4">
        Assigned to: {task.assignee}
      </p>

      <div className="flex gap-2">
        <button
          className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
          onClick={() => handleViewTask(task)}
        >
          <EyeIcon className="h-4 w-4" />
        </button>
        <button
          className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
          onClick={() => handleEditTask(task)}
        >
          <PencilIcon className="h-4 w-4" />
        </button>
      </div>
    </div>
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
        <div className="bg-white p-12 rounded-lg shadow-md border text-center">
          <h6 className="text-lg font-semibold text-gray-600">
            No tasks found matching your criteria.
          </h6>
        </div>
      )}

      {/* Task Dialog */}
      {dialogOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl p-6">
            <h4 className="text-xl font-semibold mb-4">
              {isEditing ? 'Edit Task' : selectedTask ? 'Task Details' : 'Create New Task'}
            </h4>
            <div className="space-y-4">
              {selectedTask && !isEditing ? (
                // View mode
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Title
                    </label>
                    <p className="text-lg font-semibold text-gray-800">
                      {selectedTask.title}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Description
                    </label>
                    <p className="text-sm text-gray-600">
                      {selectedTask.description}
                    </p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Status
                      </label>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        selectedTask.status === 'Completed' ? 'bg-green-100 text-green-800' :
                        selectedTask.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                        selectedTask.status === 'Pending' ? 'bg-orange-100 text-orange-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {selectedTask.status}
                      </span>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Priority
                      </label>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${
                        selectedTask.priority === 'High' ? 'bg-red-100 text-red-800 border-red-200' :
                        selectedTask.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800 border-yellow-200' :
                        'bg-green-100 text-green-800 border-green-200'
                      }`}>
                        {selectedTask.priority}
                      </span>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Assignee
                      </label>
                      <p className="text-sm text-gray-600">
                        {selectedTask.assignee}
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Due Date
                      </label>
                      <p className="text-sm text-gray-600">
                        {new Date(selectedTask.dueDate).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                // Edit/Create mode
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Title
                    </label>
                    <input
                      type="text"
                      value={formData.title}
                      onChange={(e) => setFormData({...formData, title: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      rows={3}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Status
                      </label>
                      <select
                        value={formData.status}
                        onChange={(e) => setFormData({...formData, status: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="Pending">Pending</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Completed">Completed</option>
                        <option value="Overdue">Overdue</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Priority
                      </label>
                      <select
                        value={formData.priority}
                        onChange={(e) => setFormData({...formData, priority: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="Low">Low</option>
                        <option value="Medium">Medium</option>
                        <option value="High">High</option>
                      </select>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Assignee
                      </label>
                      <input
                        type="text"
                        value={formData.assignee}
                        onChange={(e) => setFormData({...formData, assignee: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Due Date
                      </label>
                      <input
                        type="date"
                        value={formData.dueDate}
                        onChange={(e) => setFormData({...formData, dueDate: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
            <div className="flex justify-end gap-4 mt-6">
              <button
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
                onClick={() => setDialogOpen(false)}
              >
                {selectedTask && !isEditing ? 'Close' : 'Cancel'}
              </button>
              {(!selectedTask || isEditing) && (
                <button
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                  onClick={handleSaveTask}
                >
                  {isEditing ? 'Update Task' : 'Create Task'}
                </button>
              )}
              {selectedTask && !isEditing && (
                <button
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onClick={() => { setIsEditing(true); }}
                >
                  Edit Task
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Tasks;
