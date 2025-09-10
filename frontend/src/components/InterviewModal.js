import React, { useState, useEffect } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

const InterviewModal = ({ isOpen, onClose, onSubmit, selectedDate, selectedTimeRange, selectedCandidate, onCandidateSearch, editingInterview }) => {
  const [formData, setFormData] = useState({
    title: '',
    candidate: null,
    interviewer: '',
    startDate: selectedDate || new Date(),
    startTime: '10:00',
    endTime: '11:00',
    status: 'scheduled',
    notes: '',
    location: '',
    meetingType: 'in-person'
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (selectedDate) {
      setFormData(prev => ({
        ...prev,
        startDate: selectedDate
      }));
    }
  }, [selectedDate]);

  // Seçilen saat aralığını form'a uygula
  useEffect(() => {
    if (selectedTimeRange && !editingInterview) {
      const startTime = selectedTimeRange.start.toTimeString().slice(0, 5);
      const endTime = selectedTimeRange.end.toTimeString().slice(0, 5);
      
      setFormData(prev => ({
        ...prev,
        startTime,
        endTime
      }));
    }
  }, [selectedTimeRange, editingInterview]);

  useEffect(() => {
    if (selectedCandidate) {
      console.log('InterviewModal - Received selectedCandidate:', selectedCandidate);
      const candidateName = `${selectedCandidate.first_name} ${selectedCandidate.last_name}`;
      setFormData(prev => ({
        ...prev,
        candidate: selectedCandidate,
        title: `${candidateName} - ${selectedCandidate.position}`
      }));
    }
  }, [selectedCandidate]);

  // Düzenleme modu için form verilerini doldur
  useEffect(() => {
    if (editingInterview) {
      console.log('InterviewModal - Editing interview:', editingInterview);
      console.log('InterviewModal - Candidate data:', editingInterview.candidate);
      
      // Aday bilgilerini güvenli şekilde parse et
      let candidateData = null;
      if (editingInterview.candidate) {
        // API'den gelen veri formatını kontrol et
        let firstName = '';
        let lastName = '';
        
        if (editingInterview.candidate.name) {
          // API'den "name" field'ı geliyorsa (örn: "Ahmet Yılmaz")
          const nameParts = editingInterview.candidate.name.split(' ');
          firstName = nameParts[0] || '';
          lastName = nameParts.slice(1).join(' ') || '';
        } else {
          // Eğer first_name/last_name field'ları varsa
          firstName = editingInterview.candidate.first_name || editingInterview.candidate.firstName || '';
          lastName = editingInterview.candidate.last_name || editingInterview.candidate.lastName || '';
        }
        
        candidateData = {
          id: editingInterview.candidate.id,
          first_name: firstName,
          last_name: lastName,
          email: editingInterview.candidate.email || '',
          phone: editingInterview.candidate.phone || '',
          position: editingInterview.candidate.position || ''
        };
        console.log('Parsed candidate data:', candidateData);
      }
      
      const candidateName = candidateData ? `${candidateData.first_name} ${candidateData.last_name}`.trim() : '';
      const title = candidateName ? `${candidateName} - ${candidateData.position}` : (editingInterview.title || '');
      
      setFormData({
        title: title,
        candidate: candidateData,
        interviewer: editingInterview.interviewer || '',
        startDate: editingInterview.start ? new Date(editingInterview.start) : new Date(),
        startTime: editingInterview.start ? new Date(editingInterview.start).toTimeString().slice(0, 5) : '10:00',
        endTime: editingInterview.end ? new Date(editingInterview.end).toTimeString().slice(0, 5) : '11:00',
        status: editingInterview.status || 'scheduled',
        notes: editingInterview.notes || '',
        location: editingInterview.location || '',
        meetingType: editingInterview.meetingType || editingInterview.meeting_type || 'in-person'
      });
    }
  }, [editingInterview]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Mülakat başlığı gereklidir';
    }

    if (!formData.candidate) {
      newErrors.candidate = 'Aday seçimi gereklidir';
    }

    if (!formData.interviewer.trim()) {
      newErrors.interviewer = 'Mülakat yapan kişi gereklidir';
    }

    if (!formData.startDate) {
      newErrors.startDate = 'Başlangıç tarihi gereklidir';
    }

    if (!formData.startTime) {
      newErrors.startTime = 'Başlangıç saati gereklidir';
    }

    if (!formData.endTime) {
      newErrors.endTime = 'Bitiş saati gereklidir';
    }

    // Time validation
    if (formData.startTime && formData.endTime) {
      const start = new Date(`2000-01-01 ${formData.startTime}`);
      const end = new Date(`2000-01-01 ${formData.endTime}`);
      if (start >= end) {
        newErrors.endTime = 'Bitiş saati başlangıç saatinden sonra olmalıdır';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    // Combine date and time
    const startDateTime = new Date(formData.startDate);
    const [startHour, startMinute] = formData.startTime.split(':');
    startDateTime.setHours(parseInt(startHour), parseInt(startMinute), 0, 0);

    const endDateTime = new Date(formData.startDate);
    const [endHour, endMinute] = formData.endTime.split(':');
    endDateTime.setHours(parseInt(endHour), parseInt(endMinute), 0, 0);

    const interviewData = {
      title: formData.title,
      candidate: formData.candidate,
      interviewer: formData.interviewer,
      start: startDateTime,
      end: endDateTime,
      status: formData.status,
      notes: formData.notes,
      location: formData.location,
      meetingType: formData.meetingType
    };

    onSubmit(interviewData);
  };

  const handleCandidateSelect = (candidate) => {
    const candidateName = `${candidate.first_name} ${candidate.last_name}`;
    setFormData(prev => ({
      ...prev,
      candidate,
      title: `${candidateName} - ${candidate.position}`
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {editingInterview ? 'Mülakat Düzenle' : 'Yeni Mülakat Ekle'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
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
                }`}
              />
              <button
                type="button"
                onClick={onCandidateSearch}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
              >
                <span className="material-symbols-outlined text-sm">search</span>
              </button>
            </div>
            {errors.candidate && (
              <p className="mt-1 text-sm text-red-600">{errors.candidate}</p>
            )}
          </div>

          {/* Mülakat Başlığı */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Mülakat Başlığı *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.title ? 'border-red-500' : ''
              }`}
              placeholder="Örn: Ahmet Yılmaz - Teknik Mülakat"
            />
            {errors.title && (
              <p className="mt-1 text-sm text-red-600">{errors.title}</p>
            )}
          </div>

          {/* Mülakat Yapan Kişi */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Mülakat Yapan Kişi *
            </label>
            <input
              type="text"
              value={formData.interviewer}
              onChange={(e) => handleInputChange('interviewer', e.target.value)}
              className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.interviewer ? 'border-red-500' : ''
              }`}
              placeholder="Mülakat yapan kişinin adı"
            />
            {errors.interviewer && (
              <p className="mt-1 text-sm text-red-600">{errors.interviewer}</p>
            )}
          </div>

          {/* Tarih ve Saat */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tarih *
              </label>
              <DatePicker
                selected={formData.startDate}
                onChange={(date) => handleInputChange('startDate', date)}
                dateFormat="dd/MM/yyyy"
                className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.startDate ? 'border-red-500' : ''
                }`}
                placeholderText="Tarih seçin"
              />
              {errors.startDate && (
                <p className="mt-1 text-sm text-red-600">{errors.startDate}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Başlangıç Saati *
              </label>
              <DatePicker
                selected={formData.startTime ? new Date(`2000-01-01T${formData.startTime}`) : null}
                onChange={(date) => {
                  if (date) {
                    const timeString = date.toTimeString().slice(0, 5);
                    handleInputChange('startTime', timeString);
                  }
                }}
                showTimeSelect
                showTimeSelectOnly
                timeIntervals={15}
                timeCaption="Saat"
                dateFormat="HH:mm"
                className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.startTime ? 'border-red-500' : ''
                }`}
                placeholderText="Saat seçin"
              />
              {errors.startTime && (
                <p className="mt-1 text-sm text-red-600">{errors.startTime}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Bitiş Saati *
              </label>
              <DatePicker
                selected={formData.endTime ? new Date(`2000-01-01T${formData.endTime}`) : null}
                onChange={(date) => {
                  if (date) {
                    const timeString = date.toTimeString().slice(0, 5);
                    handleInputChange('endTime', timeString);
                  }
                }}
                showTimeSelect
                showTimeSelectOnly
                timeIntervals={15}
                timeCaption="Saat"
                dateFormat="HH:mm"
                className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.endTime ? 'border-red-500' : ''
                }`}
                placeholderText="Saat seçin"
              />
              {errors.endTime && (
                <p className="mt-1 text-sm text-red-600">{errors.endTime}</p>
              )}
            </div>
          </div>

          {/* Mülakat Türü ve Konum */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mülakat Türü
              </label>
              <select
                value={formData.meetingType}
                onChange={(e) => handleInputChange('meetingType', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="in-person">Yüz Yüze</option>
                <option value="video">Video Görüşme</option>
                <option value="phone">Telefon</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Konum / Link
              </label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => handleInputChange('location', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder={formData.meetingType === 'video' ? 'Zoom/Teams linki' : 'Ofis konumu'}
              />
            </div>
          </div>

          {/* Durum */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Durum
            </label>
            <select
              value={formData.status}
              onChange={(e) => handleInputChange('status', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="scheduled">Planlandı</option>
              <option value="completed">Tamamlandı</option>
              <option value="cancelled">İptal Edildi</option>
              <option value="rescheduled">Ertelendi</option>
            </select>
          </div>

          {/* Notlar */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notlar
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Mülakat hakkında notlar..."
            />
          </div>

          {/* Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
            >
              İptal
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            >
              Mülakat Ekle
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default InterviewModal;
