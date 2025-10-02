import React, { useState, useEffect } from "react";
import { Card, Typography, Box, TextField, Select, MenuItem, FormControl, InputLabel, IconButton, LinearProgress } from "@mui/material";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { MagnifyingGlassIcon, PencilIcon, CheckIcon, XMarkIcon } from "@heroicons/react/24/outline";
import { api } from "../contexts/AuthContext";

const initialProjects = [
  { id: 1, name: 'Project Alpha', status: 'In Progress', progress: 75 },
  { id: 2, name: 'Project Beta', status: 'Completed', progress: 100 },
  { id: 3, name: 'Project Gamma', status: 'Planning', progress: 10 },
];

export default function Projects() {
  const [projects, setProjects] = useState(initialProjects);
  const [filteredProjects, setFilteredProjects] = useState(initialProjects);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [sortField, setSortField] = useState('name');
  const [sortDirection, setSortDirection] = useState('asc');
  const [editingField, setEditingField] = useState(null);
  const [editValue, setEditValue] = useState('');

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    filterAndSortProjects();
  }, [projects, searchTerm, statusFilter, sortField, sortDirection]);

  const fetchProjects = async () => {
    try {
      const response = await api.get('/projects');
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const filterAndSortProjects = () => {
    let filtered = projects.filter(project =>
      project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.status.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (statusFilter !== 'All') {
      filtered = filtered.filter(project => project.status === statusFilter);
    }

    filtered.sort((a, b) => {
      const aValue = a[sortField].toLowerCase();
      const bValue = b[sortField].toLowerCase();
      if (sortDirection === 'asc') {
        return aValue.localeCompare(bValue);
      } else {
        return bValue.localeCompare(aValue);
      }
    });

    setFilteredProjects(filtered);
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handleEditField = (projectId, field, value) => {
    setEditingField({ projectId, field });
    setEditValue(value);
  };

  const handleSaveEdit = async () => {
    const updatedProject = { ...projects.find(p => p.id === editingField.projectId), [editingField.field]: editValue };
    try {
      await api.put(`/projects/${updatedProject.id}`, updatedProject);
      setProjects(projects.map(p => p.id === editingField.projectId ? updatedProject : p));
    } catch (error) {
      console.error('Error updating project:', error);
    }
    setEditingField(null);
  };

  const handleCancelEdit = () => {
    setEditingField(null);
  };

  const renderProjectCard = (project) => {
    const isEditing = editingField?.projectId === project.id;

    return (
      <Draggable key={project.id} draggableId={project.id.toString()} index={projects.indexOf(project)}>
        {(provided) => (
          <Card
            ref={provided.innerRef}
            {...provided.draggableProps}
            {...provided.dragHandleProps}
            sx={{ p: 3, cursor: 'pointer', '&:hover': { boxShadow: 3 } }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              {isEditing && editingField.field === 'name' ? (
                <TextField
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  size="small"
                  fullWidth
                />
              ) : (
                <Typography variant="h6" sx={{ color: 'text.primary' }}>{project.name}</Typography>
              )}
              <IconButton size="small" onClick={() => handleEditField(project.id, 'name', project.name)}>
                <PencilIcon style={{ width: 16, height: 16 }} />
              </IconButton>
            </Box>
            {isEditing && editingField.field === 'status' ? (
              <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                <InputLabel>Status</InputLabel>
                <Select value={editValue} onChange={(e) => setEditValue(e.target.value)}>
                  <MenuItem value="Planning">Planning</MenuItem>
                  <MenuItem value="In Progress">In Progress</MenuItem>
                  <MenuItem value="Completed">Completed</MenuItem>
                </Select>
              </FormControl>
            ) : (
              <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>{project.status}</Typography>
            )}
            {isEditing && editingField.field === 'progress' ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <TextField
                  type="number"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  size="small"
                  inputProps={{ min: 0, max: 100 }}
                  sx={{ width: 80 }}
                />
                %
                <IconButton size="small" onClick={handleSaveEdit}>
                  <CheckIcon style={{ width: 16, height: 16 }} />
                </IconButton>
                <IconButton size="small" onClick={handleCancelEdit}>
                  <XMarkIcon style={{ width: 16, height: 16 }} />
                </IconButton>
              </Box>
            ) : (
              <>
                <LinearProgress variant="determinate" value={project.progress} sx={{ mb: 1 }} />
                <Typography variant="body2" sx={{ mt: 1, color: 'text.primary' }}>{project.progress}% Complete</Typography>
                <IconButton size="small" onClick={() => handleEditField(project.id, 'progress', project.progress)} sx={{ mt: 1 }}>
                  <PencilIcon style={{ width: 16, height: 16 }} />
                </IconButton>
              </>
            )}
            {isEditing && editingField.field !== 'name' && editingField.field !== 'progress' && (
              <Box sx={{ display: 'flex', gap: 1 }}>
                <IconButton size="small" onClick={handleSaveEdit}>
                  <CheckIcon style={{ width: 16, height: 16 }} />
                </IconButton>
                <IconButton size="small" onClick={handleCancelEdit}>
                  <XMarkIcon style={{ width: 16, height: 16 }} />
                </IconButton>
              </Box>
            )}
          </Card>
        )}
      </Draggable>
    );
  };

  const onDragEnd = (result) => {
    if (!result.destination) return;
    const items = Array.from(projects);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);
    setProjects(items);
  };

  return (
    <>
      <Typography variant="h4" sx={{ mb: 3, color: 'text.primary' }}>Projects</Typography>
      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <TextField
          placeholder="Search projects..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <MagnifyingGlassIcon style={{ width: 20, height: 20, marginRight: 8 }} />,
          }}
          sx={{ minWidth: 250 }}
        />
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>Status</InputLabel>
          <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <MenuItem value="All">All</MenuItem>
            <MenuItem value="Planning">Planning</MenuItem>
            <MenuItem value="In Progress">In Progress</MenuItem>
            <MenuItem value="Completed">Completed</MenuItem>
          </Select>
        </FormControl>
      </Box>
      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="projects" direction="horizontal">
          {(provided) => (
            <Box
              {...provided.droppableProps}
              ref={provided.innerRef}
              sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 3 }}
            >
              {filteredProjects.map((project, index) => renderProjectCard(project, index))}
              {provided.placeholder}
            </Box>
          )}
        </Droppable>
      </DragDropContext>
    </>
  );
}
