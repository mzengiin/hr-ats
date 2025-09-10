import React, { useState, useEffect } from 'react';
import { searchCandidates } from '../services/api';

const CandidateSearchModal = ({ isOpen, onClose, onSelect }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  // Aday arama fonksiyonu
  const handleSearch = async (term) => {
    if (term.length < 2) {
      setCandidates([]);
      return;
    }

    setLoading(true);
    try {
      const response = await searchCandidates(term);
      console.log('Search response:', response.data);
      // API response format: { candidates: [...], total: ... }
      setCandidates(response.data.candidates || []);
    } catch (error) {
      console.error('Aday arama hatası:', error);
      setCandidates([]);
    } finally {
      setLoading(false);
    }
  };

  // Debounced search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      handleSearch(searchTerm);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm]);

  // Modal açıldığında temizle
  useEffect(() => {
    if (isOpen) {
      setSearchTerm('');
      setCandidates([]);
      setSelectedCandidate(null);
    }
  }, [isOpen]);

  const handleCandidateSelect = (candidate) => {
    setSelectedCandidate(candidate);
    // Otomatik olarak seçimi onayla
    onSelect(candidate);
  };

  const handleConfirmSelection = () => {
    if (selectedCandidate) {
      console.log('CandidateSearchModal - Confirming selection:', selectedCandidate);
      onSelect(selectedCandidate);
    }
  };

  const formatPhone = (phone) => {
    if (!phone) return '';
    // Basit telefon formatı
    return phone.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Başvurdu':
        return 'bg-blue-100 text-blue-800';
      case 'İnceleme':
        return 'bg-yellow-100 text-yellow-800';
      case 'Mülakat':
        return 'bg-purple-100 text-purple-800';
      case 'Teklif':
        return 'bg-green-100 text-green-800';
      case 'İşe Alındı':
        return 'bg-emerald-100 text-emerald-800';
      case 'Reddedildi':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Aday Ara ve Seç</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Search Input */}
        <div className="p-6 border-b border-gray-200">
          <div className="relative">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Aday adı, pozisyon veya email ile ara..."
              className="w-full px-4 py-3 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
              <span className="material-symbols-outlined">search</span>
            </span>
            {loading && (
              <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                <span className="material-symbols-outlined animate-spin">refresh</span>
              </span>
            )}
          </div>
        </div>

        {/* Results */}
        <div className="flex-1 overflow-y-auto">
          {searchTerm.length < 2 ? (
            <div className="p-6 text-center text-gray-500">
              <span className="material-symbols-outlined text-4xl mb-2">search</span>
              <p>Arama yapmak için en az 2 karakter girin</p>
            </div>
          ) : candidates.length === 0 && !loading ? (
            <div className="p-6 text-center text-gray-500">
              <span className="material-symbols-outlined text-4xl mb-2">person_search</span>
              <p>"{searchTerm}" için aday bulunamadı</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {candidates.map((candidate) => (
                <div
                  key={candidate.id}
                  onClick={() => handleCandidateSelect(candidate)}
                  className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                    selectedCandidate?.id === candidate.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {candidate.first_name} {candidate.last_name}
                        </h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(candidate.status)}`}>
                          {candidate.status}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-sm">work</span>
                          <span>{candidate.position}</span>
                        </div>
                        
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-sm">email</span>
                          <span>{candidate.email}</span>
                        </div>
                        
                        {candidate.phone && (
                          <div className="flex items-center gap-2">
                            <span className="material-symbols-outlined text-sm">phone</span>
                            <span>{formatPhone(candidate.phone)}</span>
                          </div>
                        )}
                        
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-sm">calendar_month</span>
                          <span>{new Date(candidate.application_date).toLocaleDateString('tr-TR')}</span>
                        </div>
                      </div>

                      {candidate.notes && (
                        <div className="mt-2 text-sm text-gray-500">
                          <span className="font-medium">Notlar:</span> {candidate.notes}
                        </div>
                      )}

                      {candidate.cv_file_path && (
                        <div className="mt-2 flex items-center gap-2 text-sm text-blue-600">
                          <span className="material-symbols-outlined text-sm">description</span>
                          <span>CV dosyası mevcut</span>
                        </div>
                      )}
                    </div>

                    {selectedCandidate?.id === candidate.id && (
                      <div className="flex items-center text-blue-600">
                        <span className="material-symbols-outlined">check_circle</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            İptal
          </button>
          <button
            onClick={handleConfirmSelection}
            disabled={!selectedCandidate}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            Seç
          </button>
        </div>
      </div>
    </div>
  );
};

export default CandidateSearchModal;
