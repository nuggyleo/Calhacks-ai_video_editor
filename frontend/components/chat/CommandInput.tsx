// This component is the text input field where the user types their commands.
// It will handle sending the user's message to the backend.
// It now connects to the app store to track which video is being edited.

'use client';

import { useState } from 'react';
import { useAppStore } from '@/lib/store';

const CommandInput = () => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { currentVideoId, currentVideoUrl, mediaFiles, setIsUploading } = useAppStore();
  
  // Get the current video filename
  const currentVideo = mediaFiles.find(f => f.id === currentVideoId);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim()) {
      return;
    }
    
    if (!currentVideoId) {
      alert('Please select or upload a video first');
      return;
    }
    
    setIsLoading(true);
    
    try {
      // Create a unique message ID for tracking
      const messageId = `msg_${Date.now()}_${Math.random()}`;
      
      // Add user message to store
      useAppStore.getState().addMessage({
        id: messageId,
        videoId: currentVideoId,
        role: 'user',
        content: input.trim(),
        timestamp: new Date(),
        status: 'completed'
      });
      
      // Create assistant message with pending status
      const assistantMessageId = `msg_${Date.now()}_${Math.random()}_assistant`;
      useAppStore.getState().addMessage({
        id: assistantMessageId,
        videoId: currentVideoId,
        role: 'assistant',
        content: 'Processing your request...',
        timestamp: new Date(),
        status: 'pending'
      });
      
      const response = await fetch('http://localhost:8000/api/edit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_id: currentVideoId,
          video_url: currentVideoUrl,
          command: input.trim(),
        }),
      });
      
      if (!response.ok) {
        const error = await response.json();
        const errorMessage = `Error: ${error.detail || 'Failed to process command'}`;
        
        useAppStore.getState().updateMessage(assistantMessageId, {
          content: errorMessage,
          status: 'error'
        });
        return;
      }
      
      const result = await response.json();
      console.log('Command processed:', result);
      
      // Update assistant message with successful response
      useAppStore.getState().updateMessage(assistantMessageId, {
        content: result.message || 'Your request has been processed successfully.',
        status: 'completed'
      });
      
      // Clear the input after successful submission
      setInput('');
      
    } catch (err) {
      console.error('Error submitting command:', err);
      
      // Add error message
      const assistantMessageId = `msg_${Date.now()}_${Math.random()}_error`;
      useAppStore.getState().addMessage({
        id: assistantMessageId,
        videoId: currentVideoId,
        role: 'assistant',
        content: 'Failed to submit command. Please try again.',
        timestamp: new Date(),
        status: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="space-y-2">
      {/* Current video indicator */}
      {currentVideoId && currentVideo ? (
        <div className="px-3 py-1 bg-blue-900/30 border border-blue-700 rounded text-xs text-blue-300">
          📹 Editing: <span className="font-semibold">{currentVideo.filename}</span>
        </div>
      ) : (
        <div className="px-3 py-1 bg-yellow-900/30 border border-yellow-700 rounded text-xs text-yellow-300">
          ⚠️ No video selected
        </div>
      )}
      
      {/* Input form */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={!currentVideoId || isLoading}
          placeholder={currentVideoId ? "e.g., Trim video from 0:10 to 0:45" : "Select a video first"}
          className={`
            flex-1 h-12 bg-gray-700 rounded-lg px-4 text-white placeholder-gray-400
            focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all
            ${!currentVideoId || isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-600'}
          `}
        />
        <button
          type="submit"
          disabled={!currentVideoId || isLoading}
          className={`
            px-6 py-2 rounded-lg font-medium transition-all
            ${currentVideoId && !isLoading
              ? 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer'
              : 'bg-gray-700 text-gray-400 cursor-not-allowed'
            }
          `}
        >
          {isLoading ? '🔄 Processing...' : '📤 Send'}
        </button>
      </form>
    </div>
  );
};

export default CommandInput;
