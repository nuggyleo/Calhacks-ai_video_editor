// This component is the main container for the right-side chat interface.
// It orchestrates the MessageList and CommandInput components, managing the
// overall state of the conversation with the AI editing assistant.

import MessageList from "./MessageList";
import CommandInput from "./CommandInput";

const ChatPanel = () => {
  return (
    <div className="h-full flex flex-col bg-gray-900">
      <div className="flex-grow overflow-hidden">
        <MessageList />
      </div>
      <div className="p-4 border-t border-gray-800">
        <CommandInput />
      </div>
    </div>
  );
};

export default ChatPanel;
