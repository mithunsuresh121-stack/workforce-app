import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { api } from '../contexts/AuthContext';
import {
  PaperClipIcon,
  XMarkIcon,
  EyeIcon,
  TrashIcon,
  CloudArrowUpIcon
} from '@heroicons/react/24/outline';

const TaskAttachments = ({ taskId, attachments, onAttachmentsChange, isEditing, currentUser }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const onDrop = useCallback(async (acceptedFiles) => {
    if (!isEditing) return;

    setUploading(true);
    setError('');

    try {
      for (const file of acceptedFiles) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await api.post(`/tasks/${taskId}/attachments`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        onAttachmentsChange([...attachments, response.data]);
      }
    } catch (error) {
      console.error('Upload error:', error);
      setError('Failed to upload file. Please try again.');
    } finally {
      setUploading(false);
    }
  }, [taskId, attachments, onAttachmentsChange, isEditing]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    disabled: !isEditing,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const handleDelete = async (attachmentId) => {
    if (!window.confirm('Are you sure you want to delete this attachment?')) return;

    try {
      await api.delete(`/tasks/${taskId}/attachments/${attachmentId}`);
      onAttachmentsChange(attachments.filter(att => att.id !== attachmentId));
    } catch (error) {
      console.error('Delete error:', error);
      setError('Failed to delete attachment. Please try again.');
    }
  };

  const handleDownload = (attachment) => {
    // For now, assume files are served from backend/uploads
    // In production, you'd have a proper download endpoint
    const link = document.createElement('a');
    link.href = `/uploads/${attachment.file_path.split('/').pop()}`;
    link.download = attachment.file_path.split('/').pop();
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const canDelete = (attachment) => {
    if (!currentUser) return false;
    const allowedRoles = ['SuperAdmin', 'Manager', 'CompanyAdmin'];
    return allowedRoles.includes(currentUser.role) ||
           attachment.uploaded_by === currentUser.id;
  };

  const formatFileSize = (sizeInMB) => {
    if (sizeInMB < 1) {
      return `${(sizeInMB * 1024).toFixed(0)} KB`;
    }
    return `${sizeInMB.toFixed(1)} MB`;
  };

  const getFileIcon = (fileType) => {
    if (fileType.startsWith('image/')) {
      return '🖼️';
    } else if (fileType === 'application/pdf') {
      return '📄';
    } else if (fileType.includes('wordprocessingml')) {
      return '📝';
    } else if (fileType.includes('spreadsheetml')) {
      return '📊';
    }
    return '📎';
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <PaperClipIcon className="w-5 h-5 text-neutral-500" />
        <h3 className="text-lg font-medium text-neutral-900">Attachments</h3>
      </div>

      {error && (
        <div className="p-3 bg-danger-50 border border-danger-200 text-danger-800 rounded-lg">
          {error}
        </div>
      )}

      {isEditing && (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-accent-500 bg-accent-50'
              : 'border-neutral-300 hover:border-accent-400'
          }`}
        >
          <input {...getInputProps()} />
          <CloudArrowUpIcon className="w-8 h-8 text-neutral-400 mx-auto mb-2" />
          {isDragActive ? (
            <p className="text-accent-600">Drop files here...</p>
          ) : (
            <div>
              <p className="text-neutral-600">
                Drag & drop files here, or click to select
              </p>
              <p className="text-sm text-neutral-500 mt-1">
                Supported: JPG, PNG, PDF, DOCX, XLSX (max 10MB)
              </p>
            </div>
          )}
          {uploading && (
            <div className="mt-2">
              <div className="w-6 h-6 border-2 border-accent-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="text-sm text-neutral-600 mt-1">Uploading...</p>
            </div>
          )}
        </div>
      )}

      {attachments.length > 0 && (
        <div className="space-y-2">
          {attachments.map((attachment) => (
            <div
              key={attachment.id}
              className="flex items-center justify-between p-3 bg-neutral-50 border border-neutral-200 rounded-lg"
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <span className="text-lg">{getFileIcon(attachment.file_type)}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-neutral-900 truncate">
                    {attachment.file_path.split('/').pop()}
                  </p>
                  <p className="text-xs text-neutral-500">
                    {formatFileSize(attachment.file_size)} • Uploaded {new Date(attachment.uploaded_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleDownload(attachment)}
                  className="p-1 text-neutral-400 hover:text-accent-600 hover:bg-accent-50 rounded"
                  title="Download"
                >
                  <EyeIcon className="w-4 h-4" />
                </button>
                {isEditing && canDelete(attachment) && (
                  <button
                    onClick={() => handleDelete(attachment.id)}
                    className="p-1 text-neutral-400 hover:text-danger-600 hover:bg-danger-50 rounded"
                    title="Delete"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {attachments.length === 0 && !isEditing && (
        <p className="text-neutral-500 text-sm">No attachments</p>
      )}
    </div>
  );
};

export default TaskAttachments;
