import React, { useState, useEffect, useCallback } from 'react';
import { format } from 'date-fns';
import { tr } from 'date-fns/locale';
import UserForm from './UserForm';
import DeleteConfirmModal from './DeleteConfirmModal';

const UserList = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showModal, setShowModal] = useState(false);
  const [editingUserId, setEditingUserId] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletingUser, setDeletingUser] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  // Status options
  const statusOptions = [
    { value: '', label: 'Duruma Göre Filtrele' },
    { value: 'active', label: 'Aktif' },
    { value: 'inactive', label: 'Pasif' }
  ];

  // Sort options
  const sortOptions = [
    { value: 'created_at', label: 'Tarihe Göre Sırala' },
    { value: 'full_name', label: 'İsme Göre' },
    { value: 'email', label: 'E-postaya Göre' },
    { value: 'last_login', label: 'Son Girişe Göre' }
  ];

  // Fetch users
  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      console.log('UserList - Token:', token ? 'Token exists' : 'No token');
      
      if (!token) {
        console.error('No token found in localStorage');
        window.location.href = '/login';
        return;
      }
      
      const params = new URLSearchParams({
        page: currentPage.toString(),
        per_page: '10',
        ...(searchTerm && { search: searchTerm }),
        ...(statusFilter && { status: statusFilter }),
        sort_by: sortBy,
        sort_order: sortOrder
      });

      const response = await fetch(`http://localhost:8001/api/v1/users/?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch users');
      }

      const data = await response.json();
      console.log('UserList API Response:', data);
      
      // API response yapısını kontrol et
      if (data.success && data.data) {
        setUsers(data.data.users || []);
        setTotalPages(Math.ceil((data.data.total || 0) / 10));
      } else if (data.users) {
        setUsers(data.users || []);
        setTotalPages(Math.ceil((data.total || 0) / 10));
      } else {
        setUsers([]);
        setTotalPages(1);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  }, [currentPage, searchTerm, statusFilter, sortBy, sortOrder]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  // Handle status filter
  const handleStatusFilter = (e) => {
    setStatusFilter(e.target.value);
    setCurrentPage(1);
  };

  // Handle sort dropdown
  const handleSortChange = (e) => {
    setSortBy(e.target.value);
    setCurrentPage(1);
  };

  // Handle sort order
  const handleSortOrder = (e) => {
    setSortOrder(e.target.value);
    setCurrentPage(1);
  };

  // Handle column sorting
  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
    setCurrentPage(1);
  };

  // Handle new user
  const handleNewUser = () => {
    setEditingUserId(null);
    setShowModal(true);
  };

  // Handle edit user
  const handleEditUser = (user) => {
    setEditingUserId(user.id);
    setShowModal(true);
  };

  // Handle delete user
  const handleDeleteUser = (user) => {
    setDeletingUser(user);
    setShowDeleteModal(true);
  };

  // Confirm delete user
  const confirmDeleteUser = async () => {
    if (!deletingUser) return;

    setDeleteLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8001/api/v1/users/${deletingUser.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete user');
      }

      // Refresh the list
      fetchUsers();
      setShowDeleteModal(false);
      setDeletingUser(null);
    } catch (error) {
      console.error('Error deleting user:', error);
      alert('Kullanıcı silinirken bir hata oluştu.');
    } finally {
      setDeleteLoading(false);
    }
  };

  // Cancel delete
  const cancelDelete = () => {
    setShowDeleteModal(false);
    setDeletingUser(null);
  };

  // Handle modal close
  const handleModalClose = () => {
    setShowModal(false);
    setEditingUserId(null);
    fetchUsers();
  };

  // Get status badge class
  const getStatusBadgeClass = (isActive) => {
    return isActive 
      ? 'bg-green-100 text-green-800' 
      : 'bg-red-100 text-red-800';
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'Hiç giriş yapmamış';
    return format(new Date(dateString), 'dd.MM.yyyy HH:mm', { locale: tr });
  };

  return (
    <div className="p-6 lg:p-8">
      <div className="flex flex-col flex-1 bg-white rounded-xl shadow-sm border border-gray-200">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex flex-wrap justify-between items-center gap-4">
            <div className="flex flex-col gap-1">
              <h2 className="text-2xl font-bold leading-tight tracking-[-0.015em]">
                Kullanıcı Yönetimi
              </h2>
              <p className="text-gray-500 text-sm font-normal">
                Sistem kullanıcılarını buradan yönetebilirsiniz.
              </p>
            </div>
            <button
              onClick={handleNewUser}
              className="flex items-center justify-center gap-2 min-w-[84px] cursor-pointer overflow-hidden rounded-md h-12 px-6 bg-blue-600 text-white text-base font-bold leading-normal tracking-wide shadow-sm hover:bg-opacity-90 transition-colors"
            >
              <span className="material-symbols-outlined">add</span>
              <span>Yeni Kullanıcı Ekle</span>
            </button>
          </div>

          {/* Filters */}
          <div className="mt-6 flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <span className="material-symbols-outlined text-gray-400">
                  search
                </span>
              </div>
              <input
                type="text"
                placeholder="Kullanıcı ara..."
                value={searchTerm}
                onChange={handleSearch}
                className="flex w-full min-w-0 rounded-md text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-300 bg-white h-11 placeholder:text-gray-400 pl-10 pr-4 text-base font-normal"
              />
            </div>
            <div className="flex gap-4">
              <select
                value={statusFilter}
                onChange={handleStatusFilter}
                className="flex w-full sm:w-auto min-w-0 rounded-md text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-300 bg-white h-11 px-4 text-sm font-medium"
              >
                {statusOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <select
                value={sortBy}
                onChange={handleSortChange}
                className="flex w-full sm:w-auto min-w-0 rounded-md text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-300 bg-white h-11 px-4 text-sm font-medium"
              >
                {sortOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <select
                value={sortOrder}
                onChange={handleSortOrder}
                className="flex w-full sm:w-auto min-w-0 rounded-md text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-300 bg-white h-11 px-4 text-sm font-medium"
              >
                <option value="desc">En Yeni</option>
                <option value="asc">En Eski</option>
              </select>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <table className="w-full text-left">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th 
                    className="px-6 py-4 text-sm font-semibold text-gray-600 cursor-pointer hover:bg-gray-100 select-none"
                    onClick={() => handleSort('full_name')}
                  >
                    <div className="flex items-center gap-1">
                      Kullanıcı
                      {sortBy === 'full_name' && (
                        <span className="material-symbols-outlined text-sm">
                          {sortOrder === 'asc' ? 'arrow_upward' : 'arrow_downward'}
                        </span>
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-4 text-sm font-semibold text-gray-600 cursor-pointer hover:bg-gray-100 select-none"
                    onClick={() => handleSort('email')}
                  >
                    <div className="flex items-center gap-1">
                      E-posta
                      {sortBy === 'email' && (
                        <span className="material-symbols-outlined text-sm">
                          {sortOrder === 'asc' ? 'arrow_upward' : 'arrow_downward'}
                        </span>
                      )}
                    </div>
                  </th>
                  <th className="px-6 py-4 text-sm font-semibold text-gray-600">
                    Telefon
                  </th>
                  <th className="px-6 py-4 text-sm font-semibold text-gray-600">
                    Rol
                  </th>
                  <th 
                    className="px-6 py-4 text-sm font-semibold text-gray-600 cursor-pointer hover:bg-gray-100 select-none"
                    onClick={() => handleSort('last_login')}
                  >
                    <div className="flex items-center gap-1">
                      Son Giriş
                      {sortBy === 'last_login' && (
                        <span className="material-symbols-outlined text-sm">
                          {sortOrder === 'asc' ? 'arrow_upward' : 'arrow_downward'}
                        </span>
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-4 text-sm font-semibold text-gray-600 text-center cursor-pointer hover:bg-gray-100 select-none"
                    onClick={() => handleSort('is_active')}
                  >
                    <div className="flex items-center justify-center gap-1">
                      Durum
                      {sortBy === 'is_active' && (
                        <span className="material-symbols-outlined text-sm">
                          {sortOrder === 'asc' ? 'arrow_upward' : 'arrow_downward'}
                        </span>
                      )}
                    </div>
                  </th>
                  <th className="px-6 py-4 text-sm font-semibold text-gray-600 text-center">
                    İşlemler
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {!users || users.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
                      Henüz kullanıcı bulunmuyor.
                    </td>
                  </tr>
                ) : (
                  users.map((user) => (
                    <tr key={user.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="h-10 w-10 flex-shrink-0">
                            {user.profile_photo ? (
                              <img
                                className="h-10 w-10 rounded-full object-cover"
                                src={`http://localhost:8001${user.profile_photo}`}
                                alt={user.full_name}
                              />
                            ) : (
                              <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                                <span className="material-symbols-outlined text-gray-500 text-lg">person</span>
                              </div>
                            )}
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                            <div className="text-sm text-gray-500">{user.first_name} {user.last_name}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {user.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {user.phone || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2.5 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                          {user.role?.name || 'Rol Atanmamış'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatDate(user.last_login)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeClass(user.is_active)}`}>
                          {user.is_active ? 'Aktif' : 'Pasif'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-center">
                        <div className="flex items-center justify-center space-x-2">
                          <button
                            onClick={() => handleEditUser(user)}
                            className="text-green-600 hover:text-green-800 p-1"
                            title="Düzenle"
                          >
                            <span className="material-symbols-outlined text-sm">edit</span>
                          </button>
                          <button
                            onClick={() => handleDeleteUser(user)}
                            className="text-red-600 hover:text-red-800 p-1"
                            title="Sil"
                          >
                            <span className="material-symbols-outlined text-sm">delete</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
            <div className="text-sm text-gray-500">
              Sayfa {currentPage} / {totalPages}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Önceki
              </button>
              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Sonraki
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <UserForm
          isOpen={showModal}
          onClose={handleModalClose}
          userId={editingUserId}
          onSuccess={fetchUsers}
        />
      )}

      {/* Delete Confirmation Modal */}
      <DeleteConfirmModal
        isOpen={showDeleteModal}
        onClose={cancelDelete}
        onConfirm={confirmDeleteUser}
        title="Kullanıcıyı Sil"
        message={`"${deletingUser?.full_name || deletingUser?.first_name + ' ' + deletingUser?.last_name}" kullanıcısını silmek istediğinizden emin misiniz?`}
        itemName={deletingUser?.full_name || `${deletingUser?.first_name} ${deletingUser?.last_name}`}
        isLoading={deleteLoading}
      />
    </div>
  );
};

export default UserList;