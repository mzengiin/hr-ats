import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { Calendar, momentLocalizer, Views } from 'react-big-calendar';
import moment from 'moment';
import 'moment/locale/tr'; // Türkçe locale'i import et
import 'react-big-calendar/lib/css/react-big-calendar.css';
import InterviewModal from './InterviewModal';
import CandidateSearchModal from './CandidateSearchModal';

// Custom CSS for responsive calendar
const customCalendarStyles = `
  .rbc-calendar {
    height: 100% !important;
    min-height: 600px !important;
    overflow: visible !important;
  }
  
  .rbc-month-view {
    height: 100% !important;
    overflow: visible !important;
  }
  
  .rbc-month-row {
    height: auto !important;
    min-height: 150px !important;
  }
  
  .rbc-date-cell {
    height: 150px !important;
    min-height: 150px !important;
    overflow: visible !important;
  }
  
  /* Aylık görünümde tarih hücreleri için özel kurallar */
  .rbc-month-view .rbc-date-cell {
    height: 150px !important;
    min-height: 150px !important;
    overflow: visible !important;
    position: relative !important;
  }
  
  .rbc-month-view .rbc-events-container {
    height: auto !important;
    min-height: 120px !important;
    overflow: visible !important;
    position: relative !important;
  }
  
  .rbc-events-container {
    height: 100% !important;
    overflow: visible !important;
  }
  
  .rbc-event {
    font-size: 12px !important;
    padding: 2px 4px !important;
    margin: 1px !important;
    border-radius: 4px !important;
    overflow: visible !important;
    text-overflow: ellipsis;
    white-space: nowrap;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
  }
  
  /* Aylık görünüm için özel kurallar */
  .rbc-month-view .rbc-event {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: relative !important;
    z-index: 1 !important;
  }
  
  .rbc-month-view .rbc-events-container {
    position: relative !important;
    z-index: 1 !important;
  }
  
  .rbc-month-view .rbc-date-cell {
    position: relative !important;
    z-index: 1 !important;
  }
  
  .rbc-event-content {
    font-size: 11px !important;
    line-height: 1.2 !important;
    display: block !important;
    visibility: visible !important;
  }
  
  .rbc-show-more {
    font-size: 10px !important;
    padding: 2px 4px !important;
    background: rgba(0, 0, 0, 0.1) !important;
    border-radius: 3px !important;
  }
  
  @media (max-width: 768px) {
    .rbc-date-cell {
      height: 80px !important;
      min-height: 80px;
    }
    
    .rbc-event {
      font-size: 10px !important;
      padding: 1px 2px !important;
    }
    
    .rbc-event-content {
      font-size: 9px !important;
    }
  }
  
  @media (max-width: 480px) {
    .rbc-date-cell {
      height: 60px !important;
      min-height: 60px;
    }
    
    .rbc-event {
      font-size: 8px !important;
      padding: 1px !important;
    }
    
    .rbc-event-content {
      font-size: 8px !important;
    }
  }
`;

// CSS'i head'e ekle
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = customCalendarStyles;
  document.head.appendChild(style);
}
import { interviewsAPI } from '../services/api';

// Moment'ı Türkçe olarak ayarla
moment.locale('tr');

// Moment localizer'ı ayarla
const localizer = momentLocalizer(moment);

