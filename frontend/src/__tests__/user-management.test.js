/**
 * Tests for user management components
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';
import UserList from '../components/UserList';
import UserForm from '../components/UserForm';
import RoleSelector from '../components/RoleSelector';
import { usersAPI } from '../services/api';

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
  handleAPIError: jest.fn(),
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

describe('User Management Components', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('UserList Component', () => {
    const mockUsers = [
      {
        id: '1',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        is_active: true,
        role: { name: 'admin' },
        created_at: '2023-01-01T00:00:00Z'
      },
      {
        id: '2',
        first_name: 'Jane',
        last_name: 'Smith',
        email: 'jane@example.com',
        is_active: false,
        role: { name: 'user' },
        created_at: '2023-01-02T00:00:00Z'
      }
    ];

    test('renders user list correctly', async () => {
      usersAPI.getUsers.mockResolvedValue({
        data: {
          items: mockUsers,
          total: 2,
          page: 1,
          pages: 1
        }
      });

      render(
        <TestWrapper>
          <UserList />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      });

      expect(screen.getByText('john@example.com')).toBeInTheDocument();
      expect(screen.getByText('jane@example.com')).toBeInTheDocument();
    });

    test('handles pagination', async () => {
      const mockResponse = {
        data: {
          items: mockUsers,
          total: 50,
          page: 1,
          pages: 5
        }
      };

      usersAPI.getUsers.mockResolvedValue(mockResponse);

      render(
        <TestWrapper>
          <UserList />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Page 1 of 5')).toBeInTheDocument();
      });

      const nextButton = screen.getByText('Next');
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(usersAPI.getUsers).toHaveBeenCalledWith({ page: 2 });
      });
    });

    test('handles search functionality', async () => {
      usersAPI.getUsers.mockResolvedValue({
        data: {
          items: mockUsers,
          total: 2,
          page: 1,
          pages: 1
        }
      });

      render(
        <TestWrapper>
          <UserList />
        </TestWrapper>
      );

      const searchInput = screen.getByPlaceholderText('Search users...');
      fireEvent.change(searchInput, { target: { value: 'john' } });

      await waitFor(() => {
        expect(usersAPI.searchUsers).toHaveBeenCalledWith('john', 10);
      });
    });

    test('handles user activation/deactivation', async () => {
      usersAPI.getUsers.mockResolvedValue({
        data: {
          items: mockUsers,
          total: 2,
          page: 1,
          pages: 1
        }
      });

      usersAPI.activateUser.mockResolvedValue({});
      usersAPI.deactivateUser.mockResolvedValue({});

      render(
        <TestWrapper>
          <UserList />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
      });

      // Test deactivation
      const deactivateButton = screen.getByText('Deactivate');
      fireEvent.click(deactivateButton);

      await waitFor(() => {
        expect(usersAPI.deactivateUser).toHaveBeenCalledWith('1');
      });
    });

    test('handles user deletion', async () => {
      usersAPI.getUsers.mockResolvedValue({
        data: {
          items: mockUsers,
          total: 2,
          page: 1,
          pages: 1
        }
      });

      usersAPI.deleteUser.mockResolvedValue({});

      render(
        <TestWrapper>
          <UserList />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
      });

      const deleteButton = screen.getByText('Delete');
      fireEvent.click(deleteButton);

      // Confirm deletion
      const confirmButton = screen.getByText('Yes, Delete');
      fireEvent.click(confirmButton);

      await waitFor(() => {
        expect(usersAPI.deleteUser).toHaveBeenCalledWith('1');
      });
    });
  });

  describe('UserForm Component', () => {
    test('renders create user form', () => {
      render(
        <TestWrapper>
          <UserForm mode="create" />
        </TestWrapper>
      );

      expect(screen.getByText('Create New User')).toBeInTheDocument();
      expect(screen.getByLabelText('First Name')).toBeInTheDocument();
      expect(screen.getByLabelText('Last Name')).toBeInTheDocument();
      expect(screen.getByLabelText('Email Address')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
    });

    test('renders edit user form', () => {
      const mockUser = {
        id: '1',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        role: { id: '1', name: 'admin' },
        is_active: true
      };

      render(
        <TestWrapper>
          <UserForm mode="edit" user={mockUser} />
        </TestWrapper>
      );

      expect(screen.getByText('Edit User')).toBeInTheDocument();
      expect(screen.getByDisplayValue('John')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Doe')).toBeInTheDocument();
      expect(screen.getByDisplayValue('john@example.com')).toBeInTheDocument();
    });

    test('validates form inputs', async () => {
      render(
        <TestWrapper>
          <UserForm mode="create" />
        </TestWrapper>
      );

      const submitButton = screen.getByText('Create User');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('First name is required')).toBeInTheDocument();
        expect(screen.getByText('Last name is required')).toBeInTheDocument();
        expect(screen.getByText('Email is required')).toBeInTheDocument();
        expect(screen.getByText('Password is required')).toBeInTheDocument();
      });
    });

    test('handles form submission', async () => {
      usersAPI.createUser.mockResolvedValue({
        data: { id: '1', message: 'User created successfully' }
      });

      render(
        <TestWrapper>
          <UserForm mode="create" />
        </TestWrapper>
      );

      // Fill form
      fireEvent.change(screen.getByLabelText('First Name'), {
        target: { value: 'John' }
      });
      fireEvent.change(screen.getByLabelText('Last Name'), {
        target: { value: 'Doe' }
      });
      fireEvent.change(screen.getByLabelText('Email Address'), {
        target: { value: 'john@example.com' }
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: 'password123' }
      });

      const submitButton = screen.getByText('Create User');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(usersAPI.createUser).toHaveBeenCalledWith({
          first_name: 'John',
          last_name: 'Doe',
          email: 'john@example.com',
          password: 'password123',
          role_id: expect.any(String)
        });
      });
    });
  });

  describe('RoleSelector Component', () => {
    const mockRoles = [
      { id: '1', name: 'admin', description: 'Administrator' },
      { id: '2', name: 'hr', description: 'HR Manager' },
      { id: '3', name: 'user', description: 'Regular User' }
    ];

    test('renders role options', () => {
      render(
        <TestWrapper>
          <RoleSelector roles={mockRoles} value="admin" onChange={() => {}} />
        </TestWrapper>
      );

      expect(screen.getByText('Administrator')).toBeInTheDocument();
      expect(screen.getByText('HR Manager')).toBeInTheDocument();
      expect(screen.getByText('Regular User')).toBeInTheDocument();
    });

    test('handles role selection', () => {
      const handleChange = jest.fn();

      render(
        <TestWrapper>
          <RoleSelector roles={mockRoles} value="admin" onChange={handleChange} />
        </TestWrapper>
      );

      const hrOption = screen.getByText('HR Manager');
      fireEvent.click(hrOption);

      expect(handleChange).toHaveBeenCalledWith('hr');
    });

    test('shows role descriptions', () => {
      render(
        <TestWrapper>
          <RoleSelector roles={mockRoles} value="admin" onChange={() => {}} />
        </TestWrapper>
      );

      expect(screen.getByText('Administrator')).toBeInTheDocument();
      expect(screen.getByText('HR Manager')).toBeInTheDocument();
      expect(screen.getByText('Regular User')).toBeInTheDocument();
    });
  });

  describe('User Management Integration', () => {
    test('complete user creation flow', async () => {
      const mockRoles = [
        { id: '1', name: 'admin', description: 'Administrator' }
      ];

      usersAPI.getUsers.mockResolvedValue({
        data: {
          items: [],
          total: 0,
          page: 1,
          pages: 1
        }
      });

      usersAPI.createUser.mockResolvedValue({
        data: { id: '1', message: 'User created successfully' }
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
        target: { value: 'John' }
      });
      fireEvent.change(screen.getByLabelText('Last Name'), {
        target: { value: 'Doe' }
      });
      fireEvent.change(screen.getByLabelText('Email Address'), {
        target: { value: 'john@example.com' }
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: 'password123' }
      });

      // Submit form
      const submitButton = screen.getByText('Create User');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(usersAPI.createUser).toHaveBeenCalled();
      });
    });

    test('handles API errors gracefully', async () => {
      usersAPI.getUsers.mockRejectedValue(new Error('Network error'));

      render(
        <TestWrapper>
          <UserList />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Network error')).toBeInTheDocument();
      });
    });
  });
});








