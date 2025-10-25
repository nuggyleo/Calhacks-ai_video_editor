// This component is the text input field where the user types their commands.
// It will handle sending the user's message to the backend.
// It now connects to the app store to track which video is being edited.

'use client';

import { useState } from 'react';
import { useAppStore } from '@/lib/store';

const CommandInput = () => {
  const [input, setInput] = useState('');
  const { currentVideoId, addMessage } = useAppStore();

  const handleSend = () => {
    if (!input.trim() || !currentVideoId) return;
    
    addMessage({
      id: `msg-${Date.now()}`,
      videoId: currentVideoId,
      role: 'user',
      content: input,
      timestamp: new Date(),
      status: 'pending',
    });
    
    setInput('');
  };

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder={currentVideoId ? 'Send editing command...' : 'Select a video first...'}
          disabled={!currentVideoId}
          className="flex-grow bg-gray-700 text-white px-4 py-2 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          onClick={handleSend}
          disabled={!currentVideoId || !input.trim()}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-6 py-2 rounded text-sm font-medium transition-colors disabled:cursor-not-allowed"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default CommandInput;
