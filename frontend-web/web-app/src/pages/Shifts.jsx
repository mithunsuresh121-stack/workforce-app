import React, { useState, useEffect } from "react";
import { Calendar, dateFnsLocalizer } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { Card, Typography, Box, Button, Modal, TextField, Select, MenuItem, FormControl, InputLabel } from "@mui/material";
import DashboardLayout from "../layouts/DashboardLayout";
import axios from "axios";
import 'react-big-calendar/lib/css/react-big-calendar.css';

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales: {
    'en-US': enUS,
  },
});

export default function Shifts() {
  const [shifts, setShifts] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [userRole, setUserRole] = useState('Employee');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [newShift, setNewShift] = useState({ employee_id: '', start_at: '', end_at: '', location: '' });

  useEffect(() => {
    fetchShifts();
    fetchEmployees();
    // Assume get user role from context
    setUserRole('Manager'); // Placeholder
  }, []);

  const fetchShifts = async () => {
    try {
      const response = await axios.get('/shifts');
      setShifts(response.data.map(shift => ({
        id: shift.id,
        title: `Shift for Employee ${shift.employee_id}`,
        start: new Date(shift.start_at),
        end: new Date(shift.end_at),
        resource: shift,
      })));
    } catch (error) {
      console.error('Error fetching shifts:', error);
    }
  };

  const fetchEmployees = async () => {
    try {
      const response = await axios.get('/users/employees');
      setEmployees(response.data);
    } catch (error) {
      console.error('Error fetching employees:', error);
    }
  };

  const handleSelectSlot = (slotInfo) => {
    if (userRole === 'Manager') {
      setSelectedSlot(slotInfo);
      setNewShift({ ...newShift, start_at: slotInfo.start.toISOString(), end_at: slotInfo.end.toISOString() });
      setModalOpen(true);
    }
  };

  const handleCreateShift = async () => {
    try {
      await axios.post('/shifts', newShift);
      fetchShifts();
      setModalOpen(false);
      setNewShift({ employee_id: '', start_at: '', end_at: '', location: '' });
    } catch (error) {
      console.error('Error creating shift:', error);
    }
  };

  const eventStyleGetter = (event, start, end, isSelected) => {
    return {
      style: {
        backgroundColor: isSelected ? '#1976d2' : '#4caf50',
        borderRadius: '5px',
        opacity: 0.8,
        color: 'white',
        border: '0px',
        display: 'block'
      }
    };
  };

  return (
    <DashboardLayout>
      <Typography variant="h4" mb={3}>Shift Scheduling</Typography>
      <Card sx={{ p: 3 }}>
        <Calendar
          localizer={localizer}
          events={shifts}
          startAccessor="start"
          endAccessor="end"
          style={{ height: 500 }}
          selectable={userRole === 'Manager'}
          onSelectSlot={handleSelectSlot}
          eventPropGetter={eventStyleGetter}
          views={['month', 'week', 'day']}
          defaultView="week"
        />
      </Card>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
        <Box sx={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: 400, bgcolor: 'background.paper', p: 4, borderRadius: 2 }}>
          <Typography variant="h6" mb={2}>Create New Shift</Typography>
          <FormControl fullWidth margin="normal">
            <InputLabel>Employee</InputLabel>
            <Select
              value={newShift.employee_id}
              onChange={(e) => setNewShift({ ...newShift, employee_id: e.target.value })}
            >
              {employees.map(emp => (
                <MenuItem key={emp.id} value={emp.id}>{emp.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            margin="normal"
            label="Start Time"
            type="datetime-local"
            value={newShift.start_at.slice(0, 16)}
            onChange={(e) => setNewShift({ ...newShift, start_at: e.target.value })}
          />
          <TextField
            fullWidth
            margin="normal"
            label="End Time"
            type="datetime-local"
            value={newShift.end_at.slice(0, 16)}
            onChange={(e) => setNewShift({ ...newShift, end_at: e.target.value })}
          />
          <TextField
            fullWidth
            margin="normal"
            label="Location"
            value={newShift.location}
            onChange={(e) => setNewShift({ ...newShift, location: e.target.value })}
          />
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
            <Button onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button variant="contained" onClick={handleCreateShift}>Create</Button>
          </Box>
        </Box>
      </Modal>
    </DashboardLayout>
  );
}
