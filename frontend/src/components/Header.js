import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const Header = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-gray-200 bg-white px-6 py-4 shadow-sm">
      <div className="flex items-center gap-4 text-slate-800">
        <button className="p-2 rounded-md hover:bg-gray-100 transition-colors">
          <span className="material-symbols-outlined text-gray-600">menu</span>
        </button>
      </div>
      <div className="flex items-center gap-4">
        <button 
          aria-label="Notifications" 
          className="flex items-center justify-center rounded-full size-10 text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors"
        >
          <span className="material-symbols-outlined">notifications</span>
        </button>
        <div className="flex items-center gap-3">
          <div 
            className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10" 
            style={{
              backgroundImage: `url("https://lh3.googleusercontent.com/aida-public/AB6AXuBZTsraFmqtwB9tZA6SGRgqsvXs4yBJ4dz0xFd_hCEA1YsBfGNZJBxMR4fhXXLhPC2HyuXJjtg6LF9Oz0pYt9BFP2nqnkvPg5VZnFvHSf3AIugjrFORf5rb_gTl6snuG1RucpsM6oNneCbpM2Hm4b6N_3Wcg5R6zyXA2poz0i4fZIdSpApCUzTQMKAa23iKa97RfnJXgbRbCG7VsIla1S-Y1NN-OSe606BjFyYSeKK7GcIoP8NfYFUEWRiIUjoVlNjI9ve-hxhSYwM")`
            }}
          ></div>
          <div className="text-sm">
            <div className="font-semibold text-slate-800">
              {user?.first_name || 'Kullanıcı'} {user?.last_name || ''}
            </div>
            <div className="text-gray-500">
              {user?.role || 'İK Uzmanı'}
            </div>
          </div>
          <button 
            aria-label="Logout" 
            className="flex items-center justify-center rounded-full size-10 text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors"
            onClick={handleLogout}
          >
            <span className="material-symbols-outlined">logout</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;

