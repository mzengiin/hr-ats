import React, { useState, useCallback, useEffect } from 'react';
import { Calendar, momentLocalizer, Views } from 'react-big-calendar';
import moment from 'moment';
import 'moment/locale/tr';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import InterviewModal from './InterviewModal';
import CandidateSearchModal from './CandidateSearchModal';
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
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [editingInterview, setEditingInterview] = useState(null);

  // Mülakat verilerini yükle
  const loadInterviews = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const startOfMonth = moment(date).startOf('month').toISOString();
      const endOfMonth = moment(date).endOf('month').toISOString();
      
      const response = await interviewsAPI.getCalendarInterviews(startOfMonth, endOfMonth);
      
      const calendarInterviews = response.data.interviews.map(interview => ({
        id: interview.id,
        title: interview.title,
        start: new Date(interview.start),
        end: new Date(interview.end),
        candidate: interview.candidate,
        interviewer: interview.interviewer,
        status: interview.status,
        meeting_type: interview.meeting_type,
        location: interview.location,
        notes: interview.notes
      }));
      
      setInterviews(calendarInterviews);
    } catch (err) {
      console.error('Error loading interviews:', err);
      setError('Mülakatlar yüklenirken hata oluştu');
      setInterviews([]);
    } finally {
      setLoading(false);
    }
  }, [date]);

  useEffect(() => {
    loadInterviews();
  }, [loadInterviews]);

  // Event style getter
  const eventStyleGetter = (event) => {
    let backgroundColor = '#3174ad';
    
    switch (event.status) {
      case 'completed':
        backgroundColor = '#28a745';
        break;
      case 'cancelled':
        backgroundColor = '#dc3545';
        break;
      case 'rescheduled':
        backgroundColor = '#ffc107';
        break;
      default:
        backgroundColor = '#3174ad';
    }

    return {
      style: {
        backgroundColor,
        borderRadius: '4px',
        opacity: 0.8,
        color: 'white',
        border: '0px',
        display: 'block'
      }
    };
  };

  // Event click handler
  const handleEventClick = (event) => {
    setEditingInterview(event);
    setShowInterviewModal(true);
  };

  // Slot select handler
  const handleSelectSlot = (slotInfo) => {
    setSelectedDate(slotInfo.start);
    setSelectedTimeRange({
      start: slotInfo.start,
      end: slotInfo.end
    });
    setSelectedSlot(slotInfo);
    setShowCandidateSearch(true);
  };

  // Double click handler
  const handleDoubleClickSlot = (slotInfo) => {
    handleSelectSlot(slotInfo);
  };

  // Navigation handler
  const handleNavigate = (newDate) => {
    setDate(newDate);
  };

  // View change handler
  const handleViewChange = (newView) => {
    setView(newView);
  };

  // Add interview handler
  const handleAddInterview = () => {
    setEditingInterview(null);
    setShowInterviewModal(true);
  };

  // Interview modal success handler
  const handleInterviewSuccess = () => {
    setShowInterviewModal(false);
    setEditingInterview(null);
    loadInterviews();
  };

  // Candidate search success handler
  const handleCandidateSearchSuccess = (candidate) => {
    setSelectedCandidate(candidate);
    setShowCandidateSearch(false);
    setShowInterviewModal(true);
  };

  return (
    <div className="h-screen bg-white rounded-lg shadow-sm flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 flex-shrink-0">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold text-gray-900">Mülakat Takvimi</h1>
        </div>

        <button
          onClick={handleAddInterview}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <span className="material-symbols-outlined text-sm">add</span>
          Yeni Mülakat Ekle
        </button>
      </div>

      {/* Calendar Container */}
      <div className="flex-1 flex flex-col p-4 min-h-0 overflow-hidden">
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
        
        <div className="flex-1 w-full overflow-hidden">
          <Calendar
            localizer={localizer}
            events={interviews}
            startAccessor="start"
            endAccessor="end"
            style={{ height: '100%', width: '100%' }}
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
              tomorrow: 'Yarın'
            }}
          />
        </div>
      </div>

      {/* Interview Modal */}
      {showInterviewModal && (
        <InterviewModal
          isOpen={showInterviewModal}
          onClose={() => {
            setShowInterviewModal(false);
            setEditingInterview(null);
            setSelectedCandidate(null);
          }}
          interview={editingInterview}
          candidate={selectedCandidate}
          selectedDate={selectedDate}
          selectedTimeRange={selectedTimeRange}
          onSuccess={handleInterviewSuccess}
        />
      )}

      {/* Candidate Search Modal */}
      {showCandidateSearch && (
        <CandidateSearchModal
          isOpen={showCandidateSearch}
          onClose={() => {
            setShowCandidateSearch(false);
            setSelectedDate(null);
            setSelectedTimeRange(null);
            setSelectedSlot(null);
          }}
          onSelect={handleCandidateSearchSuccess}
        />
      )}
    </div>
  );
};

export default InterviewCalendar;