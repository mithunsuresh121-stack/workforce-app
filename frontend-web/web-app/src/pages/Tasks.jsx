import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Tasks = () => {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    // Fetch tasks
    axios.get('/api/tasks').then(res => setTasks(res.data)).catch(() => {
      setTasks([
        { id: 1, title: 'Complete report', status: 'In Progress', assignee: 'John Doe' },
        { id: 2, title: 'Review code', status: 'Pending', assignee: 'Jane Smith' },
      ]);
    });
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Tasks</h1>
      <div className="space-y-4">
        {tasks.map((task) => (
          <div key={task.id} className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">{task.title}</h3>
            <p className="text-sm text-gray-500">Status: {task.status}</p>
            <p className="text-sm text-gray-500">Assignee: {task.assignee}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Tasks;
