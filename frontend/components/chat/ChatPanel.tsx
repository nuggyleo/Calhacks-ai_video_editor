// This component is the main container for the right-side chat interface.
// It orchestrates the MessageList and CommandInput components, managing the
// overall state of the conversation with the AI editing assistant.

import MessageList from "./MessageList";
import CommandInput from "./CommandInput";

const ChatPanel = () => {
  return (
    <div className="h-full flex flex-col bg-gray-800 rounded-lg overflow-hidden">
      {/* Panel Header */}
      <div className="bg-gray-900 p-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold text-white">Conversation</h2>
      </div>

      {/* Main content area */}
      <div className="flex-grow flex flex-col overflow-hidden">
        {/* Message list with scrolling */}
        <div className="flex-grow overflow-y-auto">
          <MessageList />
        </div>

        {/* Command input at the bottom */}
        <div className="p-4 border-t border-gray-700 bg-gray-900">
          <CommandInput />
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;
