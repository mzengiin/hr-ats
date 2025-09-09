import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';

const Layout = () => {
  return (
    <div className="relative flex size-full min-h-screen flex-row text-gray-800 group/design-root overflow-x-hidden" style={{fontFamily: 'Plus Jakarta Sans, Noto Sans, sans-serif'}}>
      <Sidebar />
      <main className="flex-1 bg-gray-50 relative">
        <Header />
        <div className="p-6 lg:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;

