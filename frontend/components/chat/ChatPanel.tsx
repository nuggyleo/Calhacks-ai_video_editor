// This component is the main container for the right-side chat interface.
// It orchestrates the MessageList and CommandInput components, managing the
// overall state of the conversation with the AI editing assistant.

import MessageList from "./MessageList";
import CommandInput from "./CommandInput";
import { useAppStore } from "@/lib/store";

const ChatPanel = () => {
  const { clearChat } = useAppStore();

  const handleClearChat = async () => {
    if (window.confirm("Are you sure you want to clear the chat history? This cannot be undone.")) {
      await clearChat();
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-800 rounded-lg overflow-hidden">
      {/* Panel Header */}
      <div className="bg-gray-900 p-4 border-b border-gray-700 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Conversation</h2>
        <button
          onClick={handleClearChat}
          className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-500 hover:bg-opacity-20 rounded transition-all duration-200"
          title="Clear chat history"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </button>
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

