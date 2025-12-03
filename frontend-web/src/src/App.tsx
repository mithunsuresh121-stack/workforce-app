import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';

// Lazy load components for better performance
const Login = lazy(() => import('./pages/Login'));
const Signup = lazy(() => import('./pages/Signup'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Profile = lazy(() => import('./pages/Profile'));
const Directory = lazy(() => import('./pages/Directory'));
const Tasks = lazy(() => import('./pages/Tasks'));
const Leave = lazy(() => import('./pages/Leave'));
const Shifts = lazy(() => import('./pages/Shifts'));
const Notifications = lazy(() => import('./pages/Notifications'));
const Company = lazy(() => import('./pages/Company'));
const ManagerApprovals = lazy(() => import('./pages/ManagerApprovals'));
const Documents = lazy(() => import('./pages/Documents'));
const Announcements = lazy(() => import('./pages/Announcements'));
const NotificationSettings = lazy(() => import('./pages/NotificationSettings'));

function App() {
  const AppRoutes = () => (
    <Suspense fallback={<div className="flex justify-center items-center h-screen">Loading...</div>}>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Protected routes */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout><Dashboard /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Layout><Dashboard /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/profile" element={
          <ProtectedRoute>
            <Layout><Profile /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/directory" element={
          <ProtectedRoute>
            <Layout><Directory /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/tasks" element={
          <ProtectedRoute>
            <Layout><Tasks /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/shifts" element={
          <ProtectedRoute>
            <Layout><Shifts /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/notifications" element={
          <ProtectedRoute>
            <Layout><Notifications /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/notification-settings" element={
          <ProtectedRoute>
            <Layout><NotificationSettings /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/leave" element={
          <ProtectedRoute>
            <Layout><Leave /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/company" element={
          <ProtectedRoute>
            <Layout><Company /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/manager-approvals" element={
          <ProtectedRoute>
            <Layout><ManagerApprovals /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/documents" element={
          <ProtectedRoute>
            <Layout><Documents /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/announcements" element={
          <ProtectedRoute>
            <Layout><Announcements /></Layout>
          </ProtectedRoute>
        } />
      </Routes>
    </Suspense>
  );

  const queryClient = new QueryClient();

  // If we're in a test environment, don't wrap with Router
  if (process.env.NODE_ENV === 'test') {
    return (
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </QueryClientProvider>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <AppRoutes />
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
