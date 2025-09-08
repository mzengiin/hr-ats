/**
 * User List Component with pagination and search
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { usersAPI, handleAPIError } from '../services/api';
import UserForm from './UserForm';
import RoleSelector from './RoleSelector';
import LoadingSpinner from './LoadingSpinner';
import './UserList.css';

const UserList = () => {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalUsers, setTotalUsers] = useState(0);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [selectedRole, setSelectedRole] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');

  // Available roles
  const roles = [
    { id: '1', name: 'admin', description: 'Administrator' },
    { id: '2', name: 'hr', description: 'HR Manager' },
    { id: '3', name: 'user', description: 'Regular User' }
  ];

  // Load users
  const loadUsers = async (page = 1, search = '', role = 'all', status = 'all') => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        page,
        limit: 10,
        search,
        role: role !== 'all' ? role : undefined,
        status: status !== 'all' ? status : undefined,
        sort_by: sortBy,
        sort_order: sortOrder
      };

      const response = await usersAPI.getUsers(params);
      const { users, total, page: currentPage, pages } = response.data;

      setUsers(users);
      setTotalUsers(total);
      setCurrentPage(currentPage);
      setTotalPages(pages);
    } catch (error) {
      setError(handleAPIError(error));
    } finally {
      setLoading(false);
    }
  };

  // Load users on component mount and when filters change
  useEffect(() => {
    loadUsers(currentPage, searchTerm, selectedRole, statusFilter);
  }, [currentPage, searchTerm, selectedRole, statusFilter, sortBy, sortOrder]);

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  // Handle role filter
  const handleRoleFilter = (e) => {
    setSelectedRole(e.target.value);
    setCurrentPage(1);
  };

  // Handle status filter
  const handleStatusFilter = (e) => {
    setStatusFilter(e.target.value);
    setCurrentPage(1);
  };

  // Handle sorting
  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  // Handle user activation/deactivation
  const handleToggleStatus = async (userId, isActive) => {
    try {
      if (isActive) {
        await usersAPI.deactivateUser(userId);
      } else {
        await usersAPI.activateUser(userId);
      }
      
      // Reload users
      await loadUsers(currentPage, searchTerm, selectedRole, statusFilter);
    } catch (error) {
      setError(handleAPIError(error));
    }
  };

  // Handle user deletion
  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Bu kullanıcıyı silmek istediğinizden emin misiniz?')) {
      return;
    }

    try {
      await usersAPI.deleteUser(userId);
      await loadUsers(currentPage, searchTerm, selectedRole, statusFilter);
    } catch (error) {
      setError(handleAPIError(error));
    }
  };

  // Handle user creation
  const handleUserCreated = () => {
    setShowCreateForm(false);
    loadUsers(currentPage, searchTerm, selectedRole, statusFilter);
  };

  // Handle user update
  const handleUserUpdated = () => {
    setEditingUser(null);
    loadUsers(currentPage, searchTerm, selectedRole, statusFilter);
  };

  // Handle pagination
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  // Render pagination
  const renderPagination = () => {
    if (totalPages <= 1) return null;

    const pages = [];
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    for (let i = startPage; i <= endPage; i++) {
      pages.push(
        <button
          key={i}
          className={`page-button ${i === currentPage ? 'active' : ''}`}
          onClick={() => handlePageChange(i)}
        >
          {i}
        </button>
      );
    }

    return (
      <div className="pagination">
        <button
          className="page-button"
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          Previous
        </button>
        {pages}
        <button
          className="page-button"
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          Next
        </button>
      </div>
    );
  };

  if (loading && (!users || users.length === 0)) {
    return <LoadingSpinner message="Loading users..." />;
  }

  return (
    <div className="user-list-container">
      <div className="user-list-header">
        <h1>Kullanıcı Yönetimi</h1>
        <button
          className="create-user-button"
          onClick={() => setShowCreateForm(true)}
        >
          Kullanıcı Oluştur
        </button>
      </div>

      {/* Filters */}
      <div className="filters">
        <div className="filter-group">
          <input
            type="text"
            placeholder="Search users..."
            value={searchTerm}
            onChange={handleSearch}
            className="search-input"
          />
        </div>
        
        <div className="filter-group">
          <select
            value={selectedRole}
            onChange={handleRoleFilter}
            className="filter-select"
          >
            <option value="all">All Roles</option>
            {roles.map(role => (
              <option key={role.id} value={role.name}>
                {role.description}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <select
            value={statusFilter}
            onChange={handleStatusFilter}
            className="filter-select"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      {/* Users Table */}
      <div className="users-table-container">
        <table className="users-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('first_name')}>
                Name
                {sortBy === 'first_name' && (
                  <span className="sort-indicator">
                    {sortOrder === 'asc' ? '↑' : '↓'}
                  </span>
                )}
              </th>
              <th onClick={() => handleSort('email')}>
                Email
                {sortBy === 'email' && (
                  <span className="sort-indicator">
                    {sortOrder === 'asc' ? '↑' : '↓'}
                  </span>
                )}
              </th>
              <th onClick={() => handleSort('role')}>
                Role
                {sortBy === 'role' && (
                  <span className="sort-indicator">
                    {sortOrder === 'asc' ? '↑' : '↓'}
                  </span>
                )}
              </th>
              <th onClick={() => handleSort('is_active')}>
                Status
                {sortBy === 'is_active' && (
                  <span className="sort-indicator">
                    {sortOrder === 'asc' ? '↑' : '↓'}
                  </span>
                )}
              </th>
              <th onClick={() => handleSort('created_at')}>
                Created
                {sortBy === 'created_at' && (
                  <span className="sort-indicator">
                    {sortOrder === 'asc' ? '↑' : '↓'}
                  </span>
                )}
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users && users.length > 0 ? users.map(user => (
              <tr key={user.id}>
                <td>
                  <div className="user-info">
                    <div className="user-avatar">
                      {user.first_name?.[0]}{user.last_name?.[0]}
                    </div>
                    <div className="user-details">
                      <div className="user-name">
                        {user.first_name} {user.last_name}
                      </div>
                      <div className="user-id">ID: {user.id}</div>
                    </div>
                  </div>
                </td>
                <td>{user.email}</td>
                <td>
                  <span className={`role-badge role-${user.role?.name || 'user'}`}>
                    {user.role?.name || 'User'}
                  </span>
                </td>
                <td>
                  <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td>
                  {new Date(user.created_at).toLocaleDateString()}
                </td>
                <td>
                  <div className="action-buttons">
                    <button
                      className="action-button edit"
                      onClick={() => setEditingUser(user)}
                      title="Kullanıcıyı Düzenle"
                    >
                      ✏️
                    </button>
                    <button
                      className="action-button toggle"
                      onClick={() => handleToggleStatus(user.id, user.is_active)}
                      title={user.is_active ? 'Pasifleştir' : 'Aktifleştir'}
                    >
                      {user.is_active ? '⏸️' : '▶️'}
                    </button>
                    {currentUser.id !== user.id && (
                      <button
                        className="action-button delete"
                        onClick={() => handleDeleteUser(user.id)}
                        title="Kullanıcıyı Sil"
                      >
                        🗑️
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            )) : (
              <tr>
                <td colSpan="6" className="no-users">
                  {loading ? 'Loading...' : 'No users found'}
                </td>
              </tr>
            )}
          </tbody>
        </table>

        {(!users || users.length === 0) && !loading && (
          <div className="no-users">
            <p>No users found</p>
          </div>
        )}
      </div>

      {/* Pagination */}
      {renderPagination()}

      {/* User Stats */}
      <div className="user-stats">
        <p>Showing {users ? users.length : 0} of {totalUsers} users</p>
      </div>

      {/* Create User Modal */}
      {showCreateForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <UserForm
              mode="create"
              onSuccess={handleUserCreated}
              onCancel={() => setShowCreateForm(false)}
            />
          </div>
        </div>
      )}

      {/* Edit User Modal */}
      {editingUser && (
        <div className="modal-overlay">
          <div className="modal-content">
            <UserForm
              mode="edit"
              user={editingUser}
              onSuccess={handleUserUpdated}
              onCancel={() => setEditingUser(null)}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default UserList;


