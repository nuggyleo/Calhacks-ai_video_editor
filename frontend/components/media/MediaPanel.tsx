// This component acts as a container for the left-side panel.
// It will house the FileUploader, MediaBin, and the AiToolsPanel,
// organizing all the assets and AI-powered actions in one place.

import FileUploader from "./FileUploader";
import MediaBin from "./MediaBin";
import AiToolsPanel from "../ai/AiToolsPanel";

const MediaPanel = () => {
  return (
    <div className="col-span-1 bg-gray-800 p-4 flex flex-col space-y-4">
      <h2 className="text-xl font-bold">Media & Tools</h2>
      <FileUploader />
      <MediaBin />
      <AiToolsPanel />
    </div>
  );
};

export default MediaPanel;
