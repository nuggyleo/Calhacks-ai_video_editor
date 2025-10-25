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
    <div className="space-y-3">
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSend()}
          placeholder={activeVideoId ? 'Send editing command...' : 'Select a video first...'}
          disabled={!activeVideoId || isLoading}
          className="flex-grow bg-gray-700 text-white px-4 py-2 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          onClick={handleSend}
          disabled={!activeVideoId || !input.trim() || isLoading}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-6 py-2 rounded text-sm font-medium transition-colors disabled:cursor-not-allowed"
        >
          {isLoading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
};

export default CommandInput;
