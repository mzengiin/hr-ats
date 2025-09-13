import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { candidatesAPI, handleAPIError } from '../services/api';
import { formatDateToDDMMYYYY } from '../utils/dateUtils';

const CandidateList = () => {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('Tümü');
  const [positionFilter, setPositionFilter] = useState('Tümü');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [perPage] = useState(10);
  const [statusOptions, setStatusOptions] = useState([]);
  const [positionOptions, setPositionOptions] = useState([]);
  const [selectedCandidates, setSelectedCandidates] = useState([]);
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const searchInputRef = useRef(null);
  const [isSearchFocused, setIsSearchFocused] = useState(false);

  // Load candidates function with useCallback
  const loadCandidates = useCallback(async (searchValue = searchTerm) => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        page: currentPage,
        per_page: perPage,
        search: searchValue || undefined,
        status: statusFilter !== 'Tümü' ? statusFilter : undefined,
        position: positionFilter !== 'Tümü' ? positionFilter : undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      };

      const response = await candidatesAPI.getCandidates(params);
      setCandidates(response.data.candidates);
      setTotal(response.data.total);
      setTotalPages(response.data.total_pages);
    } catch (err) {
      setError(handleAPIError(err));
      console.error('Error loading candidates:', err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, perPage, statusFilter, positionFilter, sortBy, sortOrder]);

  // Debounce search term
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Load data when filters change
  useEffect(() => {
    loadCandidates(debouncedSearchTerm);
  }, [loadCandidates, debouncedSearchTerm]);

  // Keep focus on search input after re-render
  useEffect(() => {
    if (isSearchFocused && searchInputRef.current) {
      const cursorPosition = searchInputRef.current.selectionStart;
      setTimeout(() => {
        if (searchInputRef.current) {
          searchInputRef.current.focus();
          searchInputRef.current.setSelectionRange(cursorPosition, cursorPosition);
        }
      }, 0);
    }
  }, [candidates, loading, isSearchFocused]);

  // Load initial data
  useEffect(() => {
    loadOptions();
  }, []);

  const loadOptions = async () => {
    try {
      const response = await candidatesAPI.getOptions();
      const options = response.data;
      
      setStatusOptions(['Tümü', ...options.status_options.map(opt => opt.name)]);
      setPositionOptions(['Tümü', ...options.position_options.map(opt => opt.name)]);
    } catch (err) {
      console.error('Error loading options:', err);
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  const handleSearchFocus = () => {
    setIsSearchFocused(true);
  };

  const handleSearchBlur = () => {
    setIsSearchFocused(false);
  };

  const handleFilterChange = () => {
    setCurrentPage(1);
  };

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
    setCurrentPage(1);
  };

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedCandidates(candidates.map(c => c.id));
    } else {
      setSelectedCandidates([]);
    }
  };

  const handleSelectCandidate = (candidateId) => {
    setSelectedCandidates(prev => 
      prev.includes(candidateId) 
        ? prev.filter(id => id !== candidateId)
        : [...prev, candidateId]
    );
  };

  const handleDeleteCandidate = async (candidateId) => {
    if (window.confirm('Bu adayı silmek istediğinizden emin misiniz?')) {
      try {
        await candidatesAPI.deleteCandidate(candidateId);
        loadCandidates();
        setSelectedCandidates(prev => prev.filter(id => id !== candidateId));
      } catch (err) {
        setError(handleAPIError(err));
      }
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'Başvurdu': 'bg-gray-100 text-gray-800',
      'İnceleme': 'bg-yellow-100 text-yellow-800',
      'Mülakat': 'bg-blue-100 text-blue-800',
      'Teklif': 'bg-green-100 text-green-800',
      'İşe Alındı': 'bg-purple-100 text-purple-800',
      'Reddedildi': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString) => {
    return formatDateToDDMMYYYY(dateString);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#137fec]"></div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8">
      <div className="flex flex-col flex-1 bg-white rounded-xl shadow-sm border border-gray-200">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex flex-wrap justify-between items-center gap-4">
            <div className="flex flex-col gap-1">
              <h2 className="text-2xl font-bold leading-tight tracking-[-0.015em]">
                Adaylar
              </h2>
              <p className="text-gray-500 text-sm font-normal">
                Tüm adayları buradan görüntüleyebilir ve yönetebilirsiniz.
              </p>
            </div>
            <Link
              to="/candidates/new"
              className="flex items-center justify-center gap-2 min-w-[84px] cursor-pointer overflow-hidden rounded-md h-12 px-6 bg-blue-600 text-white text-base font-bold leading-normal tracking-wide shadow-sm hover:bg-opacity-90 transition-colors"
            >
              <span className="material-symbols-outlined">add</span>
              <span>Aday Ekle</span>
            </Link>
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
                ref={searchInputRef}
                type="text"
                placeholder="İsim, pozisyon, e-posta, telefon ile ara..."
                value={searchTerm}
                onChange={handleSearch}
                onFocus={handleSearchFocus}
                onBlur={handleSearchBlur}
                className="flex w-full min-w-0 rounded-md text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-300 bg-white h-11 placeholder:text-gray-400 pl-10 pr-4 text-base font-normal"
              />
            </div>
            <div className="flex gap-4">
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  handleFilterChange();
                }}
                className="flex w-full sm:w-auto min-w-0 rounded-md text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-300 bg-white h-11 px-4 text-sm font-medium"
              >
                {statusOptions.map(option => (
                  <option key={option} value={option}>
                    {option === 'Tümü' ? 'Duruma Göre Filtrele' : option}
                  </option>
                ))}
              </select>
              <select
                value={positionFilter}
                onChange={(e) => {
                  setPositionFilter(e.target.value);
                  handleFilterChange();
                }}
                className="flex w-full sm:w-auto min-w-0 rounded-md text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-300 bg-white h-11 px-4 text-sm font-medium"
              >
                {positionOptions.map(option => (
                  <option key={option} value={option}>
                    {option === 'Tümü' ? 'Pozisyona Göre Filtrele' : option}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mx-6 mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

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
                  <th className="px-6 py-4 text-sm font-semibold text-gray-600">
                    <input
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      type="checkbox"
                      checked={selectedCandidates.length === candidates.length && candidates.length > 0}
                      onChange={handleSelectAll}
                    />
                  </th>
                  <th 
                    className="px-6 py-4 text-sm font-semibold text-gray-600 cursor-pointer hover:bg-gray-100 select-none"
                    onClick={() => handleSort('first_name')}
                  >
                    <div className="flex items-center gap-1">
                      Aday Adı
                      {sortBy === 'first_name' && (
                        <span className="material-symbols-outlined text-sm">
                          {sortOrder === 'asc' ? 'arrow_upward' : 'arrow_downward'}
                        </span>
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-4 text-sm font-semibold text-gray-600 cursor-pointer hover:bg-gray-100 select-none"
                    onClick={() => handleSort('position')}
                  >
                    <div className="flex items-center gap-1">
                      Pozisyon
                      {sortBy === 'position' && (
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
                  <th 
                    className="px-6 py-4 text-sm font-semibold text-gray-600 cursor-pointer hover:bg-gray-100 select-none"
                    onClick={() => handleSort('application_date')}
                  >
                    <div className="flex items-center gap-1">
                      Başvuru Tarihi
                      {sortBy === 'application_date' && (
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
                {candidates.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                      Henüz aday bulunmuyor.
                    </td>
                  </tr>
                ) : (
                  candidates.map((candidate) => (
                    <tr key={candidate.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <input
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          type="checkbox"
                          checked={selectedCandidates.includes(candidate.id)}
                          onChange={() => handleSelectCandidate(candidate.id)}
                        />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {candidate.first_name} {candidate.last_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {candidate.position}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(candidate.status)}`}>
                          {candidate.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatDate(candidate.application_date)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-center">
                        <div className="flex items-center justify-center space-x-2">
                          <Link
                            to={`/candidates/${candidate.id}`}
                            className="text-blue-600 hover:text-blue-800 p-1"
                            title="Görüntüle"
                          >
                            <span className="material-symbols-outlined text-sm">visibility</span>
                          </Link>
                          <Link
                            to={`/candidates/${candidate.id}/edit`}
                            className="text-green-600 hover:text-green-800 p-1"
                            title="Düzenle"
                          >
                            <span className="material-symbols-outlined text-sm">edit</span>
                          </Link>
                          <button
                            onClick={() => handleDeleteCandidate(candidate.id)}
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
              <span className="font-semibold text-gray-800">{total}</span> adaydan{' '}
              <span className="font-semibold text-gray-800">
                {((currentPage - 1) * perPage) + 1}-{Math.min(currentPage * perPage, total)}
              </span> arası gösteriliyor
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
    </div>
  );
};

export default CandidateList;
