'use client';

// Media library displaying all uploaded videos
import { useState } from 'react';
import { useAppStore } from '@/lib/store';
import FileUploader from './FileUploader';

const MediaBin = () => {
  const { mediaFiles, currentVideoId, setCurrentVideo, deleteMediaFile, renameMediaFile } = useAppStore();
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState('');

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
      
      {mediaFiles.length === 0 ? (
        <div className="text-gray-500 text-sm flex-grow flex items-center justify-center">
          <p>Your uploaded videos will appear here.</p>
        </div>
      ) : (
        <div className="flex-grow overflow-y-auto space-y-2 pr-2">
          {mediaFiles.map((file) => (
            <div
              key={file.id}
              onMouseEnter={() => setHoveredId(file.id)}
              onMouseLeave={() => setHoveredId(null)}
              onClick={() => setCurrentVideo(file.url, file.id)}
              className={`
                p-3 rounded-md cursor-pointer transition-all duration-200 relative group border-l-4
                ${currentVideoId === file.id
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
                      onClick={(e) => handleRenameClick(file.id, file.filename, e)}
                      className="p-1 hover:bg-gray-600 rounded"
                      title="Rename video"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
                    </button>
                    <button
                      onClick={(e) => handleDelete(file.id, e)}
                      className="p-1 hover:bg-red-500/20 rounded"
                      title="Delete video"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
                    </button>
                  </div>
                )}
              </div>

              {/* Selected indicator (now handled by border) */}
            </div>
          ))}
        </div>
      )}

      {/* Summary */}
      {mediaFiles.length > 0 && (
        <div className="mt-auto pt-3 border-t border-gray-700 text-xs text-gray-500">
          {mediaFiles.length} video{mediaFiles.length !== 1 ? 's' : ''} uploaded
        </div>
      )}
    </div>
  );
};

export default MediaBin;
