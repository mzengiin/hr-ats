/**
 * User Form Component for creating and editing users
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api, { usersAPI, handleAPIError } from '../services/api';
import RoleSelector from './RoleSelector';
import { validateEmail, validatePassword, validateRequired } from '../utils/validation';
import './UserForm.css';

const UserForm = ({ mode = 'create', user = null, onSuccess, onCancel }) => {
  const { user: currentUser } = useAuth();
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirm_password: '',
    role_id: '',
    is_active: true
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [availableRoles, setAvailableRoles] = useState([]);

  // Available roles
  // Available roles - will be loaded from API
  const [roles, setRoles] = useState([]);

  // Load roles from API
  useEffect(() => {
    const loadRoles = async () => {
      console.log('Loading roles from API...');
      try {
        const response = await api.get('/roles/');
        console.log('Roles API response:', response.data);
        setRoles(response.data);
        setAvailableRoles(response.data);
      } catch (error) {
        console.error('Error loading roles:', error);
        // Fallback to hardcoded roles if API fails
        const fallbackRoles = [
          { id: '1486f8d4-ea3e-40c9-a754-80e9d8e088d8', name: 'hr_manager', description: 'HR Manager' },
          { id: 'c2207ec4-b4a6-4895-9b59-ef0467602ea7', name: 'admin', description: 'Administrator role' }
        ];
        console.log('Using fallback roles:', fallbackRoles);
        setRoles(fallbackRoles);
        setAvailableRoles(fallbackRoles);
      }
    };
    
    loadRoles();
  }, []);

  // Initialize form data
  useEffect(() => {
    if (mode === 'edit' && user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        password: '',
        confirm_password: '',
        role_id: user.role?.id || '',
        is_active: user.is_active !== undefined ? user.is_active : true
      });
    } else if (roles.length > 0) {
      // Set default role for new users (first available role)
      setFormData(prev => ({
        ...prev,
        role_id: roles[0].id
      }));
    }
  }, [mode, user, roles]);

  // Handle input change
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  // Handle role selection
  const handleRoleChange = (roleId) => {
    setFormData(prev => ({
      ...prev,
      role_id: roleId
    }));

    if (errors.role_id) {
      setErrors(prev => ({
        ...prev,
        role_id: ''
      }));
    }
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};

    // Validate first name
    if (!validateRequired(formData.first_name)) {
      newErrors.first_name = 'First name is required';
    }

    // Validate last name
    if (!validateRequired(formData.last_name)) {
      newErrors.last_name = 'Last name is required';
    }

    // Validate email
    if (!validateRequired(formData.email)) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Validate password (only for create mode or if password is provided)
    if (mode === 'create' || formData.password) {
      if (!validateRequired(formData.password)) {
        newErrors.password = 'Password is required';
      } else if (!validatePassword(formData.password)) {
        newErrors.password = 'Password must be at least 8 characters long';
      }

      // Validate password confirmation
      if (formData.password !== formData.confirm_password) {
        newErrors.confirm_password = 'Passwords do not match';
      }
    }

    // Validate role
    if (!validateRequired(formData.role_id)) {
      newErrors.role_id = 'Please select a role';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    console.log('Form data being submitted:', formData);
    console.log('Available roles:', roles);
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const userData = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        role_id: formData.role_id,
        is_active: formData.is_active
      };

      // Only include password if provided
      if (formData.password) {
        userData.password = formData.password;
      }

      if (mode === 'create') {
        await usersAPI.createUser(userData);
      } else {
        await usersAPI.updateUser(user.id, userData);
      }

      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      const errorMessage = handleAPIError(error);
      setErrors({ submit: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  // Handle cancel
  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
  };

  return (
    <div className="user-form-container">
      <div className="user-form-header">
        <h2>{mode === 'create' ? 'Yeni Kullanıcı Oluştur' : 'Kullanıcıyı Düzenle'}</h2>
        <button
          type="button"
          className="close-button"
          onClick={handleCancel}
        >
          ✕
        </button>
      </div>

      <form onSubmit={handleSubmit} className="user-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="first_name" className="form-label">
              Ad *
            </label>
            <input
              type="text"
              id="first_name"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              className={`form-input ${errors.first_name ? 'error' : ''}`}
              placeholder="Adı girin"
              disabled={loading}
            />
            {errors.first_name && (
              <span className="error-message">{errors.first_name}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="last_name" className="form-label">
              Soyad *
            </label>
            <input
              type="text"
              id="last_name"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              className={`form-input ${errors.last_name ? 'error' : ''}`}
              placeholder="Soyadı girin"
              disabled={loading}
            />
            {errors.last_name && (
              <span className="error-message">{errors.last_name}</span>
            )}
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="email" className="form-label">
            Email Address *
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className={`form-input ${errors.email ? 'error' : ''}`}
            placeholder="Enter email address"
            disabled={loading || mode === 'edit'}
          />
          {mode === 'edit' && (
            <small className="form-help">Email cannot be changed</small>
          )}
          {errors.email && (
            <span className="error-message">{errors.email}</span>
          )}
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password {mode === 'create' ? '*' : '(leave blank to keep current)'}
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={`form-input ${errors.password ? 'error' : ''}`}
              placeholder={mode === 'create' ? 'Enter password' : 'Enter new password'}
              disabled={loading}
            />
            {errors.password && (
              <span className="error-message">{errors.password}</span>
            )}
          </div>

          {mode === 'create' && (
            <div className="form-group">
              <label htmlFor="confirm_password" className="form-label">
                Confirm Password *
              </label>
              <input
                type="password"
                id="confirm_password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleChange}
                className={`form-input ${errors.confirm_password ? 'error' : ''}`}
                placeholder="Confirm password"
                disabled={loading}
              />
              {errors.confirm_password && (
                <span className="error-message">{errors.confirm_password}</span>
              )}
            </div>
          )}
        </div>

        <div className="form-group">
          <label className="form-label">
            Role *
          </label>
          <RoleSelector
            roles={availableRoles}
            value={formData.role_id}
            onChange={handleRoleChange}
            disabled={loading}
          />
          {errors.role_id && (
            <span className="error-message">{errors.role_id}</span>
          )}
        </div>

        <div className="form-group">
          <label className="checkbox-container">
            <input
              type="checkbox"
              name="is_active"
              checked={formData.is_active}
              onChange={handleChange}
              disabled={loading}
            />
            <span className="checkmark"></span>
            Active User
          </label>
          <small className="form-help">
            Inactive users cannot log in to the system
          </small>
        </div>

        {/* Submit Error */}
        {errors.submit && (
          <div className="error-banner">
            <span className="error-icon">⚠️</span>
            {errors.submit}
          </div>
        )}

        {/* Form Actions */}
        <div className="form-actions">
          <button
            type="button"
            className="cancel-button"
            onClick={handleCancel}
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className={`submit-button ${loading ? 'loading' : ''}`}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                {mode === 'create' ? 'Creating...' : 'Updating...'}
              </>
            ) : (
              mode === 'create' ? 'Create User' : 'Update User'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default UserForm;


