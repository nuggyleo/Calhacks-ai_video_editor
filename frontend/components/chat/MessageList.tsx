// This component is responsible for rendering the list of messages in the chat.
// It will display the user's commands and the AI's responses.
// AI responses could be specially formatted, perhaps including images, buttons,
// or other rich media to make the interaction feel more dynamic and intelligent.

'use client';

import { useEffect, useRef } from 'react';
import { useAppStore } from '@/lib/store';

const MessageList = () => {
  const { currentVideoId, mediaFiles, messages, getMessagesByVideoId, addMessage, revertToPreviousVersion, redoLastAction } = useAppStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Get current video
  const currentVideo = mediaFiles.find(f => f.id === currentVideoId);

  // Get messages for current video
  const videoMessages = currentVideoId ? getMessagesByVideoId(currentVideoId) : [];

  // This useEffect is now simplified as we handle the initial message in FileUploader
  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [videoMessages]);

  const formatTime = (date: Date) => new Date(date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

  // Find the ID of the last message that has a video URL for revert logic
  const lastVideoMessageId = videoMessages.slice().reverse().find(m => m.videoUrl)?.id;

  return (
    <div className="h-full overflow-y-auto p-4 space-y-6">
      {videoMessages.length === 0 ? (
        <div className="flex items-center justify-center h-full">
          <div className="text-center text-gray-500">
            <p className="text-lg">
              {currentVideoId ? 'Start by sending a command' : 'Select a video to begin'}
            </p>
            {currentVideoId && (
              <p className="text-sm mt-2">e.g., "Trim the first 5 seconds"</p>
            )}
          </div>
        </div>
      ) : (
        <>
          {videoMessages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {/* Icon */}
              {message.role === 'assistant' && (
                <div className="w-8 h-8 flex-shrink-0 bg-gray-600 rounded-full flex items-center justify-center">
                  🤖
                </div>
              )}

              {/* Message Bubble */}
              <div
                className={`
                  max-w-full px-4 py-3 rounded-2xl
                  ${message.role === 'user'
                    ? 'bg-blue-600 text-white rounded-br-lg'
                    : 'bg-gray-800 text-gray-200 rounded-bl-lg'
                  }
                `}
              >
                <div className="prose prose-invert prose-sm max-w-none break-words whitespace-pre-wrap">
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

                {/* Video Attachment */}
                {message.videoUrl && (
                  <div className="mt-3 rounded-lg overflow-hidden border border-gray-600 relative group">
                    <video src={message.videoUrl} controls className="w-full" />
                    {message.id === lastVideoMessageId && (currentVideo?.versionHistory?.length ?? 0) > 1 && (
                      <button
                        onClick={() => currentVideoId && revertToPreviousVersion(currentVideoId)}
                        className="absolute top-2 right-2 bg-black/50 text-white px-3 py-1 text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity hover:bg-black/80"
                      >
                        ↩️ Revert
                      </button>
                    )}
                  </div>
                )}
                
                {/* Redo Button */}
                {message.content.includes('reverted to the previous version') && (currentVideo?.redoHistory?.length ?? 0) > 0 && (
                  <div className="mt-2">
                    <button
                      onClick={() => currentVideoId && redoLastAction(currentVideoId)}
                      className="bg-gray-600 hover:bg-gray-500 text-white px-3 py-1 text-xs rounded transition-colors"
                    >
                      ↪️ Redo
                    </button>
                  </div>
                )}
              </div>

              {/* User Icon */}
              {message.role === 'user' && (
                <div className="w-8 h-8 flex-shrink-0 bg-gray-600 rounded-full flex items-center justify-center">
                  👤
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </>
      )}
    </div>
  );
};

export default MessageList;
