'use client';

import { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { useAppStore } from '@/lib/store';

const FileUploader = ({
  accept,
  title,
  onFileUpload,
  mediaType
}: {
  accept: string;
  title: string;
  onFileUpload: (file: File) => Promise<void>;
  mediaType: 'video' | 'audio';
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { isUploading, uploadProgress } = useAppStore();

  const isThisUploaderBusy = isUploading === mediaType;

  const handleFileValidation = (file: File): boolean => {
    const fileType = file.type;
    const acceptedTypes = accept.split(',').map(t => t.trim());
    const isValid = acceptedTypes.some(t => {
      if (t.endsWith('/*')) {
        return fileType.startsWith(t.slice(0, -1));
      }
      return fileType === t;
    });

    if (!isValid) {
      setError(`Invalid file type. Please upload a ${accept}.`);
      return false;
    }
    setError(null);
    return true;
  };

  const handleFileUpload = async (file: File) => {
    if (!handleFileValidation(file)) return;
    await onFileUpload(file);
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
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  return (
    <div className="space-y-3">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200
          ${isDragging
            ? 'border-blue-500 bg-blue-500/10'
            : 'border-gray-600 hover:border-gray-500'
          }
          ${isThisUploaderBusy ? 'pointer-events-none opacity-50' : ''}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          onChange={handleFileSelect}
          className="hidden"
          disabled={isThisUploaderBusy}
        />

        {isThisUploaderBusy ? (
          <div className="space-y-2">
            <p className="text-gray-300">Uploading...</p>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <p className="text-sm text-gray-400">{Math.round(uploadProgress)}%</p>
          </div>
        ) : (
          <div>
            <p className="text-gray-300 text-lg mb-2">📹 {title}</p>
            <p className="text-sm text-gray-500">or click to browse</p>
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

export default FileUploader;
