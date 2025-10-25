// This component establishes the main three-column layout of the application.
// It uses CSS Grid or Flexbox to create the distinct sections for media,
// the video player, and the chat interface. It ensures the layout is
// responsive and visually balanced.

'use client';

import React from 'react';
import { useAppStore } from '@/lib/store';
import { useRouter } from 'next/navigation';

const AppLayout = ({ children }: { children: React.ReactNode }) => {
  const { user, logout } = useAppStore();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <main className="bg-black text-white h-screen w-screen flex flex-col">
      {/* Top Navigation Bar */}
      <div className="bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <h1 className="font-lobster text-2xl bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Cue
          </h1>
        </div>
        
        <div className="flex items-center gap-4">
          {/* User Info */}
          <div className="flex items-center gap-2 text-sm">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center font-semibold">
              {user?.email.charAt(0).toUpperCase()}
            </div>
            <span className="text-gray-300">{user?.email}</span>
          </div>
          
          {/* Logout Button */}
          <button
            onClick={handleLogout}
            className="px-4 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white text-sm rounded transition-colors border border-gray-700"
          >
            Log Out
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {children}
      </div>
    </main>
  );
};

export default AppLayout;
