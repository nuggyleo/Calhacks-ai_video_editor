// This component is responsible for rendering the list of messages in the chat.
// It will display the user's commands and the AI's responses.
// AI responses could be specially formatted, perhaps including images, buttons,
// or other rich media to make the interaction feel more dynamic and intelligent.

'use client';

import { useEffect, useRef } from 'react';
import { useAppStore } from '@/lib/store';

const MessageList = () => {
  const { currentVideoId, mediaFiles, messages, getMessagesByVideoId, addMessage } = useAppStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Get current video name
  const currentVideo = mediaFiles.find(f => f.id === currentVideoId);

  // Get messages for current video
  const videoMessages = currentVideoId ? getMessagesByVideoId(currentVideoId) : [];

  // Auto-inject AI description as a chat message if none exists yet for the current video
  useEffect(() => {
    if (!currentVideoId) return;

    const hasAiDesc = videoMessages.some(m => m.id === `ai-desc-${currentVideoId}`);
    const video = mediaFiles.find(f => f.id === currentVideoId);

    if (!hasAiDesc && video?.description) {
      addMessage({
        id: `ai-desc-${currentVideoId}`,
        videoId: currentVideoId,
        role: 'assistant',
        content: `**Video Analysis:**\n\n${video.description}`,
        timestamp: new Date(),
        status: 'completed',
      });
    }
  }, [currentVideoId, mediaFiles, videoMessages, addMessage]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [videoMessages]);

  // Format timestamp
  const formatTime = (date: Date) => {
    const d = new Date(date);
    return d.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div className="flex-grow mb-4 p-4 bg-gray-900 rounded-lg flex flex-col overflow-hidden">
      {/* Header with current video info */}
      <div className="mb-4 pb-3 border-b border-gray-700">
        {currentVideoId ? (
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-gray-400">EDITING:</span>
            <span className="text-sm font-medium text-blue-300">{currentVideo?.filename}</span>
          </div>
        ) : (
          <div className="text-xs text-yellow-400">
            ⚠️ Select a video to start editing
          </div>
        )}
      </div>

      {/* Messages container */}
      <div className="flex-grow overflow-y-auto space-y-3">
        {videoMessages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="text-gray-400 text-sm font-medium mb-1">
                {currentVideoId
                  ? 'No commands yet. Send your first editing command!'
                  : 'No video selected'}
              </p>
              <p className="text-gray-600 text-xs">
                {currentVideoId
                  ? 'Example: "Trim the first 10 seconds" or "Add fade out effect"'
                  : 'Upload or select a video from the Media panel'}
              </p>
            </div>
          </div>
        ) : (
          videoMessages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`
                  max-w-xs px-4 py-3 rounded-lg text-sm
                  ${message.role === 'user'
                    ? 'bg-blue-600 text-white rounded-br-none'
                    : 'bg-gray-800 text-gray-200 rounded-bl-none border border-gray-700'
                  }
                `}
              >
                <div className="flex items-start gap-2">
                  {message.role === 'user' ? (
                    <span className="flex-shrink-0 mt-0.5">👤</span>
                  ) : (
                    <span className="flex-shrink-0 mt-0.5">🤖</span>
                  )}
                  <div className="flex-grow">
                    <div className="break-words whitespace-pre-wrap prose prose-invert max-w-none text-sm">
                      {message.content.split('\n\n').map((paragraph, i) => (
                        <p key={i} className="mb-2 last:mb-0">
                          {paragraph.split('\n').map((line, j) => (
                            <span key={j} className="block">
                              {line.split(/(\*\*.*?\*\*)/g).map((part, k) =>
                                part.startsWith('**') && part.endsWith('**') ? (
                                  <strong key={k}>{part.slice(2, -2)}</strong>
                                ) : (
                                  part
                                )
                              )}
                            </span>
                          ))}
                        </p>
                      ))}
                    </div>
                    <div className="flex items-center justify-between gap-2 mt-1 text-xs opacity-70">
                      <span>{formatTime(message.timestamp)}</span>
                      {message.status && (
                        <span className={`
                          px-2 py-0.5 rounded-full text-xs
                          ${message.status === 'pending' ? 'bg-yellow-900/30 text-yellow-300' : ''}
                          ${message.status === 'completed' ? 'bg-green-900/30 text-green-300' : ''}
                          ${message.status === 'error' ? 'bg-red-900/30 text-red-300' : ''}
                        `}>
                          {message.status === 'pending' ? '⏳ Processing' : ''}
                          {message.status === 'completed' ? '✅ Done' : ''}
                          {message.status === 'error' ? '❌ Error' : ''}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Footer with message count */}
      {videoMessages.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-700 text-xs text-gray-500">
          {videoMessages.length} message{videoMessages.length !== 1 ? 's' : ''}
        </div>
      )}
    </div>
  );
};

export default MessageList;
