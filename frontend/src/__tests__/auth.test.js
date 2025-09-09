/**
 * Tests for authentication context and hooks
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

// Mock API service
jest.mock('../services/api', () => ({
  api: {
    post: jest.fn(),
    get: jest.fn(),
    delete: jest.fn(),
  },
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Test component that uses auth context
const TestComponent = () => {
  const { user, login, logout, loading, error } = useAuth();
  
  return (
    <div>
      <div data-testid="user">{user ? user.email : 'No user'}</div>
      <div data-testid="loading">{loading ? 'Loading...' : 'Not loading'}</div>
      <div data-testid="error">{error || 'No error'}</div>
      <button onClick={() => login('test@example.com', 'password')}>
        Login
      </button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

// Wrapper component
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>
      {children}
    </AuthProvider>
  </BrowserRouter>
);

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  describe('Initial State', () => {
    test('should have initial state', () => {
      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      );

      expect(screen.getByTestId('user')).toHaveTextContent('No user');
      expect(screen.getByTestId('loading')).toHaveTextContent('Not loading');
      expect(screen.getByTestId('error')).toHaveTextContent('No error');
    });
  });

  describe('Login Functionality', () => {
    test('should login successfully', async () => {
      const mockResponse = {
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

      api.post.mockResolvedValue(mockResponse);

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      );

      const loginButton = screen.getByText('Login');
      fireEvent.click(loginButton);

      await waitFor(() => {
        expect(api.post).toHaveBeenCalledWith('/auth/login', {
          email: 'test@example.com',
          password: 'password'
        });
      });

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
      });

      expect(localStorage.setItem).toHaveBeenCalledWith('access_token', 'mock-access-token');
      expect(localStorage.setItem).toHaveBeenCalledWith('refresh_token', 'mock-refresh-token');
    });

    test('should handle login error', async () => {
      const mockError = new Error('Invalid credentials');
      api.post.mockRejectedValue(mockError);

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      );

      const loginButton = screen.getByText('Login');
      fireEvent.click(loginButton);

      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent('Invalid credentials');
      });
    });
  });

  describe('Logout Functionality', () => {
    test('should logout successfully', async () => {
      // Set up logged in state
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'mock-access-token';
        if (key === 'refresh_token') return 'mock-refresh-token';
        return null;
      });

      api.delete.mockResolvedValue({});

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      );

      const logoutButton = screen.getByText('Logout');
      fireEvent.click(logoutButton);

      await waitFor(() => {
        expect(api.delete).toHaveBeenCalledWith('/auth/logout', {
          data: { refresh_token: 'mock-refresh-token' }
        });
      });

      expect(localStorage.removeItem).toHaveBeenCalledWith('access_token');
      expect(localStorage.removeItem).toHaveBeenCalledWith('refresh_token');
    });
  });

  describe('Token Management', () => {
    test('should refresh token when expired', async () => {
      const mockRefreshResponse = {
        data: {
          access_token: 'new-access-token',
          token_type: 'bearer',
          expires_in: 900
        }
      };

      api.post.mockResolvedValue(mockRefreshResponse);

      // Mock expired token
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'expired-token';
        if (key === 'refresh_token') return 'valid-refresh-token';
        return null;
      });

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      );

      // Simulate API call that would trigger token refresh
      await waitFor(() => {
        expect(api.post).toHaveBeenCalledWith('/auth/refresh', {
          refresh_token: 'valid-refresh-token'
        });
      });
    });
  });

  describe('Loading States', () => {
    test('should show loading during login', async () => {
      let resolveLogin;
      const loginPromise = new Promise((resolve) => {
        resolveLogin = resolve;
      });
      api.post.mockReturnValue(loginPromise);

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      );

      const loginButton = screen.getByText('Login');
      fireEvent.click(loginButton);

      expect(screen.getByTestId('loading')).toHaveTextContent('Loading...');

      // Resolve the promise
      resolveLogin({
        data: {
          access_token: 'token',
          refresh_token: 'refresh',
          user: { email: 'test@example.com' }
        }
      });

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('Not loading');
      });
    });
  });

  describe('Error Handling', () => {
    test('should clear error on successful login', async () => {
      // First login fails
      api.post.mockRejectedValueOnce(new Error('Network error'));

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      );

      const loginButton = screen.getByText('Login');
      fireEvent.click(loginButton);

      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent('Network error');
      });

      // Second login succeeds
      api.post.mockResolvedValueOnce({
        data: {
          access_token: 'token',
          refresh_token: 'refresh',
          user: { email: 'test@example.com' }
        }
      });

      fireEvent.click(loginButton);

      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent('No error');
      });
    });
  });
});

describe('useAuth Hook', () => {
  test('should throw error when used outside AuthProvider', () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    const TestComponent = () => {
      useAuth();
      return <div>Test</div>;
    };

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useAuth must be used within an AuthProvider');

    consoleError.mockRestore();
  });
});