const InterviewCalendar = () => {
  const [view, setView] = useState(Views.MONTH);
  const [date, setDate] = useState(new Date());
  const [showInterviewModal, setShowInterviewModal] = useState(false);
  const [showCandidateSearch, setShowCandidateSearch] = useState(false);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState(null);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [contextMenu, setContextMenu] = useState({ show: false, x: 0, y: 0, interview: null });
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [editingInterview, setEditingInterview] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [interviewToDelete, setInterviewToDelete] = useState(null);
  const [selectedAgendaSlot, setSelectedAgendaSlot] = useState(null);

  // Mülakat verilerini yükle
  const loadInterviews = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Takvim görünümü için tarih aralığını hesapla
      const startOfMonth = moment(date).startOf('month').toISOString();
      const endOfMonth = moment(date).endOf('month').toISOString();
      
      const response = await interviewsAPI.getCalendarInterviews(startOfMonth, endOfMonth);
      
      // API'den gelen veriyi calendar formatına çevir
      const calendarInterviews = response.data.interviews.map(interview => {
        const startDate = new Date(interview.start);
        const endDate = new Date(interview.end);
        
        console.log('Interview:', interview.title, 'Start:', startDate, 'End:', endDate);
        console.log('Start isValid:', !isNaN(startDate.getTime()), 'End isValid:', !isNaN(endDate.getTime()));
        
        return {
          id: interview.id,
          title: interview.title,
          start: startDate,
          end: endDate,
          candidate: interview.candidate,
          interviewer: interview.interviewer,
          status: interview.status,
          meeting_type: interview.meeting_type,
          location: interview.location,
          notes: interview.notes
        };
      });
      
      setInterviews(calendarInterviews);
    } catch (err) {
      console.error('Error loading interviews:', err);
      setError('Mülakatlar yüklenirken hata oluştu');
      // Hata durumunda boş array kullan
      setInterviews([]);
    } finally {
      setLoading(false);
    }
  }, [date]);

  // Component mount olduğunda ve tarih değiştiğinde verileri yükle
  useEffect(() => {
    loadInterviews();
  }, [loadInterviews]);

  // Takvim görünümünü değiştir
  const handleViewChange = (newView) => {
    setView(newView);
  };

  // Tarihi değiştir
  const handleNavigate = (newDate) => {
    setDate(newDate);
  };

  // Çift tıklama için state'ler
  const [lastClickTime, setLastClickTime] = useState(0);
  const [lastClickSlot, setLastClickSlot] = useState(null);
  const [lastClickEvent, setLastClickEvent] = useState(null);

  // Yeni mülakat ekle butonu
  const handleAddInterview = () => {
    setSelectedDate(null);
    setShowInterviewModal(true);
  };

  // Tarihe tıklama ve çift tıklama
  const handleSelectSlot = useCallback(({ start, end, action }, e) => {
    console.log('Select slot:', { start, end, action }, e);
    console.log('Last click time:', lastClickTime);
    console.log('Last click slot:', lastClickSlot);
    
    if (action === 'select') {
      // Mouse ile seçim yapıldığında sadece seçimi kaydet, modal açma
      console.log('Select action on slot:', { start, end });
      setSelectedDate(start);
      setSelectedTimeRange({ start, end });
      setSelectedSlot({ start, end });
      
      // Çift tıklama kontrolü
      const now = Date.now();
      const timeDiff = now - lastClickTime;
      
      console.log('Time diff:', timeDiff);
      console.log('Last click slot exists:', !!lastClickSlot);
      
      if (timeDiff < 500 && lastClickSlot && 
          lastClickSlot.start.getTime() === start.getTime() && 
          lastClickSlot.end.getTime() === end.getTime()) {
        // Çift tıklama - hemen modal aç
        console.log('Double click detected on slot:', { start, end });
        setShowInterviewModal(true);
        setLastClickTime(0);
        setLastClickSlot(null);
      } else {
        // Normal tıklama - sadece seçimi kaydet, modal açma
        console.log('Normal click on slot, saving selection only');
        setLastClickTime(now);
        setLastClickSlot({ start, end });
        // Modal açılmıyor - sadece seçim yapılıyor
      }
    } else if (action === 'click') {
      // Tek tıklama - sadece seçimi kaydet, modal açma
      console.log('Single click on slot:', { start, end });
      setSelectedDate(start);
      setSelectedTimeRange({ start, end });
      setSelectedSlot({ start, end });
      // Modal açılmıyor - sadece seçim yapılıyor
    } else if (action === 'doubleClick') {
      // Çift tıklama - hemen modal aç
      console.log('Double click on slot:', { start, end });
      setSelectedDate(start);
      setSelectedTimeRange({ start, end });
      setSelectedSlot({ start, end });
      setShowInterviewModal(true);
    }
  }, [lastClickTime, lastClickSlot]);

  // Çift tıklama için ayrı handler
  const handleDoubleClickSlot = useCallback(({ start, end }, e) => {
    console.log('Double click slot:', { start, end }, e);
    setSelectedDate(start);
    setSelectedTimeRange({ start, end });
    setSelectedSlot({ start, end });
    setShowInterviewModal(true);
  }, []);

  // Ajanda görünümünde çift tıklama kontrolü
  const handleAgendaDoubleClick = useCallback((start, end) => {
    console.log('Agenda double click:', { start, end });
    setSelectedDate(start);
    setSelectedTimeRange({ start, end });
    setShowInterviewModal(true);
  }, []);

  // Tarihe sağ tıklama - context menü aç
  const handleSlotRightClick = useCallback(({ start, end }, e) => {
    e.preventDefault();
    console.log('Slot right click:', { start, end }, e);
    
    setContextMenu({
      show: true,
      x: e.clientX,
      y: e.clientY,
      interview: null, // Tarih seçimi, mülakat yok
      slot: { start, end }
    });
  }, []);

  // Mülakat seç - kaldırıldı, handleEventClick kullanılıyor

  // Context menü için sağ tık
  const handleContextMenu = (event) => {
    event.preventDefault();
    setContextMenu({
      show: true,
      x: event.clientX,
      y: event.clientY
    });
  };

  // Context menüyü kapat
  const closeContextMenu = () => {
    setContextMenu({ show: false, x: 0, y: 0, interview: null, slot: null });
  };

  // Context menüden mülakat ekle
  const handleContextMenuAddInterview = () => {
    if (contextMenu.slot) {
      // Tarih seçiminden geldi
      setSelectedDate(contextMenu.slot.start);
      setSelectedTimeRange({ start: contextMenu.slot.start, end: contextMenu.slot.end });
    } else {
      // Normal ekleme
      setSelectedDate(null);
      setSelectedTimeRange(null);
    }
    setShowInterviewModal(true);
    closeContextMenu();
  };

  // Aday arama modalını aç
  const handleCandidateSearch = () => {
    setShowCandidateSearch(true);
  };

  // Aday seçimi callback'i
  const handleCandidateSelect = (candidate) => {
    console.log('InterviewCalendar - Selected candidate:', candidate);
    setShowCandidateSearch(false);
    
    if (editingInterview) {
      // Düzenleme modunda ise, seçilen adayı editingInterview'a set et
      setEditingInterview(prev => ({
        ...prev,
        candidate: candidate
      }));
    } else {
      // Yeni mülakat modunda ise, selectedCandidate'ı set et
      setSelectedCandidate(candidate);
      setShowInterviewModal(true);
    }
  };

  // Ajanda görünümünde saat aralığı seçimi
  const handleAgendaSlotSelect = (start, end) => {
    console.log('Agenda slot selected:', { start, end });
    setSelectedAgendaSlot({ start, end });
    setSelectedDate(start);
    setSelectedTimeRange({ start, end });
  };

  // Ajanda görünümünde saat aralığına sağ tıklama
  const handleAgendaSlotRightClick = (start, end, e) => {
    e.preventDefault();
    e.stopPropagation();
    console.log('Agenda slot right click:', { start, end });
    
    setSelectedAgendaSlot({ start, end });
    setSelectedDate(start);
    setSelectedTimeRange({ start, end });
    
    setContextMenu({
      show: true,
      x: e.clientX,
      y: e.clientY,
      interview: null,
      slot: { start, end }
    });
  };


  // Event tıklama - çift tıklama kontrolü
  const handleEventClick = (event, e) => {
    console.log('Event click:', event, e);
    console.log('Event coordinates:', e.clientX, e.clientY);
    
    // Çift tıklama kontrolü
    const now = Date.now();
    const timeDiff = now - lastClickTime;
    
    if (timeDiff < 500 && lastClickEvent && 
        lastClickEvent.id === event.id) {
      // Çift tıklama - düzenleme modunda aç
      console.log('Double click detected on event:', event);
      setEditingInterview(event);
      setShowInterviewModal(true);
      setSelectedCandidate(null);
      setContextMenu({ show: false, x: 0, y: 0, interview: null });
      setLastClickTime(0);
      setLastClickEvent(null);
    } else {
      // Normal tıklama - context menü aç
      setLastClickTime(now);
      setLastClickEvent(event);
      
      const newContextMenu = {
        show: true,
        x: e.clientX || 200,
        y: e.clientY || 200,
        interview: event
      };
      
      console.log('Setting context menu:', newContextMenu);
      setContextMenu(newContextMenu);
    }
  };

  // Mülakata sağ tıklama - context menü aç
  const handleEventRightClick = (event, e) => {
    e.preventDefault();
    console.log('Event right click:', event, e);
    
    setContextMenu({
      show: true,
      x: e.clientX,
      y: e.clientY,
      interview: event,
      slot: null // Mülakat seçimi, slot yok
    });
  };

  // Context menü kapat - duplicate kaldırıldı

  // Düzenle butonu
  const handleEditInterview = () => {
    setEditingInterview(contextMenu.interview);
    setShowInterviewModal(true);
    setSelectedCandidate(null);
    closeContextMenu();
  };

  // Sil butonu
  const handleDeleteInterview = () => {
    setInterviewToDelete(contextMenu.interview);
    setShowDeleteConfirm(true);
    closeContextMenu();
  };

  // Silme onayı
  const confirmDelete = async () => {
    if (interviewToDelete) {
      try {
        await interviewsAPI.deleteInterview(interviewToDelete.id);
        await loadInterviews();
        setShowDeleteConfirm(false);
        setInterviewToDelete(null);
      } catch (error) {
        console.error('Mülakat silme hatası:', error);
      }
    }
  };

  // Silme iptali
  const cancelDelete = () => {
    setShowDeleteConfirm(false);
    setInterviewToDelete(null);
  };

  // Mülakat ekleme/düzenleme işlemi
  const handleInterviewSubmit = async (interviewData) => {
    try {
      setLoading(true);
      
      // API'ye gönderilecek veriyi hazırla
      const apiData = {
        title: interviewData.title,
        candidate_id: interviewData.candidate.id,
        interviewer_name: interviewData.interviewer,
        start_datetime: interviewData.start.toISOString(),
        end_datetime: interviewData.end.toISOString(),
        status: interviewData.status,
        meeting_type: interviewData.meetingType,
        location: interviewData.location,
        notes: interviewData.notes
      };
      
      if (editingInterview) {
        // Düzenleme modu
        await interviewsAPI.updateInterview(editingInterview.id, apiData);
      } else {
        // Ekleme modu
        await interviewsAPI.createInterview(apiData);
      }
      
      // Başarılı olursa verileri yeniden yükle
      await loadInterviews();
      
      setShowInterviewModal(false);
      setSelectedDate(null);
      setEditingInterview(null);
    } catch (err) {
      console.error('Error saving interview:', err);
      setError(editingInterview ? 'Mülakat güncellenirken hata oluştu' : 'Mülakat oluşturulurken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  // Görünüm modları
  const viewOptions = [
    { key: Views.DAY, label: 'Bugün' },
    { key: Views.WEEK, label: 'Hafta' },
    { key: Views.MONTH, label: 'Ay' }
  ];

  // Event style
  const eventStyleGetter = (event) => {
    let backgroundColor = '#137fec';
    let borderColor = '#137fec';

    switch (event.status) {
      case 'completed':
        backgroundColor = '#10b981';
        borderColor = '#10b981';
        break;
      case 'cancelled':
        backgroundColor = '#ef4444';
        borderColor = '#ef4444';
        break;
      case 'scheduled':
      default:
        backgroundColor = '#137fec';
        borderColor = '#137fec';
        break;
    }

    return {
      style: {
        backgroundColor,
        borderColor,
        borderRadius: '4px',
        opacity: 0.8,
        color: 'white',
        border: '0px',
        display: 'block'
      }
    };
  };

  // Event component wrapper for right-click
  const EventWrapper = ({ event, children }) => {
    const handleContextMenu = (e) => {
      e.preventDefault();
      e.stopPropagation();
      setContextMenu({
        show: true,
        x: e.clientX,
        y: e.clientY,
        interview: event,
        slot: null
      });
    };

    return (
      <div onContextMenu={handleContextMenu}>
        {children}
      </div>
    );
  };

  // Ajanda görünümü için saat aralığı seçimi component'i
  const AgendaSlotSelector = ({ start, end, isSelected }) => {
    const [lastClickTime, setLastClickTime] = useState(0);

    const handleClick = (e) => {
      e.stopPropagation();
      
      // Çift tıklama kontrolü
      const now = Date.now();
      const timeDiff = now - lastClickTime;
      
      if (timeDiff < 500) {
        // Çift tıklama - hemen modal aç
        console.log('Double click detected on agenda slot:', { start, end });
        handleAgendaDoubleClick(start, end);
        setLastClickTime(0);
      } else {
        // Normal tıklama - sadece seçimi kaydet
        console.log('Normal click on agenda slot:', { start, end });
        handleAgendaSlotSelect(start, end);
        setLastClickTime(now);
      }
    };

    const handleRightClick = (e) => {
      handleAgendaSlotRightClick(start, end, e);
    };

    const formatTime = (date) => {
      return new Date(date).toLocaleTimeString('tr-TR', {
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    return (
      <div 
        className={`p-2 m-1 border-2 border-dashed rounded-lg cursor-pointer transition-colors ${
          isSelected 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-blue-400 hover:bg-blue-25'
        }`}
        onClick={handleClick}
        onContextMenu={handleRightClick}
      >
        <div className="text-sm font-medium text-gray-700 text-center">
          {formatTime(start)} - {formatTime(end)}
        </div>
        <div className="text-xs text-gray-500 text-center">
          {isSelected ? 'Seçili' : 'Tıklayın'}
        </div>
      </div>
    );
  };

  // Ajanda görünümü için wrapper component
  const AgendaWrapper = ({ children }) => {
    const [timeSlots, setTimeSlots] = useState([]);

    useEffect(() => {
      // Günlük saat aralıklarını oluştur (09:00 - 18:00 arası, 1 saatlik aralıklar)
      const slots = [];
      const startHour = 9;
      const endHour = 18;
      
      for (let hour = startHour; hour < endHour; hour++) {
        const start = new Date();
        start.setHours(hour, 0, 0, 0);
        const end = new Date();
        end.setHours(hour + 1, 0, 0, 0);
        slots.push({ start, end });
      }
      
      setTimeSlots(slots);
    }, []);

    return (
      <div className="agenda-wrapper">
        {/* Saat aralığı seçimi */}
        <div className="mb-4 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Saat Aralığı Seçin</h3>
          <div className="grid grid-cols-3 gap-2">
            {timeSlots.map((slot, index) => (
              <AgendaSlotSelector
                key={index}
                start={slot.start}
                end={slot.end}
                isSelected={selectedAgendaSlot && 
                  selectedAgendaSlot.start.getTime() === slot.start.getTime() &&
                  selectedAgendaSlot.end.getTime() === slot.end.getTime()}
              />
            ))}
          </div>
        </div>
        
        {/* Mevcut ajanda içeriği */}
        {children}
      </div>
    );
  };

  // Ajanda görünümü için özel component
  const AgendaEvent = ({ event }) => {
    const handleContextMenu = (e) => {
      e.preventDefault();
      e.stopPropagation();
      setContextMenu({
        show: true,
        x: e.clientX,
        y: e.clientY,
        interview: event,
        slot: null
      });
    };

    const formatTime = (date) => {
      return new Date(date).toLocaleTimeString('tr-TR', {
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('tr-TR', {
        weekday: 'short',
        day: 'numeric',
        month: 'short'
      });
    };

    return (
      <div 
        className="flex items-center gap-4 p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer"
        onContextMenu={handleContextMenu}
        onClick={() => handleEventClick(event, { clientX: 0, clientY: 0 })}
      >
        <div className="flex-shrink-0 w-16 text-center">
          <div className="text-sm font-medium text-gray-900">
            {formatDate(event.start)}
          </div>
          <div className="text-xs text-gray-500">
            {formatTime(event.start)} - {formatTime(event.end)}
          </div>
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <h3 className="text-sm font-semibold text-gray-900 truncate">
              {event.title}
            </h3>
          </div>
          
          <div className="text-xs text-gray-600 space-y-1">
            <div className="flex items-center gap-1">
              <span className="material-symbols-outlined text-xs">person</span>
              <span>{event.candidate?.name || 'Aday bilgisi yok'}</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="material-symbols-outlined text-xs">person_pin</span>
              <span>{event.interviewer || 'Mülakat yapan kişi belirtilmemiş'}</span>
            </div>
            {event.location && (
              <div className="flex items-center gap-1">
                <span className="material-symbols-outlined text-xs">location_on</span>
                <span>{event.location}</span>
              </div>
            )}
          </div>
        </div>
        
        <div className="flex-shrink-0">
          <div className={`px-2 py-1 text-xs font-medium rounded-full ${
            event.status === 'completed' ? 'bg-green-100 text-green-800' :
            event.status === 'cancelled' ? 'bg-red-100 text-red-800' :
            event.status === 'rescheduled' ? 'bg-yellow-100 text-yellow-800' :
            'bg-blue-100 text-blue-800'
          }`}>
            {event.status === 'completed' ? 'Tamamlandı' :
             event.status === 'cancelled' ? 'İptal Edildi' :
             event.status === 'rescheduled' ? 'Ertelendi' :
             'Planlandı'}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="h-full bg-white rounded-lg shadow-sm flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200 flex-shrink-0">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold text-gray-900">Mülakat Takvimi</h1>
        </div>

        {/* Yeni Mülakat Ekle Butonu */}
        <button
          onClick={handleAddInterview}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <span className="material-symbols-outlined text-sm">add</span>
          Yeni Mülakat Ekle
        </button>
      </div>

      {/* Calendar */}
      <div className="flex-1 flex flex-col p-6 min-h-0">
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex-shrink-0">
            <p className="text-red-600">{error}</p>
            <button 
              onClick={loadInterviews}
              className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
            >
              Tekrar Dene
            </button>
          </div>
        )}
        
        {loading && (
          <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg flex-shrink-0">
            <p className="text-blue-600">Mülakatlar yükleniyor...</p>
          </div>
        )}
        
        <div 
          className="flex-1 min-h-0 overflow-hidden"
          onClick={closeContextMenu}
          onContextMenu={(e) => {
            e.preventDefault();
            // Tarih seçimi için context menü aç
            const rect = e.currentTarget.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Calendar'ın içindeki tarih alanını kontrol et
            const calendarElement = e.currentTarget.querySelector('.rbc-calendar');
            if (calendarElement) {
              const calendarRect = calendarElement.getBoundingClientRect();
              const relativeX = e.clientX - calendarRect.left;
              const relativeY = e.clientY - calendarRect.top;
              
              // Eğer calendar'ın içindeyse ve bir event'e tıklanmamışsa
              const eventElement = e.target.closest('.rbc-event');
              if (!eventElement) {
                setContextMenu({
                  show: true,
                  x: e.clientX,
                  y: e.clientY,
                  interview: null,
                  slot: { start: new Date(), end: new Date() } // Tarih bilgisi
                });
              }
            }
          }}
        >
          <Calendar
            localizer={localizer}
            events={interviews}
            startAccessor="start"
            endAccessor="end"
            style={{ height: '600px', minHeight: '600px' }}
            onSelectEvent={handleEventClick}
            onSelectSlot={handleSelectSlot}
            onDoubleClickEvent={handleDoubleClickSlot}
            onDoubleClickSlot={handleDoubleClickSlot}
            view={view}
            date={date}
            onNavigate={handleNavigate}
            onView={handleViewChange}
            selectable
            selected={selectedSlot}
            eventPropGetter={eventStyleGetter}
            components={{
              eventWrapper: EventWrapper,
              agenda: {
                event: AgendaEvent,
                wrapper: AgendaWrapper
              }
            }}
            messages={{
              next: 'İleri',
              previous: 'Geri',
              today: 'Bugün',
              month: 'Ay',
              week: 'Hafta',
              day: 'Gün',
              agenda: 'Ajanda',
              date: 'Tarih',
              time: 'Saat',
              event: 'Etkinlik',
              noEventsInRange: 'Bu aralıkta mülakat bulunmuyor',
              showMore: (total) => `+${total} daha`,
              allDay: 'Tüm gün',
              work_week: 'Çalışma haftası',
              yesterday: 'Dün',
              tomorrow: 'Yarın',
              noEventsInRange: 'Bu aralıkta mülakat bulunmuyor',
              showMore: (total) => `+${total} daha`
            }}
          />
        </div>
      </div>

      {/* Context Menu - Tarih seçimi için */}
      {contextMenu.show && !contextMenu.interview && (
        <div
          className="fixed bg-white border border-gray-200 rounded-lg shadow-lg py-2 z-50"
          style={{
            left: contextMenu.x,
            top: contextMenu.y
          }}
          onClick={closeContextMenu}
        >
          <button
            onClick={handleContextMenuAddInterview}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-sm">add</span>
            Mülakat Ekle
          </button>
        </div>
      )}

      {/* Context Menu - Mülakat için */}
      {contextMenu.show && contextMenu.interview && (
        <div
          className="fixed bg-white border border-gray-200 rounded-lg shadow-xl py-2 min-w-[120px] z-50"
          style={{
            left: contextMenu.x,
            top: contextMenu.y
          }}
          onClick={closeContextMenu}
        >
          <button
            onClick={handleEditInterview}
            className="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-100 flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-sm">edit</span>
            Düzenle
          </button>
          <button
            onClick={handleDeleteInterview}
            className="w-full px-4 py-2 text-left text-red-600 hover:bg-red-50 flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-sm">delete</span>
            Sil
          </button>
        </div>
      )}

      {/* Modals */}
      {showInterviewModal && (
        <InterviewModal
          isOpen={showInterviewModal}
          onClose={() => {
            setShowInterviewModal(false);
            setSelectedDate(null);
            setSelectedTimeRange(null);
            setSelectedSlot(null);
            setSelectedCandidate(null);
            setEditingInterview(null);
          }}
          onSubmit={handleInterviewSubmit}
          selectedDate={selectedDate}
          selectedTimeRange={selectedTimeRange}
          selectedCandidate={selectedCandidate}
          onCandidateSearch={handleCandidateSearch}
          editingInterview={editingInterview}
        />
      )}

      {showCandidateSearch && (
        <CandidateSearchModal
          isOpen={showCandidateSearch}
          onClose={() => setShowCandidateSearch(false)}
          onSelect={handleCandidateSelect}
        />
      )}


      {/* Silme Onayı Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <span className="material-symbols-outlined text-red-600">warning</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Mülakatı Sil</h3>
                <p className="text-sm text-gray-500">Bu işlem geri alınamaz</p>
              </div>
            </div>
            
            <p className="text-gray-700 mb-6">
              <strong>{interviewToDelete?.title}</strong> mülakatını silmek istediğinizden emin misiniz?
            </p>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={cancelDelete}
                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
              >
                İptal
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-600 text-white hover:bg-red-700 rounded-md transition-colors"
              >
                Sil
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InterviewCalendar;
