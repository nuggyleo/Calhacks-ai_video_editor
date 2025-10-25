'use client';

// Video player with custom controls
// Supports play/pause, progress bar dragging, and time display
// Now includes drag-and-drop, click-to-upload, and toolbar for new video/chat

import { useRef, useState, useEffect, MouseEvent, DragEvent, ChangeEvent } from 'react';
import { useAppStore } from '@/lib/store';

const VideoPlayer = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const progressBarRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const { currentVideoUrl, addMediaFile, setIsUploading, isUploading, mediaFiles, currentVideoId } = useAppStore();
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [isDraggingFile, setIsDraggingFile] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  
  // Get current video name
  const currentVideo = mediaFiles.find(f => f.id === currentVideoId);
  
  // Format time as MM:SS
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  // Play/Pause toggle
  const togglePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };
  
  // Update current time as video plays
  const handleTimeUpdate = () => {
    if (videoRef.current && !isDragging) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };
  
  // Set duration when video metadata loads
  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };
  
  // Handle progress bar click/drag
  const handleProgressClick = (e: MouseEvent<HTMLDivElement>) => {
    if (progressBarRef.current && videoRef.current) {
      const rect = progressBarRef.current.getBoundingClientRect();
      const pos = (e.clientX - rect.left) / rect.width;
      const newTime = pos * duration;
      videoRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };
  
  const handleProgressMouseDown = (e: MouseEvent<HTMLDivElement>) => {
    setIsDragging(true);
    handleProgressClick(e);
  };
  
  useEffect(() => {
    const handleMouseMove = (e: globalThis.MouseEvent) => {
      if (isDragging && progressBarRef.current && videoRef.current) {
        const rect = progressBarRef.current.getBoundingClientRect();
        const pos = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        const newTime = pos * duration;
        videoRef.current.currentTime = newTime;
        setCurrentTime(newTime);
      }
    };
    
    const handleMouseUp = () => {
      setIsDragging(false);
    };
    
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, duration]);
  
  // Reset player when video ends
  const handleEnded = () => {
    setIsPlaying(false);
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
          uploadedAt: new Date(),
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
  
  if (!currentVideoUrl) {
    return (
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        className={`
          flex-grow bg-gray-900 flex items-center justify-center rounded-lg cursor-pointer
          transition-all duration-200 border-2 border-dashed
          ${isDraggingFile 
            ? 'border-blue-500 bg-blue-500/10' 
            : 'border-gray-600 hover:border-gray-500'
          }
          ${isUploading ? 'pointer-events-none opacity-50' : ''}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          onChange={handleFileSelect}
          className="hidden"
        />
        
        <div className="text-center">
          {isUploading ? (
            <div className="space-y-4">
              <p className="text-gray-300 text-lg">Uploading...</p>
              <div className="w-48 bg-gray-700 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: '100%' }}
                />
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-5xl">🎬</p>
              <p className="text-gray-300 text-xl font-medium">Drag & Drop Video Here</p>
              <p className="text-gray-500 text-sm">or click to browse</p>
            </div>
          )}
          
          {uploadError && !isUploading && (
            <div className="mt-4 p-3 bg-red-500/10 border border-red-500 rounded-lg">
              <p className="text-red-400 text-sm">{uploadError}</p>
            </div>
          )}
        </div>
      </div>
    );
  }
  
  return (
    <div className="flex-grow bg-gray-900 flex flex-col rounded-lg overflow-hidden">
      {/* Header toolbar */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-gray-400 text-sm">📹 Now Editing:</span>
          <span className="text-white font-medium truncate">{currentVideo?.filename || 'Unknown'}</span>
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
      <div className="flex-grow flex items-center justify-center bg-black">
        <video
          ref={videoRef}
          src={currentVideoUrl}
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onEnded={handleEnded}
          className="max-w-full max-h-full"
        />
      </div>
      
      {/* Custom controls */}
      <div className="bg-gray-800 p-4 space-y-3">
        {/* Progress bar */}
        <div
          ref={progressBarRef}
          onMouseDown={handleProgressMouseDown}
          className="w-full h-2 bg-gray-700 rounded-full cursor-pointer group relative"
        >
          <div
            className="h-full bg-blue-500 rounded-full relative group-hover:bg-blue-400 transition-colors"
            style={{ width: `${(currentTime / duration) * 100}%` }}
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
            {isPlaying ? '⏸ Pause' : '▶ Play'}
          </button>
          
          {/* Time display */}
          <div className="text-gray-400 text-sm font-mono">
            {formatTime(currentTime)} / {formatTime(duration)}
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
