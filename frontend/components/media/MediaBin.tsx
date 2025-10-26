'use client';

// Media library displaying all uploaded videos
import { useState } from 'react';
import { useAppStore, MediaFile } from '@/lib/store';
import FileUploader from './FileUploader';

const MediaBin = () => {
  const {
    mediaBin, activeVideoId, setActiveVideoId,
    deleteMediaFile, renameMediaFile,
    addMediaFile, setIsUploading, setUploadProgress
    , saveVideo } = useAppStore();

  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState('');
  const [savingId, setSavingId] = useState<string | null>(null);

  // Filter to show only video files
  const videoFiles = mediaBin.filter(file => file.mediaType === 'video');

  const handleFileUpload = async (file: File) => {
    const mediaType = file.type.startsWith('video/') ? 'video' : 'audio';
    setIsUploading(mediaType);
    setUploadProgress(0);

    // --- FIX: Get the latest state directly from the store ---
    const currentMediaBin = useAppStore.getState().mediaBin;
    const existingFilesCount = currentMediaBin.filter(f => f.mediaType === mediaType).length;
    const newFileName = `${mediaType === 'video' ? 'Video' : 'Audio'} ${existingFilesCount + 1}`;
    // --- End Fix ---

    if (mediaType === 'audio') {
      // For audio, we bypass the backend processing and add it directly.
      const audioUrl = URL.createObjectURL(file);
      addMediaFile({
        id: `audio-${Date.now()}`,
        filename: newFileName, // Use the new name
        url: audioUrl,
        type: file.type,
        mediaType: 'audio',
        uploadedAt: new Date(),
        description: "Audio file",
        isAnalyzing: false,
      });
      setUploadProgress(100);
      setTimeout(() => setIsUploading(false), 500);
      return;
    }

    // --- VIDEO UPLOAD LOGIC ---
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch('/api/upload', { method: 'POST', body: formData });
      if (response.ok) {
        const data = await response.json();
        const newFileId = data.file_id;
        addMediaFile({
          id: newFileId,
          filename: newFileName, // Use the new name
          url: `http://localhost:8000${data.url}`,
          type: file.type,
          mediaType: 'video', // Explicitly set
          uploadedAt: new Date(),
          description: data.description || "",
          isAnalyzing: false,
        });
        setUploadProgress(100);
        setActiveVideoId(newFileId); // <-- CORRECTED: Use the correct function
      } else {
        console.error("Upload failed");
      }
    } catch (err) {
      console.error("Upload error:", err);
    }
    finally {
      // Use a timeout to let the progress bar finish
      setTimeout(() => setIsUploading(false), 500);
    }
  };

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    deleteMediaFile(id);
  };

  const handleRenameClick = (id: string, currentName: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(id);
    setEditingName(currentName);
  };

  const handleRenameSubmit = (id: string, e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (editingName.trim()) {
      renameMediaFile(id, editingName.trim());
    }

    setEditingId(null);
    setEditingName('');
  };

  const handleRenameCancel = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(null);
    setEditingName('');
  };

  const handleSaveVideo = async (file: typeof videoFiles[0], e: React.MouseEvent) => {
    e.stopPropagation();
    setSavingId(file.id);
    try {
      await saveVideo(file.url, file.filename, file.description);
      setTimeout(() => setSavingId(null), 2000); // Show success for 2 seconds
    } catch (error) {
      console.error('Failed to save video:', error);
      alert('Failed to save video');
      setSavingId(null);
    }
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="h-full flex flex-col space-y-4">
      <FileUploader />

      {videoFiles.length === 0 ? (
        <div className="text-gray-500 text-sm flex-grow flex items-center justify-center">
          <p>Your uploaded videos will appear here.</p>
        </div>
      ) : (
        <div className="flex-grow overflow-y-auto space-y-2 pr-2">
          {videoFiles.map((file) => (
            <div
              key={file.id}
              onMouseEnter={() => setHoveredId(file.id)}
              onMouseLeave={() => setHoveredId(null)}
              onClick={() => setActiveVideoId(file.id)}
              className={`
                p-3 rounded-md cursor-pointer transition-all duration-200 relative group border-l-4
                ${activeVideoId === file.id
                  ? 'bg-gray-700 border-blue-500'
                  : 'bg-gray-800 border-transparent hover:bg-gray-700/50'
                }
              `}
            >
              {/* Main content */}
              <div className="flex items-center justify-between">
                <div className="flex-grow min-w-0">
                  {editingId === file.id ? (
                    <form onSubmit={(e) => handleRenameSubmit(file.id, e)} onClick={(e) => e.stopPropagation()}>
                      <input
                        type="text"
                        value={editingName}
                        onChange={(e) => setEditingName(e.target.value)}
                        autoFocus
                        onBlur={(e) => handleRenameSubmit(file.id, e as any)}
                        className="w-full bg-gray-700 text-white px-2 py-1 rounded text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-400"
                      />
                    </form>
                  ) : (
                    <>
                      <p className="text-white text-sm font-medium truncate">
                        {file.filename}
                      </p>
                      <p className="text-gray-400 text-xs mt-1">
                        {formatDate(file.uploadedAt)}
                      </p>
                    </>
                  )}
                </div>

                {/* Action buttons */}
                {hoveredId === file.id && editingId !== file.id && (
                  <div className="ml-2 flex gap-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => handleSaveVideo(file, e)}
                      className="p-1 hover:bg-green-500/20 rounded"
                      title={savingId === file.id ? "Saved!" : "Save to collection"}
                      disabled={savingId === file.id}
                    >
                      {savingId === file.id ? (
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-green-400">
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                      ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-green-400">
                          <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                          <polyline points="17 21 17 13 7 13 7 21" />
                          <polyline points="7 3 7 8 15 8" />
                        </svg>
                      )}
                    </button>
                    <button
                      onClick={(e) => handleRenameClick(file.id, file.filename, e)}
                      className="p-1 hover:bg-gray-600 rounded"
                      title="Rename video"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" /></svg>
                    </button>
                    <button
                      onClick={(e) => handleDelete(file.id, e)}
                      className="p-1 hover:bg-red-500/20 rounded"
                      title="Delete video"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18" /><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" /><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" /><line x1="10" x2="10" y1="11" y2="17" /><line x1="14" x2="14" y1="11" y2="17" /></svg>
                    </button>
                  </div>
                )}
              </div>

              {/* Selected indicator */}
              {activeVideoId === file.id && (
                <div className="absolute top-2 right-2 w-2 h-2 bg-white rounded-full"></div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Summary */}
      {videoFiles.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-700 text-xs text-gray-500">
          {videoFiles.length} video{videoFiles.length !== 1 ? 's' : ''} uploaded
        </div>
      )}
    </div>
  );
};

export default MediaBin;
