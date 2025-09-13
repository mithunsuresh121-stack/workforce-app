
import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

// Create AuthContext
export const AuthContext = createContext();

// AuthProvider component to wrap app and provide auth state
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Configure axios interceptors for token handling
  useEffect(() => {
    // Request interceptor to add token to headers
    axios.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle token expiration
    axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid, logout user
          logout();
        }
        return Promise.reject(error);
      }
    );
  }, []);

  // Load user from token on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token by fetching user profile
      fetchUserProfile();
    } else {
      setLoading(false);
    }
  }, []);

  // Fetch current user profile
  const fetchUserProfile = async () => {
    try {
      const response = await axios.get('/auth/me');
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user profile:', error);
      // If token is invalid, logout
      logout();
    } finally {
      setLoading(false);
    }
  };

  // Login function with API call
  const login = async (email, password) => {
    try {
      const response = await axios.post('/auth/login', { email, password });
      const { access_token } = response.data;

      // Store token
      localStorage.setItem('token', access_token);

      // Fetch user profile
      await fetchUserProfile();

      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed. Please try again.'
      };
    }
  };

  // Logout function
  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  const value = {
    user,
    login,
    logout,
    isAuthenticated: !!user,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
