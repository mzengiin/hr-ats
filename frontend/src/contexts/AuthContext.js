/**
 * Authentication Context for managing user authentication state
 */
import React, { createContext, useContext, useReducer, useEffect, useCallback, useMemo } from 'react';
import api from '../services/api';

// Initial state
const initialState = {
  user: null,
  accessToken: null,
  refreshToken: null,
  loading: false,
  error: null,
  isAuthenticated: false,
};

// Action types
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  REFRESH_TOKEN_SUCCESS: 'REFRESH_TOKEN_SUCCESS',
  REFRESH_TOKEN_FAILURE: 'REFRESH_TOKEN_FAILURE',
  CLEAR_ERROR: 'CLEAR_ERROR',
  SET_LOADING: 'SET_LOADING',
  SET_USER: 'SET_USER',
};

// Reducer function
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
      return {
        ...state,
        loading: true,
        error: null,
      };

    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        loading: false,
        user: action.payload.user,
        accessToken: action.payload.accessToken,
        refreshToken: action.payload.refreshToken,
        isAuthenticated: true,
        error: null,
      };

    case AUTH_ACTIONS.LOGIN_FAILURE:
      console.log('🔄 AuthContext Reducer: LOGIN_FAILURE dispatched with payload:', action.payload);
      return {
        ...state,
        loading: false,
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        error: action.payload,
      };

    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        loading: false,
        error: null,
      };

    case AUTH_ACTIONS.REFRESH_TOKEN_SUCCESS:
      return {
        ...state,
        accessToken: action.payload.accessToken,
        error: null,
      };

    case AUTH_ACTIONS.REFRESH_TOKEN_FAILURE:
      return {
        ...state,
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        error: action.payload,
      };

    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };

    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
      };

    case AUTH_ACTIONS.SET_USER:
      return {
        ...state,
        user: action.payload,
      };

    default:
      return state;
  }
};

// Create context
const AuthContext = createContext();

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// AuthProvider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = () => {
      const accessToken = localStorage.getItem('access_token');
      const refreshToken = localStorage.getItem('refresh_token');
      const userData = localStorage.getItem('user_data');

      if (accessToken && refreshToken && userData) {
        try {
          const user = JSON.parse(userData);
          dispatch({
            type: AUTH_ACTIONS.LOGIN_SUCCESS,
            payload: {
              user,
              accessToken,
              refreshToken,
            },
          });
        } catch (error) {
          console.error('Error parsing user data:', error);
          clearAuthData();
        }
      }
    };

    initializeAuth();
  }, []);

  // Clear auth data from localStorage
  const clearAuthData = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
  }, []);

  // Refresh access token
  const refreshAccessToken = useCallback(async () => {
    try {
      if (!state.refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await api.post('/auth/refresh', {
        refresh_token: state.refreshToken,
      });

      const { access_token } = response.data;

      // Update access token in localStorage
      localStorage.setItem('access_token', access_token);

      dispatch({
        type: AUTH_ACTIONS.REFRESH_TOKEN_SUCCESS,
        payload: { accessToken: access_token },
      });

      return access_token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      dispatch({
        type: AUTH_ACTIONS.REFRESH_TOKEN_FAILURE,
        payload: 'Session expired. Please login again.',
      });
      throw error;
    }
  }, [state.refreshToken]);

  // Logout function
  const logout = useCallback(async () => {
    try {
      if (state.refreshToken) {
        await api.post('/auth/logout', {
          refresh_token: state.refreshToken,
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearAuthData();
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  }, [state.refreshToken, clearAuthData]);

  // Set up axios interceptor for token refresh
  useEffect(() => {
    const responseInterceptor = api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const newToken = await refreshAccessToken();
            if (newToken) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              return api(originalRequest);
            }
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError);
            logout();
          }
        }

        return Promise.reject(error);
      }
    );

    return () => {
      api.interceptors.response.eject(responseInterceptor);
    };
  }, [state.refreshToken, refreshAccessToken, logout]);

  // Set up axios interceptor for adding auth header
  useEffect(() => {
    const requestInterceptor = api.interceptors.request.use(
      (config) => {
        if (state.accessToken) {
          config.headers.Authorization = `Bearer ${state.accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    return () => {
      api.interceptors.request.eject(requestInterceptor);
    };
  }, [state.accessToken]);

  // Login function
  const login = useCallback(async (email, password) => {
    try {
      console.log('🔐 AuthContext: Login started for:', email);
      dispatch({ type: AUTH_ACTIONS.LOGIN_START });

      const response = await api.post('/auth/login', {
        email,
        password,
      });

      console.log('🔐 AuthContext: Login response:', response.data);

      const { access_token, refresh_token, user } = response.data;

      // Store tokens and user data in localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user_data', JSON.stringify(user));

      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: {
          user,
          accessToken: access_token,
          refreshToken: refresh_token,
        },
      });

      console.log('✅ AuthContext: Login successful');
      return { success: true };
    } catch (error) {
      console.log('❌ AuthContext: Login error:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Login failed';
      console.log('❌ AuthContext: Error message:', errorMessage);
      
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: errorMessage,
      });
      
      console.log('❌ AuthContext: LOGIN_FAILURE dispatched with:', errorMessage);
      return { success: false, error: errorMessage };
    }
  }, []);


  // Get current user info
  const getCurrentUser = async () => {
    try {
      const response = await api.get('/auth/me');
      const user = response.data;

      // Update user data in localStorage
      localStorage.setItem('user_data', JSON.stringify(user));

      dispatch({
        type: AUTH_ACTIONS.SET_USER,
        payload: user,
      });

      return user;
    } catch (error) {
      console.error('Get current user error:', error);
      throw error;
    }
  };

  // Change password
  const changePassword = async (currentPassword, newPassword) => {
    try {
      await api.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });

      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message || 'Password change failed';
      return { success: false, error: errorMessage };
    }
  };

  // Logout from all devices
  const logoutAllDevices = async () => {
    try {
      await api.post('/auth/logout-all');
      clearAuthData();
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message || 'Logout all failed';
      return { success: false, error: errorMessage };
    }
  };

  // Clear error
  const clearError = useCallback(() => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  }, []);

  // Set loading
  const setLoading = useCallback((loading) => {
    dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: loading });
  }, []);

  const value = useMemo(() => ({
    // State
    user: state.user,
    accessToken: state.accessToken,
    refreshToken: state.refreshToken,
    loading: state.loading,
    error: state.error,
    isAuthenticated: state.isAuthenticated,

    // Actions
    login,
    logout,
    refreshAccessToken,
    getCurrentUser,
    changePassword,
    logoutAllDevices,
    clearError,
    setLoading,
  }), [
    state.user,
    state.accessToken,
    state.refreshToken,
    state.loading,
    state.error,
    state.isAuthenticated,
    login,
    logout,
    refreshAccessToken,
    getCurrentUser,
    changePassword,
    logoutAllDevices,
    clearError,
    setLoading,
  ]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

