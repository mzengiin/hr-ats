import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import UserList from './UserList';
import UserProfile from './UserProfile';
import FileUpload from './FileUpload';
import FileList from './FileList';
import CandidateCard from './CandidateCard';
import api from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [files, setFiles] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  // Mock data for demonstration
  const mockCandidates = [
    {
      id: 1,
      name: "Zeynep Kaya",
      position: "Senior Backend Developer",
      skills: ["Python", "Django"],
      stage: "pre-screening",
      avatar: "ZK"
    },
    {
      id: 2,
      name: "Caner Öztürk",
      position: "Senior Frontend Developer", 
      skills: ["React Native", "Mobile"],
      stage: "pre-screening",
      avatar: "CÖ"
    },
    {
      id: 3,
      name: "Ahmet Demir",
      position: "Senior Frontend Developer",
      skills: ["React", "Node.js"],
      stage: "technical",
      avatar: "AD"
    },
    {
      id: 4,
      name: "Mehmet Yılmaz",
      position: "Senior Backend Developer",
      skills: ["Java", "Spring"],
      stage: "hr",
      avatar: "MY"
    }
  ];

  const stages = [
    { key: 'pre-screening', name: 'Ön Eleme', count: 2 },
    { key: 'technical', name: 'Teknik', count: 1 },
    { key: 'hr', name: 'İK', count: 1 },
    { key: 'reference', name: 'Referans', count: 0 }
  ];

  // Load files on component mount
  useEffect(() => {
    loadFiles();
    setCandidates(mockCandidates);
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
    loadFiles();
  };

  const handleUploadError = (error) => {
    console.error('Upload error:', error);
  };

  const handleFileDeleted = (fileId) => {
    setFiles(prevFiles => prevFiles.filter(file => file.id !== fileId));
  };

  const handleFileDownloaded = (file) => {
    console.log('File downloaded:', file);
  };

  const handleCandidateClick = (candidate) => {
    setSelectedCandidate(candidate);
  };

  const getCandidatesByStage = (stage) => {
    return candidates.filter(candidate => candidate.stage === stage);
  };

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <div className="logo">
            <h1>CVFlow ATS</h1>
          </div>
        </div>
        <div className="header-right">
          <button className="btn-primary">
            Yeni Pozisyon
          </button>
          <div className="user-menu">
            <span className="user-role">İK</span>
            <div className="user-avatar">
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </div>
            <button onClick={logout} className="logout-btn">
              Çıkış
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="dashboard-main">
        {activeTab === 'overview' && (
          <>
            {/* Overview Section */}
            <section className="overview-section">
              <h2>Genel Bakış</h2>
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-icon">💼</div>
                  <div className="stat-content">
                    <h3>4</h3>
                    <p>Açık Pozisyonlar</p>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">👥</div>
                  <div className="stat-content">
                    <h3>5</h3>
                    <p>Pipeline'daki Adaylar</p>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">⏱️</div>
                  <div className="stat-content">
                    <h3>42</h3>
                    <p>Ort. İşe Alım Süresi (Gün)</p>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">✅</div>
                  <div className="stat-content">
                    <h3>5</h3>
                    <p>Bu Ay İşe Alınan</p>
                  </div>
                </div>
              </div>
            </section>

            {/* Recruitment Flow */}
            <section className="recruitment-flow">
              <h2>İşe Alım Akışı</h2>
              <div className="kanban-board">
                {stages.map(stage => (
                  <div key={stage.key} className="kanban-column">
                    <div className="column-header">
                      <h3>{stage.name}</h3>
                      <span className="candidate-count">{stage.count}</span>
                    </div>
                    <div className="candidates-list">
                      {getCandidatesByStage(stage.key).map(candidate => (
                        <CandidateCard
                          key={candidate.id}
                          candidate={candidate}
                          onClick={() => handleCandidateClick(candidate)}
                        />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </>
        )}

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
            <h2>Kullanıcı Yönetimi</h2>
            <UserList />
          </div>
        )}
        
        {activeTab === 'profile' && (
          <div className="dashboard-card">
            <h2>Profil Ayarları</h2>
            <UserProfile />
          </div>
        )}
      </main>

      {/* Navigation */}
      <nav className="dashboard-nav">
        <button 
          className={`nav-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Genel Bakış
        </button>
        <button 
          className={`nav-button ${activeTab === 'files' ? 'active' : ''}`}
          onClick={() => setActiveTab('files')}
        >
          📄 CV Dosyaları
        </button>
        <button 
          className={`nav-button ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          👥 Kullanıcı Yönetimi
        </button>
        <button 
          className={`nav-button ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          ⚙️ Profil Ayarları
        </button>
      </nav>

      {/* Candidate Detail Modal */}
      {selectedCandidate && (
        <div className="modal-overlay" onClick={() => setSelectedCandidate(null)}>
          <div className="candidate-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="candidate-info">
                <div className="candidate-avatar">{selectedCandidate.avatar}</div>
                <div>
                  <h2>{selectedCandidate.name}</h2>
                  <p>Başvurulan Pozisyon: {selectedCandidate.position}</p>
                  <div className="skills">
                    {selectedCandidate.skills.map((skill, index) => (
                      <span key={index} className="skill-tag">{skill}</span>
                    ))}
                  </div>
                </div>
              </div>
              <button 
                className="close-btn"
                onClick={() => setSelectedCandidate(null)}
              >
                ✕
              </button>
            </div>
            <div className="modal-content">
              <div className="cv-preview">
                <h3>CV Önizleme</h3>
                <div className="pdf-placeholder">
                  <p>PDF Görüntüleyici</p>
                  <p>CV_{selectedCandidate.name.replace(' ', '_')}_v2.pdf</p>
                  <a href="#" className="open-link">Yeni sekmede aç ↗</a>
                </div>
              </div>
              <div className="notes-section">
                <h3>Notlar</h3>
                <button className="add-note-btn">+ Not Ekle</button>
                <div className="notes-list">
                  <div className="note">
                    <div className="note-header">
                      <span className="note-author">Ayşe Yılmaz</span>
                      <span className="note-date">2024-07-29 14:30</span>
                    </div>
                    <p>Teknik mülakat çok başarılı geçti. Adayın problem çözme yeteneği üst düzeyde.</p>
                  </div>
                  <div className="note">
                    <div className="note-header">
                      <span className="note-author">Ali Kaya</span>
                      <span className="note-date">2024-07-25 11:00</span>
                    </div>
                    <p>İK görüşmesinde kültür uyumu pozitif olarak değerlendirildi. Ekip çalışmasına yatkın.</p>
                  </div>
                </div>
              </div>
              <div className="files-section">
                <h3>Dosyalar</h3>
                <div className="files-list">
                  <div className="file-item">
                    <span>CV_{selectedCandidate.name.replace(' ', '_')}_v2.pdf (v2)</span>
                    <a href="#" className="file-link">↗</a>
                  </div>
                  <div className="file-item">
                    <span>CoverLetter.pdf (v1)</span>
                    <a href="#" className="file-link">↗</a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;

