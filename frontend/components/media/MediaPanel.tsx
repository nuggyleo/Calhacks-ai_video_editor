'use client';

// This component acts as a container for the left-side panel.
// It will house the FileUploader, MediaBin, AudioBin with tabs
// organizing all the assets in one place.

import { useState } from 'react';
import MediaBin from "./MediaBin";
import AudioBin from "./AudioBin";
import PromptGuide from "./PromptGuide"; // Import the new component
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";

const MediaPanel = () => {
  const [activeTab, setActiveTab] = useState<'video' | 'audio'>('video');

  return (
    <PanelGroup direction="vertical" className="h-full">
      {/* Upper Panel: Media Bins */}
      <Panel defaultSize={40} minSize={30}>
        <div className="h-full flex flex-col bg-gray-800 p-4 space-y-4">
          <h2 className="text-3xl font-lobster text-center py-2 flex-shrink-0 text-white">My Media</h2>

          {/* Tabs */}
          <div className="flex gap-2 border-b border-gray-700 flex-shrink-0">
            <button
              onClick={() => setActiveTab('video')}
              className={`
                flex-1 py-2 px-4 text-sm font-medium transition-all duration-200 relative
                ${activeTab === 'video'
                  ? 'text-white'
                  : 'text-gray-400 hover:text-gray-300'
                }
              `}
            >
              📹 Videos
              {activeTab === 'video' && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-400 to-purple-500" />
              )}
            </button>
            <button
              onClick={() => setActiveTab('audio')}
              className={`
                flex-1 py-2 px-4 text-sm font-medium transition-all duration-200 relative
                ${activeTab === 'audio'
                  ? 'text-white'
                  : 'text-gray-400 hover:text-gray-300'
                }
              `}
            >
              🎵 Audio
              {activeTab === 'audio' && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-400 to-purple-500" />
              )}
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-hidden">
            {activeTab === 'video' ? <MediaBin /> : <AudioBin />}
          </div>
        </div>
      </Panel>

      <PanelResizeHandle className="h-2 bg-gray-900 hover:bg-blue-600 transition-colors" />

      {/* Lower Panel: Prompt Guide */}
      <Panel defaultSize={60} minSize={20}>
        <div className="h-full p-4 bg-gray-800">
          <PromptGuide />
        </div>
      </Panel>
    </PanelGroup>
  );
};

export default MediaPanel;
