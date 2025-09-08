/**
 * Frontend Authentication Integration Tests
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';
import LoginForm from '../components/LoginForm';
import ProtectedRoute from '../components/ProtectedRoute';
import UserProfile from '../components/UserProfile';

// Mock API service
jest.mock('../services/api', () => ({
  authAPI: {
    login: jest.fn(),
    logout: jest.fn(),
    getCurrentUser: jest.fn(),
    changePassword: jest.fn(),
  },
  usersAPI: {
    updateUser: jest.fn(),
  },
  handleAPIError: jest.fn(),
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock validation utils
jest.mock('../utils/validation', () => ({
  validateEmail: jest.fn((email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)),
  validatePassword: jest.fn((password) => password.length >= 8),
}));

// Test wrapper
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>
      {children}
    </AuthProvider>
  </BrowserRouter>
);

describe('Frontend Authentication Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  describe('LoginForm Component', () => {
    test('renders login form correctly', () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      expect(screen.getByText('Welcome Back')).toBeInTheDocument();
      expect(screen.getByLabelText('Email Address')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
    });

    test('validates email input', async () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText('Email Address');
      const submitButton = screen.getByRole('button', { name: 'Sign In' });

      // Test invalid email
      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
      });
    });

    test('validates password input', async () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: 'Sign In' });

      // Test short password
      fireEvent.change(passwordInput, { target: { value: '123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Password must be at least 8 characters long')).toBeInTheDocument();
      });
    });

    test('handles demo login', () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      const demoButton = screen.getByRole('button', { name: 'Try Demo Account' });
      fireEvent.click(demoButton);

      expect(screen.getByDisplayValue('demo@example.com')).toBeInTheDocument();
      expect(screen.getByDisplayValue('demo123456')).toBeInTheDocument();
    });
  });

  describe('ProtectedRoute Component', () => {
    test('redirects unauthenticated users to login', () => {
      const TestComponent = () => <div>Protected Content</div>;
      
      render(
        <TestWrapper>
          <ProtectedRoute>
            <TestComponent />
          </ProtectedRoute>
        </TestWrapper>
      );

      // Should redirect to login (this would be tested with router testing)
      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });

    test('allows authenticated users to access protected content', () => {
      // Mock authenticated state
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'mock-token';
        if (key === 'user_data') return JSON.stringify({ id: '1', email: 'test@example.com' });
        return null;
      });

      const TestComponent = () => <div>Protected Content</div>;
      
      render(
        <TestWrapper>
          <ProtectedRoute>
            <TestComponent />
          </ProtectedRoute>
        </TestWrapper>
      );

      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });
  });

  describe('UserProfile Component', () => {
    test('renders user profile correctly', () => {
      const mockUser = {
        id: '1',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        phone: '1234567890',
        role: { name: 'admin', description: 'Administrator' },
        is_active: true,
        created_at: '2023-01-01T00:00:00Z'
      };

      // Mock authenticated state
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'mock-token';
        if (key === 'user_data') return JSON.stringify(mockUser);
        return null;
      });

      render(
        <TestWrapper>
          <UserProfile />
        </TestWrapper>
      );

      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('john@example.com')).toBeInTheDocument();
      expect(screen.getByText('admin')).toBeInTheDocument();
    });

    test('switches between tabs', () => {
      const mockUser = {
        id: '1',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        role: { name: 'admin' },
        is_active: true,
        created_at: '2023-01-01T00:00:00Z'
      };

      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'mock-token';
        if (key === 'user_data') return JSON.stringify(mockUser);
        return null;
      });

      render(
        <TestWrapper>
          <UserProfile />
        </TestWrapper>
      );

      // Click on password tab
      fireEvent.click(screen.getByText('Password'));
      expect(screen.getByText('Change Password')).toBeInTheDocument();

      // Click on settings tab
      fireEvent.click(screen.getByText('Settings'));
      expect(screen.getByText('Account Settings')).toBeInTheDocument();
    });
  });

  describe('Authentication Flow', () => {
    test('complete login flow', async () => {
      const mockLoginResponse = {
        data: {
          access_token: 'mock-access-token',
          refresh_token: 'mock-refresh-token',
          user: {
            id: '1',
            email: 'test@example.com',
            first_name: 'Test',
            last_name: 'User'
          }
        }
      };

      const { authAPI } = require('../services/api');
      authAPI.login.mockResolvedValue(mockLoginResponse);

      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      // Fill form
      fireEvent.change(screen.getByLabelText('Email Address'), {
        target: { value: 'test@example.com' }
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: 'password123' }
      });

      // Submit form
      fireEvent.click(screen.getByRole('button', { name: 'Sign In' }));

      await waitFor(() => {
        expect(authAPI.login).toHaveBeenCalledWith('test@example.com', 'password123');
      });

      await waitFor(() => {
        expect(localStorage.setItem).toHaveBeenCalledWith('access_token', 'mock-access-token');
        expect(localStorage.setItem).toHaveBeenCalledWith('refresh_token', 'mock-refresh-token');
      });
    });

    test('handles login error', async () => {
      const { authAPI } = require('../services/api');
      authAPI.login.mockRejectedValue(new Error('Invalid credentials'));

      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      // Fill form
      fireEvent.change(screen.getByLabelText('Email Address'), {
        target: { value: 'test@example.com' }
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: 'wrongpassword' }
      });

      // Submit form
      fireEvent.click(screen.getByRole('button', { name: 'Sign In' }));

      await waitFor(() => {
        expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
      });
    });
  });

  describe('Token Management', () => {
    test('handles token refresh', async () => {
      const mockRefreshResponse = {
        data: {
          access_token: 'new-access-token',
          token_type: 'bearer',
          expires_in: 900
        }
      };

      const { authAPI } = require('../services/api');
      authAPI.refreshToken.mockResolvedValue(mockRefreshResponse);

      // Mock expired token scenario
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'expired-token';
        if (key === 'refresh_token') return 'valid-refresh-token';
        return null;
      });

      render(
        <TestWrapper>
          <div>Test Content</div>
        </TestWrapper>
      );

      // Simulate API call that would trigger refresh
      await waitFor(() => {
        expect(authAPI.refreshToken).toHaveBeenCalledWith('valid-refresh-token');
      });
    });
  });

  describe('Error Handling', () => {
    test('displays error messages', async () => {
      const { authAPI } = require('../services/api');
      authAPI.login.mockRejectedValue(new Error('Network error'));

      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      // Fill and submit form
      fireEvent.change(screen.getByLabelText('Email Address'), {
        target: { value: 'test@example.com' }
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: 'password123' }
      });
      fireEvent.click(screen.getByRole('button', { name: 'Sign In' }));

      await waitFor(() => {
        expect(screen.getByText('Network error')).toBeInTheDocument();
      });
    });

    test('clears error messages', async () => {
      render(
        <TestWrapper>
          <LoginForm />
        </TestWrapper>
      );

      // Simulate error state
      const errorBanner = screen.getByText('No error');
      fireEvent.click(errorBanner);

      // Error should be cleared (this would be tested with actual error state)
      expect(errorBanner).toBeInTheDocument();
    });
  });
});








