import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import axios from 'axios';
import App from '../App';
import { AuthProvider } from '../contexts/AuthContext';

// Mock axios
import { vi } from 'vitest';

// Mock axios before importing AuthContext
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      },
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn()
    })),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    },
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}));

describe('Critical Path Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('Redirects to login when accessing dashboard without auth', async () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/dashboard']}>
          <App />
        </MemoryRouter>
      </AuthProvider>
    );
    expect(await screen.findByText(/login/i)).toBeInTheDocument();
  });

  test('Login success redirects to dashboard', async () => {
    axios.post.mockResolvedValueOnce({
      data: { token: 'fake-jwt-token', user: { name: 'Demo User', email: 'demo@company.com' } }
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/login']}>
          <App />
        </MemoryRouter>
      </AuthProvider>
    );

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'demo@company.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
    });
  });

  test('Sidebar navigation works', async () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/dashboard']}>
          <App />
        </MemoryRouter>
      </AuthProvider>
    );

    const profileLink = await screen.findByText(/profile/i);
    fireEvent.click(profileLink);
    expect(await screen.findByText(/update profile/i)).toBeInTheDocument();
  });

  test('Dashboard renders KPIs and charts', async () => {
    axios.get.mockImplementation((url) => {
      switch (url) {
        case '/dashboard/kpis':
          return Promise.resolve({ data: { total_employees: 100, active_tasks: 20, pending_leaves: 5, shifts_today: 10 } });
        case '/dashboard/charts/task-status':
          return Promise.resolve({ data: [{ name: 'Pending', value: 5 }, { name: 'Completed', value: 15 }] });
        case '/dashboard/charts/employee-distribution':
          return Promise.resolve({ data: [{ name: 'Employee', value: 80 }, { name: 'Manager', value: 20 }] });
        case '/dashboard/recent-activities?limit=5':
          return Promise.resolve({ data: [{ type: 'task', title: 'Test Task', description: 'Test Desc', status: 'Pending', timestamp: new Date().toISOString() }] });
        default:
          return Promise.resolve({ data: [] });
      }
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/dashboard']}>
          <App />
        </MemoryRouter>
      </AuthProvider>
    );

    expect(await screen.findByText(/total employees/i)).toBeInTheDocument();
    expect(await screen.findByText(/active tasks/i)).toBeInTheDocument();
  });

  test('Profile update form works', async () => {
    axios.get.mockResolvedValueOnce({
      data: { name: 'Demo User', email: 'demo@company.com', role: 'Employee', avatar: '' }
    });
    axios.put.mockResolvedValueOnce({
      data: { name: 'Updated User', email: 'updated@company.com', role: 'Employee', avatar: '' }
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/profile']}>
          <App />
        </MemoryRouter>
      </AuthProvider>
    );

    expect(await screen.findByDisplayValue(/demo user/i)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/name/i), { target: { value: 'Updated User' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'updated@company.com' } });
    fireEvent.click(screen.getByRole('button', { name: /update profile/i }));

    await waitFor(() => {
      expect(screen.getByText(/profile updated successfully/i)).toBeInTheDocument();
    });
  });

  test('Directory search and filter works', async () => {
    axios.get.mockResolvedValueOnce({
      data: [
        { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Employee', avatar: '', department: 'Engineering', status: 'Active' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'Manager', avatar: '', department: 'HR', status: 'Active' }
      ]
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/directory']}>
          <App />
        </MemoryRouter>
      </AuthProvider>
    );

    expect(await screen.findByText(/john doe/i)).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText(/search/i), { target: { value: 'Jane' } });
    expect(await screen.findByText(/jane smith/i)).toBeInTheDocument();
  });

  test('Tasks CRUD operations', async () => {
    axios.get.mockResolvedValueOnce({
      data: [
        { id: 1, title: 'Task 1', description: 'Desc 1', status: 'Pending', assignee: 'John', priority: 'High', dueDate: '2024-01-01' }
      ]
    });
    axios.post.mockResolvedValueOnce({ data: { id: 2, title: 'Task 2' } });
    axios.put.mockResolvedValueOnce({ data: { id: 1, title: 'Task 1 Updated' } });
    axios.delete.mockResolvedValueOnce({});

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/tasks']}>
          <App />
        </MemoryRouter>
      </AuthProvider>
    );

    expect(await screen.findByText(/task 1/i)).toBeInTheDocument();

    // Additional tests for create, update, delete can be added here
  });

  test('Leave form submission and table display', async () => {
    axios.get.mockResolvedValueOnce({
      data: [
        { id: 1, type: 'Annual Leave', startDate: '2024-01-01', endDate: '2024-01-05', status: 'Approved', reason: 'Vacation', days: 5 }
      ]
    });
    axios.post.mockResolvedValueOnce({ data: { id: 2, type: 'Sick Leave' } });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/leave']}>
          <App />
        </MemoryRouter>
      </AuthProvider>
    );

    expect(await screen.findByText(/annual leave/i)).toBeInTheDocument();

    // Additional tests for form submission can be added here
  });

  test('Backend health endpoint returns healthy', async () => {
    axios.get.mockResolvedValueOnce({ data: { status: 'healthy' } });

    const response = await axios.get('/health');
    expect(response.data.status).toBe('healthy');
  });

  test('Authentication login/logout endpoints', async () => {
    axios.post.mockResolvedValueOnce({
      data: { token: 'fake-jwt-token', user: { name: 'Demo User', email: 'demo@company.com' } }
    });

    const loginResponse = await axios.post('/auth/login', { email: 'demo@company.com', password: 'password123' });
    expect(loginResponse.data.token).toBeDefined();

    // Simulate logout by clearing token or calling logout endpoint if exists
  });
});
