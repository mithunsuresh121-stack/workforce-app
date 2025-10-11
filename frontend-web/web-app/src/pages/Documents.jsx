import React, { useEffect, useState } from 'react';
import { api, useAuth } from '../contexts/AuthContext';
import { DocumentIcon, UploadIcon, EyeIcon, DownloadIcon } from '@heroicons/react/24/outline';

const Documents = () => {
  const { user: currentUser } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState(null);
  const [docType, setDocType] = useState('OTHER');
  const [accessRole, setAccessRole] = useState('EMPLOYEE');
  const [showUploadForm, setShowUploadForm] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get('/api/documents/list');
      setDocuments(response.data);
    } catch (err) {
      setError('Failed to load documents.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', docType);
    formData.append('access_role', accessRole);

    try {
      setUploading(true);
      const response = await api.post('/api/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setDocuments([...documents, response.data]);
      setFile(null);
      setDocType('OTHER');
      setAccessRole('EMPLOYEE');
      setShowUploadForm(false);
      alert('Document uploaded successfully!');
    } catch (err) {
      setError('Failed to upload document.');
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (documentId) => {
    try {
      const response = await api.get(`/api/documents/download/${documentId}`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `document_${documentId}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('Failed to download document.');
    }
  };

  const canUpload = currentUser?.role === 'Manager' || currentUser?.role === 'CompanyAdmin' || currentUser?.role === 'SuperAdmin';

  if (loading) return <div className="p-6">Loading documents...</div>;
  if (error) return <div className="p-6 text-red-600">{error}</div>;

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-neutral-900">Documents</h1>
        {canUpload && (
          <button
            onClick={() => setShowUploadForm(!showUploadForm)}
            className="bg-accent-500 text-white px-4 py-2 rounded-lg hover:bg-accent-600 flex items-center space-x-2"
          >
            <UploadIcon className="w-4 h-4" />
            <span>{showUploadForm ? 'Cancel' : 'Upload Document'}</span>
          </button>
        )}
      </div>

      {showUploadForm && canUpload && (
        <form onSubmit={handleUpload} className="bg-white p-6 rounded-lg border mb-6">
          <h2 className="text-lg font-medium mb-4">Upload New Document</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">File</label>
              <input
                type="file"
                required
                onChange={(e) => setFile(e.target.files[0])}
                className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Type</label>
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
                className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500"
              >
                <option value="POLICY">Policy</option>
                <option value="PAYSLIP">Payslip</option>
                <option value="NOTICE">Notice</option>
                <option value="OTHER">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Access Role</label>
              <select
                value={accessRole}
                onChange={(e) => setAccessRole(e.target.value)}
                className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500"
              >
                <option value="EMPLOYEE">Employee</option>
                <option value="MANAGER">Manager</option>
                <option value="ADMIN">Admin</option>
              </select>
            </div>
          </div>
          <button
            type="submit"
            disabled={uploading}
            className="mt-4 bg-accent-500 text-white px-6 py-2 rounded-lg hover:bg-accent-600 disabled:opacity-50 flex items-center space-x-2"
          >
            <UploadIcon className="w-4 h-4" />
            <span>{uploading ? 'Uploading...' : 'Upload'}</span>
          </button>
        </form>
      )}

      <div className="bg-white rounded-lg border overflow-hidden">
        <table className="min-w-full divide-y divide-neutral-200">
          <thead className="bg-neutral-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">File</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Access</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">Uploaded</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-neutral-200">
            {documents.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-neutral-500">
                  <DocumentIcon className="w-12 h-12 mx-auto mb-4 text-neutral-300" />
                  <p>No documents available.</p>
                </td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                      {doc.type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-900">
                    {doc.file_path.split('/').pop()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      doc.access_role === 'EMPLOYEE' ? 'bg-green-100 text-green-800' :
                      doc.access_role === 'MANAGER' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {doc.access_role}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleDownload(doc.id)}
                      className="text-accent-600 hover:text-accent-900 mr-3"
                      title="Download"
                    >
                      <DownloadIcon className="w-5 h-5" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Documents;
