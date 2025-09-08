/**
 * Login Form Component with validation
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { validateEmail, validatePassword } from '../utils/validation';
import './LoginForm.css';

const LoginForm = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login, error, clearError, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const from = location.state?.from?.pathname || '/dashboard';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, location]);

  // Clear errors when component mounts
  useEffect(() => {
    clearError();
  }, [clearError]);

  // Handle input change
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};

    // Validate email
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Validate password
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (!validatePassword(formData.password)) {
      newErrors.password = 'Password must be at least 8 characters long';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    clearError();

    try {
      const result = await login(formData.email, formData.password);
      
      if (result.success) {
        const from = location.state?.from?.pathname || '/dashboard';
        navigate(from, { replace: true });
      }
    } catch (error) {
      console.error('Login error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle demo login
  const handleDemoLogin = () => {
    setFormData({
      email: 'demo@example.com',
      password: 'demo123456'
    });
  };

  return (
    <div className="login-form-container">
      <div className="login-form-card">
        <div className="login-form-header">
          <h1>Tekrar Hoş Geldiniz</h1>
          <p>Hesabınıza giriş yapın</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {/* Email Field */}
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              E-posta Adresi
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={`form-input ${errors.email ? 'error' : ''}`}
              placeholder="E-posta adresinizi girin"
              disabled={isSubmitting}
              autoComplete="email"
            />
            {errors.email && (
              <span className="error-message">{errors.email}</span>
            )}
          </div>

          {/* Password Field */}
          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Şifre
            </label>
            <div className="password-input-container">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className={`form-input ${errors.password ? 'error' : ''}`}
                placeholder="Şifrenizi girin"
                disabled={isSubmitting}
                autoComplete="current-password"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                disabled={isSubmitting}
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
            {errors.password && (
              <span className="error-message">{errors.password}</span>
            )}
          </div>

          {/* Remember Me & Forgot Password */}
          <div className="form-options">
            <label className="checkbox-container">
              <input
                type="checkbox"
                name="rememberMe"
                disabled={isSubmitting}
              />
              <span className="checkmark"></span>
              Beni hatırla
            </label>
            <a href="/forgot-password" className="forgot-password">
              Şifremi unuttum?
            </a>
          </div>

          {/* Error Message */}
          {error && (
            <div className="error-banner">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            className={`submit-button ${isSubmitting ? 'loading' : ''}`}
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <span className="spinner"></span>
                Giriş yapılıyor...
              </>
            ) : (
              'Giriş Yap'
            )}
          </button>

          {/* Demo Login Button */}
          <button
            type="button"
            className="demo-button"
            onClick={handleDemoLogin}
            disabled={isSubmitting}
          >
            Demo Hesabı Dene
          </button>
        </form>

        {/* Sign Up Link */}
        <div className="signup-link">
          <p>
            Don't have an account?{' '}
            <a href="/register" className="signup-link-text">
              Sign up here
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;



