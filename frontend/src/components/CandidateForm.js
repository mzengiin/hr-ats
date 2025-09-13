import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import InputMask from 'react-input-mask';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { registerLocale, setDefaultLocale } from 'react-datepicker';
import { tr } from 'date-fns/locale';
import { candidatesAPI, handleAPIError } from '../services/api';
import { formatDateToDDMMYYYY, formatDateToYYYYMMDD, parseDDMMYYYY } from '../utils/dateUtils';
import DeleteConfirmModal from './DeleteConfirmModal';

// Register Turkish locale
registerLocale('tr', tr);
setDefaultLocale('tr');
// Native file download without external library

const CandidateForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEdit = Boolean(id);

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    position: '',
    application_channel: '',
    application_date: '',
    hr_specialist: '',
    status: '',
    notes: ''
  });

  const [displayDate, setDisplayDate] = useState('');

  const [cvFile, setCvFile] = useState(null);
  const [existingCv, setExistingCv] = useState(null);
  const [showCvUpload, setShowCvUpload] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [errors, setErrors] = useState({});
  const [options, setOptions] = useState({
    positions: [],
    applicationChannels: [],
    statuses: [],
    hrSpecialists: []
  });
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  // Load options and existing data
  useEffect(() => {
    loadOptions();
    if (isEdit) {
      loadCandidate();
    } else {
      // For new candidates, show CV upload by default
      setShowCvUpload(true);
      setExistingCv(null);
    }
  }, [id, isEdit]);

  // Debug formData changes
  useEffect(() => {
    console.log('FormData changed:', formData);
  }, [formData]);

  const loadOptions = async () => {
    try {
      const response = await candidatesAPI.getOptions();
      const optionsData = response.data;

      setOptions(prev => ({
        ...prev,
        positions: optionsData.position_options,
        applicationChannels: optionsData.application_channel_options,
        statuses: optionsData.status_options,
        hrSpecialists: optionsData.hr_specialist_options
      }));
    } catch (err) {
      setError(handleAPIError(err));
    }
  };

  const loadCandidate = async () => {
    try {
      setLoading(true);
      console.log('Loading candidate with ID:', id);
      const response = await candidatesAPI.getCandidate(id);
      const candidate = response.data;
      console.log('Loaded candidate:', candidate);
      
      const newFormData = {
        first_name: candidate.first_name || '',
        last_name: candidate.last_name || '',
        email: candidate.email || '',
        phone: candidate.phone || '',
        position: candidate.position || '',
        application_channel: candidate.application_channel || '',
        application_date: candidate.application_date || '',
        hr_specialist: candidate.hr_specialist || '',
        status: candidate.status || '',
        notes: candidate.notes || ''
      };
      
      console.log('Setting form data:', newFormData);
      setFormData(newFormData);
      
      // Set display date for DD/MM/YYYY format
      if (candidate.application_date) {
        setDisplayDate(formatDateToDDMMYYYY(candidate.application_date));
      }
      
      // Set existing CV info
      if (candidate.cv_file_path) {
        setExistingCv({
          path: candidate.cv_file_path,
          name: candidate.cv_file_path.split('/').pop() || 'CV.pdf'
        });
        setShowCvUpload(false);
      } else {
        setExistingCv(null);
        setShowCvUpload(true);
      }
    } catch (err) {
      console.error('Error loading candidate:', err);
      setError(handleAPIError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
    
    if (name === 'application_date') {
      // Handle date input - convert from YYYY-MM-DD to DD/MM/YYYY for display
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
      
      // Convert to DD/MM/YYYY for display
      if (value) {
        setDisplayDate(formatDateToDDMMYYYY(value));
      } else {
        setDisplayDate('');
      }
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleInvalid = (e) => {
    const fieldName = e.target.name;
    const fieldLabels = {
      'first_name': 'Ad',
      'last_name': 'Soyad',
      'email': 'E-posta',
      'phone': 'Telefon',
      'position': 'Pozisyon',
      'application_channel': 'Başvuru Kanalı',
      'application_date': 'Başvuru Tarihi',
      'hr_specialist': 'İK Uzmanı',
      'status': 'Aday Durumu'
    };
    
    const label = fieldLabels[fieldName] || fieldName;
    e.target.setCustomValidity(`${label} alanı zorunludur.`);
  };

  const handleInput = (e) => {
    e.target.setCustomValidity('');
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Check file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        setError('Dosya boyutu 10MB\'dan büyük olamaz');
        return;
      }
      
      // Check file type
      const allowedTypes = ['.pdf', '.doc', '.docx'];
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
      
      if (!allowedTypes.includes(fileExtension)) {
        setError('Sadece PDF, DOC ve DOCX dosyaları yüklenebilir');
        return;
      }
      
      setCvFile(file);
      setError(null);
    }
  };

  const handleRemoveCv = () => {
    setShowDeleteModal(true);
  };

  // Confirm delete CV
  const confirmDeleteCv = async () => {
    setDeleteLoading(true);
    try {
      if (id && existingCv) {
        // Delete from backend
        await candidatesAPI.deleteCandidateCv(id);
      }
      setExistingCv(null);
      setCvFile(null);
      setShowCvUpload(true);
      setError(null);
      setSuccessMessage('CV dosyası başarıyla silindi.');
      setShowDeleteModal(false);
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
    } catch (err) {
      console.error('Error deleting CV:', err);
      setError(handleAPIError(err));
    } finally {
      setDeleteLoading(false);
    }
  };

  // Cancel delete
  const cancelDelete = () => {
    setShowDeleteModal(false);
  };

  const handleViewCv = async () => {
    if (id) {
      try {
        const response = await candidatesAPI.viewCandidateCv(id);
        
        // Get file extension from response headers or default to .pdf
        const contentDisposition = response.headers['content-disposition'];
        let filename = `${formData.first_name}_${formData.last_name}_CV.pdf`;
        
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }
        
        // Determine blob type based on filename extension
        const fileExtension = filename.split('.').pop().toLowerCase();
        const mimeTypeMap = {
          'pdf': 'application/pdf',
          'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          'doc': 'application/msword',
          'txt': 'text/plain'
        };
        const mimeType = mimeTypeMap[fileExtension] || 'application/octet-stream';
        
        const blob = new Blob([response.data], { type: mimeType });
        const url = window.URL.createObjectURL(blob);
        window.open(url, '_blank');
      } catch (err) {
        setError(handleAPIError(err));
      }
    }
  };

  const handleDownloadCv = async () => {
    if (id) {
      try {
        const response = await candidatesAPI.downloadCandidateCv(id);
        
        // Get filename from response headers
        const contentDisposition = response.headers['content-disposition'];
        let filename = `${formData.first_name}_${formData.last_name}_CV`; // fallback
        
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }
        
        console.log('Download filename from backend:', filename);
        
        // Get MIME type from response headers
        const contentType = response.headers['content-type'] || 'application/octet-stream';
        console.log('Content-Type from backend:', contentType);
        
        // Create blob with correct MIME type
        const blob = new Blob([response.data], { type: contentType });
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename; // Use filename from backend
        link.style.display = 'none';
        
        // Add to DOM and trigger download
        document.body.appendChild(link);
        link.click();
        
        // Clean up
        setTimeout(() => {
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        }, 100);
        
      } catch (err) {
        console.error('Download error:', err);
        setError(handleAPIError(err));
      }
    }
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.first_name.trim()) {
      newErrors.first_name = 'Ad alanı zorunludur';
    }
    
    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Soyad alanı zorunludur';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'E-posta alanı zorunludur';
    } else {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        newErrors.email = 'Geçerli bir e-posta adresi girin';
      }
    }
    
    if (!formData.phone.trim()) {
      newErrors.phone = 'Telefon alanı zorunludur';
    }
    
    if (!formData.position) {
      newErrors.position = 'Pozisyon alanı zorunludur';
    }
    
    if (!formData.application_channel) {
      newErrors.application_channel = 'Başvuru Kanalı alanı zorunludur';
    }
    
    if (!formData.application_date) {
      newErrors.application_date = 'Başvuru Tarihi alanı zorunludur';
    }
    
    if (!formData.hr_specialist) {
      newErrors.hr_specialist = 'İK Uzmanı alanı zorunludur';
    }
    
    if (!formData.status) {
      newErrors.status = 'Aday Durumu alanı zorunludur';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    setError(null);

    try {
      const formDataToSend = new FormData();
      
      // Add form fields
      Object.keys(formData).forEach(key => {
        if (formData[key]) {
          formDataToSend.append(key, formData[key]);
        }
      });

      // Add CV file if selected
      if (cvFile) {
        formDataToSend.append('cv_file', cvFile);
      }

      let response;
      if (isEdit) {
        response = await candidatesAPI.updateCandidate(id, formDataToSend);
        setSuccessMessage('Aday bilgileri başarıyla güncellendi!');
        
        // If CV was uploaded, update the UI state
        if (cvFile && response.data.cv_file_path) {
          setExistingCv({
            path: response.data.cv_file_path,
            name: response.data.cv_file_path.split('/').pop() || 'CV.pdf'
          });
          setShowCvUpload(false);
          setCvFile(null);
        }
      } else {
        response = await candidatesAPI.createCandidate(formDataToSend);
        setSuccessMessage('Aday başarıyla eklendi!');
        // Yeni eklenen adayı düzenleme modunda aç
        setTimeout(() => {
          navigate(`/candidates/${response.data.id}/edit`);
        }, 2000);
      }

      // Success message'ı 3 saniye sonra temizle
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
    } catch (err) {
      setError(handleAPIError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    navigate('/candidates');
  };

  if (loading && isEdit) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#137fec]"></div>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 min-h-screen">
      <main className="p-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-bold text-gray-800">
              {isEdit ? 'Aday Bilgisi Düzenleme' : 'Aday Bilgisi Girişi'}
            </h2>
            <button
              onClick={() => navigate('/candidates')}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              <span className="material-symbols-outlined text-lg">arrow_back</span>
              Geri Dön
            </button>
          </div>
          
          <div className="bg-white p-8 rounded-lg shadow-sm">
            {error && (
              <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
                {error}
              </div>
            )}
            
            {successMessage && (
              <div className="mb-6 p-4 bg-green-100 border border-green-400 text-green-700 rounded flex items-center gap-2">
                <span className="material-symbols-outlined text-lg">check_circle</span>
                {successMessage}
              </div>
            )}

            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Ad */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="first_name">
                  Ad *
                </label>
                <input
                  className={`w-full mt-1 px-3 py-2.5 text-sm text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#137fec] focus:border-[#137fec] placeholder:text-gray-400 ${
                    errors.first_name ? 'border-red-500' : ''
                  }`}
                  id="first_name"
                  name="first_name"
                  type="text"
                  placeholder="Adayın adını girin"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  onInvalid={handleInvalid}
                  onInput={handleInput}
                  required
                />
                {errors.first_name && (
                  <p className="mt-1 text-sm text-red-600">{errors.first_name}</p>
                )}
              </div>

              {/* Soyad */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="last_name">
                  Soyad *
                </label>
                <input
                  className={`w-full mt-1 px-3 py-2.5 text-sm text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#137fec] focus:border-[#137fec] placeholder:text-gray-400 ${
                    errors.last_name ? 'border-red-500' : ''
                  }`}
                  id="last_name"
                  name="last_name"
                  type="text"
                  placeholder="Adayın soyadını girin"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  onInvalid={handleInvalid}
                  onInput={handleInput}
                  required
                />
                {errors.last_name && (
                  <p className="mt-1 text-sm text-red-600">{errors.last_name}</p>
                )}
              </div>

              {/* E-posta */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="email">
                  E-posta *
                </label>
                <input
                  className={`w-full mt-1 px-3 py-2.5 text-sm text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#137fec] focus:border-[#137fec] placeholder:text-gray-400 ${
                    errors.email ? 'border-red-500' : ''
                  }`}
                  id="email"
                  name="email"
                  type="email"
                  placeholder="Adayın e-posta adresini girin"
                  value={formData.email}
                  onChange={handleInputChange}
                  onInvalid={handleInvalid}
                  onInput={handleInput}
                  required
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600">{errors.email}</p>
                )}
              </div>

              {/* Telefon */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="phone">
                  Telefon *
                </label>
                <InputMask
                  mask="(999) 999 99 99"
                  value={formData.phone}
                  onChange={handleInputChange}
                >
                  {(inputProps) => (
                    <input
                      {...inputProps}
                      className={`w-full mt-1 px-3 py-2.5 text-sm text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#137fec] focus:border-[#137fec] placeholder:text-gray-400 ${
                        errors.phone ? 'border-red-500' : ''
                      }`}
                      id="phone"
                      name="phone"
                      type="tel"
                      placeholder="(5xx) xxx xx xx"
                      onInvalid={handleInvalid}
                      onInput={handleInput}
                      required
                    />
                  )}
                </InputMask>
                {errors.phone && (
                  <p className="mt-1 text-sm text-red-600">{errors.phone}</p>
                )}
              </div>

              {/* Pozisyon */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="position">
                  Pozisyon *
                </label>
                <select
                  className={`w-full mt-1 px-3 py-2.5 text-sm text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#137fec] focus:border-[#137fec] ${
                    errors.position ? 'border-red-500' : ''
                  }`}
                  id="position"
                  name="position"
                  value={formData.position}
                  onChange={handleInputChange}
                  onInvalid={handleInvalid}
                  onInput={handleInput}
                  required
                >
                  <option value="">Pozisyon seçin</option>
                  {options.positions.map(position => (
                    <option key={position.id} value={position.name}>{position.name}</option>
                  ))}
                </select>
                {errors.position && (
                  <p className="mt-1 text-sm text-red-600">{errors.position}</p>
                )}
              </div>

              {/* Başvuru Kanalı */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="application_channel">
                  Başvuru Kanalı *
                </label>
                <select
                  className={`w-full mt-1 px-3 py-2.5 text-sm text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#137fec] focus:border-[#137fec] ${
                    errors.application_channel ? 'border-red-500' : ''
                  }`}
                  id="application_channel"
                  name="application_channel"
                  value={formData.application_channel}
                  onChange={handleInputChange}
                  onInvalid={handleInvalid}
                  onInput={handleInput}
                  required
                >
                  <option value="">Başvuru kanalı seçin</option>
                  {options.applicationChannels.map(channel => (
                    <option key={channel.id} value={channel.name}>{channel.name}</option>
                  ))}
                </select>
                {errors.application_channel && (
                  <p className="mt-1 text-sm text-red-600">{errors.application_channel}</p>
                )}
              </div>

              {/* Başvuru Tarihi */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="application_date">
                  Başvuru Tarihi *
                </label>
                <DatePicker
                  selected={formData.application_date ? new Date(formData.application_date) : null}
                  onChange={(date) => {
                    // Clear error for this field when user selects a date
                    if (errors.application_date) {
                      setErrors(prev => ({
                        ...prev,
                        application_date: ''
                      }));
                    }
                    
                    if (date) {
                      const isoDate = date.toISOString();
                      setFormData(prev => ({
                        ...prev,
                        application_date: isoDate
                      }));
                      setDisplayDate(formatDateToDDMMYYYY(isoDate));
                    }
                  }}
                  dateFormat="dd/MM/yyyy"
                  placeholderText="GG/AA/YYYY"
                  locale="tr"
                  className={`w-full mt-1 px-3 py-2.5 text-sm text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#137fec] focus:border-[#137fec] ${
                    errors.application_date ? 'border-red-500' : ''
                  }`}
                  wrapperClassName="w-full"
                  showPopperArrow={false}
                  popperPlacement="bottom-start"
                  onInvalid={handleInvalid}
                  onInput={handleInput}
                  required
                />
                {errors.application_date && (
                  <p className="mt-1 text-sm text-red-600">{errors.application_date}</p>
                )}
              </div>

              {/* İK Uzmanı */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="hr_specialist">
                  İK Uzmanı (Ekleyen) *
                </label>
                <select
                  className={`w-full mt-1 px-3 py-2.5 text-sm text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#137fec] focus:border-[#137fec] ${
                    errors.hr_specialist ? 'border-red-500' : ''
                  }`}
                  id="hr_specialist"
                  name="hr_specialist"
                  value={formData.hr_specialist}
                  onChange={handleInputChange}
                  onInvalid={handleInvalid}
                  onInput={handleInput}
                  required
                >
                  <option value="">İK uzmanı seçin</option>
                  {options.hrSpecialists.map(specialist => (
                    <option key={specialist.id} value={specialist.name}>{specialist.name}</option>
                  ))}
                </select>
                {errors.hr_specialist && (
                  <p className="mt-1 text-sm text-red-600">{errors.hr_specialist}</p>
                )}
              </div>

              {/* Aday Durumu */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="status">
                  Aday Durumu *
                </label>
                <select
                  className={`w-full mt-1 px-3 py-2.5 text-sm text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#137fec] focus:border-[#137fec] ${
                    errors.status ? 'border-red-500' : ''
                  }`}
                  id="status"
                  name="status"
                  value={formData.status}
                  onChange={handleInputChange}
                  onInvalid={handleInvalid}
                  onInput={handleInput}
                  required
                >
                  <option value="">Durum seçin</option>
                  {options.statuses.map(status => (
                    <option key={status.id} value={status.name}>{status.name}</option>
                  ))}
                </select>
                {errors.status && (
                  <p className="mt-1 text-sm text-red-600">{errors.status}</p>
                )}
              </div>

              {/* Kısa Not */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="notes">
                  Kısa Not
                </label>
                <textarea
                  className="w-full mt-1 px-3 py-2.5 text-sm text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#137fec] focus:border-[#137fec] placeholder:text-gray-400 resize-none"
                  id="notes"
                  name="notes"
                  rows="4"
                  placeholder="Aday hakkında kısa bir not ekleyin"
                  value={formData.notes}
                  onChange={handleInputChange}
                />
              </div>

              {/* CV Yönetimi */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Aday CV Dosyası
                </label>
                
                {/* Mevcut CV Gösterimi */}
                {existingCv && !showCvUpload && (
                  <div className="mt-1 p-4 bg-white border border-gray-200 rounded-md shadow-sm">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="material-symbols-outlined text-2xl text-gray-500">
                          description
                        </span>
                        <div>
                          <p className="text-sm font-medium text-gray-900">{existingCv.name}</p>
                          <p className="text-sm text-gray-500 capitalize">
                            {existingCv.name.split('.').pop()?.toLowerCase() || 'dosya'} dosyası
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {existingCv.path && existingCv.path.toLowerCase().endsWith('.pdf') && (
                          <button
                            type="button"
                            onClick={handleViewCv}
                            className="text-blue-600 hover:text-blue-800 p-1"
                            title="Görüntüle"
                          >
                            <span className="material-symbols-outlined text-sm">visibility</span>
                          </button>
                        )}
                        <button
                          type="button"
                          onClick={handleDownloadCv}
                          className="text-green-600 hover:text-green-800 p-1"
                          title="İndir"
                        >
                          <span className="material-symbols-outlined text-sm">download</span>
                        </button>
                        <button
                          type="button"
                          onClick={handleRemoveCv}
                          className="text-red-600 hover:text-red-800 p-1"
                          title="Sil"
                        >
                          <span className="material-symbols-outlined text-sm">delete</span>
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {/* Yeni CV Yükleme */}
                {showCvUpload && (
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
                        <label className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500" htmlFor="cv_file">
                          <span>Dosya yükle</span>
                          <input
                            className="sr-only"
                            id="cv_file"
                            name="cv_file"
                            type="file"
                            accept=".pdf,.doc,.docx"
                            onChange={handleFileChange}
                          />
                        </label>
                        <p className="pl-1">veya sürükleyip bırakın</p>
                      </div>
                      <p className="text-xs text-gray-500">
                        PDF, DOC, DOCX up to 10MB
                      </p>
                      {cvFile && (
                        <p className="text-sm text-green-600 font-medium">
                          Seçilen dosya: {cvFile.name}
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Butonlar */}
              <div className="md:col-span-2 flex justify-end gap-4">
                <button
                  type="button"
                  onClick={handleCancel}
                  className="inline-flex justify-center py-2 px-6 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400"
                >
                  İptal
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="inline-flex justify-center py-2 px-6 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-[#137fec] hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#137fec] disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Kaydediliyor...' : 'Kaydet'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>

      {/* Delete Confirmation Modal */}
      <DeleteConfirmModal
        isOpen={showDeleteModal}
        onClose={cancelDelete}
        onConfirm={confirmDeleteCv}
        title="CV Dosyasını Sil"
        message="CV dosyasını silmek istediğinizden emin misiniz?"
        itemName="CV dosyası"
        isLoading={deleteLoading}
      />
    </div>
  );
};

export default CandidateForm;
