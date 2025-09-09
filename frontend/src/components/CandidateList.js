import React, { useState, useEffect } from 'react';
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

  // Load initial data
  useEffect(() => {
    loadCandidates();
    loadOptions();
  }, [currentPage, searchTerm, statusFilter, positionFilter]);

  const loadCandidates = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        page: currentPage,
        per_page: perPage,
        search: searchTerm || undefined,
        status: statusFilter !== 'Tümü' ? statusFilter : undefined,
        position: positionFilter !== 'Tümü' ? positionFilter : undefined,
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
  };

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
    e.preventDefault();
    setCurrentPage(1);
    loadCandidates();
  };

  const handleFilterChange = () => {
    setCurrentPage(1);
    loadCandidates();
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
    <div className="bg-[#F8F9FA] min-h-screen">
      <main className="p-8">
        <div className="mx-auto max-w-full">
          {/* Header */}
          <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
            <h2 className="text-2xl font-bold text-gray-900">Adaylar</h2>
            <Link
              to="/candidates/new"
              className="flex min-w-[120px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-11 px-5 bg-[#137fec] text-white text-base font-semibold leading-normal shadow-sm hover:bg-blue-700 transition-colors"
            >
              <span className="material-symbols-outlined text-xl">add</span>
              <span className="truncate">Aday Ekle</span>
            </Link>
          </div>

          {/* Search and Filters */}
          <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-4 flex-1">
              <form onSubmit={handleSearch} className="relative flex-1 max-w-md">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">search</span>
                <input
                  className="w-full min-w-[250px] resize-none overflow-hidden rounded-md text-gray-800 focus:outline-0 focus:ring-2 focus:ring-[#137fec] border border-gray-300 bg-white h-11 placeholder:text-gray-500 pl-10 pr-4 text-sm font-normal leading-normal"
                  placeholder="İsim, pozisyon, e-posta, telefon ile ara"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </form>
              
              <div className="relative">
                <select
                  className="w-full appearance-none rounded-md border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-700 focus:border-[#137fec] focus:ring-2 focus:ring-[#137fec]/50"
                  value={statusFilter}
                  onChange={(e) => {
                    setStatusFilter(e.target.value);
                    handleFilterChange();
                  }}
                >
                  {statusOptions.map(option => (
                    <option key={option} value={option}>Durum: {option}</option>
                  ))}
                </select>
                <span className="material-symbols-outlined pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">expand_more</span>
              </div>
              
              <div className="relative">
                <select
                  className="w-full appearance-none rounded-md border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-700 focus:border-[#137fec] focus:ring-2 focus:ring-[#137fec]/50"
                  value={positionFilter}
                  onChange={(e) => {
                    setPositionFilter(e.target.value);
                    handleFilterChange();
                  }}
                >
                  {positionOptions.map(option => (
                    <option key={option} value={option}>Pozisyon: {option}</option>
                  ))}
                </select>
                <span className="material-symbols-outlined pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">expand_more</span>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}

          {/* Table */}
          <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <p className="text-sm text-gray-600">
                <span className="font-semibold text-gray-800">{total}</span> adaydan{' '}
                <span className="font-semibold text-gray-800">
                  {((currentPage - 1) * perPage) + 1}-{Math.min(currentPage * perPage, total)}
                </span> arası gösteriliyor
              </p>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">Sırala:</span>
                <button className="flex items-center gap-1 rounded-md px-2 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100">
                  Tarih
                  <span className="material-symbols-outlined text-base">arrow_downward</span>
                </button>
                <button className="flex items-center gap-1 rounded-md px-2 py-1.5 text-sm font-medium text-gray-500 hover:bg-gray-100">
                  İsim
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="border-b border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                      <input
                        className="rounded border-gray-300 text-[#137fec] focus:ring-[#137fec]/50"
                        type="checkbox"
                        checked={selectedCandidates.length === candidates.length && candidates.length > 0}
                        onChange={handleSelectAll}
                      />
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Aday Adı</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Pozisyon</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Durum</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Başvuru Tarihi</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">İşlemler</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {candidates.map((candidate) => (
                    <tr key={candidate.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 align-middle">
                        <input
                          className="rounded border-gray-300 text-[#137fec] focus:ring-[#137fec]/50"
                          type="checkbox"
                          checked={selectedCandidates.includes(candidate.id)}
                          onChange={() => handleSelectCandidate(candidate.id)}
                        />
                      </td>
                      <td className="px-4 py-3 text-sm font-medium text-gray-800 align-middle">
                        {candidate.first_name} {candidate.last_name}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600 align-middle">
                        {candidate.position}
                      </td>
                      <td className="px-4 py-3 align-middle">
                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusColor(candidate.status)}`}>
                          {candidate.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600 align-middle">
                        {formatDate(candidate.application_date)}
                      </td>
                      <td className="px-4 py-3 text-right align-middle">
                        <div className="flex items-center gap-2">
                          <Link
                            to={`/candidates/${candidate.id}`}
                            className="p-1.5 text-gray-500 hover:text-[#137fec]"
                            title="Detayları Görüntüle"
                          >
                            <span className="material-symbols-outlined text-lg">visibility</span>
                          </Link>
                          <Link
                            to={`/candidates/${candidate.id}/edit`}
                            className="p-1.5 text-gray-500 hover:text-green-600"
                            title="Düzenle"
                          >
                            <span className="material-symbols-outlined text-lg">edit</span>
                          </Link>
                          <button
                            onClick={() => handleDeleteCandidate(candidate.id)}
                            className="p-1.5 text-gray-500 hover:text-red-600"
                            title="Sil"
                          >
                            <span className="material-symbols-outlined text-lg">delete</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="mt-6 flex items-center justify-between">
              <button
                className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
              >
                Önceki
              </button>
              
              <nav className="flex items-center gap-2">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const pageNum = i + 1;
                  return (
                    <button
                      key={pageNum}
                      className={`flex size-8 items-center justify-center rounded-md text-sm font-medium ${
                        currentPage === pageNum
                          ? 'bg-[#137fec] text-white'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                      onClick={() => setCurrentPage(pageNum)}
                    >
                      {pageNum}
                    </button>
                  );
                })}
                {totalPages > 5 && (
                  <>
                    <span className="text-gray-500">...</span>
                    <button
                      className="flex size-8 items-center justify-center rounded-md text-sm font-medium text-gray-600 hover:bg-gray-100"
                      onClick={() => setCurrentPage(totalPages)}
                    >
                      {totalPages}
                    </button>
                  </>
                )}
              </nav>
              
              <button
                className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
              >
                Sonraki
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default CandidateList;
