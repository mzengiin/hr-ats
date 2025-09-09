import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { candidatesAPI, handleAPIError } from '../services/api';
import { formatDateToDDMMYYYY, formatDateToTurkish } from '../utils/dateUtils';
// Native file download without external library

const CandidateDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [candidate, setCandidate] = useState(null);
  const [interviews, setInterviews] = useState([]);
  const [caseStudies, setCaseStudies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadCandidateData();
  }, [id]);

  const loadCandidateData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [candidateRes, interviewsRes, caseStudiesRes] = await Promise.all([
        candidatesAPI.getCandidate(id),
        candidatesAPI.getCandidateInterviews(id),
        candidatesAPI.getCandidateCaseStudies(id)
      ]);

      setCandidate(candidateRes.data);
      setInterviews(interviewsRes.data.interviews);
      setCaseStudies(caseStudiesRes.data.case_studies);
    } catch (err) {
      setError(handleAPIError(err));
      console.error('Error loading candidate data:', err);
    } finally {
      setLoading(false);
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

  const getInterviewStatusColor = (status) => {
    const colors = {
      'Olumlu': 'bg-green-100 text-green-800',
      'Olumsuz': 'bg-red-100 text-red-800',
      'Beklemede': 'bg-gray-100 text-gray-800',
      'Planlandı': 'bg-blue-100 text-blue-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getCaseStudyStatusColor = (status) => {
    const colors = {
      'Başarılı': 'bg-green-100 text-green-800',
      'Başarısız': 'bg-red-100 text-red-800',
      'Değerlendiriliyor': 'bg-yellow-100 text-yellow-800',
      'Beklemede': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString) => {
    return formatDateToTurkish(dateString);
  };

  const formatDateTime = (dateString, timeString) => {
    return formatDateToTurkish(dateString) + ' ' + timeString;
  };

  const handleDownloadCV = async () => {
    if (candidate?.id) {
      try {
        const response = await candidatesAPI.downloadCandidateCv(candidate.id);
        
        // Get file extension from response headers
        const contentDisposition = response.headers['content-disposition'];
        let filename = `${candidate.first_name}_${candidate.last_name}_CV`; // fallback without extension
        
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }
        
        console.log('Detail Download filename:', filename);
        
        // Determine blob type based on filename extension
        let fileExtension = filename.split('.').pop().toLowerCase();
        const mimeTypeMap = {
          'pdf': 'application/pdf',
          'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          'doc': 'application/msword',
          'txt': 'text/plain'
        };
        
        // If no extension in filename, try to determine from response content-type
        if (fileExtension === filename || fileExtension.length > 4) {
          const contentType = response.headers['content-type'];
          console.log('Content-Type from response:', contentType);
          if (contentType) {
            if (contentType.includes('pdf')) {
              fileExtension = 'pdf';
            } else if (contentType.includes('docx')) {
              fileExtension = 'docx';
            } else if (contentType.includes('doc')) {
              fileExtension = 'doc';
            } else {
              fileExtension = 'pdf'; // default fallback
            }
            filename = `${candidate.first_name}_${candidate.last_name}_CV.${fileExtension}`;
          }
        }
        
        console.log('Final filename:', filename);
        console.log('Final file extension:', fileExtension);
        
        const mimeType = mimeTypeMap[fileExtension] || 'application/octet-stream';
        
        console.log('Detail File extension:', fileExtension);
        console.log('Detail MIME type:', mimeType);
        
        // Create blob with correct MIME type
        const blob = new Blob([response.data], { type: mimeType });
        
        // Single download method
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename; // Explicit filename with extension
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
        console.error('Detail Download error:', err);
        setError(handleAPIError(err));
      }
    }
  };

  const handleViewCV = async () => {
    if (candidate?.id) {
      try {
        const response = await candidatesAPI.viewCandidateCv(candidate.id);
        
        // Get file extension from response headers or default to .pdf
        const contentDisposition = response.headers['content-disposition'];
        let filename = `${candidate.first_name}_${candidate.last_name}_CV.pdf`;
        
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#137fec]"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-50 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Hata</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/candidates')}
            className="px-4 py-2 bg-[#137fec] text-white rounded hover:bg-blue-700"
          >
            Aday Listesine Dön
          </button>
        </div>
      </div>
    );
  }

  if (!candidate) {
    return (
      <div className="bg-gray-50 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Aday Bulunamadı</h2>
          <button
            onClick={() => navigate('/candidates')}
            className="px-4 py-2 bg-[#137fec] text-white rounded hover:bg-blue-700"
          >
            Aday Listesine Dön
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 min-h-screen">
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
                  <div className="h-24 w-24 rounded-full bg-gray-200 flex items-center justify-center">
                    <span className="material-symbols-outlined text-4xl text-gray-400">
                      person
                    </span>
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
                <p className="mt-1">
                  <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${getStatusColor(candidate.status)}`}>
                    {candidate.status}
                  </span>
                </p>
              </div>
            </div>

            {/* Additional Info */}
            <div className="mt-8 grid grid-cols-1 gap-x-8 gap-y-6 md:grid-cols-2 lg:grid-cols-3">
              <div>
                <p className="text-sm font-medium text-gray-500">Pozisyon</p>
                <p className="text-base font-semibold text-gray-800">{candidate.position}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Başvuru Tarihi</p>
                <p className="text-base font-semibold text-gray-800">{formatDate(candidate.application_date)}</p>
              </div>
              <div className="col-span-1 md:col-span-2 lg:col-span-1">
                <p className="text-sm font-medium text-gray-500">CV</p>
                <div className="mt-2 flex gap-2">
                  {candidate.cv_file_path && candidate.cv_file_path.toLowerCase().endsWith('.pdf') && (
                    <button
                      onClick={handleViewCV}
                      className="flex items-center justify-center gap-2 rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
                    >
                      <span className="material-symbols-outlined text-base">visibility</span>
                      Görüntüle
                    </button>
                  )}
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

            {/* Notes */}
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
                        <p className="font-semibold text-gray-800">{interview.interview_type}</p>
                        <p className="text-sm text-gray-500">Mülakatı Yapan: {interview.interviewer}</p>
                        <p className="text-sm text-gray-500">Tarih: {formatDateTime(interview.date, interview.time)}</p>
                      </div>
                      <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${getInterviewStatusColor(interview.status)}`}>
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
                <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
                  <span className="material-symbols-outlined text-4xl text-gray-400 mb-2">event</span>
                  <p className="text-gray-500">Henüz mülakat kaydı bulunmuyor</p>
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
                        <p className="text-sm text-gray-500">Gönderim Tarihi: {formatDate(caseStudy.submission_date)}</p>
                      </div>
                      <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${getCaseStudyStatusColor(caseStudy.status)}`}>
                        {caseStudy.status}
                      </span>
                    </div>
                    {caseStudy.notes && (
                      <div className="mt-4 border-t border-gray-200 pt-4">
                        <p className="text-sm font-medium text-gray-600">Değerlendirme Notu:</p>
                        <p className="mt-1 text-sm text-gray-800">{caseStudy.notes}</p>
                      </div>
                    )}
                    {caseStudy.solution_file_path && (
                      <div className="mt-4 border-t border-gray-200 pt-4">
                        <p className="text-sm font-medium text-gray-600">Çözüm:</p>
                        <div className="mt-2 flex gap-2">
                          <button
                            onClick={() => window.open(caseStudy.solution_file_path, '_blank')}
                            className="flex items-center justify-center gap-2 rounded-md bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-200"
                          >
                            <span className="material-symbols-outlined text-sm">visibility</span>
                            Çözümü Görüntüle
                          </button>
                          <button
                            onClick={() => window.open(caseStudy.solution_file_path, '_blank')}
                            className="flex items-center justify-center gap-2 rounded-md bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-200"
                          >
                            <span className="material-symbols-outlined text-sm">download</span>
                            Çözümü İndir
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
                  <span className="material-symbols-outlined text-4xl text-gray-400 mb-2">assignment</span>
                  <p className="text-gray-500">Henüz vaka çalışması bulunmuyor</p>
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
