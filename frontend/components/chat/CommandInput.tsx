// This component is the text input field where the user types their commands.
// It will handle sending the user's message to the backend.
// It now connects to the app store to track which video is being edited.

'use client';

import { useState } from 'react';
import { useAppStore } from '@/lib/store';

const CommandInput = () => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { activeVideoId, mediaBin, messages, addMessage, updateMessage, handleSuccessfulEdit } = useAppStore();

  const handleSend = async () => {
    if (!input.trim() || !activeVideoId) return;

    setIsLoading(true);

    // Add user message to the single global thread
    const userMessageId = `msg-user-${Date.now()}`;
    addMessage({
      id: userMessageId,
      role: 'user',
      content: input,
      timestamp: new Date(),
      status: 'completed',
    });

    const assistantMessageId = `assistant-${Date.now()}`;
    addMessage({
      id: assistantMessageId,
      role: 'assistant',
      content: '🧠 Processing...',
      timestamp: new Date(),
      status: 'pending',
    });

    setInput('');

    try {
      // Create a simple dictionary for the backend from the mediaBin
      const mediaBinForApi = mediaBin.reduce((acc, file) => {
        acc[file.id] = file.url; // Or file path if that's what backend expects
        return acc;
      }, {} as Record<string, string>);

      // --- NEW: Prepare the full chat history for the backend ---
      const chatHistoryForApi = messages.map(msg => ({
        role: msg.role,
        content: msg.content,
      }));

      const response = await fetch('http://localhost:8000/api/edit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          active_video_id: activeVideoId,
          media_bin: mediaBinForApi,
          command: input.trim(),
          chat_history: chatHistoryForApi, // <-- SEND FULL HISTORY
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const result = await response.json();

      const fullUrl = result.output_url ? `http://localhost:8000${result.output_url}` : undefined;
      const messageContent = result.message || 'I received a response, but it was empty.';

      // --- NEW: Use the single atomic action to sync state ---
      if (fullUrl && activeVideoId) {
        handleSuccessfulEdit(activeVideoId, fullUrl, assistantMessageId, messageContent);
      } else {
        // If there's no new video, just update the message text.
        updateMessage(assistantMessageId, {
          content: messageContent,
          status: 'completed',
          timestamp: new Date(),
        });
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
    <div className="relative">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSend()}
        placeholder={activeVideoId ? 'Send an editing command...' : 'Select a video to start'}
        disabled={!activeVideoId || isLoading}
        className="w-full bg-gray-700 text-white px-4 py-3 pr-12 rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <button
        onClick={handleSend}
        disabled={!activeVideoId || !input.trim() || isLoading}
        className="absolute right-3 top-1/2 -translate-y-1/2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white p-2 rounded-md transition-colors"
        aria-label="Send command"
      >
        {isLoading ? (
          <svg className="w-5 h-5 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="m22 2-7 20-4-9-9-4Z" />
            <path d="M22 2 11 13" />
          </svg>
        )}
      </button>
    </div>
  );
};

export default CommandInput;
