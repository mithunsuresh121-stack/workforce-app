import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const api = axios.create({
  baseURL: '/api',
});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Set axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
      delete api.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Load user on mount
  useEffect(() => {
    const loadUser = async () => {
      if (token) {
        try {
          const response = await api.get('/auth/me');
          setUser(response.data);
          setError(null);
        } catch (error) {
          console.error('Failed to load user:', error);
          if (error.response?.status === 401 || error.response?.status === 500) {
            setError(error.response?.data?.detail || 'Session expired. Please login again.');
            logout();
          } else {
            setError('Failed to load user profile');
          }
        }
      }
      setLoading(false);
    };
    loadUser();
  }, [token]);

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      const { access_token } = response.data;
      setToken(access_token);
      localStorage.setItem('token', access_token);
      setError(null);
      // Reload user
      const userResponse = await api.get('/auth/me');
      setUser(userResponse.data);
      return { success: true };
    } catch (error) {
      const errMsg = error.response?.data?.detail || 'Login failed';
      setError(errMsg);
      return { success: false, error: errMsg };
    }
  };

  const signup = async (userData) => {
    try {
      await api.post('/auth/signup', userData);
      setError(null);
      // Auto login after signup
      return await login(userData.email, userData.password);
    } catch (error) {
      const errMsg = error.response?.data?.detail || 'Signup failed';
      setError(errMsg);
      return { success: false, error: errMsg };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setError(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    delete api.defaults.headers.common['Authorization'];
  };

  const isAuthenticated = () => !!user;

  const hasRole = (role) => user?.role === role;

  const isSuperAdmin = () => user?.role === 'SuperAdmin';

  const isCompanyAdmin = () => ['SuperAdmin', 'CompanyAdmin'].includes(user?.role);

  const isManager = () => ['SuperAdmin', 'CompanyAdmin', 'Manager'].includes(user?.role);

  const value = {
    user,
    token,
    loading,
    error,
    setError,
    login,
    signup,
    logout,
    isAuthenticated,
    hasRole,
    isSuperAdmin,
    isCompanyAdmin,
    isManager,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
