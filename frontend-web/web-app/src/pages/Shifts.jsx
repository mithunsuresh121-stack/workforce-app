import React, { useEffect, useState } from 'react';
import { api, useAuth } from '../contexts/AuthContext';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';

const localizer = momentLocalizer(moment);

const Shifts = () => {
  const { user: currentUser } = useAuth();
  const [shifts, setShifts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchShifts = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await api.get('/shifts/my-shifts/');
        // Map shifts to calendar events
        const events = response.data.map(shift => ({
          id: shift.id,
          title: `Shift: ${shift.status}`,
          start: new Date(shift.start_at),
          end: new Date(shift.end_at),
          allDay: false,
          resource: shift,
        }));
        setShifts(events);
      } catch (err) {
        setError('Failed to load shifts.');
      } finally {
        setLoading(false);
      }
    };
    fetchShifts();
  }, [currentUser]);

  const eventStyleGetter = (event) => {
    let backgroundColor = '#3174ad'; // default blue
    if (event.resource.status === 'COMPLETED') backgroundColor = '#4caf50'; // green
    else if (event.resource.status === 'CANCELLED') backgroundColor = '#f44336'; // red
    else if (event.resource.status === 'ON_LEAVE') backgroundColor = '#ff9800'; // orange

    const style = {
      backgroundColor,
      borderRadius: '5px',
      opacity: 0.8,
      color: 'white',
      border: '0px',
      display: 'block',
    };
    return { style };
  };

  if (loading) return <div>Loading shifts...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-4">My Shifts</h1>
      <Calendar
        localizer={localizer}
        events={shifts}
        startAccessor="start"
        endAccessor="end"
        style={{ height: 600 }}
        eventPropGetter={eventStyleGetter}
      />
    </div>
  );
};

export default Shifts;
