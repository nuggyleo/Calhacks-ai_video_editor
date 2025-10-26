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
    setActiveVideoVersion, setPlaybackState, addEditedMediaToLibrary,
    saveVideo
  } = useAppStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const activeVideo = mediaBin.find(f => f.id === activeVideoId);

  // Auto-inject AI description - DISABLED
  // Vision analysis is now triggered manually, not automatically on upload
  // useEffect(() => {
  //   if (!activeVideoId) return;
  //   const hasAiDesc = messages.some(m => m.id === `ai-desc-${activeVideoId}`);
  //   if (!hasAiDesc && activeVideo?.description) {
  //     addMessage({
  //       id: `ai-desc-${activeVideoId}`,
  //       role: 'assistant',
  //       content: `**Video Analysis for ${activeVideo.filename}:**\n\n${activeVideo.description}`,
  //       timestamp: new Date(),
  //       status: 'completed',
  //     });
  //   }
  // }, [activeVideoId, activeVideo?.description, addMessage]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const formatTime = (date: Date) => new Date(date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

  // Handlers to control the main player
  // Note: These handlers are kept for potential future use with preview functionality
  // Currently, preview videos in messages don't sync with the main player
  const handlePreviewPlay = (e: React.SyntheticEvent<HTMLVideoElement>, messageUrl: string) => {
    e.preventDefault();
    // Removed setActiveVideoVersion to prevent overwriting original video in media bin
    // User should click "Add to Media" to add edited videos as new files
    setPlaybackState({ isPlaying: true });
  };
  const handlePreviewPause = (e: React.SyntheticEvent<HTMLVideoElement>) => {
    e.preventDefault();
    setPlaybackState({ isPlaying: false });
  };
  const handlePreviewSeek = (e: React.SyntheticEvent<HTMLVideoElement>, messageUrl: string) => {
    e.preventDefault();
    const newTime = e.currentTarget.currentTime;
    // Removed setActiveVideoVersion to prevent overwriting original video in media bin
    setPlaybackState({ currentTime: newTime });
  };

  return (
    <div className="h-full p-6 bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="mb-6 pb-4 border-b border-gray-800 flex-shrink-0">
        {activeVideoId ? (
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-xs font-semibold text-gray-500 tracking-wider">EDITING</span>
            <span className="text-sm font-medium text-white">{activeVideo?.filename}</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span>Upload a video to start editing</span>
          </div>
        )}
      </div>

      {/* Messages container */}
      <div className="flex-1 overflow-y-auto space-y-6 pr-2">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 mx-auto bg-gradient-to-br from-purple-600/20 to-blue-600/20 rounded-full flex items-center justify-center border-2 border-gray-700">
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-purple-400">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
              </div>
              <div>
                <p className="text-lg font-light text-gray-400">
                  {activeVideoId ? 'Start a conversation' : 'Select a video to begin'}
                </p>
                {activeVideoId && (
                  <p className="text-sm text-gray-600 mt-2">
                    Try: "Trim the first 5 seconds"
                  </p>
                )}
              </div>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`flex items-start gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {message.role === 'assistant' && (
                <div className="w-9 h-9 flex-shrink-0 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full flex items-center justify-center shadow-lg">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white">
                    <path d="M12 8V4H8" />
                    <rect width="16" height="12" x="4" y="8" rx="2" />
                    <path d="M2 14h2" />
                    <path d="M20 14h2" />
                    <path d="M15 13v2" />
                    <path d="M9 13v2" />
                  </svg>
                </div>
              )}
              <div className={`max-w-md px-4 py-3 rounded-2xl backdrop-blur-sm ${message.role === 'user' ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white shadow-lg' : 'bg-gray-800/80 text-gray-100 border border-gray-700/50'}`}>
                {/* Message Content, Video, Buttons etc. go here, structured cleanly */}
                <div className="prose prose-invert prose-sm max-w-none break-words whitespace-pre-wrap">{message.content}</div>
                {message.videoUrl && (
                  <div className="mt-3 space-y-2">
                    <div className="rounded-lg overflow-hidden border border-gray-600">
                      {(() => {
                        const urlLower = message.videoUrl!.toLowerCase();
                        const isAudio = message.mediaType === 'audio' ||
                          urlLower.includes('.mp3') ||
                          urlLower.includes('.wav') ||
                          urlLower.includes('.m4a') ||
                          urlLower.includes('.aac') ||
                          urlLower.includes('extracted_audio');
                        return isAudio ? (
                          <audio
                            src={message.videoUrl}
                            controls
                            className="w-full"
                          />
                        ) : (
                          <video
                            src={message.videoUrl}
                            controls
                            onPlay={(e) => handlePreviewPlay(e, message.videoUrl!)}
                            onPause={handlePreviewPause}
                            onSeeked={(e) => handlePreviewSeek(e, message.videoUrl!)}
                            className="w-full"
                          />
                        );
                      })()}
                    </div>
                    {/* Action buttons */}
                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          // Improved media type detection - check URL for audio extensions
                          const urlLower = message.videoUrl!.toLowerCase();
                          const isAudio = message.mediaType === 'audio' ||
                            urlLower.includes('.mp3') ||
                            urlLower.includes('.wav') ||
                            urlLower.includes('.m4a') ||
                            urlLower.includes('.aac') ||
                            urlLower.includes('extracted_audio');
                          const mediaType = isAudio ? 'audio' : 'video';

                          // Get filename from URL if not provided
                          const urlFilename = message.videoUrl!.split('/').pop() || '';
                          const filename = message.mediaFilename || urlFilename || `${mediaType}-${Date.now()}.${mediaType === 'audio' ? 'mp3' : 'mp4'}`;

                          console.log('Adding to library:', { url: message.videoUrl, filename, mediaType, messageMediaType: message.mediaType, urlLower });
                          addEditedMediaToLibrary(message.videoUrl!, filename, mediaType);
                        }}
                        className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all transform hover:scale-[1.02]"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                          <polyline points="7 10 12 15 17 10" />
                          <line x1="12" y1="15" x2="12" y2="3" />
                        </svg>
                        Add to Media
                      </button>

                      {/* Save to Project button - only show for videos */}
                      {(() => {
                        const urlLower = message.videoUrl!.toLowerCase();
                        const isAudio = message.mediaType === 'audio' ||
                          urlLower.includes('.mp3') ||
                          urlLower.includes('.wav') ||
                          urlLower.includes('.m4a') ||
                          urlLower.includes('.aac') ||
                          urlLower.includes('extracted_audio');

                        console.log('Save button check:', {
                          messageId: message.id,
                          hasVideoUrl: !!message.videoUrl,
                          isAudio,
                          mediaType: message.mediaType,
                          url: message.videoUrl
                        });

                        return !isAudio;
                      })() && (
                          <button
                            onClick={async () => {
                              const urlFilename = message.videoUrl!.split('/').pop() || '';
                              const filename = message.mediaFilename || urlFilename || `video-${Date.now()}.mp4`;
                              console.log('Saving video to project:', { url: message.videoUrl, filename, description: message.content });

                              try {
                                await saveVideo(message.videoUrl!, filename, message.content);
                                // Show success feedback
                                const button = document.activeElement as HTMLButtonElement;
                                if (button) {
                                  const originalText = button.innerHTML;
                                  button.innerHTML = '✅ Saved!';
                                  button.disabled = true;
                                  setTimeout(() => {
                                    button.innerHTML = originalText;
                                    button.disabled = false;
                                  }, 2000);
                                }
                              } catch (error) {
                                console.error('Failed to save video:', error);
                                alert('Failed to save video');
                              }
                            }}
                            className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:from-gray-600 disabled:to-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all transform hover:scale-[1.02] shadow-lg"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                              <polyline points="17 21 17 13 7 13 7 21" />
                              <polyline points="7 3 7 8 15 8" />
                            </svg>
                            💾 Save to Collection
                          </button>
                        )}
                    </div>
                  </div>
                )}
                <div className="text-xs text-gray-400 mt-2 text-right">{formatTime(message.timestamp)}</div>
              </div>
              {message.role === 'user' && (
                <div className="w-9 h-9 flex-shrink-0 bg-gradient-to-br from-gray-700 to-gray-600 rounded-full flex items-center justify-center border-2 border-gray-600 shadow-lg">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-300">
                    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
                    <circle cx="12" cy="7" r="4" />
                  </svg>
                </div>
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
