import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { candidatesAPI, handleAPIError } from '../services/api';
import { formatDateToDDMMYYYY } from '../utils/dateUtils';

const CandidateDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [interviews, setInterviews] = useState([]);
  const [caseStudies, setCaseStudies] = useState([]);

  useEffect(() => {
    if (id) {
      loadCandidateDetail();
    }
  }, [id]);

  const loadCandidateDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load candidate data
      const candidateResponse = await candidatesAPI.getCandidate(id);
      setCandidate(candidateResponse.data);
      
      // Load interviews and case studies in parallel
      const [interviewsResponse, caseStudiesResponse] = await Promise.all([
        candidatesAPI.getCandidateInterviews(id),
        candidatesAPI.getCandidateCaseStudies(id)
      ]);
      
      setInterviews(interviewsResponse.data);
      setCaseStudies(caseStudiesResponse.data);
    } catch (err) {
      setError(handleAPIError(err));
      console.error('Error loading candidate detail:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      // Candidate statuses
      'Başvurdu': 'bg-gray-100 text-gray-800',
      'İnceleme': 'bg-yellow-100 text-yellow-800',
      'Değerlendirme': 'bg-yellow-100 text-yellow-800',
      'Mülakat': 'bg-blue-100 text-blue-800',
      'Teklif': 'bg-green-100 text-green-800',
      'İşe Alındı': 'bg-purple-100 text-purple-800',
      'Reddedildi': 'bg-red-100 text-red-800',
      
      // Interview statuses
      'scheduled': 'bg-blue-100 text-blue-800',
      'completed': 'bg-green-100 text-green-800',
      'cancelled': 'bg-red-100 text-red-800',
      'rescheduled': 'bg-yellow-100 text-yellow-800',
      'Olumlu': 'bg-green-100 text-green-800',
      'Beklemede': 'bg-gray-100 text-gray-800',
      
      // Case study statuses
      'Başarılı': 'bg-green-100 text-green-800',
      'Değerlendiriliyor': 'bg-yellow-100 text-yellow-800',
      'Beklemede': 'bg-gray-100 text-gray-800',
      'Başarısız': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const handleDownloadCV = () => {
    if (candidate?.cv_file_path) {
      // Create download link
      const link = document.createElement('a');
      link.href = `http://localhost:8001${candidate.cv_file_path}`;
      link.download = `${candidate.first_name}_${candidate.last_name}_CV.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleViewCV = () => {
    if (candidate?.cv_file_path) {
      window.open(`http://localhost:8001${candidate.cv_file_path}`, '_blank');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#137fec]"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-[#F8F9FA] min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">Hata</div>
          <div className="text-gray-600 mb-4">{error}</div>
          <button
            onClick={() => navigate('/candidates')}
            className="px-4 py-2 bg-[#137fec] text-white rounded-md hover:bg-blue-700"
          >
            Aday Listesine Dön
          </button>
        </div>
      </div>
    );
  }

  if (!candidate) {
    return (
      <div className="bg-[#F8F9FA] min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-600 text-xl mb-4">Aday bulunamadı</div>
          <button
            onClick={() => navigate('/candidates')}
            className="px-4 py-2 bg-[#137fec] text-white rounded-md hover:bg-blue-700"
          >
            Aday Listesine Dön
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#F8F9FA] min-h-screen">
      <main className="p-8">
        <div className="mx-auto max-w-6xl">
          {/* Header */}
          <header className="mb-8 flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900">Aday Profili</h1>
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/candidates')}
                className="flex items-center justify-center gap-2 rounded-md bg-gray-200 px-4 py-2 text-sm font-medium text-gray-800 hover:bg-gray-300"
              >
                <span className="material-symbols-outlined text-base">arrow_back</span>
                Geri Dön
              </button>
              <Link
                to={`/candidates/${candidate.id}/edit`}
                className="flex items-center justify-center gap-2 rounded-md bg-[#137fec] px-4 py-2 text-sm font-medium text-white hover:bg-opacity-90"
              >
                <span className="material-symbols-outlined text-base">edit</span>
                Profili Düzenle
              </Link>
            </div>
          </header>

          {/* Candidate Info Card */}
          <div className="mb-8 rounded-lg bg-white p-8 shadow-sm">
            <div className="flex flex-col gap-8 md:flex-row md:items-start md:justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-4">
                  {/* Placeholder avatar instead of profile photo */}
                  <div className="h-24 w-24 rounded-full bg-gray-200 flex items-center justify-center">
                    <span className="material-symbols-outlined text-4xl text-gray-400">person</span>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">
                      {candidate.first_name} {candidate.last_name}
                    </h2>
                    <p className="text-sm text-gray-500">{candidate.email}</p>
                    <p className="text-sm text-gray-500">{candidate.phone}</p>
                  </div>
                </div>
              </div>
              <div className="shrink-0">
                <p className="text-sm font-medium text-gray-500">Durum</p>
                <p className={`mt-1 inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${getStatusColor(candidate.status)}`}>
                  {candidate.status}
                </p>
              </div>
            </div>

            <div className="mt-8 grid grid-cols-1 gap-x-8 gap-y-6 md:grid-cols-2 lg:grid-cols-3">
              <div>
                <p className="text-sm font-medium text-gray-500">Pozisyon</p>
                <p className="text-base font-semibold text-gray-800">{candidate.position}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Başvuru Tarihi</p>
                <p className="text-base font-semibold text-gray-800">
                  {formatDateToDDMMYYYY(candidate.application_date)}
                </p>
              </div>
              <div className="col-span-1 md:col-span-2 lg:col-span-1">
                <p className="text-sm font-medium text-gray-500">CV</p>
                <div className="mt-2 flex gap-2">
                  <button
                    onClick={handleViewCV}
                    className="flex items-center justify-center gap-2 rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
                  >
                    <span className="material-symbols-outlined text-base">visibility</span>
                    Görüntüle
                  </button>
                  <button
                    onClick={handleDownloadCV}
                    className="flex items-center justify-center gap-2 rounded-md bg-[#137fec] px-4 py-2 text-sm font-medium text-white hover:bg-opacity-90"
                  >
                    <span className="material-symbols-outlined text-base">download</span>
                    İndir
                  </button>
                </div>
              </div>
            </div>

            {candidate.notes && (
              <div className="mt-6">
                <p className="text-sm font-medium text-gray-500">Kısa Not</p>
                <p className="mt-1 text-base text-gray-800">{candidate.notes}</p>
              </div>
            )}
          </div>

          {/* Interviews Section */}
          <div className="mb-8">
            <h3 className="mb-4 text-xl font-bold text-gray-900">Mülakatlar</h3>
            <div className="space-y-4">
              {interviews.length > 0 ? (
                interviews.map((interview) => (
                  <div key={interview.id} className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                    <div className="flex flex-wrap items-center justify-between gap-4">
                      <div>
                        <p className="font-semibold text-gray-800">{interview.title}</p>
                        <p className="text-sm text-gray-500">Mülakatı Yapan: {interview.interviewer_name}</p>
                        <p className="text-sm text-gray-500">Tarih: {formatDateToDDMMYYYY(interview.start_datetime)}</p>
                        <p className="text-sm text-gray-500">Tür: {interview.meeting_type}</p>
                        {interview.location && (
                          <p className="text-sm text-gray-500">Konum: {interview.location}</p>
                        )}
                      </div>
                      <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${getStatusColor(interview.status)}`}>
                        {interview.status}
                      </span>
                    </div>
                    {interview.notes && (
                      <div className="mt-4 border-t border-gray-200 pt-4">
                        <p className="text-sm font-medium text-gray-600">Değerlendirme Notu:</p>
                        <p className="mt-1 text-sm text-gray-800">{interview.notes}</p>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <span className="material-symbols-outlined text-4xl mb-2 block">event_available</span>
                  <p>Bu aday için henüz mülakat kaydı bulunmuyor.</p>
                </div>
              )}
            </div>
          </div>

          {/* Case Studies Section */}
          <div>
            <h3 className="mb-4 text-xl font-bold text-gray-900">Vaka Çalışmaları</h3>
            <div className="space-y-4">
              {caseStudies.length > 0 ? (
                caseStudies.map((caseStudy) => (
                  <div key={caseStudy.id} className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                    <div className="flex flex-wrap items-center justify-between gap-4">
                      <div>
                        <p className="font-semibold text-gray-800">{caseStudy.title}</p>
                        <p className="text-sm text-gray-500">Teslim Tarihi: {formatDateToDDMMYYYY(caseStudy.due_date)}</p>
                        {caseStudy.description && (
                          <p className="text-sm text-gray-600 mt-1">{caseStudy.description}</p>
                        )}
                      </div>
                      <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${getStatusColor(caseStudy.status)}`}>
                        {caseStudy.status}
                      </span>
                    </div>
                    {caseStudy.notes && (
                      <div className="mt-4 border-t border-gray-200 pt-4">
                        <p className="text-sm font-medium text-gray-600">Değerlendirme Notu:</p>
                        <p className="mt-1 text-sm text-gray-800">{caseStudy.notes}</p>
                      </div>
                    )}
                    {caseStudy.file_path && (
                      <div className="mt-3 flex gap-2">
                        <button 
                          onClick={() => window.open(`http://localhost:8001${caseStudy.file_path}`, '_blank')}
                          className="flex items-center justify-center gap-2 rounded-md bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-200"
                        >
                          <span className="material-symbols-outlined text-sm">visibility</span>
                          Çözümü Görüntüle
                        </button>
                        <button 
                          onClick={() => {
                            const link = document.createElement('a');
                            link.href = `http://localhost:8001${caseStudy.file_path}`;
                            link.download = `${caseStudy.title}_cozum.pdf`;
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                          }}
                          className="flex items-center justify-center gap-2 rounded-md bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-200"
                        >
                          <span className="material-symbols-outlined text-sm">download</span>
                          Çözümü İndir
                        </button>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <span className="material-symbols-outlined text-4xl mb-2 block">assignment</span>
                  <p>Bu aday için henüz vaka çalışması bulunmuyor.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default CandidateDetail;