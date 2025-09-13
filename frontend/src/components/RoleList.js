import React, { useState, useEffect, useCallback } from 'react';
import { format } from 'date-fns';
import { tr } from 'date-fns/locale';
import RoleForm from './RoleForm';
import DeleteConfirmModal from './DeleteConfirmModal';

const RoleList = () => {
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showModal, setShowModal] = useState(false);
  const [editingRoleId, setEditingRoleId] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletingRole, setDeletingRole] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  // Sort options
  const sortOptions = [
    { value: 'created_at', label: 'Tarihe Göre Sırala' },
    { value: 'name', label: 'Rol Adına Göre' },
    { value: 'description', label: 'Açıklamaya Göre' }
  ];

  // Fetch roles
  const fetchRoles = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      console.log('RoleList - Token:', token ? 'Token exists' : 'No token');
      
      if (!token) {
        console.error('No token found in localStorage');
        window.location.href = '/login';
        return;
      }
      
      const params = new URLSearchParams({
        page: currentPage.toString(),
        per_page: '10',
        ...(searchTerm && { search: searchTerm }),
        sort_by: sortBy,
        sort_order: sortOrder
      });

      const response = await fetch(`http://localhost:8001/api/v1/roles/?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch roles');
      }

      const data = await response.json();
      setRoles(data.roles);
      setTotalPages(Math.ceil(data.total / 10));
    } catch (error) {
      console.error('Error fetching roles:', error);
    } finally {
      setLoading(false);
    }
  }, [currentPage, searchTerm, sortBy, sortOrder]);

  useEffect(() => {
    fetchRoles();
  }, [fetchRoles]);

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
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

  // Handle new role
  const handleNewRole = () => {
    setEditingRoleId(null);
    setShowModal(true);
  };

  // Handle edit role
  const handleEditRole = (role) => {
    setEditingRoleId(role.id);
    setShowModal(true);
  };

  // Handle delete role
  const handleDeleteRole = (role) => {
    setDeletingRole(role);
    setShowDeleteModal(true);
  };

  // Confirm delete role
  const confirmDeleteRole = async () => {
    if (!deletingRole) return;

    setDeleteLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8001/api/v1/roles/${deletingRole.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete role');
      }

      // Refresh the list
      fetchRoles();
      setShowDeleteModal(false);
      setDeletingRole(null);
    } catch (error) {
      console.error('Error deleting role:', error);
      alert('Rol silinirken bir hata oluştu.');
    } finally {
      setDeleteLoading(false);
    }
  };

  // Cancel delete
  const cancelDelete = () => {
    setShowDeleteModal(false);
    setDeletingRole(null);
  };

  // Handle modal close
  const handleModalClose = () => {
    setShowModal(false);
    setEditingRoleId(null);
    fetchRoles();
  };

  // Format date
  const formatDate = (dateString) => {
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
                Rol Yönetimi
              </h2>
              <p className="text-gray-500 text-sm font-normal">
                Sistem rollerini buradan yönetebilirsiniz.
              </p>
            </div>
            <button
              onClick={handleNewRole}
              className="flex items-center justify-center gap-2 min-w-[84px] cursor-pointer overflow-hidden rounded-md h-12 px-6 bg-blue-600 text-white text-base font-bold leading-normal tracking-wide shadow-sm hover:bg-opacity-90 transition-colors"
            >
              <span className="material-symbols-outlined">add</span>
              <span>Yeni Rol Ekle</span>
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
                placeholder="Rol ara..."
                value={searchTerm}
                onChange={handleSearch}
                className="flex w-full min-w-0 rounded-md text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-300 bg-white h-11 placeholder:text-gray-400 pl-10 pr-4 text-base font-normal"
              />
            </div>
            <div className="flex gap-4">
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
                    onClick={() => handleSort('name')}
                  >
                    <div className="flex items-center gap-1">
                      Rol Adı
                      {sortBy === 'name' && (
                        <span className="material-symbols-outlined text-sm">
                          {sortOrder === 'asc' ? 'arrow_upward' : 'arrow_downward'}
                        </span>
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-4 text-sm font-semibold text-gray-600 cursor-pointer hover:bg-gray-100 select-none"
                    onClick={() => handleSort('description')}
                  >
                    <div className="flex items-center gap-1">
                      Açıklama
                      {sortBy === 'description' && (
                        <span className="material-symbols-outlined text-sm">
                          {sortOrder === 'asc' ? 'arrow_upward' : 'arrow_downward'}
                        </span>
                      )}
                    </div>
                  </th>
                  <th className="px-6 py-4 text-sm font-semibold text-gray-600">
                    Yetkiler
                  </th>
                  <th 
                    className="px-6 py-4 text-sm font-semibold text-gray-600 cursor-pointer hover:bg-gray-100 select-none"
                    onClick={() => handleSort('created_at')}
                  >
                    <div className="flex items-center gap-1">
                      Oluşturulma Tarihi
                      {sortBy === 'created_at' && (
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
                {roles.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                      Henüz rol bulunmuyor.
                    </td>
                  </tr>
                ) : (
                  roles.map((role) => (
                    <tr key={role.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {role.name}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {role.description || '-'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {role.permissions && role.permissions.length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {role.permissions.slice(0, 3).map((permission, index) => (
                              <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                {permission}
                              </span>
                            ))}
                            {role.permissions.length > 3 && (
                              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                                +{role.permissions.length - 3} daha
                              </span>
                            )}
                          </div>
                        ) : (
                          '-'
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatDate(role.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-center">
                        <div className="flex items-center justify-center space-x-2">
                          <button
                            onClick={() => handleEditRole(role)}
                            className="text-green-600 hover:text-green-800 p-1"
                            title="Düzenle"
                          >
                            <span className="material-symbols-outlined text-sm">edit</span>
                          </button>
                          <button
                            onClick={() => handleDeleteRole(role)}
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
        <RoleForm
          isOpen={showModal}
          onClose={handleModalClose}
          roleId={editingRoleId}
          onSuccess={fetchRoles}
        />
      )}

      {/* Delete Confirmation Modal */}
      <DeleteConfirmModal
        isOpen={showDeleteModal}
        onClose={cancelDelete}
        onConfirm={confirmDeleteRole}
        title="Rolü Sil"
        message={`"${deletingRole?.name}" rolünü silmek istediğinizden emin misiniz?`}
        itemName={deletingRole?.name}
        isLoading={deleteLoading}
      />
    </div>
  );
};

export default RoleList;