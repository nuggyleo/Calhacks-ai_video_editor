// This component serves as the container for the central part of the UI.
// Its main responsibility is to hold the VideoPlayer and the visual TimelineView,
// creating the primary workspace for viewing the edited video.

import VideoPlayer from "./VideoPlayer";
import TimelineView from "./TimelineView";

const PlayerPanel = () => {
  return (
    <div className="col-span-3 bg-black flex flex-col p-4">
      <VideoPlayer />
      <TimelineView />
    </div>
  );
};

export default PlayerPanel;
