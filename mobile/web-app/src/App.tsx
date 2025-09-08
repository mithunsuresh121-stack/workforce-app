import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import LoginScreen from './screens/LoginScreen';
import SignupScreen from './screens/SignupScreen';
import DashboardScreen from './screens/DashboardScreen';
import EmployeesScreen from './screens/EmployeesScreen';
import TasksScreen from './screens/TasksScreen';
import ReportsScreen from './screens/ReportsScreen';
import ChatAssistantScreen from './screens/ChatAssistantScreen';
import CompanyManagementScreen from './screens/CompanyManagementScreen';
import SystemSettingsScreen from './screens/SystemSettingsScreen';
import TeamsScreen from './screens/TeamsScreen';
import MyTeamScreen from './screens/MyTeamScreen';
import DirectoryScreen from './screens/DirectoryScreen';
import ProfileScreen from './screens/ProfileScreen';
import LeaveManagementScreen from './screens/LeaveManagementScreen';
import ShiftManagementScreen from './screens/ShiftManagementScreen';
import NotificationPreferencesScreen from './screens/NotificationPreferencesScreen';

function App() {
  const authToken = localStorage.getItem('authToken');

  return (
    <Router>
      <div className="min-h-screen bg-background">
        <Routes>
          <Route path="/login" element={<LoginScreen />} />
          <Route path="/signup" element={<SignupScreen />} />
          <Route path="/" element={authToken ? <AppLayout /> : <Navigate to="/login" />}>
            <Route index element={<DashboardScreen />} />
            <Route path="dashboard" element={<DashboardScreen />} />
            <Route path="employees" element={<EmployeesScreen />} />
            <Route path="tasks" element={<TasksScreen />} />
            <Route path="reports" element={<ReportsScreen />} />
            <Route path="chat" element={<ChatAssistantScreen />} />
          <Route path="company" element={<CompanyManagementScreen />} />
          <Route path="settings" element={<SystemSettingsScreen />} />
          <Route path="teams" element={<TeamsScreen />} />
          <Route path="my-team" element={<MyTeamScreen />} />
          <Route path="directory" element={<DirectoryScreen />} />
          <Route path="profile" element={<ProfileScreen />} />
          <Route path="leaves" element={<LeaveManagementScreen />} />
          <Route path="shifts" element={<ShiftManagementScreen />} />
          <Route path="notifications" element={<NotificationPreferencesScreen />} />
          </Route>
        </Routes>
      </div>
    </Router>
  );
}

export default App;
