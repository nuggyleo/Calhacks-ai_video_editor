// This component establishes the main three-column layout of the application.
// It uses CSS Grid or Flexbox to create the distinct sections for media,
// the video player, and the chat interface. It ensures the layout is
// responsive and visually balanced.

import React from 'react';

const AppLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <main className="bg-black text-white h-screen w-screen flex">
      {children}
    </main>
  );
};

export default AppLayout;
