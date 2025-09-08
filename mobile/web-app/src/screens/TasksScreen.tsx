import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Alert, { AlertDescription, AlertTitle } from '../components/ui/Alert';
import Skeleton from '../components/ui/skeleton';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { getTasks, deleteTask, createTask, updateTask, getEmployees, getCurrentUserProfile } from '../lib/api';

const TasksScreen: React.FC = () => {
  const [tasks, setTasks] = useState<any[]>([]);
  const [filteredTasks, setFilteredTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [currentPage, setCurrentPage] = useState(1);
  const [tasksPerPage] = useState(5);
  const [operationLoading, setOperationLoading] = useState(false);

  // New state for enhanced functionality
  const [employees, setEmployees] = useState<any[]>([]);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingTask, setEditingTask] = useState<any>(null);
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [assigneeFilter, setAssigneeFilter] = useState('');

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: 'Pending',
    priority: 'Medium',
    assignee_id: '',
    due_at: ''
  });

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getTasks();
        setTasks(data);
        setFilteredTasks(data);
      } catch (err) {
        setError('Failed to load tasks. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, []);

  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        const data = await getEmployees();
        setEmployees(data);
      } catch (err) {
        console.error('Failed to load employees:', err);
      }
    };

    fetchEmployees();
  }, []);

  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        const user = await getCurrentUserProfile();
        setCurrentUser(user);
      } catch (err) {
        console.error('Failed to load current user:', err);
      }
    };

    fetchCurrentUser();
  }, []);

  useEffect(() => {
    const filtered = tasks.filter(task => {
      const matchesSearch = task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        task.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        task.status.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (task.assignee && task.assignee.toLowerCase().includes(searchTerm.toLowerCase()));

      const matchesStatus = !statusFilter || task.status === statusFilter;
      const matchesPriority = !priorityFilter || task.priority === priorityFilter;
      const matchesAssignee = !assigneeFilter || task.assignee_id === parseInt(assigneeFilter);

      return matchesSearch && matchesStatus && matchesPriority && matchesAssignee;
    });
    setFilteredTasks(filtered);
    setCurrentPage(1); // Reset to first page when filtering
  }, [searchTerm, tasks, statusFilter, priorityFilter, assigneeFilter]);

  // Pagination logic
  const indexOfLastTask = currentPage * tasksPerPage;
  const indexOfFirstTask = indexOfLastTask - tasksPerPage;
  const currentTasks = filteredTasks.slice(indexOfFirstTask, indexOfLastTask);
  const totalPages = Math.ceil(filteredTasks.length / tasksPerPage);

  const handlePageChange = (pageNumber: number) => {
    setCurrentPage(pageNumber);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleDeleteTask = async (taskId: number) => {
    try {
      setOperationLoading(true);
      const success = await deleteTask(taskId);
      if (success) {
        setTasks(tasks.filter(task => task.id !== taskId));
        setFilteredTasks(filteredTasks.filter(task => task.id !== taskId));
      } else {
        setError('Failed to delete task. Please try again.');
      }
    } catch (err) {
      setError('Failed to delete task. Please try again.');
    } finally {
      setOperationLoading(false);
    }
  };

  const handleCreateTask = async () => {
    if (!currentUser) {
      setError('User not authenticated. Please log in again.');
      return;
    }

    try {
      setOperationLoading(true);
      const taskData = {
        ...formData,
        company_id: currentUser.company_id,
        assignee_id: formData.assignee_id ? parseInt(formData.assignee_id) : null,
        due_at: formData.due_at || null
      };
      const newTask = await createTask(taskData);
      if (newTask) {
        setTasks([...tasks, newTask]);
        setShowCreateModal(false);
        setFormData({
          title: '',
          description: '',
          status: 'Pending',
          priority: 'Medium',
          assignee_id: '',
          due_at: ''
        });
      }
    } catch (err) {
      setError('Failed to create task. Please try again.');
    } finally {
      setOperationLoading(false);
    }
  };

  const handleEditTask = (task: any) => {
    setEditingTask(task);
    setFormData({
      title: task.title,
      description: task.description,
      status: task.status,
      priority: task.priority,
      assignee_id: task.assignee_id?.toString() || '',
      due_at: task.due_at || ''
    });
    setShowEditModal(true);
  };

  const handleUpdateTask = async () => {
    if (!currentUser) {
      setError('User not authenticated. Please log in again.');
      return;
    }

    try {
      setOperationLoading(true);
      const taskData = {
        ...formData,
        company_id: currentUser.company_id,
        assignee_id: formData.assignee_id ? parseInt(formData.assignee_id) : null,
        due_at: formData.due_at || null
      };
      const updatedTask = await updateTask(editingTask.id, taskData);
      if (updatedTask) {
        setTasks(tasks.map(task => task.id === editingTask.id ? updatedTask : task));
        setShowEditModal(false);
        setEditingTask(null);
      }
    } catch (err) {
      setError('Failed to update task. Please try again.');
    } finally {
      setOperationLoading(false);
    }
  };

  const handleFormChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'Critical': return 'bg-red-100 text-red-800';
      case 'High': return 'bg-orange-100 text-orange-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'Low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Pending': return 'bg-gray-100 text-gray-800';
      case 'In Progress': return 'bg-blue-100 text-blue-800';
      case 'Completed': return 'bg-green-100 text-green-800';
      case 'Overdue': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Tasks</h1>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading tasks...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Tasks</h1>
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Tasks</h1>
        <Button onClick={() => setShowCreateModal(true)}>Create Task</Button>
      </div>

      {/* Filters */}
      <div className="mb-6 space-y-4">
        <div className="flex flex-wrap gap-4">
          <Input
            type="text"
            placeholder="Search tasks..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="max-w-md"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">All Status</option>
            <option value="Pending">Pending</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
            <option value="Overdue">Overdue</option>
          </select>
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">All Priority</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>
          <select
            value={assigneeFilter}
            onChange={(e) => setAssigneeFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">All Assignees</option>
            {employees.map(employee => (
              <option key={employee.id} value={employee.id}>{employee.full_name}</option>
            ))}
          </select>
        </div>
      </div>
      
      {filteredTasks.length > 0 ? (
        <>
          {viewMode === 'grid' ? (
            // Grid view with cards
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {currentTasks.map((task) => (
                <Card key={task.id} className="shadow-sm hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-lg">{task.title}</CardTitle>
                      <span className={`px-2 py-1 rounded-full text-xs ${getPriorityColor(task.priority)}`}>
                        {task.priority}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600 mb-4">{task.description}</p>
                    <div className="flex justify-between items-center">
                      <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(task.status)}`}>
                        {task.status}
                      </span>
                      <div className="flex space-x-2">
                        <Button variant="outline" size="sm" onClick={() => handleEditTask(task)}>Edit</Button>
                        <Button variant="destructive" size="sm" onClick={() => handleDeleteTask(task.id)}>Delete</Button>
                      </div>
                    </div>
                    <div className="mt-4 text-sm text-gray-500">
                      <p>Assignee: {task.assignee}</p>
                      <p>Due: {task.dueDate}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            // List view with table
            <div className="border rounded-lg overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Title</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Priority</TableHead>
                    <TableHead>Assignee</TableHead>
                    <TableHead>Due Date</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {currentTasks.map((task) => (
                    <TableRow key={task.id}>
                      <TableCell className="font-medium">{task.title}</TableCell>
                      <TableCell>{task.description}</TableCell>
                      <TableCell>
                        <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(task.status)}`}>
                          {task.status}
                        </span>
                      </TableCell>
                      <TableCell>
                        <span className={`px-2 py-1 rounded-full text-xs ${getPriorityColor(task.priority)}`}>
                          {task.priority}
                        </span>
                      </TableCell>
                      <TableCell>{task.assignee}</TableCell>
                      <TableCell>{task.dueDate}</TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button variant="outline" size="sm" onClick={() => handleEditTask(task)}>Edit</Button>
                          <Button variant="destructive" size="sm" onClick={() => handleDeleteTask(task.id)}>Delete</Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
          
          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-gray-500">
                Showing {indexOfFirstTask + 1} to {Math.min(indexOfLastTask, filteredTasks.length)} of {filteredTasks.length} tasks
              </div>
              <div className="flex space-x-2">
                <Button 
                  onClick={() => handlePageChange(currentPage - 1)} 
                  disabled={currentPage === 1}
                  variant="outline"
                >
                  Previous
                </Button>
                {[...Array(totalPages)].map((_, index) => (
                  <Button
                    key={index}
                    onClick={() => handlePageChange(index + 1)}
                    variant={currentPage === index + 1 ? "default" : "outline"}
                  >
                    {index + 1}
                  </Button>
                ))}
                <Button 
                  onClick={() => handlePageChange(currentPage + 1)} 
                  disabled={currentPage === totalPages}
                  variant="outline"
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-500">No tasks found matching your search criteria.</p>
        </div>
      )}

      {/* Create Task Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Create New Task</h2>
            <div className="space-y-4">
              <Input
                type="text"
                placeholder="Task Title"
                value={formData.title}
                onChange={(e) => handleFormChange('title', e.target.value)}
              />
              <textarea
                placeholder="Description"
                value={formData.description}
                onChange={(e) => handleFormChange('description', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                rows={3}
              />
              <select
                value={formData.status}
                onChange={(e) => handleFormChange('status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="Pending">Pending</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
                <option value="Overdue">Overdue</option>
              </select>
              <select
                value={formData.priority}
                onChange={(e) => handleFormChange('priority', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
              <select
                value={formData.assignee_id}
                onChange={(e) => handleFormChange('assignee_id', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                disabled={!currentUser || !['Manager', 'CompanyAdmin', 'SuperAdmin'].includes(currentUser.role)}
              >
                <option value="">
                  {currentUser && ['Manager', 'CompanyAdmin', 'SuperAdmin'].includes(currentUser.role)
                    ? 'Select Assignee'
                    : 'Only managers can assign tasks'}
                </option>
                {employees.map(employee => (
                  <option key={employee.id} value={employee.id}>{employee.full_name}</option>
                ))}
              </select>
              <Input
                type="datetime-local"
                value={formData.due_at}
                onChange={(e) => handleFormChange('due_at', e.target.value)}
              />
            </div>
            <div className="flex justify-end space-x-2 mt-4">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>Cancel</Button>
              <Button onClick={handleCreateTask} disabled={operationLoading}>
                {operationLoading ? 'Creating...' : 'Create'}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Task Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Edit Task</h2>
            <div className="space-y-4">
              <Input
                type="text"
                placeholder="Task Title"
                value={formData.title}
                onChange={(e) => handleFormChange('title', e.target.value)}
              />
              <textarea
                placeholder="Description"
                value={formData.description}
                onChange={(e) => handleFormChange('description', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                rows={3}
              />
              <select
                value={formData.status}
                onChange={(e) => handleFormChange('status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="Pending">Pending</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
                <option value="Overdue">Overdue</option>
              </select>
              <select
                value={formData.priority}
                onChange={(e) => handleFormChange('priority', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
              <select
                value={formData.assignee_id}
                onChange={(e) => handleFormChange('assignee_id', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                disabled={!currentUser || !['Manager', 'CompanyAdmin', 'SuperAdmin'].includes(currentUser.role)}
              >
                <option value="">
                  {currentUser && ['Manager', 'CompanyAdmin', 'SuperAdmin'].includes(currentUser.role)
                    ? 'Select Assignee'
                    : 'Only managers can assign tasks'}
                </option>
                {employees.map(employee => (
                  <option key={employee.id} value={employee.id}>{employee.full_name}</option>
                ))}
              </select>
              <Input
                type="datetime-local"
                value={formData.due_at}
                onChange={(e) => handleFormChange('due_at', e.target.value)}
              />
            </div>
            <div className="flex justify-end space-x-2 mt-4">
              <Button variant="outline" onClick={() => setShowEditModal(false)}>Cancel</Button>
              <Button onClick={handleUpdateTask} disabled={operationLoading}>
                {operationLoading ? 'Updating...' : 'Update'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TasksScreen;
