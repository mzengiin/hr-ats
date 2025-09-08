import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import './FileList.css';

const FileList = ({ files = [], loading = false, error = null, onFileDeleted, onFileDownloaded }) => {
  const { isAuthenticated } = useAuth();
  const [deletingFileId, setDeletingFileId] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getFileTypeLabel = (mimeType) => {
    switch (mimeType) {
      case 'application/pdf':
        return 'PDF';
      case 'application/msword':
        return 'DOC';
      case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return 'DOCX';
      default:
        return 'Unknown';
    }
  };

  const getFileTypeIcon = (mimeType) => {
    switch (mimeType) {
      case 'application/pdf':
        return '📄';
      case 'application/msword':
      case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return '📝';
      default:
        return '📁';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleDownload = async (file) => {
    try {
      const response = await api.get(`/files/${file.id}`, {
        responseType: 'blob'
      });

      // Create blob URL and trigger download
      const blob = new Blob([response.data], { type: file.mime_type });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = file.original_filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      if (onFileDownloaded) {
        onFileDownloaded(file);
      }
    } catch (error) {
      console.error('Download failed:', error);
      alert('Download failed. Please try again.');
    }
  };

  const handleDeleteClick = (fileId) => {
    setShowDeleteConfirm(fileId);
  };

  const handleDeleteConfirm = async (fileId) => {
    setDeletingFileId(fileId);
    try {
      await api.delete(`/files/${fileId}`);
      if (onFileDeleted) {
        onFileDeleted(fileId);
      }
    } catch (error) {
      console.error('Delete failed:', error);
      alert('Delete failed. Please try again.');
    } finally {
      setDeletingFileId(null);
      setShowDeleteConfirm(null);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteConfirm(null);
  };

  if (!isAuthenticated) {
    return (
      <div className="file-list-container">
        <div className="file-list-unauthorized">
          <h3>Please log in to view files</h3>
          <p>You need to be authenticated to view your uploaded files.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="file-list-container">
        <div className="file-list-loading">
          <div className="loading-spinner"></div>
          <p>Loading files...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="file-list-container">
        <div className="file-list-error">
          <h3>Error loading files</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (files.length === 0) {
    return (
      <div className="file-list-container">
        <div className="file-list-empty">
          <div className="empty-icon">📁</div>
          <h3>No files uploaded yet</h3>
          <p>Upload your first CV file to get started.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="file-list-container">
      <div className="file-list-header">
        <h3>Your CV Files ({files.length})</h3>
      </div>

      <div className="file-list">
        {files.map((file) => (
          <div key={file.id} className="file-item">
            <div className="file-icon">
              {getFileTypeIcon(file.mime_type)}
            </div>
            
            <div className="file-info">
              <div className="file-name">{file.original_filename}</div>
              <div className="file-details">
                <span className="file-size">{formatFileSize(file.file_size)}</span>
                <span className="file-type">{getFileTypeLabel(file.mime_type)}</span>
                <span className="file-date">{formatDate(file.upload_date)}</span>
              </div>
            </div>

            <div className="file-actions">
              <button
                className="btn btn-download"
                onClick={() => handleDownload(file)}
                title="Download file"
              >
                Download
              </button>
              <button
                className="btn btn-delete"
                onClick={() => handleDeleteClick(file.id)}
                disabled={deletingFileId === file.id}
                title="Delete file"
              >
                {deletingFileId === file.id ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>Confirm Delete</h3>
            <p>Are you sure you want to delete this file? This action cannot be undone.</p>
            <div className="modal-actions">
              <button
                className="btn btn-secondary"
                onClick={handleDeleteCancel}
              >
                Cancel
              </button>
              <button
                className="btn btn-danger"
                onClick={() => handleDeleteConfirm(showDeleteConfirm)}
                disabled={deletingFileId === showDeleteConfirm}
              >
                {deletingFileId === showDeleteConfirm ? 'Deleting...' : 'Yes, Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileList;
