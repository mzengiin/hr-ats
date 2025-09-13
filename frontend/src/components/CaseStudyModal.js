import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import CandidateSearchModal from './CandidateSearchModal';

const CaseStudyModal = ({ caseStudy, onClose, onSave }) => {
  const isViewOnly = caseStudy?.viewOnly || false;
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    candidate: null,
    candidate_id: '',
    due_date: new Date(),
    status: 'Beklemede',
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [showCandidateSearch, setShowCandidateSearch] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [fileLoading, setFileLoading] = useState(false);

  // Status options
  const statusOptions = [
    { value: 'Beklemede', label: 'Beklemede' },
    { value: 'Devam Ediyor', label: 'Devam Ediyor' },
    { value: 'Tamamlandı', label: 'Tamamlandı' },
    { value: 'İptal Edildi', label: 'İptal Edildi' }
  ];

  // Initialize form data
  useEffect(() => {
    if (caseStudy) {
      setFormData({
        title: caseStudy.title || '',
        description: caseStudy.description || '',
        candidate: caseStudy.candidate_name ? {
          id: caseStudy.candidate_id,
          first_name: caseStudy.candidate_name.split(' ')[0] || '',
          last_name: caseStudy.candidate_name.split(' ').slice(1).join(' ') || '',
          position: ''
        } : null,
        candidate_id: caseStudy.candidate_id || '',
        due_date: caseStudy.due_date ? new Date(caseStudy.due_date) : new Date(),
        status: caseStudy.status || 'Beklemede',
        notes: caseStudy.notes || ''
      });
      
      // Set uploaded file if exists
      if (caseStudy.file_path) {
        setUploadedFile({
          name: caseStudy.file_path.split('/').pop() || 'Dosya',
          path: caseStudy.file_path,
          type: caseStudy.file_path.split('.').pop()?.toLowerCase() || 'unknown'
        });
      }
    }
  }, [caseStudy]);

  // Handle candidate selection from search modal
  const handleCandidateSelect = (candidate) => {
    setFormData(prev => ({
      ...prev,
      candidate: candidate,
      candidate_id: candidate.id
    }));
    setShowCandidateSearch(false);
  };

  // Handle form input changes
  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.candidate) {
      newErrors.candidate = 'Aday seçimi zorunludur';
    }
    
    if (!formData.title.trim()) {
      newErrors.title = 'Vaka çalışması başlığı zorunludur';
    }
    
    if (!formData.due_date) {
      newErrors.due_date = 'Son teslim tarihi zorunludur';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('Oturum süreniz dolmuş. Lütfen tekrar giriş yapın.');
        window.location.href = '/login';
        return;
      }

      const url = caseStudy 
        ? `http://localhost:8001/api/v1/case-studies/${caseStudy.id}`
        : 'http://localhost:8001/api/v1/case-studies/';
      
      const method = caseStudy ? 'PUT' : 'POST';

      // Prepare data for API
      const apiData = {
        title: formData.title,
        description: formData.description,
        candidate_id: formData.candidate_id,
        due_date: formData.due_date.toISOString(),
        status: formData.status,
        notes: formData.notes
      };

      console.log('Sending request to:', url);
      console.log('Request data:', apiData);
      console.log('Token:', token ? 'Present' : 'Missing');

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(apiData)
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        if (response.status === 401) {
          alert('Oturum süreniz dolmuş. Lütfen tekrar giriş yapın.');
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user_data');
          window.location.href = '/login';
          return;
        }
        const errorText = await response.text();
        console.error('API Error:', errorText);
        throw new Error(`Failed to save case study: ${response.status} ${errorText}`);
      }

      const result = await response.json();
      
      // If there's a file to upload and it's a new case study
      if (uploadedFile && uploadedFile.file && !caseStudy) {
        try {
          const fileFormData = new FormData();
          fileFormData.append('file', uploadedFile.file);

          const fileResponse = await fetch(`http://localhost:8001/api/v1/case-studies/${result.id}/upload`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`
            },
            body: fileFormData
          });

          if (fileResponse.ok) {
            const fileResult = await fileResponse.json();
            console.log('File uploaded successfully:', fileResult);
          }
        } catch (fileError) {
          console.error('Error uploading file:', fileError);
          // Don't fail the whole operation if file upload fails
        }
      }

      onSave();
      onClose();
    } catch (error) {
      console.error('Error saving case study:', error);
      alert('Vaka çalışması kaydedilirken hata oluştu: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle file upload
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // If it's a new case study, just store the file locally for now
    if (!caseStudy) {
      setUploadedFile({
        name: file.name,
        path: null, // Will be set after saving
        type: file.type.split('/')[1] || file.name.split('.').pop()?.toLowerCase() || 'unknown',
        file: file // Store the actual file object
      });
      alert('Dosya seçildi. Vaka çalışmasını kaydettikten sonra dosya yüklenecek.');
      return;
    }

    setFileLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`http://localhost:8001/api/v1/case-studies/${caseStudy.id}/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to upload file');
      }

      const result = await response.json();
      
      // Update uploaded file state
      setUploadedFile({
        name: file.name,
        path: result.file_path,
        type: file.type.split('/')[1] || file.name.split('.').pop()?.toLowerCase() || 'unknown'
      });

      alert('Dosya başarıyla yüklendi.');
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Dosya yüklenirken hata oluştu.');
    } finally {
      setFileLoading(false);
    }
  };

  // Handle file download
  const handleFileDownload = () => {
    if (uploadedFile) {
      const link = document.createElement('a');
      link.href = `http://localhost:8001/api/v1/files/download?path=${encodeURIComponent(uploadedFile.path)}`;
      link.download = uploadedFile.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  // Handle file delete
  const handleFileDelete = async () => {
    if (!uploadedFile || !caseStudy) return;

    if (window.confirm('Dosyayı silmek istediğinizden emin misiniz?')) {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`http://localhost:8001/api/v1/case-studies/${caseStudy.id}/file`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to delete file');
        }

        setUploadedFile(null);
        alert('Dosya başarıyla silindi.');
      } catch (error) {
        console.error('Error deleting file:', error);
        alert('Dosya silinirken hata oluştu.');
      }
    }
  };

  // Handle file view (for PDF)
  const handleFileView = () => {
    if (uploadedFile && uploadedFile.type === 'pdf') {
      window.open(`http://localhost:8001/api/v1/files/download?path=${encodeURIComponent(uploadedFile.path)}`, '_blank');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[95vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {isViewOnly ? 'Vaka Çalışmasını Görüntüle' : (caseStudy ? 'Vaka Çalışmasını Düzenle' : 'Yeni Vaka Çalışması Ata')}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Form */}
        <form id="case-study-form" onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-4">
          {/* Aday Seçimi */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Aday Seçimi *
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={formData.candidate ? 
                  `${formData.candidate.first_name || ''} ${formData.candidate.last_name || ''}`.trim() + 
                  (formData.candidate.first_name || formData.candidate.last_name ? ' - ' : '') + 
                  formData.candidate.position : ''}
                placeholder="Aday seçmek için tıklayın"
                readOnly
                className={`flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.candidate ? 'border-red-500' : ''
                } ${isViewOnly ? 'bg-gray-50' : ''}`}
              />
              {!isViewOnly && (
                <button
                  type="button"
                  onClick={() => setShowCandidateSearch(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
                >
                  <span className="material-symbols-outlined text-sm">search</span>
                </button>
              )}
            </div>
            {errors.candidate && (
              <p className="mt-1 text-sm text-red-600">{errors.candidate}</p>
            )}
          </div>

          {/* Vaka Çalışması Başlığı */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Vaka Çalışması Başlığı *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              readOnly={isViewOnly}
              className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.title ? 'border-red-500' : ''
              } ${isViewOnly ? 'bg-gray-50' : ''}`}
              placeholder="Örn: Frontend Geliştirici Rolü İçin Tasarım"
            />
            {errors.title && (
              <p className="mt-1 text-sm text-red-600">{errors.title}</p>
            )}
          </div>

          {/* Açıklama */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Açıklama
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              placeholder="Vaka çalışması ile ilgili detaylı açıklamaları buraya yazın."
              rows="4"
              readOnly={isViewOnly}
              className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none ${isViewOnly ? 'bg-gray-50' : ''}`}
            />
          </div>

          {/* Tarih ve Durum */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Son Teslim Tarihi *
              </label>
              <DatePicker
                selected={formData.due_date}
                onChange={(date) => handleInputChange('due_date', date)}
                dateFormat="dd.MM.yyyy"
                readOnly={isViewOnly}
                className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.due_date ? 'border-red-500' : ''
                } ${isViewOnly ? 'bg-gray-50' : ''}`}
                placeholderText="Tarih seçin"
                showTimeSelect={false}
                locale="tr"
              />
              {errors.due_date && (
                <p className="mt-1 text-sm text-red-600">{errors.due_date}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Durum
              </label>
              <select
                value={formData.status}
                onChange={(e) => handleInputChange('status', e.target.value)}
                disabled={isViewOnly}
                className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 h-[42px] ${isViewOnly ? 'bg-gray-50' : ''}`}
              >
                {statusOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Notlar */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notlar
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              placeholder="Ek notlar..."
              rows="3"
              readOnly={isViewOnly}
              className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none ${isViewOnly ? 'bg-gray-50' : ''}`}
            />
          </div>

          {/* Dosya Yükleme */}
          {!isViewOnly && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Vaka Çalışması Dosyası
              </label>
            
            {uploadedFile ? (
              // Show uploaded file
              <div className="mt-1 p-4 border border-gray-300 rounded-md bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      {uploadedFile.type === 'pdf' ? (
                        <span className="material-symbols-outlined text-red-500 text-2xl">picture_as_pdf</span>
                      ) : uploadedFile.type === 'doc' || uploadedFile.type === 'docx' ? (
                        <span className="material-symbols-outlined text-blue-500 text-2xl">description</span>
                      ) : (
                        <span className="material-symbols-outlined text-gray-500 text-2xl">insert_drive_file</span>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {uploadedFile.name}
                      </p>
                      <p className="text-sm text-gray-500 capitalize">
                        {uploadedFile.type} dosyası
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {uploadedFile.type === 'pdf' && (
                      <button
                        type="button"
                        onClick={handleFileView}
                        className="text-blue-600 hover:text-blue-800 p-1"
                        title="Görüntüle"
                      >
                        <span className="material-symbols-outlined text-sm">visibility</span>
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={handleFileDownload}
                      className="text-green-600 hover:text-green-800 p-1"
                      title="İndir"
                    >
                      <span className="material-symbols-outlined text-sm">download</span>
                    </button>
                    <button
                      type="button"
                      onClick={handleFileDelete}
                      className="text-red-600 hover:text-red-800 p-1"
                      title="Sil"
                    >
                      <span className="material-symbols-outlined text-sm">delete</span>
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              // Show upload area
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                <div className="space-y-1 text-center">
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400"
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 48 48"
                  >
                    <path
                      d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                    />
                  </svg>
                  <div className="flex text-sm text-gray-600">
                    <label className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                      <span>{fileLoading ? 'Yükleniyor...' : 'Dosya yükle'}</span>
                      <input
                        type="file"
                        className="sr-only"
                        onChange={handleFileUpload}
                        accept=".pdf,.doc,.docx,.png,.jpg,.jpeg"
                        disabled={fileLoading}
                      />
                    </label>
                    <p className="pl-1">veya sürükleyip bırakın</p>
                  </div>
                  <p className="text-xs text-gray-500">
                    PNG, JPG, PDF up to 10MB
                  </p>
                </div>
              </div>
            )}
            </div>
          )}

          {/* Dosya Görüntüleme (View Only) */}
          {isViewOnly && uploadedFile && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Vaka Çalışması Dosyası
              </label>
              <div className="mt-1 p-4 border border-gray-300 rounded-md bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      {uploadedFile.type === 'pdf' ? (
                        <span className="material-symbols-outlined text-red-500 text-2xl">picture_as_pdf</span>
                      ) : uploadedFile.type === 'doc' || uploadedFile.type === 'docx' ? (
                        <span className="material-symbols-outlined text-blue-500 text-2xl">description</span>
                      ) : (
                        <span className="material-symbols-outlined text-gray-500 text-2xl">insert_drive_file</span>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {uploadedFile.name}
                      </p>
                      <p className="text-sm text-gray-500 capitalize">
                        {uploadedFile.type} dosyası
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {uploadedFile.type === 'pdf' && (
                      <button
                        type="button"
                        onClick={handleFileView}
                        className="text-blue-600 hover:text-blue-800 p-1"
                        title="Görüntüle"
                      >
                        <span className="material-symbols-outlined text-sm">visibility</span>
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={handleFileDownload}
                      className="text-green-600 hover:text-green-800 p-1"
                      title="İndir"
                    >
                      <span className="material-symbols-outlined text-sm">download</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </form>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50">
          {isViewOnly ? (
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Kapat
            </button>
          ) : (
            <>
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                İptal
              </button>
              <button
                type="submit"
                form="case-study-form"
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Kaydediliyor...' : (caseStudy ? 'Güncelle' : 'Oluştur')}
              </button>
            </>
          )}
        </div>
      </div>

      {/* Candidate Search Modal */}
      <CandidateSearchModal
        isOpen={showCandidateSearch}
        onClose={() => setShowCandidateSearch(false)}
        onSelect={handleCandidateSelect}
      />
    </div>
  );
};

export default CaseStudyModal;
