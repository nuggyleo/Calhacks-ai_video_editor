'use client';

import { useEffect } from 'react';
import { useAppStore } from '@/lib/store';

const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const { login, logout, authStatus, setAuthStatus } = useAppStore();

  useEffect(() => {
    if (authStatus !== 'loading') return;

    try {
      const token = localStorage.getItem('token');
      const userEmail = localStorage.getItem('userEmail');
      
      if (token && userEmail) {
        // Simple check: if we have both token and email, consider user logged in
        login({ email: userEmail }, token);
      } else {
        setAuthStatus('unauthenticated');
      }
    } catch (error) {
      console.error('Failed to process authentication:', error);
      logout();
    }
  }, [authStatus, login, logout, setAuthStatus]);

  return <>{children}</>;
};

export default AuthProvider;
