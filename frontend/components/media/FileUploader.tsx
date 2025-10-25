'use client';

// Video file uploader with drag-and-drop support
import { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { useAppStore } from '@/lib/store';

const FileUploader = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const { addMediaFile, setUploadProgress, setIsUploading, isUploading, uploadProgress } = useAppStore();
  
  const handleUpload = async (file: File) => {
    if (!file.type.startsWith('video/')) {
      setError('Please upload a valid video file');
      return;
    }
    
    setError(null);
    setIsUploading(true);
    setUploadProgress(0);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const xhr = new XMLHttpRequest();
      
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const progress = (e.loaded / e.total) * 100;
          setUploadProgress(progress);
        }
      });
      
      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          try {
            const response = JSON.parse(xhr.responseText);
            addMediaFile({
              id: response.file_id,
              filename: response.filename,
              url: `http://localhost:8000${response.url}`,
              type: file.type,
              uploadedAt: new Date(),
            });
            
            setUploadProgress(100);
            setTimeout(() => {
              setIsUploading(false);
              setUploadProgress(0);
            }, 500);
          } catch (e) {
            console.error('Parse error:', xhr.responseText);
            setError('Upload succeeded but response parsing failed');
            setIsUploading(false);
          }
        } else {
          setError(`Upload failed: ${xhr.status}`);
          setIsUploading(false);
        }
      });
      
      xhr.addEventListener('error', () => {
        setError('Network error during upload');
        setIsUploading(false);
      });
      
      // Use the Next.js API route instead of calling backend directly
      xhr.open('POST', '/api/upload');
      xhr.send(formData);
      
    } catch (err) {
      setError('Upload failed');
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
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200
          ${isDragging 
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
        
        {isUploading ? (
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
            <p className="text-gray-300 text-lg mb-2">📹 Drag & Drop Video Here</p>
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
