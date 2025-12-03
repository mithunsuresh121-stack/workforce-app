import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';

interface User {
  id: string;
  email: string;
  name: string;
  company_id: string;
  role: 'ADMIN' | 'MANAGER' | 'EMPLOYEE';
  token: string;
  refresh_token?: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  refetchUser: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Simple fetch-based API wrapper for authenticated requests
export const api = {
  get: (url: string) => fetch(url, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  }),
  post: (url: string, data: any) => fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(data),
  }),
};

// API base URL (same as in useProcurement)
const getApiBase = (): string => {
  return import.meta.env.VITE_API_URL || (process.env.NODE_ENV === 'production'
    ? 'https://api.workforce-app.com'
    : 'http://localhost:8000');
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const apiBase = getApiBase();

  // Check for existing token on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token (simple check; in prod, call /api/auth/me)
      fetch(`${apiBase}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
        .then(res => {
          if (res.ok) {
            return res.json();
          }
          throw new Error('Invalid token');
        })
        .then((userData: Omit<User, 'token'>) => {
          setUser({ ...userData, token });
          setIsLoading(false);
        })
        .catch(() => {
          localStorage.removeItem('token');
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }
  }, [apiBase]);

  const loginMutation = useMutation({
    mutationFn: async ({ email, password }: { email: string; password: string }) => {
      const response = await fetch(`${apiBase}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }
      return response.json();
    },
    onSuccess: (data) => {
      const { access_token, refresh_token, user: userData } = data;
      localStorage.setItem('token', access_token);
      if (refresh_token) localStorage.setItem('refresh_token', refresh_token);
      setUser({ ...userData, token: access_token });
      setError(null);
      queryClient.invalidateQueries({ queryKey: ['user'] });
    },
    onError: (err: any) => {
      setError(err.message);
      localStorage.removeItem('token');
    },
  });

  const registerMutation = useMutation({
    mutationFn: async ({ email, password, name }: { email: string; password: string; name: string }) => {
      const response = await fetch(`${apiBase}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, name }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }
      return response.json();
    },
    onError: (err: any) => {
      setError(err.message);
    },
  });

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    queryClient.clear();
  };

  const refetchUser = () => {
    // Implement token refresh logic if refresh_token exists
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken && user) {
      fetch(`${apiBase}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })
        .then(res => res.json())
        .then((data) => {
          localStorage.setItem('token', data.access_token);
          setUser(prev => prev ? { ...prev, token: data.access_token } : null);
        })
        .catch(() => logout());
    }
  };

  const login = async (email: string, password: string) => {
    setError(null);
    await loginMutation.mutateAsync({ email, password });
  };

  const register = async (email: string, password: string, name: string) => {
    setError(null);
    await registerMutation.mutateAsync({ email, password, name });
    // Auto-login after successful registration
    await login(email, password);
  };

  return (
    <AuthContext.Provider value={{
      user,
      login,
      register,
      logout,
      isAuthenticated: !!user,
      isLoading,
      error,
      refetchUser,
    }}>
      {children}
    </AuthContext.Provider>
  );
};
