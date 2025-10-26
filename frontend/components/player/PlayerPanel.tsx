// This component serves as the container for the central part of the UI.
// Its main responsibility is to hold the VideoPlayer and the visual TimelineView,
// creating the primary workspace for viewing the edited video.

import VideoPlayer from "./VideoPlayer";

const PlayerPanel = () => {
  return (
    <div className="w-full h-full bg-black flex flex-col overflow-hidden">
      <div className="flex-1 overflow-hidden p-4 flex items-center justify-center">
        <VideoPlayer />
      </div>
    </div>
  );
};

export default PlayerPanel;
