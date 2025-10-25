// This component is the main container for the right-side chat interface.
// It orchestrates the MessageList and CommandInput components, managing the
// overall state of the conversation with the AI editing assistant.

import MessageList from "./MessageList";
import CommandInput from "./CommandInput";

const ChatPanel = () => {
  return (
    <div className="col-span-2 bg-gray-800 flex flex-col p-4">
      <MessageList />
      <CommandInput />
    </div>
  );
};

export default ChatPanel;
