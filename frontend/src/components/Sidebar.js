import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const Sidebar = ({ isCollapsed, onToggle }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [expandedMenus, setExpandedMenus] = useState([]);

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: 'dashboard', path: '/dashboard' },
    { id: 'candidates', label: 'Aday Yönetimi', icon: 'groups', path: '/candidates' },
    { id: 'interviews', label: 'Mülakat Takvimi', icon: 'calendar_month', path: '/interviews' },
    { id: 'case-studies', label: 'Vaka Çalışmaları', icon: 'work', path: '/case-studies' },
    { 
      id: 'user-role-management', 
      label: 'Kullanıcı/Rol Yönetimi', 
      icon: 'manage_accounts', 
      path: '/user-role-management',
      subItems: [
        { id: 'users', label: 'Kullanıcı Yönetimi', icon: 'person', path: '/users' },
        { id: 'roles', label: 'Rol Yönetimi', icon: 'admin_panel_settings', path: '/roles' }
      ]
    },
    { id: 'reports', label: 'Raporlar', icon: 'monitoring', path: '/reports' },
  ];

  const handleMenuClick = (item) => {
    if (item.subItems) {
      // Toggle submenu
      setExpandedMenus(prev => 
        prev.includes(item.id) 
          ? prev.filter(id => id !== item.id)
          : [...prev, item.id]
      );
    } else {
      navigate(item.path);
    }
  };

  const handleSubMenuClick = (path) => {
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
            const isExpanded = expandedMenus.includes(item.id);
            const isActive = location.pathname === item.path || 
              (item.subItems && item.subItems.some(subItem => location.pathname === subItem.path));
            
            return (
              <div key={item.id}>
                <button
                  onClick={() => handleMenuClick(item)}
                  className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors w-full ${
                    isActive 
                      ? 'bg-blue-50 text-[#137fec]' 
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  } ${isCollapsed ? 'justify-center' : ''}`}
                >
                  <span className="material-symbols-outlined">{item.icon}</span>
                  {!isCollapsed && (
                    <>
                      <p className="text-sm font-medium flex-1 text-left">{item.label}</p>
                      {item.subItems && (
                        <span className={`material-symbols-outlined text-sm transition-transform ${
                          isExpanded ? 'rotate-180' : ''
                        }`}>
                          expand_more
                        </span>
                      )}
                    </>
                  )}
                </button>
                
                {/* Submenu */}
                {item.subItems && isExpanded && !isCollapsed && (
                  <div className="ml-4 mt-1 space-y-1">
                    {item.subItems.map((subItem) => {
                      const isSubActive = location.pathname === subItem.path;
                      return (
                        <button
                          key={subItem.id}
                          onClick={() => handleSubMenuClick(subItem.path)}
                          className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors w-full text-sm ${
                            isSubActive 
                              ? 'bg-blue-50 text-[#137fec]' 
                              : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                          }`}
                        >
                          <span className="material-symbols-outlined text-base">{subItem.icon}</span>
                          <p className="font-medium">{subItem.label}</p>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
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
