/**
 * User Profile Component
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { usersAPI, handleAPIError } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import { formatTurkishPhone, validateTurkishPhone } from '../utils/phoneMask';
import './UserProfile.css';

const UserProfile = () => {
  const { user, getCurrentUser, changePassword, logout } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [activeTab, setActiveTab] = useState('profile');
  const [profileData, setProfileData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
  });
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  // Load user data
  useEffect(() => {
    if (user) {
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone: user.phone || '',
      });
    }
  }, [user]);

  // Handle profile update
  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await usersAPI.updateUser(user.id, profileData);
      await getCurrentUser(); // Refresh user data
      setSuccess('Profile updated successfully');
    } catch (error) {
      setError(handleAPIError(error));
    } finally {
      setLoading(false);
    }
  };

  // Handle password change
  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    // Validate passwords match
    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('New passwords do not match');
      setLoading(false);
      return;
    }

    try {
      const result = await changePassword(
        passwordData.current_password,
        passwordData.new_password
      );

      if (result.success) {
        setSuccess('Password changed successfully');
        setPasswordData({
          current_password: '',
          new_password: '',
          confirm_password: '',
        });
      } else {
        setError(result.error);
      }
    } catch (error) {
      setError(handleAPIError(error));
    } finally {
      setLoading(false);
    }
  };

  // Handle input changes
  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePasswordChangeInput = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Clear messages
  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  if (!user) {
    return <LoadingSpinner message="Loading profile..." />;
  }

  return (
    <div className="user-profile-container">
      <div className="profile-header">
        <div className="profile-avatar">
          <span className="avatar-text">
            {user.first_name?.[0]}{user.last_name?.[0]}
          </span>
        </div>
        <div className="profile-info">
          <h1>{user.first_name} {user.last_name}</h1>
          <p className="profile-email">{user.email}</p>
          <span className={`role-badge role-${user.role?.name || 'user'}`}>
            {user.role?.name || 'User'}
          </span>
        </div>
      </div>

      <div className="profile-tabs">
        <button
          className={`tab-button ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          Profil
        </button>
        <button
          className={`tab-button ${activeTab === 'password' ? 'active' : ''}`}
          onClick={() => setActiveTab('password')}
        >
          Şifre
        </button>
        <button
          className={`tab-button ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          Ayarlar
        </button>
      </div>

      <div className="profile-content">
        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <form onSubmit={handleProfileUpdate} className="profile-form">
            <h2>Profil Bilgileri</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="first_name">Ad</label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={profileData.first_name}
                  onChange={handleProfileChange}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="last_name">Soyad</label>
                <input
                  type="text"
                  id="last_name"
                  name="last_name"
                  value={profileData.last_name}
                  onChange={handleProfileChange}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="email">E-posta Adresi</label>
              <input
                type="email"
                id="email"
                name="email"
                value={profileData.email}
                onChange={handleProfileChange}
                required
                disabled
              />
              <small>E-posta değiştirilemez</small>
            </div>

            <div className="form-group">
              <label htmlFor="phone">Telefon Numarası</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={profileData.phone}
                onChange={(e) => {
                  const formatted = formatTurkishPhone(e.target.value);
                  setProfileData(prev => ({
                    ...prev,
                    phone: formatted
                  }));
                }}
                placeholder="0XXX XXX XX XX"
                maxLength="15"
              />
              {profileData.phone && !validateTurkishPhone(profileData.phone) && (
                <small className="error-text">
                  Lütfen geçerli bir Türk telefon numarası girin (0XXX XXX XX XX)
                </small>
              )}
            </div>

            <button
              type="submit"
              className="submit-button"
              disabled={loading}
            >
              {loading ? 'Güncelleniyor...' : 'Profili Güncelle'}
            </button>
          </form>
        )}

        {/* Password Tab */}
        {activeTab === 'password' && (
          <form onSubmit={handlePasswordChange} className="password-form">
            <h2>Şifre Değiştir</h2>
            
            <div className="form-group">
              <label htmlFor="current_password">Mevcut Şifre</label>
              <input
                type="password"
                id="current_password"
                name="current_password"
                value={passwordData.current_password}
                onChange={handlePasswordChangeInput}
                required
                placeholder="Mevcut şifrenizi girin"
              />
            </div>

            <div className="form-group">
              <label htmlFor="new_password">Yeni Şifre</label>
              <input
                type="password"
                id="new_password"
                name="new_password"
                value={passwordData.new_password}
                onChange={handlePasswordChangeInput}
                required
                placeholder="Enter new password"
                minLength="8"
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirm_password">Confirm New Password</label>
              <input
                type="password"
                id="confirm_password"
                name="confirm_password"
                value={passwordData.confirm_password}
                onChange={handlePasswordChangeInput}
                required
                placeholder="Confirm new password"
                minLength="8"
              />
            </div>

            <button
              type="submit"
              className="submit-button"
              disabled={loading}
            >
              {loading ? 'Changing...' : 'Change Password'}
            </button>
          </form>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="settings-form">
            <h2>Account Settings</h2>
            
            <div className="setting-item">
              <div className="setting-info">
                <h3>Account Status</h3>
                <p>Your account is {user.is_active ? 'active' : 'inactive'}</p>
              </div>
              <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                {user.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <h3>Role</h3>
                <p>{user.role?.description || 'No role assigned'}</p>
              </div>
              <span className="role-badge">
                {user.role?.name || 'User'}
              </span>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <h3>Member Since</h3>
                <p>{new Date(user.created_at).toLocaleDateString()}</p>
              </div>
            </div>

            <div className="setting-actions">
              <button
                className="danger-button"
                onClick={() => {
                  if (window.confirm('Are you sure you want to logout from all devices?')) {
                    logout();
                  }
                }}
              >
                Logout All Devices
              </button>
            </div>
          </div>
        )}

        {/* Messages */}
        {error && (
          <div className="message error" onClick={clearMessages}>
            <span className="message-icon">⚠️</span>
            {error}
          </div>
        )}

        {success && (
          <div className="message success" onClick={clearMessages}>
            <span className="message-icon">✅</span>
            {success}
          </div>
        )}
      </div>
    </div>
  );
};

export default UserProfile;



