import React, { useState, useEffect } from "react";
import { Card, Typography, Box, List, ListItem, ListItemText, Divider, TextField, IconButton } from "@mui/material";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { PencilIcon, CheckIcon, XMarkIcon } from "@heroicons/react/24/outline";
import DashboardLayout from "../layouts/DashboardLayout";
import { api } from "../contexts/AuthContext";

const initialKpis = [
  { id: 'active-projects', title: 'Active Projects', value: 12, editable: false },
  { id: 'total-employees', title: 'Total Employees', value: 89, editable: false },
  { id: 'completed-tasks', title: 'Completed Tasks', value: 156, editable: false },
];

const initialActivities = [
  { id: 1, primary: 'New employee onboarded', secondary: '2 hours ago' },
  { id: 2, primary: 'Project deadline met', secondary: '5 hours ago' },
  { id: 3, primary: 'Task assigned to team', secondary: '1 day ago' },
  { id: 4, primary: 'Performance review completed', secondary: '2 days ago' },
];

const data = [
  { name: 'Jan', tasks: 40 },
  { name: 'Feb', tasks: 30 },
  { name: 'Mar', tasks: 20 },
  { name: 'Apr', tasks: 27 },
  { name: 'May', tasks: 18 },
  { name: 'Jun', tasks: 23 },
];

export default function Dashboard() {
  const [kpis, setKpis] = useState(initialKpis);
  const [activities, setActivities] = useState(initialActivities);
  const [editingKpi, setEditingKpi] = useState(null);
  const [editValue, setEditValue] = useState('');

  useEffect(() => {
    fetchKpis();
    fetchActivities();
    const interval = setInterval(fetchActivities, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchKpis = async () => {
    try {
      const response = await api.get('/dashboard/kpis');
      const data = response.data;
      setKpis([
        { id: 'active-projects', title: 'Active Projects', value: data.active_tasks || 12, editable: false },
        { id: 'total-employees', title: 'Total Employees', value: data.total_employees || 89, editable: false },
        { id: 'completed-tasks', title: 'Completed Tasks', value: data.completed_tasks || 156, editable: false },
      ]);
    } catch (error) {
      console.error('Error fetching KPIs:', error);
    }
  };

  const fetchActivities = async () => {
    try {
      const response = await api.get('/dashboard/recent-activities');
      setActivities(response.data.map(activity => ({
        id: activity.id || activity.entity_id,
        primary: activity.title,
        secondary: new Date(activity.timestamp).toLocaleString(),
      })));
    } catch (error) {
      console.error('Error fetching activities:', error);
    }
  };

  const handleEditKpi = (kpi) => {
    setEditingKpi(kpi.id);
    setEditValue(kpi.title);
  };

  const handleSaveKpi = () => {
    setKpis(kpis.map(k => k.id === editingKpi ? { ...k, title: editValue } : k));
    setEditingKpi(null);
  };

  const handleCancelEdit = () => {
    setEditingKpi(null);
  };

  const onDragEnd = (result) => {
    if (!result.destination) return;
    const items = Array.from(kpis);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);
    setKpis(items);
  };

  return (
    <DashboardLayout>
      <Typography variant="h4" sx={{ mb: 3, color: 'text.primary' }}>Dashboard Overview</Typography>
      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="kpis" direction="horizontal">
          {(provided) => (
            <Box
              {...provided.droppableProps}
              ref={provided.innerRef}
              sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }, gap: 3, mb: 4 }}
            >
              {kpis.map((kpi, index) => (
                <Draggable key={kpi.id} draggableId={kpi.id} index={index}>
                  {(provided) => (
                    <Card
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      {...provided.dragHandleProps}
                      sx={{ p: 3, cursor: 'pointer', '&:hover': { boxShadow: 3 } }}
                    >
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        {editingKpi === kpi.id ? (
                          <TextField
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            size="small"
                            fullWidth
                          />
                        ) : (
                      <Typography variant="h6" sx={{ color: 'text.secondary' }}>{kpi.title}</Typography>
                        )}
                        {editingKpi === kpi.id ? (
                          <Box>
                            <IconButton size="small" onClick={handleSaveKpi}>
                              <CheckIcon style={{ width: 16, height: 16 }} />
                            </IconButton>
                            <IconButton size="small" onClick={handleCancelEdit}>
                              <XMarkIcon style={{ width: 16, height: 16 }} />
                            </IconButton>
                          </Box>
                        ) : (
                          <IconButton size="small" onClick={() => handleEditKpi(kpi)}>
                            <PencilIcon style={{ width: 16, height: 16 }} />
                          </IconButton>
                        )}
                      </Box>
                      <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'primary.main' }}>{kpi.value}</Typography>
                    </Card>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </Box>
          )}
        </Droppable>
      </DragDropContext>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' }, gap: 3 }}>
        <Card sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ mb: 2, color: 'text.primary' }}>Task Completion Trends</Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="tasks" fill="var(--mui-palette-primary-main)" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ mb: 2, color: 'text.primary' }}>Recent Activity</Typography>
          <List sx={{ maxHeight: 300, overflow: 'auto' }}>
            {activities.map((activity, index) => (
              <React.Fragment key={activity.id}>
                <ListItem>
                  <ListItemText primary={activity.primary} secondary={activity.secondary} />
                </ListItem>
                {index < activities.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Card>
      </Box>
    </DashboardLayout>
  );
}
