import { http, HttpResponse } from 'msw';

// Mock data
const mockUser = {
  id: '1',
  name: 'Demo User',
  email: 'demo@company.com',
  company_id: '1',
  role: 'EMPLOYEE',
  avatar: '',
  department: 'Engineering',
  status: 'Active',
};

const mockNotifications = [
  {
    id: '1',
    title: 'Test Notification',
    message: 'Test message',
    type: 'TASK_CREATED',
    status: 'UNREAD',
    created_at: new Date().toISOString(),
  },
];

const mockKPIs = {
  total_employees: 100,
  active_tasks: 20,
  pending_leaves: 5,
  shifts_today: 10,
};

const mockTaskStatusChart = [
  { name: 'Pending', value: 5 },
  { name: 'Completed', value: 15 },
];

const mockEmployeeDistributionChart = [
  { name: 'Employee', value: 80 },
  { name: 'Manager', value: 20 },
];

const mockRecentActivities = [
  {
    type: 'task',
    title: 'Test Task',
    description: 'Test Desc',
    status: 'Pending',
    timestamp: new Date().toISOString(),
  },
];

const mockProfile = {
  name: 'Demo User',
  email: 'demo@company.com',
  role: 'Employee',
  avatar: '',
};

const mockDirectory = [
  {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    role: 'Employee',
    avatar: '',
    department: 'Engineering',
    status: 'Active',
  },
  {
    id: 2,
    name: 'Jane Smith',
    email: 'jane@example.com',
    role: 'Manager',
    avatar: '',
    department: 'HR',
    status: 'Active',
  },
];

const mockTasks = [
  {
    id: 1,
    title: 'Task 1',
    description: 'Desc 1',
    status: 'Pending',
    assignee: 'John',
    priority: 'High',
    dueDate: '2024-01-01',
  },
];

const mockLeaves = [
  {
    id: 1,
    type: 'Annual Leave',
    startDate: '2024-01-01',
    endDate: '2024-01-05',
    status: 'Approved',
    reason: 'Vacation',
    days: 5,
  },
];

const mockPreferences = {
  email_notifications: true,
  websocket_notifications: true,
  task_notifications: true,
  shift_notifications: false,
  general_notifications: true,
};

export const handlers = [
  // Auth endpoints
  http.get('/api/auth/me', () => {
    return HttpResponse.json(mockUser);
  }),
  http.post('/api/auth/login', () => {
    return HttpResponse.json({
      access_token: 'fake-jwt-token',
      refresh_token: 'fake-refresh',
      user: mockUser,
    });
  }),

  // Dashboard endpoints
  http.get('/dashboard/kpis', () => {
    return HttpResponse.json(mockKPIs);
  }),
  http.get('/dashboard/charts/task-status', () => {
    return HttpResponse.json(mockTaskStatusChart);
  }),
  http.get('/dashboard/charts/employee-distribution', () => {
    return HttpResponse.json(mockEmployeeDistributionChart);
  }),
  http.get('/dashboard/recent-activities', () => {
    return HttpResponse.json(mockRecentActivities);
  }),

  // Profile endpoints
  http.get('/profile', () => {
    return HttpResponse.json(mockProfile);
  }),
  http.put('/profile', () => {
    return HttpResponse.json({ ...mockProfile, name: 'Updated User' });
  }),

  // Directory endpoints
  http.get('/directory', () => {
    return HttpResponse.json(mockDirectory);
  }),

  // Tasks endpoints
  http.get('/tasks', () => {
    return HttpResponse.json(mockTasks);
  }),
  http.post('/tasks', () => {
    return HttpResponse.json({ id: 2, title: 'Task 2' });
  }),
  http.put('/tasks/:id', () => {
    return HttpResponse.json({ id: 1, title: 'Task 1 Updated' });
  }),
  http.delete('/tasks/:id', () => {
    return HttpResponse.json({});
  }),

  // Leave endpoints
  http.get('/leave', () => {
    return HttpResponse.json(mockLeaves);
  }),
  http.post('/leave', () => {
    return HttpResponse.json({ id: 2, type: 'Sick Leave' });
  }),

  // Notifications endpoints
  http.get('http://localhost:3000/api/notifications/', () => {
    return HttpResponse.json(mockNotifications);
  }),
  http.post('http://localhost:3000/api/notifications/mark-read/:id', () => {
    return HttpResponse.json({});
  }),

  // Notification preferences endpoints
  http.get('/notification-preferences/', () => {
    return HttpResponse.json(mockPreferences);
  }),
  http.post('/notification-preferences/', () => {
    return HttpResponse.json({});
  }),

  // Health endpoint
  http.get('/health', () => {
    return HttpResponse.json({ status: 'healthy' });
  }),
];
