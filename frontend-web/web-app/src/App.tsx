import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginScreen from './screens/LoginScreen';
import ProfileScreen from './screens/ProfileScreen';
import DirectoryScreen from './screens/DirectoryScreen';
import DashboardScreen from './screens/DashboardScreen';
import TasksScreen from './screens/TasksScreen';
import LeaveScreen from './screens/LeaveScreen';

function App() {
  const authToken = localStorage.getItem('auth_token');

  return (
    <div className="App">
      <Routes>
        <Route path="/login" element={<LoginScreen />} />
        <Route path="/" element={authToken ? <DashboardScreen /> : <Navigate to="/login" />} />
        <Route path="/dashboard" element={authToken ? <DashboardScreen /> : <Navigate to="/login" />} />
        <Route path="/profile" element={authToken ? <ProfileScreen /> : <Navigate to="/login" />} />
        <Route path="/directory" element={authToken ? <DirectoryScreen /> : <Navigate to="/login" />} />
        <Route path="/tasks" element={authToken ? <TasksScreen /> : <Navigate to="/login" />} />
        <Route path="/leave" element={authToken ? <LeaveScreen /> : <Navigate to="/login" />} />
      </Routes>
    </div>
  );
}

export default App;
