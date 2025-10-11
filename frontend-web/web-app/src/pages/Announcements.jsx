import React, { useEffect, useState } from 'react';
import { api, useAuth } from '../contexts/AuthContext';
import { BellIcon, PlusIcon } from '@heroicons/react/24/outline';

const Announcements = () => {
  const { user: currentUser } = useAuth();
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [creating, setCreating] = useState(false);
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);

  useEffect(() => {
    fetchAnnouncements();
  }, []);

  const fetchAnnouncements = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get('/api/notifications/list');
      setAnnouncements(response.data);
    } catch (err) {
      setError('Failed to load announcements.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!title.trim() || !message.trim()) return;

    try {
      setCreating(true);
      const response = await api.post('/api/notifications/announce', {
        title: title.trim(),
        message: message.trim(),
      });
      setAnnouncements([response.data, ...announcements]);
      setTitle('');
      setMessage('');
      setShowCreateForm(false);
      alert('Announcement created successfully!');
    } catch (err) {
      setError('Failed to create announcement.');
    } finally {
      setCreating(false);
    }
  };

  const canCreate = currentUser?.role === 'CompanyAdmin' || currentUser?.role === 'SuperAdmin';

  if (loading) return <div className="p-6">Loading announcements...</div>;
  if (error) return <div className="p-6 text-red-600">{error}</div>;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-neutral-900">Announcements</h1>
        {canCreate && (
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="bg-accent-500 text-white px-4 py-2 rounded-lg hover:bg-accent-600 flex items-center space-x-2"
          >
            <PlusIcon className="w-4 h-4" />
            <span>{showCreateForm ? 'Cancel' : 'Create Announcement'}</span>
          </button>
        )}
      </div>

      {showCreateForm && canCreate && (
        <form onSubmit={handleCreate} className="bg-white p-6 rounded-lg border mb-6">
          <h2 className="text-lg font-medium mb-4">Create New Announcement</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Title</label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500"
                placeholder="Announcement title"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Message</label>
              <textarea
                required
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500"
                placeholder="Announcement message"
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={creating}
            className="mt-4 bg-accent-500 text-white px-6 py-2 rounded-lg hover:bg-accent-600 disabled:opacity-50 flex items-center space-x-2"
          >
            <PlusIcon className="w-4 h-4" />
            <span>{creating ? 'Creating...' : 'Create'}</span>
          </button>
        </form>
      )}

      <div className="space-y-4">
        {announcements.length === 0 ? (
          <div className="text-center py-12">
            <BellIcon className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
            <p className="text-neutral-500">No announcements found.</p>
          </div>
        ) : (
          announcements.map((announcement) => (
            <div
              key={announcement.id}
              className="bg-white p-6 rounded-lg border border-neutral-200"
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold text-neutral-900">{announcement.title}</h3>
                <span className="text-sm text-neutral-400">
                  {new Date(announcement.created_at).toLocaleDateString()}
                </span>
              </div>
              <p className="text-neutral-600 whitespace-pre-wrap">{announcement.message}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Announcements;
