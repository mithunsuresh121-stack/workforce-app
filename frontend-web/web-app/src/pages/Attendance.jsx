import React, { useState, useEffect } from "react";
import { Card, Typography, Box, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from "@mui/material";
import DashboardLayout from "../layouts/DashboardLayout";
import axios from "axios";

export default function Attendance() {
  const [attendanceHistory, setAttendanceHistory] = useState([]);
  const [activeAttendance, setActiveAttendance] = useState(null);

  useEffect(() => {
    fetchAttendanceHistory();
    fetchActiveAttendance();
  }, []);

  const fetchAttendanceHistory = async () => {
    try {
      const response = await axios.get('/attendance/my');
      setAttendanceHistory(response.data);
    } catch (error) {
      console.error('Error fetching attendance history:', error);
    }
  };

  const fetchActiveAttendance = async () => {
    try {
      const response = await axios.get('/attendance/active');
      setActiveAttendance(response.data);
    } catch (error) {
      setActiveAttendance(null);
    }
  };

  const handleClockIn = async () => {
    try {
      const position = await getCurrentPosition();
      const payload = {
        employee_id: 1, // Assume current user id
        notes: `Clocked in at ${position ? `${position.coords.latitude}, ${position.coords.longitude}` : 'Location not available'}`
      };
      await axios.post('/attendance/clock-in', payload);
      fetchActiveAttendance();
      fetchAttendanceHistory();
    } catch (error) {
      console.error('Error clocking in:', error);
    }
  };

  const handleClockOut = async () => {
    if (!activeAttendance) return;
    try {
      const position = await getCurrentPosition();
      const payload = {
        attendance_id: activeAttendance.id,
        employee_id: 1, // Assume current user id
        notes: `Clocked out at ${position ? `${position.coords.latitude}, ${position.coords.longitude}` : 'Location not available'}`
      };
      await axios.put('/attendance/clock-out', payload);
      setActiveAttendance(null);
      fetchAttendanceHistory();
    } catch (error) {
      console.error('Error clocking out:', error);
    }
  };

  const getCurrentPosition = () => {
    return new Promise((resolve, reject) => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(resolve, reject);
      } else {
        reject(new Error('Geolocation not supported'));
      }
    });
  };

  return (
    <DashboardLayout>
      <Typography variant="h4" mb={3}>Attendance</Typography>
      <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
        <Button variant="contained" color="primary" onClick={handleClockIn} disabled={!!activeAttendance}>
          Clock In
        </Button>
        <Button variant="contained" color="secondary" onClick={handleClockOut} disabled={!activeAttendance}>
          Clock Out
        </Button>
      </Box>
      {activeAttendance && (
        <Card sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6">Active Session</Typography>
          <Typography>Clocked in at: {new Date(activeAttendance.clock_in_time).toLocaleString()}</Typography>
        </Card>
      )}
      <Card sx={{ p: 3 }}>
        <Typography variant="h6" mb={2}>Daily Log</Typography>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Clock In</TableCell>
                <TableCell>Clock Out</TableCell>
                <TableCell>Hours</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {attendanceHistory.map((record) => (
                <TableRow key={record.id}>
                  <TableCell>{new Date(record.clock_in_time).toLocaleDateString()}</TableCell>
                  <TableCell>{new Date(record.clock_in_time).toLocaleTimeString()}</TableCell>
                  <TableCell>{record.clock_out_time ? new Date(record.clock_out_time).toLocaleTimeString() : 'Active'}</TableCell>
                  <TableCell>{record.total_hours ? `${record.total_hours.toFixed(2)}h` : '-'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
    </DashboardLayout>
  );
}
