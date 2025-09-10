import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const Sidebar = ({ isCollapsed, onToggle }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: 'dashboard', path: '/dashboard' },
    { id: 'candidates', label: 'Aday Yönetimi', icon: 'groups', path: '/candidates' },
    { id: 'interviews', label: 'Mülakat Takvimi', icon: 'calendar_month', path: '/interviews' },
    { id: 'case-studies', label: 'Vaka Çalışmaları', icon: 'work', path: '/case-studies' },
    { id: 'users', label: 'Kullanıcı Yönetimi', icon: 'manage_accounts', path: '/users' },
    { id: 'reports', label: 'Raporlar', icon: 'monitoring', path: '/reports' },
  ];

  const handleMenuClick = (path) => {
    navigate(path);
  };

  return (
    <div className={`bg-white border-r border-gray-200 flex flex-col justify-between p-4 transition-all duration-300 ease-in-out ${
      isCollapsed ? 'w-20' : 'w-70'
    }`}>
      <div>
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-2">
            <svg className="h-8 w-8 text-[#137fec]" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0012 9.75c-2.551 0-5.056.2-7.5.582V21M3 21h18M12 6.75h.008v.008H12V6.75z" strokeLinecap="round" strokeLinejoin="round"></path>
            </svg>
            {!isCollapsed && (
              <h1 className="text-gray-800 text-xl font-bold leading-normal">HR-ATS</h1>
            )}
          </div>
        </div>
        
        <nav className="flex flex-col gap-2">
          {menuItems.map((item) => {
            // Check if current path starts with the menu item path (for sub-routes)
            const isActive = location.pathname === item.path || 
              (item.path !== '/dashboard' && location.pathname.startsWith(item.path));
            return (
              <button
                key={item.id}
                onClick={() => handleMenuClick(item.path)}
                className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                  isActive 
                    ? 'bg-blue-50 text-[#137fec]' 
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                } ${isCollapsed ? 'justify-center' : ''}`}
              >
                <span className="material-symbols-outlined">{item.icon}</span>
                {!isCollapsed && (
                  <p className="text-sm font-medium">{item.label}</p>
                )}
              </button>
            );
          })}
        </nav>
      </div>
      
      <button 
        className={`flex items-center justify-center gap-3 w-full h-10 px-4 rounded-md text-gray-600 hover:bg-gray-100 hover:text-gray-900 ${
          isCollapsed ? 'justify-center' : ''
        }`}
        onClick={onToggle}
      >
        <span className={`material-symbols-outlined transition-transform ${
          isCollapsed ? 'rotate-180' : ''
        }`}>
          keyboard_double_arrow_left
        </span>
        {!isCollapsed && (
          <span className="truncate text-sm font-medium">
            {isCollapsed ? 'Menüyü Aç' : 'Menüyü Kapat'}
          </span>
        )}
      </button>
    </div>
  );
};

export default Sidebar;
