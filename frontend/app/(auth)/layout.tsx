'use client';

import React, { useEffect } from 'react';
import { useAppStore } from '@/lib/store';
import { useRouter } from 'next/navigation';

const AuthLayout = ({ children }: { children: React.ReactNode }) => {
  const { authStatus } = useAppStore();
  const router = useRouter();

  useEffect(() => {
    if (authStatus === 'authenticated') {
      router.push('/');
    }
  }, [authStatus, router]);

  if (authStatus === 'loading' || authStatus === 'authenticated') {
    return (
      <div className="w-screen h-screen bg-black flex items-center justify-center">
        <p className="text-white">Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="w-full max-w-md p-8 space-y-8 bg-gray-900 rounded-lg shadow-lg">
        {children}
      </div>
    </div>
  );
};

export default AuthLayout;
