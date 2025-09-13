/**
 * Final Login Form Component - No Page Refresh
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const LoginFormFinal = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loginError, setLoginError] = useState('');

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
    setLoginError('');
  }, [clearError]);

  // Handle input change
  const handleChange = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
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

    // Clear login error
    if (loginError) {
      setLoginError('');
    }
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = 'E-posta adresi gereklidir';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Lütfen geçerli bir e-posta adresi girin';
    }

    if (!formData.password) {
      newErrors.password = 'Şifre gereklidir';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Şifre en az 6 karakter olmalıdır';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission - CRITICAL FIX
  const handleSubmit = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('🔐 Form submit prevented, starting validation...');

    if (!validateForm()) {
      console.log('❌ Validation failed');
      return false;
    }

    console.log('✅ Validation passed, starting login process...');
    
    setIsSubmitting(true);
    setLoginError('');
    clearError();

    // Use setTimeout to prevent page refresh
    setTimeout(async () => {
      try {
        console.log('🔐 Login attempt started:', { email: formData.email });
        
        const result = await login(formData.email, formData.password);
        
        console.log('🔐 Login result:', result);
        
        if (result && result.success) {
          console.log('✅ Login successful, navigating to dashboard');
          const from = location.state?.from?.pathname || '/dashboard';
          navigate(from, { replace: true });
        } else {
          console.log('❌ Login failed, result:', result);
          setLoginError('Kullanıcı adı veya şifre hatalı. Lütfen tekrar deneyin.');
        }
      } catch (error) {
        console.error('❌ Login error:', error);
        setLoginError('Kullanıcı adı veya şifre hatalı. Lütfen tekrar deneyin.');
      } finally {
        setIsSubmitting(false);
      }
    }, 100);

    return false;
  };

  // Handle demo login
  const handleDemoLogin = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('🎮 Demo login clicked');
    setFormData({
      email: 'demo@example.com',
      password: 'demo123'
    });
    
    return false;
  };

  // Get error message to display
  const getErrorMessage = () => {
    if (loginError) return loginError;
    if (error) {
      if (error.includes('Invalid credentials') || 
          error.includes('Unauthorized') || 
          error.includes('401') || 
          error.includes('incorrect')) {
        return 'Kullanıcı adı veya şifre hatalı. Lütfen tekrar deneyin.';
      }
      return error;
    }
    return null;
  };

  const errorMessage = getErrorMessage();

  return (
    <div className="bg-gray-50 min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8" style={{fontFamily: 'Plus Jakarta Sans, Noto Sans, sans-serif'}}>
      <div className="max-w-md w-full">
        {/* Single White Frame - Logo, Title and Form */}
        <div className="bg-white rounded-lg p-8 shadow-lg">
          {/* Logo and Title */}
          <div className="text-center mb-8">
            <img 
              src="/logo.png" 
              alt="IK-ATS Logo" 
              className="mx-auto h-16 w-auto"
            />
            <h2 className="mt-6 text-3xl font-bold tracking-tight text-gray-900">IK-ATS'e Hoş Geldiniz</h2>
            <p className="mt-2 text-sm text-gray-600">Lütfen hesabınıza giriş yapın</p>
          </div>

          {/* Error Banner */}
          {errorMessage && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-4 flex items-center">
              <span className="text-red-400 mr-2">
                <span className="material-symbols-outlined text-lg">error</span>
              </span>
              <span className="text-red-700 text-sm font-medium">
                {errorMessage}
              </span>
            </div>
          )}

          {/* Debug Info */}
          <div className="mb-4 bg-blue-50 border border-blue-200 rounded-md p-2 text-xs text-blue-700">
            <strong>Debug:</strong> Form submission test - Sayfa yenilenmemeli
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                E-posta Adresi
              </label>
              <div className="mt-1">
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className={`appearance-none block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    errors.email ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="E-posta adresinizi girin"
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600">{errors.email}</p>
                )}
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Şifre
              </label>
              <div className="mt-1 relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className={`appearance-none block w-full px-3 py-2 pr-10 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    errors.password ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Şifrenizi girin"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setShowPassword(!showPassword);
                  }}
                >
                  <span className="material-symbols-outlined text-gray-400 hover:text-gray-600">
                    {showPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
                {errors.password && (
                  <p className="mt-1 text-sm text-red-600">{errors.password}</p>
                )}
              </div>
            </div>

            {/* Remember Me and Forgot Password */}
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
                  Beni hatırla
                </label>
              </div>

              <div className="text-sm">
                <a href="#" className="font-medium text-blue-600 hover:text-blue-500">
                  Şifremi Unuttum
                </a>
              </div>
            </div>

            {/* Submit Button */}
            <div>
              <button
                type="submit"
                disabled={isSubmitting}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  handleSubmit(e);
                }}
              >
                {isSubmitting ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Giriş yapılıyor...
                  </span>
                ) : (
                  'Giriş Yap'
                )}
              </button>
            </div>

            {/* Demo Login Button */}
            <div>
              <button
                type="button"
                onClick={handleDemoLogin}
                className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Demo Hesabı Dene
              </button>
            </div>
          </form>

          {/* Register Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Hesabınız yok mu?{' '}
              <a href="#" className="font-medium text-blue-600 hover:text-blue-500">
                Kayıt olun
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginFormFinal;
