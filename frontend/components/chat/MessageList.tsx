// This component is responsible for rendering the list of messages in the chat.
// It will display the user's commands and the AI's responses.
// AI responses could be specially formatted, perhaps including images, buttons,
// or other rich media to make the interaction feel more dynamic and intelligent.

'use client';

import { useEffect, useRef } from 'react';
import { useAppStore } from '@/lib/store';

const MessageList = () => {
  const {
    activeVideoId, mediaBin, messages, addMessage,
    revertToPreviousVersion, redoLastAction,
    setActiveVideoVersion, setPlaybackState
  } = useAppStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const activeVideo = mediaBin.find(f => f.id === activeVideoId);

  // Auto-inject AI description
  useEffect(() => {
    if (!activeVideoId) return;
    const hasAiDesc = messages.some(m => m.id === `ai-desc-${activeVideoId}`);
    if (!hasAiDesc && activeVideo?.description) {
      addMessage({
        id: `ai-desc-${activeVideoId}`,
        role: 'assistant',
        content: `**Video Analysis for ${activeVideo.filename}:**\n\n${activeVideo.description}`,
        timestamp: new Date(),
        status: 'completed',
      });
    }
  }, [activeVideoId, activeVideo?.description, addMessage]); // Simplified dependencies

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const formatTime = (date: Date) => new Date(date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

  const lastVideoMessageId = messages.slice().reverse().find(m => m.videoUrl)?.id;

  // Handlers to control the main player
  const handlePreviewPlay = (e: React.SyntheticEvent<HTMLVideoElement>, messageUrl: string) => {
    e.preventDefault();
    if (activeVideo?.url !== messageUrl) {
      setActiveVideoVersion(activeVideoId!, messageUrl);
    }
    setPlaybackState({ isPlaying: true });
  };
  const handlePreviewPause = (e: React.SyntheticEvent<HTMLVideoElement>) => {
    e.preventDefault();
    setPlaybackState({ isPlaying: false });
  };
  const handlePreviewSeek = (e: React.SyntheticEvent<HTMLVideoElement>, messageUrl: string) => {
    e.preventDefault();
    const newTime = e.currentTarget.currentTime;
    if (activeVideo?.url !== messageUrl) {
      setActiveVideoVersion(activeVideoId!, messageUrl);
    }
    setPlaybackState({ currentTime: newTime });
  };

  return (
    <div className="flex-grow mb-4 p-4 bg-gray-900 rounded-lg flex flex-col overflow-hidden">
      {/* Header */}
      <div className="mb-4 pb-3 border-b border-gray-700">
        {activeVideoId ? (
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-gray-400">EDITING:</span>
            <span className="text-sm font-medium text-blue-300">{activeVideo?.filename}</span>
          </div>
        ) : (
          <div className="text-xs text-yellow-400">⚠️ Select a video to start editing</div>
        )}
      </div>

      {/* Messages container */}
      <div className="flex-grow overflow-y-auto space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500">
              <p className="text-lg">
                {activeVideoId ? 'Start by sending a command' : 'Select a video to begin'}
              </p>
              {activeVideoId && <p className="text-sm mt-2">e.g., "Trim the first 5 seconds"</p>}
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`flex items-start gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {message.role === 'assistant' && (
                <div className="w-8 h-8 flex-shrink-0 bg-gray-600 rounded-full flex items-center justify-center">🤖</div>
              )}
              <div className={`max-w-md px-4 py-3 rounded-2xl ${message.role === 'user' ? 'bg-blue-600 text-white rounded-br-lg' : 'bg-gray-800 text-gray-200 rounded-bl-lg'}`}>
                {/* Message Content, Video, Buttons etc. go here, structured cleanly */}
                <div className="prose prose-invert prose-sm max-w-none break-words whitespace-pre-wrap">{message.content}</div>
                {message.videoUrl && (
                  <div className="mt-3 rounded-lg overflow-hidden border border-gray-600 relative group">
                    <video
                      src={message.videoUrl}
                      controls
                      onPlay={(e) => handlePreviewPlay(e, message.videoUrl!)}
                      onPause={handlePreviewPause}
                      onSeeked={(e) => handlePreviewSeek(e, message.videoUrl!)}
                      className="w-full"
                    />
                    {message.id === lastVideoMessageId && (activeVideo?.versionHistory?.length ?? 0) > 1 && (
                      <button
                        onClick={() => activeVideoId && revertToPreviousVersion(activeVideoId)}
                        className="absolute top-2 right-2 bg-black/50 text-white px-3 py-1 text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity hover:bg-black/80"
                      >
                        ↩️ Revert
                      </button>
                    )}
                  </div>
                )}
                {message.content.includes('reverted to the previous version') && (activeVideo?.redoHistory?.length ?? 0) > 0 && (
                  <div className="mt-2">
                    <button onClick={() => activeVideoId && redoLastAction(activeVideoId)} className="bg-gray-600 hover:bg-gray-500 text-white px-3 py-1 text-xs rounded transition-colors">
                      ↪️ Redo
                    </button>
                  </div>
                )}
                <div className="text-xs text-gray-400 mt-2 text-right">{formatTime(message.timestamp)}</div>
              </div>
              {message.role === 'user' && (
                <div className="w-8 h-8 flex-shrink-0 bg-gray-600 rounded-full flex items-center justify-center">👤</div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default MessageList;
