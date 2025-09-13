import React, { useState, useEffect, useCallback } from 'react';
import { format } from 'date-fns';
import { tr } from 'date-fns/locale';
import CaseStudyModal from './CaseStudyModal';
import DeleteConfirmModal from './DeleteConfirmModal';

const CaseStudyList = () => {
  const [caseStudies, setCaseStudies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showModal, setShowModal] = useState(false);
  const [editingCaseStudy, setEditingCaseStudy] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletingCaseStudy, setDeletingCaseStudy] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  // Status options
  const statusOptions = [
    { value: '', label: 'Duruma Göre Filtrele' },
    { value: 'Beklemede', label: 'Beklemede' },
    { value: 'Devam Ediyor', label: 'Devam Ediyor' },
    { value: 'Tamamlandı', label: 'Tamamlandı' },
    { value: 'İptal Edildi', label: 'İptal Edildi' }
  ];

  // Sort options
  const sortOptions = [
    { value: 'created_at', label: 'Tarihe Göre Sırala' },
    { value: 'title', label: 'Başlığa Göre' },
    { value: 'due_date', label: 'Teslim Tarihine Göre' },
    { value: 'status', label: 'Duruma Göre' }
  ];

  // Fetch case studies
  const fetchCaseStudies = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      console.log('CaseStudyList - Token:', token ? 'Token exists' : 'No token');
      console.log('CaseStudyList - Token value:', token);
      
      if (!token) {
        console.error('No token found in localStorage');
        // Redirect to login if no token
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

      const response = await fetch(`http://localhost:8001/api/v1/case-studies/?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch case studies');
      }

      const data = await response.json();
      setCaseStudies(data.case_studies);
      setTotalPages(Math.ceil(data.total / 10));
    } catch (error) {
      console.error('Error fetching case studies:', error);
    } finally {
      setLoading(false);
    }
  }, [currentPage, searchTerm, statusFilter, sortBy, sortOrder]);

  useEffect(() => {
    fetchCaseStudies();
  }, [fetchCaseStudies]);

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

  // Handle new case study
  const handleNewCaseStudy = () => {
    setEditingCaseStudy(null);
    setShowModal(true);
  };

  // Handle edit case study
  const handleEditCaseStudy = (caseStudy) => {
    setEditingCaseStudy(caseStudy);
    setShowModal(true);
  };

  // Handle view case study
  const handleViewCaseStudy = (caseStudy) => {
    setEditingCaseStudy({...caseStudy, viewOnly: true});
    setShowModal(true);
  };

  // Handle delete case study
  const handleDeleteCaseStudy = (caseStudy) => {
    setDeletingCaseStudy(caseStudy);
    setShowDeleteModal(true);
  };

  // Confirm delete case study
  const confirmDeleteCaseStudy = async () => {
    if (!deletingCaseStudy) return;

    setDeleteLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8001/api/v1/case-studies/${deletingCaseStudy.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete case study');
      }

      // Refresh the list
      fetchCaseStudies();
      setShowDeleteModal(false);
      setDeletingCaseStudy(null);
    } catch (error) {
      console.error('Error deleting case study:', error);
      alert('Vaka çalışması silinirken bir hata oluştu.');
    } finally {
      setDeleteLoading(false);
    }
  };

  // Cancel delete
  const cancelDelete = () => {
    setShowDeleteModal(false);
    setDeletingCaseStudy(null);
  };

  // Handle modal close
  const handleModalClose = () => {
    setShowModal(false);
    setEditingCaseStudy(null);
    fetchCaseStudies();
  };

  // Get status badge class
  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'Tamamlandı':
        return 'bg-green-100 text-green-800';
      case 'Devam Ediyor':
        return 'bg-blue-100 text-blue-800';
      case 'Beklemede':
        return 'bg-yellow-100 text-yellow-800';
      case 'İptal Edildi':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Format date
  const formatDate = (dateString) => {
    return format(new Date(dateString), 'dd.MM.yyyy', { locale: tr });
  };

  return (
    <div className="p-6 lg:p-8">
      <div className="flex flex-col flex-1 bg-white rounded-xl shadow-sm border border-gray-200">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex flex-wrap justify-between items-center gap-4">
            <div className="flex flex-col gap-1">
              <h2 className="text-2xl font-bold leading-tight tracking-[-0.015em]">
                Vaka Çalışmaları
              </h2>
              <p className="text-gray-500 text-sm font-normal">
                Adaylara atanan vaka çalışmalarını buradan takip edebilirsiniz.
              </p>
            </div>
            <button
              onClick={handleNewCaseStudy}
              className="flex items-center justify-center gap-2 min-w-[84px] cursor-pointer overflow-hidden rounded-md h-12 px-6 bg-blue-600 text-white text-base font-bold leading-normal tracking-wide shadow-sm hover:bg-opacity-90 transition-colors"
            >
              <span className="material-symbols-outlined">add</span>
              <span>Yeni Vaka Çalışması Ata</span>
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
                placeholder="Başlık veya adaya göre ara..."
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
                    onClick={() => handleSort('title')}
                  >
                    <div className="flex items-center gap-1">
                      Vaka Çalışması Başlığı
                      {sortBy === 'title' && (
                        <span className="material-symbols-outlined text-sm">
                          {sortOrder === 'asc' ? 'arrow_upward' : 'arrow_downward'}
                        </span>
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-4 text-sm font-semibold text-gray-600 cursor-pointer hover:bg-gray-100 select-none"
                    onClick={() => handleSort('candidate_name')}
                  >
                    <div className="flex items-center gap-1">
                      Aday
                      {sortBy === 'candidate_name' && (
                        <span className="material-symbols-outlined text-sm">
                          {sortOrder === 'asc' ? 'arrow_upward' : 'arrow_downward'}
                        </span>
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-4 text-sm font-semibold text-gray-600 cursor-pointer hover:bg-gray-100 select-none"
                    onClick={() => handleSort('due_date')}
                  >
                    <div className="flex items-center gap-1">
                      Son Teslim Tarihi
                      {sortBy === 'due_date' && (
                        <span className="material-symbols-outlined text-sm">
                          {sortOrder === 'asc' ? 'arrow_upward' : 'arrow_downward'}
                        </span>
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-4 text-sm font-semibold text-gray-600 text-center cursor-pointer hover:bg-gray-100 select-none"
                    onClick={() => handleSort('status')}
                  >
                    <div className="flex items-center justify-center gap-1">
                      Durum
                      {sortBy === 'status' && (
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
                {caseStudies.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                      Henüz vaka çalışması bulunmuyor.
                    </td>
                  </tr>
                ) : (
                  caseStudies.map((caseStudy) => (
                    <tr key={caseStudy.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {caseStudy.title}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {caseStudy.candidate_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatDate(caseStudy.due_date)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeClass(caseStudy.status)}`}>
                          {caseStudy.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-center">
                        <div className="flex items-center justify-center space-x-2">
                          <button
                            onClick={() => handleViewCaseStudy(caseStudy)}
                            className="text-blue-600 hover:text-blue-800 p-1"
                            title="Görüntüle"
                          >
                            <span className="material-symbols-outlined text-sm">visibility</span>
                          </button>
                          <button
                            onClick={() => handleEditCaseStudy(caseStudy)}
                            className="text-green-600 hover:text-green-800 p-1"
                            title="Düzenle"
                          >
                            <span className="material-symbols-outlined text-sm">edit</span>
                          </button>
                          <button
                            onClick={() => handleDeleteCaseStudy(caseStudy)}
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
        <CaseStudyModal
          caseStudy={editingCaseStudy}
          onClose={handleModalClose}
          onSave={fetchCaseStudies}
        />
      )}

      {/* Delete Confirmation Modal */}
      <DeleteConfirmModal
        isOpen={showDeleteModal}
        onClose={cancelDelete}
        onConfirm={confirmDeleteCaseStudy}
        title="Vaka Çalışmasını Sil"
        message={`"${deletingCaseStudy?.title}" vaka çalışmasını silmek istediğinizden emin misiniz?`}
        itemName={deletingCaseStudy?.title}
        isLoading={deleteLoading}
      />
    </div>
  );
};

export default CaseStudyList;
