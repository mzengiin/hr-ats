/**
 * API Service with token management
 */
import axios from 'axios';

// Create axios instance - CORS sorununu önlemek için güncellendi
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8001/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // CORS için gerekli
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Check if error is 401 and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // Attempt to refresh the token
        const response = await axios.post(
          `${process.env.REACT_APP_API_URL || 'http://localhost:8001/api/v1'}/auth/refresh`,
          { refresh_token: refreshToken },
          { timeout: 5000 }
        );

        const { access_token } = response.data;

        // Update the token in localStorage
        localStorage.setItem('access_token', access_token);

        // Update the original request with new token
        originalRequest.headers.Authorization = `Bearer ${access_token}`;

        // Retry the original request
        return api(originalRequest);
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        
        // Clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
        
        // Redirect to login page
        window.location.href = '/login';
        
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// API methods
export const authAPI = {
  // Login
  login: (email, password) => 
    api.post('/auth/login', { email, password }),

  // Logout
  logout: (refreshToken) => 
    api.post('/auth/logout', { refresh_token: refreshToken }),

  // Refresh token
  refreshToken: (refreshToken) => 
    api.post('/auth/refresh', { refresh_token: refreshToken }),

  // Get current user
  getCurrentUser: () => 
    api.get('/auth/me'),

  // Change password
  changePassword: (currentPassword, newPassword) => 
    api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    }),

  // Logout all devices
  logoutAllDevices: () => 
    api.post('/auth/logout-all'),

  // Validate token
  validateToken: () => 
    api.get('/auth/validate'),
};

export const usersAPI = {
  // Get users list
  getUsers: (params = {}) => 
    api.get('/users/', { params }),

  // Get user by ID
  getUser: (id) => 
    api.get(`/users/${id}`),

  // Create user
  createUser: (userData) => 
    api.post('/users/', userData),

  // Update user
  updateUser: (id, userData) => 
    api.put(`/users/${id}`, userData),

  // Delete user
  deleteUser: (id) => 
    api.delete(`/users/${id}`),

  // Activate user
  activateUser: (id) => 
    api.patch(`/users/${id}/activate`),

  // Deactivate user
  deactivateUser: (id) => 
    api.patch(`/users/${id}/deactivate`),

  // Search users
  searchUsers: (searchTerm, limit = 10) => 
    api.get(`/users/search/${searchTerm}`, { params: { limit } }),

  // Get user stats
  getUserStats: () => 
    api.get('/users/stats/overview/'),
};

export const dashboardAPI = {
  // Get dashboard statistics
  getStatistics: () => 
    api.get('/dashboard/statistics'),

  // Get candidate status distribution
  getCandidateStatusDistribution: () => 
    api.get('/dashboard/candidate-status-distribution'),

  // Get position application volume
  getPositionApplicationVolume: () => 
    api.get('/dashboard/position-application-volume'),

  // Get upcoming interviews
  getUpcomingInterviews: () => 
    api.get('/dashboard/upcoming-interviews'),

  // Get all dashboard data
  getDashboardData: () => 
    api.get('/dashboard/dashboard-data'),
};

export const candidatesAPI = {
  // Get candidates list with pagination and filters
  getCandidates: (params = {}) => 
    api.get('/candidates', { params }),

  // Get candidate by ID
  getCandidate: (id) => 
    api.get(`/candidates/${id}`),

  // Create new candidate
  createCandidate: (formData) => 
    api.post('/candidates/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),

  // Update candidate
  updateCandidate: (id, formData) => 
    api.put(`/candidates/${id}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),

  // Delete candidate
  deleteCandidate: (id) => 
    api.delete(`/candidates/${id}`),

  // Get all options
  getOptions: () => 
    api.get('/candidates/candidates-options'),

  // Get candidate interviews
  getCandidateInterviews: (candidateId) => 
    api.get(`/candidates/candidates/${candidateId}/interviews`),

  // Get candidate case studies
  getCandidateCaseStudies: (candidateId) => 
    api.get(`/candidates/candidates/${candidateId}/case-studies`),

  // Download candidate CV
  downloadCandidateCv: (candidateId) => 
    api.get(`/candidates/${candidateId}/cv/download`, {
      responseType: 'blob'
    }),

  // View candidate CV
  viewCandidateCv: (candidateId) => 
    api.get(`/candidates/${candidateId}/cv/view`, {
      responseType: 'blob'
    }),

  // Delete candidate CV
  deleteCandidateCv: (candidateId) => 
    api.delete(`/candidates/${candidateId}/cv`),
};

// Error handler
export const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        if (Array.isArray(data.detail)) {
          return data.detail.map(err => err.msg || err.message || JSON.stringify(err)).join(', ');
        }
        return data.detail || 'Bad request';
      case 401:
        return 'Unauthorized. Please login again.';
      case 403:
        return 'Access denied. You don\'t have permission to perform this action.';
      case 404:
        return 'Resource not found';
      case 409:
        if (Array.isArray(data.detail)) {
          return data.detail.map(err => err.msg || err.message || JSON.stringify(err)).join(', ');
        }
        return data.detail || 'Conflict. Resource already exists.';
      case 422:
        if (Array.isArray(data.detail)) {
          return data.detail.map(err => err.msg || err.message || JSON.stringify(err)).join(', ');
        }
        return data.detail || 'Validation error';
      case 429:
        return 'Too many requests. Please try again later.';
      case 500:
        return 'Internal server error. Please try again later.';
      default:
        if (Array.isArray(data.detail)) {
          return data.detail.map(err => err.msg || err.message || JSON.stringify(err)).join(', ');
        }
        return data.detail || `Error ${status}`;
    }
  } else if (error.request) {
    // Network error
    return 'Network error. Please check your connection.';
  } else {
    // Other error
    return error.message || 'An unexpected error occurred';
  }
};

// Request timeout handler
export const withTimeout = (promise, timeoutMs = 10000) => {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Request timeout')), timeoutMs)
    )
  ]);
};

export default api;


