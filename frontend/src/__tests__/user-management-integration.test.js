/**
 * User Management Integration Tests
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';
import UserList from '../components/UserList';
import UserForm from '../components/UserForm';
import RoleSelector from '../components/RoleSelector';

// Mock API service
jest.mock('../services/api', () => ({
  usersAPI: {
    getUsers: jest.fn(),
    getUser: jest.fn(),
    createUser: jest.fn(),
    updateUser: jest.fn(),
    deleteUser: jest.fn(),
    activateUser: jest.fn(),
    deactivateUser: jest.fn(),
    searchUsers: jest.fn(),
    getUserStats: jest.fn(),
  },
  handleAPIError: jest.fn((error) => error.message || 'An error occurred'),
}));

// Mock auth context
const mockAuthContext = {
  user: {
    id: '1',
    email: 'admin@example.com',
    role: { name: 'admin', permissions: { users: ['create', 'read', 'update', 'delete'] } }
  },
  isAuthenticated: true,
  loading: false,
  error: null,
};

// Test wrapper
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    <AuthProvider value={mockAuthContext}>
      {children}
    </AuthProvider>
  </BrowserRouter>
);

describe('User Management Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Complete User Management Flow', () => {
    test('full user management workflow', async () => {
      const mockUsers = [
        {
          id: '1',
          first_name: 'John',
          last_name: 'Doe',
          email: 'john@example.com',
          is_active: true,
          role: { id: '1', name: 'admin' },
          created_at: '2023-01-01T00:00:00Z'
        }
      ];

      const { usersAPI } = require('../services/api');

      // Mock initial load
      usersAPI.getUsers.mockResolvedValue({
        data: {
          items: mockUsers,
          total: 1,
          page: 1,
          pages: 1
        }
      });

      render(
        <TestWrapper>
          <UserList />
        </TestWrapper>
      );

      // Wait for users to load
      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
      });

      // Test search functionality
      const searchInput = screen.getByPlaceholderText('Search users...');
      fireEvent.change(searchInput, { target: { value: 'john' } });

      await waitFor(() => {
        expect(usersAPI.searchUsers).toHaveBeenCalledWith('john', 10);
      });

      // Test role filtering
      const roleFilter = screen.getByDisplayValue('All Roles');
      fireEvent.change(roleFilter, { target: { value: 'admin' } });

      await waitFor(() => {
        expect(usersAPI.getUsers).toHaveBeenCalledWith({
          page: 1,
          limit: 10,
          search: 'john',
          role: 'admin',
          status: 'all',
          sort_by: 'created_at',
          sort_order: 'desc'
        });
      });

      // Test status filtering
      const statusFilter = screen.getByDisplayValue('All Status');
      fireEvent.change(statusFilter, { target: { value: 'active' } });

      await waitFor(() => {
        expect(usersAPI.getUsers).toHaveBeenCalledWith({
          page: 1,
          limit: 10,
          search: 'john',
          role: 'admin',
          status: 'active',
          sort_by: 'created_at',
          sort_order: 'desc'
        });
      });
    });

    test('user creation workflow', async () => {
      const { usersAPI } = require('../services/api');

      // Mock empty initial state
      usersAPI.getUsers.mockResolvedValue({
        data: {
          items: [],
          total: 0,
          page: 1,
          pages: 1
        }
      });

      // Mock successful creation
      usersAPI.createUser.mockResolvedValue({
        data: { id: '2', message: 'User created successfully' }
      });

      render(
        <TestWrapper>
          <UserList />
        </TestWrapper>
      );

      // Click create user button
      const createButton = screen.getByText('Create User');
      fireEvent.click(createButton);

      // Fill form
      fireEvent.change(screen.getByLabelText('First Name'), {
        target: { value: 'Jane' }
      });
      fireEvent.change(screen.getByLabelText('Last Name'), {
        target: { value: 'Smith' }
      });
      fireEvent.change(screen.getByLabelText('Email Address'), {
        target: { value: 'jane@example.com' }
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: 'password123' }
      });
      fireEvent.change(screen.getByLabelText('Confirm Password'), {
        target: { value: 'password123' }
      });

      // Submit form
      const submitButton = screen.getByText('Create User');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(usersAPI.createUser).toHaveBeenCalledWith({
          first_name: 'Jane',
          last_name: 'Smith',
          email: 'jane@example.com',
          password: 'password123',
          role_id: expect.any(String),
          is_active: true
        });
      });
    });

    test('user editing workflow', async () => {
      const mockUser = {
        id: '1',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        role: { id: '1', name: 'admin' },
        is_active: true
      };

      const { usersAPI } = require('../services/api');

      // Mock successful update
      usersAPI.updateUser.mockResolvedValue({
        data: { message: 'User updated successfully' }
      });

      render(
        <TestWrapper>
          <UserForm mode="edit" user={mockUser} />
        </TestWrapper>
      );

      // Update form
      fireEvent.change(screen.getByLabelText('First Name'), {
        target: { value: 'Johnny' }
      });

      // Submit form
      const submitButton = screen.getByText('Update User');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(usersAPI.updateUser).toHaveBeenCalledWith('1', {
          first_name: 'Johnny',
          last_name: 'Doe',
          email: 'john@example.com',
          role_id: '1',
          is_active: true
        });
      });
    });

    test('user activation/deactivation workflow', async () => {
      const mockUsers = [
        {
          id: '1',
          first_name: 'John',
          last_name: 'Doe',
          email: 'john@example.com',
          is_active: true,
          role: { id: '1', name: 'admin' },
          created_at: '2023-01-01T00:00:00Z'
        }
      ];

      const { usersAPI } = require('../services/api');

      usersAPI.getUsers.mockResolvedValue({
        data: {
          items: mockUsers,
          total: 1,
          page: 1,
          pages: 1
        }
      });

      usersAPI.deactivateUser.mockResolvedValue({});

      render(
        <TestWrapper>
          <UserList />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
      });

      // Click deactivate button
      const deactivateButton = screen.getByTitle('Deactivate');
      fireEvent.click(deactivateButton);

      await waitFor(() => {
        expect(usersAPI.deactivateUser).toHaveBeenCalledWith('1');
      });
    });

    test('user deletion workflow', async () => {
      const mockUsers = [
        {
          id: '1',
          first_name: 'John',
          last_name: 'Doe',
          email: 'john@example.com',
          is_active: true,
          role: { id: '1', name: 'admin' },
          created_at: '2023-01-01T00:00:00Z'
        }
      ];

      const { usersAPI } = require('../services/api');

      usersAPI.getUsers.mockResolvedValue({
        data: {
          items: mockUsers,
          total: 1,
          page: 1,
          pages: 1
        }
      });

      usersAPI.deleteUser.mockResolvedValue({});

      // Mock window.confirm
      window.confirm = jest.fn(() => true);

      render(
        <TestWrapper>
          <UserList />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
      });

      // Click delete button
      const deleteButton = screen.getByTitle('Delete User');
      fireEvent.click(deleteButton);

      // Confirm deletion
      expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete this user?');

      await waitFor(() => {
        expect(usersAPI.deleteUser).toHaveBeenCalledWith('1');
      });
    });
  });

  describe('Error Handling', () => {
    test('handles API errors gracefully', async () => {
      const { usersAPI, handleAPIError } = require('../services/api');

      usersAPI.getUsers.mockRejectedValue(new Error('Network error'));
      handleAPIError.mockReturnValue('Network error');

      render(
        <TestWrapper>
          <UserList />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Network error')).toBeInTheDocument();
      });
    });

    test('handles form validation errors', async () => {
      render(
        <TestWrapper>
          <UserForm mode="create" />
        </TestWrapper>
      );

      // Submit empty form
      const submitButton = screen.getByText('Create User');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('First name is required')).toBeInTheDocument();
        expect(screen.getByText('Last name is required')).toBeInTheDocument();
        expect(screen.getByText('Email is required')).toBeInTheDocument();
        expect(screen.getByText('Password is required')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    test('role selector is keyboard accessible', () => {
      const mockRoles = [
        { id: '1', name: 'admin', description: 'Administrator' },
        { id: '2', name: 'user', description: 'Regular User' }
      ];

      render(
        <TestWrapper>
          <RoleSelector roles={mockRoles} value="admin" onChange={() => {}} />
        </TestWrapper>
      );

      const trigger = screen.getByRole('button');
      expect(trigger).toHaveAttribute('aria-haspopup', 'listbox');
      expect(trigger).toHaveAttribute('aria-expanded', 'false');

      // Test keyboard navigation
      fireEvent.keyDown(trigger, { key: 'Enter' });
      expect(trigger).toHaveAttribute('aria-expanded', 'true');
    });

    test('form inputs have proper labels', () => {
      render(
        <TestWrapper>
          <UserForm mode="create" />
        </TestWrapper>
      );

      expect(screen.getByLabelText('First Name *')).toBeInTheDocument();
      expect(screen.getByLabelText('Last Name *')).toBeInTheDocument();
      expect(screen.getByLabelText('Email Address *')).toBeInTheDocument();
      expect(screen.getByLabelText('Password *')).toBeInTheDocument();
    });
  });

  describe('Responsive Design', () => {
    test('form adapts to mobile layout', () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      render(
        <TestWrapper>
          <UserForm mode="create" />
        </TestWrapper>
      );

      // Check that form elements are present
      expect(screen.getByText('Create New User')).toBeInTheDocument();
      expect(screen.getByLabelText('First Name *')).toBeInTheDocument();
    });
  });
});








