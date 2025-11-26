import React, { useEffect, useState, useMemo } from 'react';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  Squares2X2Icon,
  ListBulletIcon,
  PencilIcon,
  EyeIcon,
  FunnelIcon,
  XMarkIcon,
  CalendarDaysIcon,
  UserIcon,
  FlagIcon
} from '@heroicons/react/24/outline';
import { api, useAuth } from '../contexts/AuthContext';
import TaskAttachments from '../components/TaskAttachments';

const Tasks = () => {
  const { user: currentUser } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [taskAttachments, setTaskAttachments] = useState([]);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: 'Pending',
    assignee_id: '',
    priority: 'Medium',
    due_at: ''
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError('');

        // Fetch tasks and users in parallel
        const [tasksResponse, usersResponse] = await Promise.all([
          api.get('/tasks'),
          api.get('/users')
        ]);

        setTasks(tasksResponse.data);
        setUsers(usersResponse.data);
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Failed to load tasks and users. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
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

  const getUserNameById = (userId) => {
    const user = users.find(u => u.id === userId);
    return user ? user.full_name : 'Unknown User';
  };

  const canCreateTask = () => {
    return currentUser && ['Manager', 'CompanyAdmin', 'SuperAdmin'].includes(currentUser.role);
  };

  const canEditTask = (task) => {
    if (!currentUser) return false;
    const allowedRoles = ['Manager', 'CompanyAdmin', 'SuperAdmin'];
    return allowedRoles.includes(currentUser.role) || task.assignee_id === currentUser.id;
  };

  const handleCreateTask = () => {
    if (!canCreateTask()) {
      setError('You do not have permission to create tasks.');
      return;
    }

    setIsEditing(false);
    setFormData({
      title: '',
      description: '',
      status: 'Pending',
      assignee_id: '',
      priority: 'Medium',
      due_at: ''
    });
    setDialogOpen(true);
  };

  const handleEditTask = async (task) => {
    if (!canEditTask(task)) {
      setError('You do not have permission to edit this task.');
      return;
    }

    setIsEditing(true);
    setSelectedTask(task);
    setFormData({
      title: task.title,
      description: task.description,
      status: task.status,
      assignee_id: task.assignee_id || '',
      priority: task.priority,
      due_at: task.due_at ? new Date(task.due_at).toISOString().split('T')[0] : ''
    });

    try {
      const response = await api.get(`/tasks/${task.id}/attachments`);
      setTaskAttachments(response.data);
    } catch (error) {
      console.error('Error fetching attachments:', error);
      setTaskAttachments([]);
    }

    setDialogOpen(true);
  };

  const handleViewTask = async (task) => {
    setSelectedTask(task);
    setIsEditing(false);

    try {
      const response = await api.get(`/tasks/${task.id}/attachments`);
      setTaskAttachments(response.data);
    } catch (error) {
      console.error('Error fetching attachments:', error);
      setTaskAttachments([]);
    }

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
    <div className="bg-surface border border-border rounded-lg p-6 hover:shadow-linear-lg transition-all duration-200 group cursor-pointer"
         onClick={() => handleViewTask(task)}>
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-neutral-900 flex-1 mr-3 group-hover:text-accent-600 transition-colors">
          {task.title}
        </h3>
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${
          task.priority === 'High' ? 'bg-danger-100 text-danger-700' :
          task.priority === 'Medium' ? 'bg-warning-100 text-warning-700' :
          'bg-success-100 text-success-700'
        }`}>
          <FlagIcon className="w-3 h-3 inline mr-1" />
          {task.priority}
        </div>
      </div>

      <p className="text-neutral-600 mb-4 line-clamp-2">
        {task.description}
      </p>

      <div className="flex justify-between items-center mb-4">
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${
          task.status === 'Completed' ? 'bg-success-100 text-success-700' :
          task.status === 'In Progress' ? 'bg-accent-100 text-accent-700' :
          task.status === 'Pending' ? 'bg-warning-100 text-warning-700' :
          'bg-danger-100 text-danger-700'
        }`}>
          {task.status}
        </div>
        <div className="flex items-center gap-1 text-neutral-500 text-sm">
          <CalendarDaysIcon className="w-4 h-4" />
          {new Date(task.dueDate).toLocaleDateString()}
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-neutral-600">
          <UserIcon className="w-4 h-4" />
          <span className="text-sm">{getUserNameById(task.assignee_id)}</span>
        </div>
        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            className="p-2 text-neutral-400 hover:text-accent-600 hover:bg-accent-50 rounded-lg transition-colors"
            onClick={(e) => {
              e.stopPropagation();
              handleViewTask(task);
            }}
          >
            <EyeIcon className="w-4 h-4" />
          </button>
          {canEditTask(task) && (
            <button
              className="p-2 text-neutral-400 hover:text-accent-600 hover:bg-accent-50 rounded-lg transition-colors"
              onClick={(e) => {
                e.stopPropagation();
                handleEditTask(task);
              }}
            >
              <PencilIcon className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-accent-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-neutral-600">Loading tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="bg-surface border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-semibold text-neutral-900">Tasks</h1>
              <p className="text-neutral-600 mt-1">Manage and track your team's tasks</p>
            </div>
            <button
              onClick={handleCreateTask}
              className="flex items-center gap-2 px-4 py-2 bg-accent-500 text-white rounded-lg hover:bg-accent-600 transition-colors duration-200 font-medium"
            >
              <PlusIcon className="w-5 h-5" />
              New Task
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6">
        {error && (
          <div className="mb-6 p-4 bg-danger-50 border border-danger-200 text-danger-800 rounded-lg">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p>{error}</p>
              <button
                onClick={() => setError('')}
                className="ml-auto text-current hover:opacity-70"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {/* Filters and View Controls */}
        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search tasks..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="relative">
              <FunnelIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400 w-5 h-5" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent appearance-none bg-white"
              >
                <option value="">All Statuses</option>
                <option value="Pending">Pending</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
                <option value="Overdue">Overdue</option>
              </select>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('grid')}
                className={`flex items-center justify-center p-2 rounded-lg transition-colors duration-200 ${
                  viewMode === 'grid'
                    ? 'bg-accent-100 text-accent-600 border border-accent-200'
                    : 'text-neutral-600 border border-neutral-200 hover:bg-neutral-50'
                }`}
              >
                <Squares2X2Icon className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`flex items-center justify-center p-2 rounded-lg transition-colors duration-200 ${
                  viewMode === 'list'
                    ? 'bg-accent-100 text-accent-600 border border-accent-200'
                    : 'text-neutral-600 border border-neutral-200 hover:bg-neutral-50'
                }`}
              >
                <ListBulletIcon className="w-5 h-5" />
              </button>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => {
                  setSearchTerm('');
                  setStatusFilter('');
                }}
                className="w-full px-4 py-2 text-neutral-600 border border-neutral-200 rounded-lg hover:bg-neutral-50 transition-colors duration-200"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Results Summary */}
        <div className="flex items-center justify-between mb-6">
          <p className="text-neutral-600">
            Showing {filteredTasks.length} of {tasks.length} tasks
          </p>
          {(searchTerm || statusFilter) && (
            <div className="flex items-center gap-2 text-sm text-neutral-500">
              <span>Filtered by:</span>
              {searchTerm && <span className="px-2 py-1 bg-neutral-100 rounded">"{searchTerm}"</span>}
              {statusFilter && <span className="px-2 py-1 bg-neutral-100 rounded">{statusFilter}</span>}
            </div>
          )}
        </div>

        {/* Tasks Display */}
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTasks.map((task) => (
              <TaskCard key={task.id} task={task} />
            ))}
          </div>
        ) : (
          <div className="bg-surface border border-border rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-neutral-50 border-b border-border">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-medium text-neutral-700">
                      Title
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-neutral-700">
                      Status
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-neutral-700">
                      Priority
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-neutral-700">
                      Assignee
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-neutral-700">
                      Due Date
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-neutral-700">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filteredTasks.map((task) => (
                    <tr key={task.id} className="hover:bg-neutral-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-medium text-neutral-900">{task.title}</div>
                        <div className="text-sm text-neutral-600 mt-1 line-clamp-1">{task.description}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className={`inline-flex px-3 py-1 rounded-full text-xs font-medium ${
                          task.status === 'Completed' ? 'bg-success-100 text-success-700' :
                          task.status === 'In Progress' ? 'bg-accent-100 text-accent-700' :
                          task.status === 'Pending' ? 'bg-warning-100 text-warning-700' :
                          'bg-danger-100 text-danger-700'
                        }`}>
                          {task.status}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className={`inline-flex px-3 py-1 rounded-full text-xs font-medium ${
                          task.priority === 'High' ? 'bg-danger-100 text-danger-700' :
                          task.priority === 'Medium' ? 'bg-warning-100 text-warning-700' :
                          'bg-success-100 text-success-700'
                        }`}>
                          <FlagIcon className="w-3 h-3 mr-1" />
                          {task.priority}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <UserIcon className="w-4 h-4 text-neutral-400" />
                          <span className="text-neutral-700">{getUserNameById(task.assignee_id)}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2 text-neutral-600">
                          <CalendarDaysIcon className="w-4 h-4" />
                          {task.due_at ? new Date(task.due_at).toLocaleDateString() : 'No due date'}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex gap-2">
                          <button
                            className="p-2 text-neutral-400 hover:text-accent-600 hover:bg-accent-50 rounded-lg transition-colors"
                            onClick={() => handleViewTask(task)}
                          >
                            <EyeIcon className="w-4 h-4" />
                          </button>
                          {canEditTask(task) && (
                            <button
                              className="p-2 text-neutral-400 hover:text-accent-600 hover:bg-accent-50 rounded-lg transition-colors"
                              onClick={() => handleEditTask(task)}
                            >
                              <PencilIcon className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {filteredTasks.length === 0 && (
          <div className="bg-surface border border-border rounded-lg p-12 text-center">
            <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">
              No tasks found
            </h3>
            <p className="text-neutral-600">
              {searchTerm || statusFilter
                ? "No tasks match your current filters. Try adjusting your search criteria."
                : "Get started by creating your first task."
              }
            </p>
          </div>
        )}
      </div>

      {/* Task Dialog */}
      {dialogOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 p-4">
          <div className="bg-surface rounded-lg shadow-linear-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-border">
              <h2 className="text-xl font-semibold text-neutral-900">
                {isEditing ? 'Edit Task' : selectedTask ? 'Task Details' : 'Create New Task'}
              </h2>
              <button
                onClick={() => setDialogOpen(false)}
                className="p-2 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 rounded-lg transition-colors"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-6">
              {selectedTask && !isEditing ? (
                // View mode
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                      Title
                    </label>
                    <h3 className="text-xl font-semibold text-neutral-900">
                      {selectedTask.title}
                    </h3>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                      Description
                    </label>
                    <p className="text-neutral-600 bg-neutral-50 p-4 rounded-lg">
                      {selectedTask.description}
                    </p>
                  </div>
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-2">
                        Status
                      </label>
                      <div className={`inline-flex px-3 py-2 rounded-lg text-sm font-medium ${
                        selectedTask.status === 'Completed' ? 'bg-success-100 text-success-700' :
                        selectedTask.status === 'In Progress' ? 'bg-accent-100 text-accent-700' :
                        selectedTask.status === 'Pending' ? 'bg-warning-100 text-warning-700' :
                        'bg-danger-100 text-danger-700'
                      }`}>
                        {selectedTask.status}
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-2">
                        Priority
                      </label>
                      <div className={`inline-flex px-3 py-2 rounded-lg text-sm font-medium ${
                        selectedTask.priority === 'High' ? 'bg-danger-100 text-danger-700' :
                        selectedTask.priority === 'Medium' ? 'bg-warning-100 text-warning-700' :
                        'bg-success-100 text-success-700'
                      }`}>
                        <FlagIcon className="w-4 h-4 mr-2" />
                        {selectedTask.priority}
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-2">
                        Assignee
                      </label>
                      <div className="flex items-center gap-2">
                        <UserIcon className="w-5 h-5 text-neutral-400" />
                        <span className="text-neutral-700">{getUserNameById(selectedTask.assignee_id)}</span>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-2">
                        Due Date
                      </label>
                      <div className="flex items-center gap-2">
                        <CalendarDaysIcon className="w-5 h-5 text-neutral-400" />
                        <span className="text-neutral-700">
                          {selectedTask.due_at ? new Date(selectedTask.due_at).toLocaleDateString() : 'No due date'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                // Edit/Create mode
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                      Title *
                    </label>
                    <input
                      type="text"
                      value={formData.title}
                      onChange={(e) => setFormData({...formData, title: e.target.value})}
                      className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent"
                      placeholder="Enter task title"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                      Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent resize-none"
                      rows={4}
                      placeholder="Enter task description"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-2">
                        Status
                      </label>
                      <select
                        value={formData.status}
                        onChange={(e) => setFormData({...formData, status: e.target.value})}
                        className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent bg-white"
                      >
                        <option value="Pending">Pending</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Completed">Completed</option>
                        <option value="Overdue">Overdue</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-2">
                        Priority
                      </label>
                      <select
                        value={formData.priority}
                        onChange={(e) => setFormData({...formData, priority: e.target.value})}
                        className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent bg-white"
                      >
                        <option value="Low">Low</option>
                        <option value="Medium">Medium</option>
                        <option value="High">High</option>
                      </select>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-2">
                        Assignee
                      </label>
                      <select
                        value={formData.assignee_id}
                        onChange={(e) => setFormData({...formData, assignee_id: e.target.value})}
                        className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent bg-white"
                      >
                        <option value="">Select assignee</option>
                        {users.map((user) => (
                          <option key={user.id} value={user.id}>
                            {user.full_name} ({user.role})
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-2">
                        Due Date
                      </label>
                      <input
                        type="date"
                        value={formData.due_at}
                        onChange={(e) => setFormData({...formData, due_at: e.target.value})}
                        className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <TaskAttachments
                    taskId={selectedTask.id}
                    attachments={taskAttachments}
                    onAttachmentsChange={setTaskAttachments}
                    isEditing={false}
                    currentUser={currentUser}
                  />
                </div>
              )}
            </div>
            <div className="flex justify-end gap-3 p-6 border-t border-border bg-neutral-50">
              <button
                onClick={() => setDialogOpen(false)}
                className="px-4 py-2 text-neutral-600 border border-neutral-200 rounded-lg hover:bg-neutral-50 transition-colors duration-200"
              >
                {selectedTask && !isEditing ? 'Close' : 'Cancel'}
              </button>
              {(!selectedTask || isEditing) && (
                <button
                  onClick={handleSaveTask}
                  className="px-4 py-2 bg-accent-500 text-white rounded-lg hover:bg-accent-600 transition-colors duration-200 font-medium"
                >
                  {isEditing ? 'Update Task' : 'Create Task'}
                </button>
              )}
              {selectedTask && !isEditing && (
                <button
                  onClick={() => { setIsEditing(true); }}
                  className="px-4 py-2 bg-neutral-600 text-white rounded-lg hover:bg-neutral-700 transition-colors duration-200 font-medium"
                >
                  Edit Task
                </button>
              )}
                    </div>
                  </div>
                  {selectedTask && (
                    <TaskAttachments
                      taskId={selectedTask.id}
                      attachments={taskAttachments}
                      onAttachmentsChange={setTaskAttachments}
                      isEditing={isEditing}
                      currentUser={currentUser}
                    />
                  )}
                </div>
              )}
    </div>
  );
};

export default Tasks;
