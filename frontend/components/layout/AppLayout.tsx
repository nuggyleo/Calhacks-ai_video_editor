// This component establishes the main three-column layout of the application.
// It uses CSS Grid or Flexbox to create the distinct sections for media,
// the video player, and the chat interface. It ensures the layout is
// responsive and visually balanced.

import React from 'react';

const AppLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <main className="bg-gray-900 text-white h-screen w-screen flex">
      {/* We can define the grid columns here, e.g., 1fr 3fr 1.5fr */}
      <div className="grid grid-cols-6 w-full h-full">
        {children}
      </div>
    </main>
  );
};

export default AppLayout;
