'use client';

// This component acts as a container for the left-side panel.
// It will house the FileUploader, MediaBin, AudioBin with tabs
// organizing all the assets in one place.

import { useState } from 'react';
import MediaBin from "./MediaBin";
import AudioBin from "./AudioBin";

const MediaPanel = () => {
  const [activeTab, setActiveTab] = useState<'video' | 'audio'>('video');

  return (
    <div className="col-span-1 bg-gray-800 p-4 flex flex-col space-y-4">
      <h2 className="text-3xl font-lobster text-center py-2">My Media</h2>
      
      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-700">
        <button
          onClick={() => setActiveTab('video')}
          className={`
            flex-1 py-2 px-4 text-sm font-medium transition-all duration-200
            ${activeTab === 'video'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-gray-400 hover:text-gray-300'
            }
          `}
        >
          📹 Videos
        </button>
        <button
          onClick={() => setActiveTab('audio')}
          className={`
            flex-1 py-2 px-4 text-sm font-medium transition-all duration-200
            ${activeTab === 'audio'
              ? 'text-purple-400 border-b-2 border-purple-400'
              : 'text-gray-400 hover:text-gray-300'
            }
          `}
        >
          🎵 Audio
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'video' ? <MediaBin /> : <AudioBin />}
      </div>
    </div>
  );
};

export default MediaPanel;
