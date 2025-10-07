import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { AuthProvider } from './contexts/AuthContext';
import theme from './theme';
import ProtectedRoute from './components/ProtectedRoute';
import DashboardLayout from './layouts/DashboardLayout';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Employees from './pages/Employees';
import Projects from './pages/Projects';
import Profile from './pages/Profile';
import Directory from './pages/Directory';
import Tasks from './pages/Tasks';
import Leave from './pages/Leave';

import Company from './pages/Company';
import Attendance from './pages/Attendance';
import Shifts from './pages/Shifts';
import Documents from './pages/Documents';

function App() {
  const AppRoutes = () => (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      {/* Protected routes */}
      <Route path="/" element={
        <ProtectedRoute>
          <DashboardLayout><Dashboard /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <DashboardLayout><Dashboard /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/employees" element={
        <ProtectedRoute>
          <DashboardLayout><Employees /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/projects" element={
        <ProtectedRoute>
          <DashboardLayout><Projects /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/tasks" element={
        <ProtectedRoute>
          <DashboardLayout><Tasks /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/attendance" element={
        <ProtectedRoute>
          <DashboardLayout><Attendance /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/leaves" element={
        <ProtectedRoute>
          <DashboardLayout><Leave /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/documents" element={
        <ProtectedRoute>
          <DashboardLayout><Documents /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/shifts" element={
        <ProtectedRoute>
          <DashboardLayout><Shifts /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/profile" element={
        <ProtectedRoute>
          <DashboardLayout><Profile /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/directory" element={
        <ProtectedRoute>
          <DashboardLayout><Directory /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/company" element={
        <ProtectedRoute>
          <DashboardLayout><Company /></DashboardLayout>
        </ProtectedRoute>
      } />
    </Routes>
  );

  // If we're in a test environment, don't wrap with Router or AuthProvider
  if (process.env.NODE_ENV === 'test') {
    return <AppRoutes />;
  }

  return (
    <AuthProvider>
      <ThemeProvider theme={theme}>
        <Router>
          <AppRoutes />
        </Router>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;
