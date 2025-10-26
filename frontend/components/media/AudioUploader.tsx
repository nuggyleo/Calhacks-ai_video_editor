'use client';

// Audio file uploader with drag-and-drop support
import { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { useAppStore } from '@/lib/store';

const AudioUploader = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const {
    addMediaFile,
    setUploadProgress,
    setIsUploading,
    isUploading,
    uploadProgress,
  } = useAppStore();

  const handleUpload = async (file: File) => {
    if (!file.type.startsWith('audio/')) {
      setError('Please upload a valid audio file');
      return;
    }

    setError(null);
    setIsUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('mediaType', 'audio'); // Indicate this is an audio file

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();

        // Add audio file to the store (no analysis needed for audio)
        addMediaFile({
          id: data.file_id,
          filename: data.filename,
          url: `http://localhost:8000${data.url}`,
          type: file.type,
          mediaType: 'audio', // This is an audio file
          uploadedAt: new Date(),
          description: data.description || "",
          isAnalyzing: false,
        });

        setUploadProgress(100);
        setTimeout(() => {
          setIsUploading(false);
          setUploadProgress(0);
        }, 500);
      } else {
        const errorText = await response.text();
        console.error('Upload failed:', errorText);
        setError(`Upload failed: ${response.statusText}`);
        setIsUploading(false);
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError('An error occurred during upload.');
      setIsUploading(false);
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

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

  return (
    <div className="space-y-3">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        className={`
          border-2 border-dashed rounded-lg p-3 text-center cursor-pointer
          transition-all duration-200
          ${isDragging
            ? 'border-purple-500 bg-purple-500/10'
            : 'border-gray-600 hover:border-gray-500'
          }
          ${isUploading ? 'pointer-events-none opacity-50' : ''}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          onChange={handleFileSelect}
          className="hidden"
        />

        {isUploading ? (
          <div className="space-y-2">
            <p className="text-gray-300">Uploading...</p>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-purple-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <p className="text-sm text-gray-400">{Math.round(uploadProgress)}%</p>
          </div>
        ) : (
          <div>
            <p className="text-gray-300 text-lg">🎵 Upload Audio</p>
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500 rounded-lg p-3">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}
    </div>
  );
};

export default AudioUploader;

