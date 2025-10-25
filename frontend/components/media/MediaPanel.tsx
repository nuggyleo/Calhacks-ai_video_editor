// This component acts as a container for the left-side panel.
// It will house the FileUploader, MediaBin, and the AiToolsPanel,
// organizing all the assets and AI-powered actions in one place.

import MediaBin from "./MediaBin";

const MediaPanel = () => {
  return (
    <div className="col-span-1 bg-gray-800 p-4 flex flex-col space-y-4">
      <h2 className="text-3xl font-lobster text-center py-2">My Media</h2>
      <MediaBin />
    </div>
  );
};

export default MediaPanel;
