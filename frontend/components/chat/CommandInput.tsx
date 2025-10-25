// This component is the text input field where the user types their commands.
// It will handle sending the user's message to the backend.
// It now connects to the app store to track which video is being edited.

'use client';

import { useState } from 'react';
import { useAppStore } from '@/lib/store';

const CommandInput = () => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { currentVideoId, currentVideoUrl, mediaFiles, addMessage, updateMessage, setCurrentVideoUrl } = useAppStore();

  const handleSend = async () => {
    if (!input.trim() || !currentVideoId || !currentVideoUrl) return;

    setIsLoading(true);

    const userMessageId = `msg-${Date.now()}`;
    addMessage({
      id: userMessageId,
      videoId: currentVideoId,
      role: 'user',
      content: input,
      timestamp: new Date(),
      status: 'completed',
    });

    const assistantMessageId = `assistant-${Date.now()}`;
    addMessage({
      id: assistantMessageId,
      videoId: currentVideoId,
      role: 'assistant',
      content: '🧠 Processing...',
      timestamp: new Date(),
      status: 'pending',
    });

    setInput('');

    try {
      const video = mediaFiles.find(f => f.id === currentVideoId);
      
      const response = await fetch('http://localhost:8000/api/edit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          video_id: currentVideoId,
          video_url: currentVideoUrl,
          command: input.trim(),
          video_description: video?.description || '',
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      
      const result = await response.json();
      
      // If the backend sent back a new video URL, update the player and the message
      const fullUrl = result.output_url ? `http://localhost:8000${result.output_url}` : undefined;

      updateMessage(assistantMessageId, {
        content: result.message || 'I received a response, but it was empty.',
        status: 'completed',
        timestamp: new Date(),
        videoUrl: fullUrl, // Attach the new video URL to the message
      });
      
      if (fullUrl && currentVideoId) {
        setCurrentVideoUrl(fullUrl, currentVideoId);
      }
      
    } catch (error) {
      console.error('Failed to send command:', error);
      updateMessage(assistantMessageId, {
        content: 'Sorry, I encountered an error. Please try again.',
        status: 'error',
        timestamp: new Date(),
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSend()}
          placeholder={currentVideoId ? 'Send editing command...' : 'Select a video first...'}
          disabled={!currentVideoId || isLoading}
          className="flex-grow bg-gray-700 text-white px-4 py-2 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          onClick={handleSend}
          disabled={!currentVideoId || !input.trim() || isLoading}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-6 py-2 rounded text-sm font-medium transition-colors disabled:cursor-not-allowed"
        >
          {isLoading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
};

export default CommandInput;
