import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';

const Layout = () => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <div className="relative flex size-full min-h-screen flex-row text-gray-800 group/design-root overflow-x-hidden" style={{fontFamily: 'Plus Jakarta Sans, Noto Sans, sans-serif'}}>
      <Sidebar isCollapsed={isSidebarCollapsed} onToggle={toggleSidebar} />
      <main className="flex-1 bg-gray-50 relative">
        <Header onMenuClick={toggleSidebar} />
        <div className="p-6 lg:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;

