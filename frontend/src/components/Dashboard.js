import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import UserList from './UserList';
import UserProfile from './UserProfile';
import FileUpload from './FileUpload';
import FileList from './FileList';
import api from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('files');

  // Load files on component mount
  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/files/');
      setFiles(response.data.files || []);
    } catch (err) {
      setError('Dosyalar yüklenemedi');
      console.error('Error loading files:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = (uploadData) => {
    console.log('Upload successful:', uploadData);
    // Reload files after successful upload
    loadFiles();
  };

  const handleUploadError = (error) => {
    console.error('Upload error:', error);
  };

  const handleFileDeleted = (fileId) => {
    // Remove file from local state
    setFiles(prevFiles => prevFiles.filter(file => file.id !== fileId));
  };

  const handleFileDownloaded = (file) => {
    console.log('File downloaded:', file);
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="dashboard-title">
          <h1>CVFlow Kontrol Paneli</h1>
          <p>Tekrar hoş geldiniz, {user?.email || 'Kullanıcı'}!</p>
        </div>
        <div className="dashboard-actions">
          <button onClick={logout} className="logout-button">
            Çıkış Yap
          </button>
        </div>
      </header>

      <nav className="dashboard-nav">
        <button 
          className={`nav-button ${activeTab === 'files' ? 'active' : ''}`}
          onClick={() => setActiveTab('files')}
        >
          CV Dosyaları
        </button>
        <button 
          className={`nav-button ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          Kullanıcı Yönetimi
        </button>
        <button 
          className={`nav-button ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          Profil Ayarları
        </button>
      </nav>

      <main className="dashboard-content">
        {activeTab === 'files' && (
          <div className="files-section">
            <div className="file-upload-section">
              <FileUpload 
                onUploadSuccess={handleUploadSuccess}
                onUploadError={handleUploadError}
              />
            </div>
            <div className="file-list-section">
              <FileList 
                files={files}
                loading={loading}
                error={error}
                onFileDeleted={handleFileDeleted}
                onFileDownloaded={handleFileDownloaded}
              />
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="dashboard-card">
            <h2>User Management</h2>
            <UserList />
          </div>
        )}
        
        {activeTab === 'profile' && (
          <div className="dashboard-card">
            <h2>Profile Settings</h2>
            <UserProfile />
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;

