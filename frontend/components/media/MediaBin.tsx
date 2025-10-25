'use client';

// Media library displaying all uploaded videos
import { useState } from 'react';
import { useAppStore } from '@/lib/store';

const MediaBin = () => {
  const { mediaBin, activeVideoId, setActiveVideoId, deleteMediaFile, renameMediaFile } = useAppStore();
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
    <div className="flex-grow bg-gray-900 rounded-lg p-4 flex flex-col">
      <h3 className="text-lg font-semibold mb-3 text-white">My Media</h3>

      {mediaBin.length === 0 ? (
        <div className="text-gray-500 text-sm flex-grow flex items-center justify-center">
          No media uploaded yet. Start by uploading a video above.
        </div>
      ) : (
        <div className="flex-grow overflow-y-auto space-y-2">
          {mediaBin.map((file) => (
            <div
              key={file.id}
              onMouseEnter={() => setHoveredId(file.id)}
              onMouseLeave={() => setHoveredId(null)}
              onClick={() => setActiveVideoId(file.id)}
              className={`
                p-3 rounded-lg cursor-pointer transition-all duration-200 relative group
                ${activeVideoId === file.id
                  ? 'bg-blue-600 border-2 border-blue-400'
                  : 'bg-gray-800 border-2 border-transparent hover:bg-gray-700'
                }
              `}
            >
              {/* Main content */}
              <div className="flex items-start justify-between">
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
                  <div className="ml-2 flex gap-1 flex-shrink-0">
                    <button
                      onClick={(e) => handleRenameClick(file.id, file.filename, e)}
                      className="px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors"
                      title="Rename video"
                    >
                      ✏️
                    </button>
                    <button
                      onClick={(e) => handleDelete(file.id, e)}
                      className="px-2 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition-colors"
                      title="Delete video"
                    >
                      🗑️
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
      {mediaBin.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-700 text-xs text-gray-500">
          {mediaBin.length} video{mediaBin.length !== 1 ? 's' : ''} uploaded
        </div>
      )}
    </div>
  );
};

export default MediaBin;
