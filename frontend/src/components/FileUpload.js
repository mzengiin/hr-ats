import React, { useState, useCallback, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import './FileUpload.css';

const FileUpload = ({ onUploadSuccess, onUploadError }) => {
  const { user, isAuthenticated } = useAuth();
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [errors, setErrors] = useState([]);
  const fileInputRef = useRef(null);

  // Supported file types and max size
  const SUPPORTED_TYPES = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
  const MAX_FILES = 50;

  const validateFile = (file) => {
    const errors = [];

    // Check file type
    if (!SUPPORTED_TYPES.includes(file.type)) {
      errors.push(`${file.name}: Unsupported file type. Supported formats: PDF, DOC, DOCX`);
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      errors.push(`${file.name}: File too large. Maximum size is 10MB`);
    }

    // Check if file is empty
    if (file.size === 0) {
      errors.push(`${file.name}: Empty file not allowed`);
    }

    return errors;
  };

  const handleFiles = useCallback((newFiles) => {
    const fileArray = Array.from(newFiles);
    const allErrors = [];
    const validFiles = [];

    // Check total file count
    if (files.length + fileArray.length > MAX_FILES) {
      allErrors.push(`Maximum ${MAX_FILES} files allowed`);
      setErrors(allErrors);
      return;
    }

    // Validate each file
    fileArray.forEach(file => {
      const fileErrors = validateFile(file);
      if (fileErrors.length === 0) {
        validFiles.push({
          file,
          id: Date.now() + Math.random(),
          name: file.name,
          size: file.size,
          type: file.type,
          status: 'ready'
        });
      } else {
        allErrors.push(...fileErrors);
      }
    });

    if (allErrors.length > 0) {
      setErrors(allErrors);
    } else {
      setErrors([]);
    }

    setFiles(prev => [...prev, ...validFiles]);
  }, [files.length]);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  }, [handleFiles]);

  const handleFileInput = useCallback((e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  }, [handleFiles]);

  const removeFile = useCallback((fileId) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
  }, []);

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

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setErrors([]);

    try {
      const formData = new FormData();
      files.forEach(fileObj => {
        formData.append('files', fileObj.file);
      });

      const response = await api.post('/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setFiles([]);
      if (onUploadSuccess) {
        onUploadSuccess(response.data);
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Upload failed';
      setErrors([errorMessage]);
      if (onUploadError) {
        onUploadError(error);
      }
    } finally {
      setUploading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="file-upload-container">
        <div className="file-upload-unauthorized">
          <h3>Please log in to upload files</h3>
          <p>You need to be authenticated to upload CV files.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="file-upload-container">
      <div className="file-upload-header">
        <h3>CV Dosyalarını Yükle</h3>
        <p>PDF, DOC veya DOCX formatında CV dosyalarınızı yükleyin</p>
      </div>

      <div
        className={`file-upload-dropzone ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="file-upload-content">
          <div className="file-upload-icon">📁</div>
          <p className="file-upload-text">
            {dragActive ? 'Dosyaları buraya bırakın' : 'Dosyaları buraya sürükleyin'}
          </p>
          <p className="file-upload-subtext">veya dosya seçmek için tıklayın</p>
          <div className="file-upload-info">
            <p>Desteklenen formatlar: PDF, DOC, DOCX</p>
            <p>Maksimum dosya boyutu: 10MB</p>
            <p>Maksimum dosya sayısı: {MAX_FILES}</p>
          </div>
        </div>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,.doc,.docx"
        onChange={handleFileInput}
        className="file-upload-input"
        aria-label="file input"
      />

      {errors.length > 0 && (
        <div className="file-upload-errors">
          <div className="error-header">
            <span className="error-icon">⚠️</span>
            <span className="error-title">Upload Errors</span>
          </div>
          {errors.map((error, index) => (
            <div key={index} className="error-message">
              <span className="error-bullet">•</span>
              {error}
            </div>
          ))}
        </div>
      )}

      {files.length > 0 && (
        <div className="file-upload-list">
          <h4>Selected Files ({files.length})</h4>
          <div className="file-list">
            {files.map((fileObj) => (
              <div key={fileObj.id} className="file-item">
                <div className="file-info">
                  <span className="file-name">{fileObj.name}</span>
                  <span className="file-size">{formatFileSize(fileObj.size)}</span>
                  <span className="file-type">{getFileTypeLabel(fileObj.type)}</span>
                </div>
                <button
                  type="button"
                  className="file-remove"
                  onClick={() => removeFile(fileObj.id)}
                  disabled={uploading}
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
          <div className="file-upload-actions">
            <button
              type="button"
              className="btn btn-primary"
              onClick={uploadFiles}
              disabled={uploading || files.length === 0}
            >
              {uploading ? 'Uploading...' : `Upload ${files.length} File${files.length !== 1 ? 's' : ''}`}
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setFiles([])}
              disabled={uploading}
            >
              Clear All
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
