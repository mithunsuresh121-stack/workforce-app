import React, { useState, useEffect } from "react";
import { Card, Typography, Box, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from "@mui/material";
import { api } from '../contexts/AuthContext';

export default function Attendance() {
  const [attendanceHistory, setAttendanceHistory] = useState([]);
  const [activeAttendance, setActiveAttendance] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAttendanceHistory();
    fetchActiveAttendance();
  }, []);

  const fetchAttendanceHistory = async () => {
    try {
      const response = await api.get('/attendance/history');
      setAttendanceHistory(response.data);
    } catch (error) {
      console.error('Error fetching attendance history:', error);
    }
  };

  const fetchActiveAttendance = async () => {
    try {
      const response = await api.get('/attendance/active');
      setActiveAttendance(response.data);
    } catch (error) {
      setActiveAttendance(null);
    }
  };

  const getCurrentPosition = () => {
    return new Promise((resolve, reject) => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 5000,
          maximumAge: 0
        });
      } else {
        reject(new Error('Geolocation not supported'));
      }
    });
  };

  const handleClockIn = async () => {
    setLoading(true);
    try {
      let position = null;
      try {
        position = await getCurrentPosition();
      } catch (geoError) {
        console.warn('Geolocation failed:', geoError);
      }

      const payload = {
        employee_id: 1, // Will be overridden by backend from token
        notes: position ? `Clocked in at ${position.coords.latitude}, ${position.coords.longitude}` : 'Location not available'
      };

      const params = {};
      if (position) {
        params.lat = position.coords.latitude;
        params.lng = position.coords.longitude;
      }
      params.ip_address = 'client_ip'; // Backend will get real IP

      await api.post('/attendance/clock-in', payload, { params });
      fetchActiveAttendance();
      fetchAttendanceHistory();
    } catch (error) {
      console.error('Error clocking in:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClockOut = async () => {
    if (!activeAttendance) return;
    setLoading(true);
    try {
      let position = null;
      try {
        position = await getCurrentPosition();
      } catch (geoError) {
        console.warn('Geolocation failed:', geoError);
      }

      const payload = {
        attendance_id: activeAttendance.id,
        employee_id: 1, // Will be overridden by backend
        notes: position ? `Clocked out at ${position.coords.latitude}, ${position.coords.longitude}` : 'Location not available'
      };

      const params = {};
      if (position) {
        params.lat = position.coords.latitude;
        params.lng = position.coords.longitude;
      }
      params.ip_address = 'client_ip';

      await api.put('/attendance/clock-out', payload, { params });
      setActiveAttendance(null);
      fetchAttendanceHistory();
    } catch (error) {
      console.error('Error clocking out:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h4" sx={{ color: 'text.primary', mb: 3 }}>Attendance</Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleClockIn}
          disabled={!!activeAttendance || loading}
        >
          {loading ? 'Processing...' : 'Clock In'}
        </Button>
        <Button
          variant="contained"
          color="secondary"
          onClick={handleClockOut}
          disabled={!activeAttendance || loading}
        >
          {loading ? 'Processing...' : 'Clock Out'}
        </Button>
      </Box>

      {activeAttendance && (
        <Card sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" sx={{ color: 'text.primary', mb: 2 }}>Active Session</Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
            <Box>
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>Clocked In</Typography>
              <Typography sx={{ color: 'text.primary' }}>
                {new Date(activeAttendance.clock_in_time).toLocaleString()}
              </Typography>
            </Box>
            {activeAttendance.lat && (
              <Box>
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>Location</Typography>
                <Typography sx={{ color: 'text.primary' }}>
                  {activeAttendance.lat.toFixed(4)}, {activeAttendance.lng.toFixed(4)}
                </Typography>
              </Box>
            )}
          </Box>
        </Card>
      )}

      <Card sx={{ overflow: 'hidden' }}>
        <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6" sx={{ color: 'text.primary' }}>Attendance History</Typography>
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: 'grey.50' }}>
                <TableCell>Date</TableCell>
                <TableCell>Clock In</TableCell>
                <TableCell>Clock Out</TableCell>
                <TableCell>Hours</TableCell>
                <TableCell>Location</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {attendanceHistory.map((record) => (
                <TableRow key={record.id} hover>
                  <TableCell>{new Date(record.clock_in_time).toLocaleDateString()}</TableCell>
                  <TableCell>{new Date(record.clock_in_time).toLocaleTimeString()}</TableCell>
                  <TableCell>
                    {record.clock_out_time ? new Date(record.clock_out_time).toLocaleTimeString() : 'Active'}
                  </TableCell>
                  <TableCell>{record.total_hours ? `${record.total_hours.toFixed(2)}h` : '-'}</TableCell>
                  <TableCell>
                    {record.lat ? `${record.lat.toFixed(4)}, ${record.lng.toFixed(4)}` : '-'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        {attendanceHistory.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="body1" sx={{ color: 'text.secondary' }}>
              No attendance records found
            </Typography>
          </Box>
        )}
      </Card>
    </Box>
  );
}
