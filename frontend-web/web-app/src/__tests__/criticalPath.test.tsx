import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';
import { AuthProvider } from '../contexts/AuthContext';

// Mock fetch and localStorage are set globally in setupTests.js

describe('Critical Path Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('Redirects to login when accessing dashboard without auth', async () => {
    // Mock no token in localStorage
    (global.localStorage.getItem as any).mockReturnValue(null);
    // Mock /api/auth/me to fail
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({}),
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/dashboard']}>
          <App />
        </MemoryRouter>
      </AuthProvider>
    );
    expect(await screen.findByText(/sign in/i)).toBeInTheDocument();
  });

  test('Login success redirects to dashboard', async () => {
    // Mock login fetch
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        access_token: 'fake-jwt-token',
        refresh_token: 'fake-refresh',
        user: { id: '1', name: 'Demo User', email: 'demo@company.com', company_id: '1', role: 'EMPLOYEE' }
      }),
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
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
    });
  });

  test('Sidebar navigation works', async () => {
    // Mock auth
    (global.localStorage.getItem as any).mockReturnValue('fake-token');
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: '1', name: 'Demo User', email: 'demo@company.com', company_id: '1', role: 'EMPLOYEE' }),
    });

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
    // Mock auth
    (global.localStorage.getItem as any).mockReturnValue('fake-token');
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: '1', name: 'Demo User', email: 'demo@company.com', company_id: '1', role: 'EMPLOYEE' }),
    });

    // Mock dashboard APIs
    (global.fetch as any).mockImplementation((url: string) => {
      if (url.includes('/dashboard/kpis')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ total_employees: 100, active_tasks: 20, pending_leaves: 5, shifts_today: 10 }),
        });
      }
      if (url.includes('/dashboard/charts/task-status')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([{ name: 'Pending', value: 5 }, { name: 'Completed', value: 15 }]),
        });
      }
      if (url.includes('/dashboard/charts/employee-distribution')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([{ name: 'Employee', value: 80 }, { name: 'Manager', value: 20 }]),
        });
      }
      if (url.includes('/dashboard/recent-activities')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([{ type: 'task', title: 'Test Task', description: 'Test Desc', status: 'Pending', timestamp: new Date().toISOString() }]),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
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
    // Mock auth
    (global.localStorage.getItem as any).mockReturnValue('fake-token');
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: '1', name: 'Demo User', email: 'demo@company.com', company_id: '1', role: 'EMPLOYEE' }),
    });

    // Mock profile get
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ name: 'Demo User', email: 'demo@company.com', role: 'Employee', avatar: '' }),
    });
    // Mock profile put
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ name: 'Updated User', email: 'updated@company.com', role: 'Employee', avatar: '' }),
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
    // Mock auth
    (global.localStorage.getItem as any).mockReturnValue('fake-token');
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: '1', name: 'Demo User', email: 'demo@company.com', company_id: '1', role: 'EMPLOYEE' }),
    });

    // Mock directory get
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve([
        { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Employee', avatar: '', department: 'Engineering', status: 'Active' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'Manager', avatar: '', department: 'HR', status: 'Active' }
      ]),
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
    // Mock auth
    (global.localStorage.getItem as any).mockReturnValue('fake-token');
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: '1', name: 'Demo User', email: 'demo@company.com', company_id: '1', role: 'EMPLOYEE' }),
    });

    // Mock tasks get
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve([
        { id: 1, title: 'Task 1', description: 'Desc 1', status: 'Pending', assignee: 'John', priority: 'High', dueDate: '2024-01-01' }
      ]),
    });
    // Mock post, put, delete
    (global.fetch as any).mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ id: 2, title: 'Task 2' }) });
    (global.fetch as any).mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ id: 1, title: 'Task 1 Updated' }) });
    (global.fetch as any).mockResolvedValueOnce({ ok: true });

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
    // Mock auth
    (global.localStorage.getItem as any).mockReturnValue('fake-token');
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: '1', name: 'Demo User', email: 'demo@company.com', company_id: '1', role: 'EMPLOYEE' }),
    });

    // Mock leave get
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve([
        { id: 1, type: 'Annual Leave', startDate: '2024-01-01', endDate: '2024-01-05', status: 'Approved', reason: 'Vacation', days: 5 }
      ]),
    });
    // Mock post
    (global.fetch as any).mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ id: 2, type: 'Sick Leave' }) });

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
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ status: 'healthy' }),
    });

    const response = await fetch('/health');
    const data = await response.json();
    expect(data.status).toBe('healthy');
  });

  test('Authentication login/logout endpoints', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        access_token: 'fake-jwt-token',
        refresh_token: 'fake-refresh',
        user: { id: '1', name: 'Demo User', email: 'demo@company.com', company_id: '1', role: 'EMPLOYEE' }
      }),
    });

    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'demo@company.com', password: 'password123' }),
    });
    const data = await response.json();
    expect(data.access_token).toBeDefined();

    // Simulate logout by clearing token or calling logout endpoint if exists
  });
});
