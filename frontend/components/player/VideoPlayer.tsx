'use client';

// Video player with custom controls
// Supports play/pause, progress bar dragging, and time display
// Now includes drag-and-drop, click-to-upload, and toolbar for new video/chat

import { useRef, useState, useEffect, MouseEvent, DragEvent, ChangeEvent } from 'react';
import { useAppStore } from '@/lib/store';

const funQuotes = [
  "Every frame tells a story. What's yours?",
  "Lights, camera... AI action! 🎬",
  "Your next masterpiece starts here.",
  "Cut. Edit. Perfect. Repeat.",
  "Hollywood magic, AI powered.",
  "Transform footage into feelings.",
  "From raw clips to reel art.",
  "Where creativity meets technology.",
  "Edit smarter, not harder.",
  "Your vision, our AI precision.",
  "Because every second matters.",
  "Directing made delightful.",
];

const VideoPlayer = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const progressBarRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const {
    mediaBin, activeVideoId, activeAudioId, addMediaFile,
    setIsUploading, isUploading,
    playbackState, setPlaybackState // <-- NEW: Get playback state and setter
  } = useAppStore();

  // Local state for dragging is still needed
  const [isDraggingProgressBar, setIsDraggingProgressBar] = useState(false);
  const [isDraggingFile, setIsDraggingFile] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [duration, setDuration] = useState(0);
  const [currentQuoteIndex, setCurrentQuoteIndex] = useState(0);

  // Rotate quotes every 3 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentQuoteIndex((prev) => (prev + 1) % funQuotes.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  // Get the active video or audio file from the mediaBin
  const activeVideo = mediaBin.find(f => f.id === activeVideoId);
  const activeAudio = mediaBin.find(f => f.id === activeAudioId);
  const activeVideoUrl = activeVideo?.url;
  const activeAudioUrl = activeAudio?.url;

  // Format time as MM:SS
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // --- SYNC WITH GLOBAL STATE ---

  // Effect to control play/pause from global state
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    if (playbackState.isPlaying) {
      video.play().catch(e => console.error("Play interrupted", e));
    } else {
      video.pause();
    }
  }, [playbackState.isPlaying, activeVideoUrl]); // Re-run if the video source changes

  // Effect to control seeking from global state
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    // Only seek if the difference is significant, to avoid fighting with onTimeUpdate
    if (Math.abs(video.currentTime - playbackState.currentTime) > 0.5) {
      video.currentTime = playbackState.currentTime;
    }
  }, [playbackState.currentTime]);

  // --- UPDATE GLOBAL STATE FROM THIS PLAYER ---

  // Play/Pause toggle
  const togglePlayPause = () => {
    // Just update the global state; the effect will handle the rest
    setPlaybackState({ isPlaying: !playbackState.isPlaying });
  };

  // Update global time as video plays
  const handleTimeUpdate = () => {
    if (videoRef.current && !isDraggingProgressBar) {
      setPlaybackState({ currentTime: videoRef.current.currentTime });
    }
  };

  // Update local player state when video loads
  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };

  // Handle progress bar seeking
  const handleProgressClick = (e: MouseEvent<HTMLDivElement>) => {
    if (progressBarRef.current && videoRef.current) {
      const rect = progressBarRef.current.getBoundingClientRect();
      const pos = (e.clientX - rect.left) / rect.width;
      const newTime = pos * duration;
      setPlaybackState({ currentTime: newTime, isPlaying: playbackState.isPlaying });
    }
  };

  const handleProgressMouseDown = (e: MouseEvent<HTMLDivElement>) => {
    setIsDraggingProgressBar(true);
    handleProgressClick(e);
  };

  useEffect(() => {
    const handleMouseMove = (e: globalThis.MouseEvent) => {
      if (isDraggingProgressBar && progressBarRef.current && videoRef.current) {
        const rect = progressBarRef.current.getBoundingClientRect();
        const pos = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        const newTime = pos * duration;
        setPlaybackState({ currentTime: newTime, isPlaying: playbackState.isPlaying });
      }
    };

    const handleMouseUp = () => {
      setIsDraggingProgressBar(false);
    };

    if (isDraggingProgressBar) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDraggingProgressBar, duration, playbackState.isPlaying, setPlaybackState]);

  // Reset global state when video ends
  const handleEnded = () => {
    setPlaybackState({ isPlaying: false });
  };

  // Handle file upload
  const handleUpload = async (file: File) => {
    if (!file.type.startsWith('video/')) {
      setUploadError('Please upload a valid video file');
      return;
    }

    setUploadError(null);
    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        addMediaFile({
          id: result.file_id,
          filename: result.filename,
          url: `http://localhost:8000${result.url}`,
          type: file.type,
          mediaType: 'video', // VideoPlayer only handles video uploads
          uploadedAt: new Date(),
          description: result.description || 'No description available.',
          isAnalyzing: false,
        });

        setTimeout(() => {
          setIsUploading(false);
        }, 500);
      } else {
        setUploadError('Upload failed');
        setIsUploading(false);
      }
    } catch (err) {
      setUploadError('Upload error occurred');
      setIsUploading(false);
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDraggingFile(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDraggingFile(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDraggingFile(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleUpload(files[0]);
    }
  };

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleUpload(files[0]);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleUploadNewVideo = () => {
    fileInputRef.current?.click();
  };

  // Show audio player if audio is selected
  if (activeAudioUrl && !activeVideoUrl) {
    return (
      <div className="w-full bg-gray-900 flex flex-col rounded-lg overflow-hidden">
        {/* Header toolbar */}
        <div className="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-2">
            <span className="text-gray-400 text-sm">🎵 Now Playing:</span>
            <span className="text-white font-medium truncate">{activeAudio?.filename || 'Unknown'}</span>
          </div>
        </div>
        
        {/* Audio display area */}
        <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-purple-900/20 to-black p-8">
          <div className="text-center space-y-6">
            {/* Large audio icon */}
            <div className="w-32 h-32 mx-auto bg-gradient-to-br from-purple-600/30 to-blue-600/30 rounded-full flex items-center justify-center border-2 border-purple-500/50">
              <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-purple-400">
                <path d="M9 18V5l12-2v13"/>
                <circle cx="6" cy="18" r="3"/>
                <circle cx="18" cy="16" r="3"/>
              </svg>
            </div>
            
            <div>
              <h3 className="text-2xl font-light text-white mb-2">{activeAudio?.filename}</h3>
              <p className="text-sm text-gray-500">Audio file</p>
            </div>
            
            {/* HTML5 Audio Player */}
            <div className="w-full max-w-md mx-auto">
              <audio
                src={activeAudioUrl}
                controls
                className="w-full"
                style={{ 
                  filter: 'invert(1) hue-rotate(180deg)',
                  borderRadius: '8px'
                }}
              />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!activeVideoUrl) {
    return (
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        className={`
          flex-grow flex items-center justify-center cursor-pointer
          transition-all duration-300 relative overflow-hidden
          ${isDraggingFile ? 'bg-purple-500/5' : 'bg-black'}
          ${isUploading ? 'pointer-events-none' : ''}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          onChange={handleFileSelect}
          className="hidden"
        />

        {/* Background gradient effect */}
        <div className="absolute inset-0 bg-gradient-radial from-purple-900/20 via-transparent to-transparent opacity-50" />

        <div className="text-center space-y-8 z-10 px-8">
          {isUploading ? (
            <div className="space-y-6 animate-pulse">
              <div className="font-lobster text-6xl bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
                Cue
              </div>
              <p className="text-gray-400 text-xl font-light">Processing your video...</p>
              <div className="w-64 h-1 bg-gray-800 rounded-full mx-auto overflow-hidden">
                <div className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 animate-shimmer" />
              </div>
            </div>
          ) : (
            <div className="space-y-12">
              {/* Logo */}
              <div className="font-lobster text-9xl bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent animate-pulse-slow">
                Cue
              </div>

              {/* Dynamic Quote */}
              <div className="h-10 flex items-center justify-center">
                <p 
                  key={currentQuoteIndex}
                  className="text-2xl font-light text-gray-400 animate-fade-in-out italic"
                >
                  {funQuotes[currentQuoteIndex]}
                </p>
              </div>

              {/* Upload prompt */}
              <div className="space-y-6 pt-8">
                <div className={`
                  w-24 h-24 mx-auto rounded-full flex items-center justify-center
                  bg-gradient-to-br from-purple-600/20 to-blue-600/20 border-2
                  transition-all duration-300
                  ${isDraggingFile 
                    ? 'border-purple-500 scale-110' 
                    : 'border-gray-700 hover:border-purple-600 hover:scale-105'
                  }
                `}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-purple-400">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 3 7 8"/>
                    <line x1="12" x2="12" y1="3" y2="15"/>
                  </svg>
                </div>
                
                <div className="space-y-3">
                  <p className="text-3xl font-light text-gray-300">
                    {isDraggingFile ? 'Drop your video here' : 'Upload a video to start'}
                  </p>
                  <p className="text-base text-gray-500">
                    Drag & drop or click to browse
                  </p>
                </div>

                {/* Supported formats */}
                <div className="flex items-center justify-center gap-4 text-sm text-gray-600 pt-4">
                  <span>MP4</span>
                  <span>•</span>
                  <span>MOV</span>
                  <span>•</span>
                  <span>AVI</span>
                  <span>•</span>
                  <span>WebM</span>
                </div>
              </div>
            </div>
          )}

          {uploadError && !isUploading && (
            <div className="mt-6 p-4 bg-red-500/10 border border-red-500/50 rounded-xl backdrop-blur-sm">
              <p className="text-red-400 text-sm">{uploadError}</p>
            </div>
          )}
        </div>

        <style jsx>{`
          @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(400%); }
          }
          
          @keyframes pulse-slow {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
          }

          @keyframes fade-in-out {
            0% { opacity: 0; transform: translateY(-10px); }
            10% { opacity: 1; transform: translateY(0); }
            90% { opacity: 1; transform: translateY(0); }
            100% { opacity: 0; transform: translateY(10px); }
          }

          .animate-shimmer {
            animation: shimmer 2s infinite;
          }

          .animate-pulse-slow {
            animation: pulse-slow 3s ease-in-out infinite;
          }

          .animate-fade-in-out {
            animation: fade-in-out 3s ease-in-out;
          }

          .bg-gradient-radial {
            background: radial-gradient(circle at center, var(--tw-gradient-stops));
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="w-full bg-gray-900 flex flex-col rounded-lg overflow-hidden">
      {/* Header toolbar */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-gray-400 text-sm">📹 Now Editing:</span>
          <span className="text-white font-medium truncate">{activeVideo?.filename || 'Unknown'}</span>
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleUploadNewVideo}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors flex items-center gap-1"
            title="Upload a new video"
          >
            ➕ Upload Video
          </button>
        </div>
      </div>

      {/* Video display area */}
      <div className="w-full flex items-center justify-center bg-black p-4">
        <video
          ref={videoRef}
          key={activeVideoUrl}
          src={activeVideoUrl}
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onEnded={handleEnded}
          className="max-w-full w-auto h-auto rounded"
        />
      </div>

      {/* Custom controls */}
      <div className="bg-gray-800 p-4 space-y-3 flex-shrink-0">
        {/* Progress bar */}
        <div
          ref={progressBarRef}
          onMouseDown={handleProgressMouseDown}
          className="w-full h-2 bg-gray-700 rounded-full cursor-pointer group relative"
        >
          <div
            className="h-full bg-blue-500 rounded-full relative group-hover:bg-blue-400 transition-colors"
            style={{ width: `${(playbackState.currentTime / duration) * 100}%` }}
          >
            <div className="absolute right-0 top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </div>

        {/* Controls row */}
        <div className="flex items-center justify-between">
          {/* Play/Pause button */}
          <button
            onClick={togglePlayPause}
            className="bg-blue-500 hover:bg-blue-600 text-white rounded-lg px-6 py-2 font-medium transition-colors"
          >
            {playbackState.isPlaying ? '⏸ Pause' : '▶ Play'}
          </button>

          {/* Time display */}
          <div className="text-gray-400 text-sm font-mono">
            {formatTime(playbackState.currentTime)} / {formatTime(duration)}
          </div>
        </div>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="video/*"
        onChange={handleFileSelect}
        className="hidden"
      />
    </div>
  );
};

export default VideoPlayer;
