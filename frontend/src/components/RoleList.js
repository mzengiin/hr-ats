import React, { useState, useEffect } from 'react';
import api from '../services/api';
import RoleForm from './RoleForm';

const RoleList = () => {
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [itemsPerPage] = useState(10);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRoleId, setEditingRoleId] = useState(null);

  useEffect(() => {
    fetchRoles();
  }, [currentPage, searchTerm]);

  const fetchRoles = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/roles?page=${currentPage}&limit=${itemsPerPage}&search=${searchTerm}`);
      
      if (response.data.success) {
        setRoles(response.data.data.roles);
        setTotalPages(response.data.data.total_pages);
      } else {
        setError('Roller yüklenirken hata oluştu');
      }
    } catch (error) {
      console.error('Error fetching roles:', error);
      setError('Roller yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  const handleEdit = (roleId) => {
    setEditingRoleId(roleId);
    setIsModalOpen(true);
  };

  const handleAddNew = () => {
    setEditingRoleId(null);
    setIsModalOpen(true);
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    setEditingRoleId(null);
  };

  const handleModalSuccess = () => {
    fetchRoles();
  };

  const handleDelete = async (roleId) => {
    if (window.confirm('Bu rolü silmek istediğinizden emin misiniz?')) {
      try {
        const response = await api.delete(`/roles/${roleId}`);
        if (response.data.success) {
          fetchRoles();
        } else {
          alert('Rol silinirken hata oluştu');
        }
      } catch (error) {
        console.error('Error deleting role:', error);
        alert('Rol silinirken hata oluştu');
      }
    }
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#137fec]"></div>
      </div>
    );
  }

  return (
    <div className="bg-[#F8F9FA] min-h-screen">
      <main className="p-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Rol Yönetimi</h1>
            <p className="text-gray-600 mt-2">Sistem rollerini yönetin</p>
          </div>
          <button
            onClick={handleAddNew}
            className="flex items-center gap-2 px-4 py-2.5 text-sm font-semibold text-white bg-[#137fec] rounded-lg shadow-sm hover:bg-blue-700 transition-colors"
          >
            <span className="material-symbols-outlined">add</span>
            Yeni Rol Ekle
          </button>
        </div>

        {/* Search and Filters */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 mb-6">
          <div className="flex gap-4 items-center">
            <div className="flex-1">
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                  search
                </span>
                <input
                  type="text"
                  placeholder="Rol ara..."
                  value={searchTerm}
                  onChange={handleSearch}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Roles Table */}
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-gray-50 text-gray-500 uppercase tracking-wider text-xs">
                <tr>
                  <th className="px-6 py-3" scope="col">Rol Adı</th>
                  <th className="px-6 py-3" scope="col">Açıklama</th>
                  <th className="px-6 py-3" scope="col">Kullanıcı Sayısı</th>
                  <th className="px-6 py-3" scope="col">Oluşturulma Tarihi</th>
                  <th className="px-6 py-3" scope="col">Durum</th>
                  <th className="px-6 py-3" scope="col">İşlemler</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {roles.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                      <span className="material-symbols-outlined text-4xl text-gray-300 mb-4 block">admin_panel_settings</span>
                      <p>Henüz rol bulunmuyor</p>
                    </td>
                  </tr>
                ) : (
                  roles.map((role) => (
                    <tr key={role.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="p-2 bg-blue-100 rounded-lg mr-3">
                            <span className="material-symbols-outlined text-blue-600 text-lg">admin_panel_settings</span>
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">{role.name}</div>
                            <div className="text-gray-500 text-sm">{role.code}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-gray-500 max-w-xs">
                        <div className="truncate">{role.description || 'Açıklama yok'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-500">
                        {role.user_count || 0} kullanıcı
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-500">
                        {new Date(role.created_at).toLocaleDateString('tr-TR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2.5 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          role.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {role.is_active ? 'Aktif' : 'Pasif'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleEdit(role.id)}
                            className="text-[#137fec] hover:text-blue-700 transition-colors"
                          >
                            <span className="material-symbols-outlined text-lg">edit</span>
                          </button>
                          <button
                            onClick={() => handleDelete(role.id)}
                            className="text-red-600 hover:text-red-700 transition-colors"
                          >
                            <span className="material-symbols-outlined text-lg">delete</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
              <div className="flex-1 flex justify-between sm:hidden">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Önceki
                </button>
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Sonraki
                </button>
              </div>
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700">
                    Sayfa <span className="font-medium">{currentPage}</span> / <span className="font-medium">{totalPages}</span>
                  </p>
                </div>
                <div>
                  <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                    <button
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <span className="material-symbols-outlined">chevron_left</span>
                    </button>
                    {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                      <button
                        key={page}
                        onClick={() => handlePageChange(page)}
                        className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                          page === currentPage
                            ? 'z-10 bg-[#137fec] border-[#137fec] text-white'
                            : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                        }`}
                      >
                        {page}
                      </button>
                    ))}
                    <button
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === totalPages}
                      className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <span className="material-symbols-outlined">chevron_right</span>
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Role Form Modal */}
        <RoleForm
          isOpen={isModalOpen}
          onClose={handleModalClose}
          roleId={editingRoleId}
          onSuccess={handleModalSuccess}
        />
      </main>
    </div>
  );
};

export default RoleList;
