import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';

const DashboardNew = () => {
  const [dashboardData, setDashboardData] = useState({
    statistics: {
      totalApplications: 0,
      activeCandidates: 0,
      interviewsThisMonth: 0,
      hiredCandidates: 0
    },
    candidateStatusDistribution: [],
    positionApplicationVolume: [],
    upcomingInterviews: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const response = await dashboardAPI.getDashboardData();
        
        if (response.data.success) {
          setDashboardData(response.data.data);
        } else {
          console.error('Failed to fetch dashboard data');
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Fallback to mock data if API fails
        const mockData = {
          statistics: {
            totalApplications: 1250,
            activeCandidates: 320,
            interviewsThisMonth: 85,
            hiredCandidates: 15
          },
          candidateStatusDistribution: [
            { status: 'Başvurdu', count: 450, percentage: 25, color: '#137fec' },
            { status: 'İnceleme', count: 360, percentage: 20, color: '#4ade80' },
            { status: 'Mülakat', count: 270, percentage: 15, color: '#facc15' },
            { status: 'Teklif', count: 90, percentage: 5, color: '#f87171' },
            { status: 'İşe Alındı', count: 45, percentage: 2.5, color: '#fb923c' },
            { status: 'Reddedildi', count: 585, percentage: 32.5, color: '#a78bfa' }
          ],
          positionApplicationVolume: [
            { position: 'Yazılım Mühendisi', count: 200, percentage: 20 },
            { position: 'Ürün Yöneticisi', count: 700, percentage: 70 },
            { position: 'Pazarlama Uzmanı', count: 800, percentage: 80 },
            { position: 'Satış Temsilcisi', count: 1000, percentage: 100 },
            { position: 'Veri Analisti', count: 900, percentage: 90 },
            { position: 'UX Tasarımcısı', count: 100, percentage: 10 }
          ],
          upcomingInterviews: [
            {
              id: 1,
              candidateName: 'Elif Demir',
              position: 'Yazılım Mühendisi',
              date: '2024-07-20',
              time: '10:00',
              status: 'Planlandı',
              interviewer: 'Ayşe Demir'
            },
            {
              id: 2,
              candidateName: 'Ahmet Yılmaz',
              position: 'Ürün Yöneticisi',
              date: '2024-07-21',
              time: '14:00',
              status: 'Onaylandı',
              interviewer: 'Mehmet Kaya'
            },
            {
              id: 3,
              candidateName: 'Ayşe Kaya',
              position: 'Pazarlama Uzmanı',
              date: '2024-07-22',
              time: '11:00',
              status: 'Beklemede',
              interviewer: 'Elif Can'
            },
            {
              id: 4,
              candidateName: 'Mehmet Can',
              position: 'Satış Temsilcisi',
              date: '2024-07-23',
              time: '15:00',
              status: 'Planlandı',
              interviewer: 'Zeynep Öz'
            },
            {
              id: 5,
              candidateName: 'Zeynep Tekin',
              position: 'Veri Analisti',
              date: '2024-07-24',
              time: '09:00',
              status: 'Onaylandı',
              interviewer: 'Can Yılmaz'
            }
          ]
        };
        setDashboardData(mockData);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const getStatusColor = (status) => {
    const colors = {
      'Planlandı': 'bg-blue-100 text-blue-800',
      'Onaylandı': 'bg-green-100 text-green-800',
      'Beklemede': 'bg-yellow-100 text-yellow-800',
      'Tamamlandı': 'bg-green-100 text-green-800',
      'İptal': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#137fec]"></div>
      </div>
    );
  }

  return (
    <div className="bg-[#F8F9FA]">
      <main className="p-8">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
          <button className="flex items-center gap-2 px-4 py-2.5 text-sm font-semibold text-white bg-[#137fec] rounded-lg shadow-sm hover:bg-blue-700">
            <span className="material-symbols-outlined">add</span>
            Yeni İlan Oluştur
          </button>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-xl border border-gray-200 flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Toplam Başvuru Sayısı</p>
              <p className="text-3xl font-bold mt-1 text-gray-900">{dashboardData.statistics?.totalApplications?.toLocaleString() || '0'}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <span className="material-symbols-outlined text-[#137fec]">folder_open</span>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl border border-gray-200 flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Aktif Süreçteki Aday Sayısı</p>
              <p className="text-3xl font-bold mt-1 text-gray-900">{dashboardData.statistics?.activeCandidates?.toLocaleString() || '0'}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <span className="material-symbols-outlined text-green-500">person_search</span>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl border border-gray-200 flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Bu Ay Görüşülen Aday Sayısı</p>
              <p className="text-3xl font-bold mt-1 text-gray-900">{dashboardData.statistics?.interviewsThisMonth?.toLocaleString() || '0'}</p>
            </div>
            <div className="p-3 bg-yellow-100 rounded-lg">
              <span className="material-symbols-outlined text-yellow-500">calendar_month</span>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl border border-gray-200 flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">İşe Alınan Aday Sayısı</p>
              <p className="text-3xl font-bold mt-1 text-gray-900">{dashboardData.statistics?.hiredCandidates?.toLocaleString() || '0'}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <span className="material-symbols-outlined text-purple-500">person_add</span>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 mt-8">
          {/* Candidate Status Distribution */}
          <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-gray-200">
            <h3 className="text-lg font-semibold mb-4 text-gray-900">Aday Durum Dağılımı</h3>
            <div className="flex items-center justify-center gap-8">
              <div className="pie-chart w-36 h-36 rounded-full" style={{
                background: `conic-gradient(
                  #137fec 0% 25%,
                  #4ade80 25% 45%,
                  #facc15 45% 60%,
                  #f87171 60% 75%,
                  #fb923c 75% 90%,
                  #a78bfa 90% 100%
                )`
              }}></div>
              <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                {dashboardData.candidateStatusDistribution?.map((item, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <span 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: item.color }}
                    ></span>
                    {item.status}
                  </div>
                )) || []}
              </div>
            </div>
          </div>

          {/* Position Application Volume */}
          <div className="lg:col-span-3 bg-white p-6 rounded-xl border border-gray-200">
            <h3 className="text-lg font-semibold mb-4 text-gray-900">Pozisyonlara Göre Başvuru Yoğunluğu</h3>
            <div className="grid grid-cols-6 gap-6 items-end h-56">
              {dashboardData.positionApplicationVolume?.map((item, index) => (
                <div key={index} className="flex flex-col items-center gap-2">
                  <div 
                    className="w-full rounded-t-md transition-all duration-300 hover:opacity-80" 
                    style={{
                      height: `${item.percentage}%`,
                      backgroundColor: '#137fec'
                    }}
                  ></div>
                  <p className="text-xs text-gray-500 text-center">{item.position}</p>
                </div>
              )) || []}
            </div>
          </div>
        </div>

        {/* Upcoming Interviews Table */}
        <div className="mt-8 bg-white rounded-xl border border-gray-200 overflow-hidden">
          <h3 className="text-lg font-semibold p-6 text-gray-900">Yaklaşan Mülakatlar</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-gray-50 text-gray-500 uppercase tracking-wider text-xs">
                <tr>
                  <th className="px-6 py-3" scope="col">Aday Adı</th>
                  <th className="px-6 py-3" scope="col">Pozisyon</th>
                  <th className="px-6 py-3" scope="col">Mülakat Tarihi</th>
                  <th className="px-6 py-3" scope="col">Durum</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {dashboardData.upcomingInterviews?.map((interview) => (
                  <tr key={interview.id}>
                    <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                      {interview.candidateName}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-500">
                      {interview.position}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-500">
                      {interview.date} {interview.time}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2.5 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(interview.status)}`}>
                        {interview.status}
                      </span>
                    </td>
                  </tr>
                )) || []}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardNew;
