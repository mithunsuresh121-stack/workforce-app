import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import ProfileProfessional from './pages/Profile_professional';
import SuperAdminApprovals from './pages/SuperAdminApprovals';
import Directory from './pages/Directory';
import Tasks from './pages/Tasks';
import Leave from './pages/Leave';
import Company from './pages/Company';

function App() {
  const AppRoutes = () => (
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
      <Route path="/profile-professional" element={
        <ProtectedRoute>
          <Layout><ProfileProfessional /></Layout>
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
      <Route path="/leave" element={
        <ProtectedRoute>
          <Layout><Leave /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/approvals" element={
        <ProtectedRoute>
          <Layout><SuperAdminApprovals /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/company" element={
        <ProtectedRoute>
          <Layout><Company /></Layout>
        </ProtectedRoute>
      } />
    </Routes>
  );

  // If we're in a test environment, don't wrap with Router
  if (process.env.NODE_ENV === 'test') {
    return <AppRoutes />;
  }

  return (
    <Router>
      <AppRoutes />
    </Router>
  );
}

export default App;
