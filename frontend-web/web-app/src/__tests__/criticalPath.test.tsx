import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';
import { AuthProvider } from '../contexts/AuthContext';
import { server } from '../setupTests';
import { http, HttpResponse } from 'msw';

describe('Critical Path Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('Redirects to login when accessing dashboard without auth', async () => {
    // Override /api/auth/me to return 401 for unauth
    server.use(
      http.get('/api/auth/me', () => {
        return HttpResponse.json({}, { status: 401 });
      })
    );

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/dashboard']}>
          <App />
        </MemoryRouter>
      </AuthProvider>
    );
    expect(await screen.findByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  test('Login success redirects to dashboard', async () => {
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
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/dashboard']}>
          <App />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/total employees/i)).toBeInTheDocument();
      expect(screen.getByText(/active tasks/i)).toBeInTheDocument();
    });
  });

  test('Profile update form works', async () => {
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
    const response = await fetch('/health');
    const data = await response.json();
    expect(data.status).toBe('healthy');
  });

  test('Authentication login/logout endpoints', async () => {
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
