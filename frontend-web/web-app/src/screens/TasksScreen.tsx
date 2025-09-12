import React, { useEffect, useState } from 'react';
import { getTasks, createTask, updateTask } from '../api/taskApi.js';

interface Task {
  id: number;
  title: string;
  description?: string;
  status: string;
  assigned_to: number;
  created_by: number;
  created_at: string;
  updated_at: string;
}

const TasksScreen: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newTask, setNewTask] = useState({ title: '', description: '' });

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getTasks();
      setTasks(data);
    } catch (err: any) {
      setError('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createTask({
        title: newTask.title,
        description: newTask.description,
        assigned_to: 1, // TODO: Get current user ID
      });
      setNewTask({ title: '', description: '' });
      fetchTasks();
    } catch (err: any) {
      setError('Failed to create task');
    }
  };

  const handleUpdateStatus = async (id: number, status: string) => {
    try {
      await updateTask(id, { status });
      fetchTasks();
    } catch (err: any) {
      setError('Failed to update task');
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Tasks</h1>
      {error && <div className="mb-4 text-red-600">{error}</div>}
      <form onSubmit={handleCreateTask} className="mb-4">
        <input
          type="text"
          placeholder="Task title"
          value={newTask.title}
          onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
          className="border border-gray-300 rounded px-3 py-2 mr-2"
          required
        />
        <input
          type="text"
          placeholder="Description"
          value={newTask.description}
          onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
          className="border border-gray-300 rounded px-3 py-2 mr-2"
        />
        <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">
          Add Task
        </button>
      </form>
      {loading ? (
        <div>Loading tasks...</div>
      ) : (
        <ul>
          {tasks.map((task) => (
            <li key={task.id} className="mb-2 p-2 border border-gray-300 rounded">
              <h3 className="font-semibold">{task.title}</h3>
              <p>{task.description}</p>
              <p>Status: {task.status}</p>
              <button
                onClick={() => handleUpdateStatus(task.id, task.status === 'pending' ? 'completed' : 'pending')}
                className="px-2 py-1 bg-green-600 text-white rounded"
              >
                Toggle Status
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default TasksScreen;
