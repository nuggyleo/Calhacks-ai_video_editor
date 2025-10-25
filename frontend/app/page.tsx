// This is the main page component that assembles the entire application layout.
// It will import and arrange the three main panels: Media, Player, and Chat.

import AppLayout from "@/components/layout/AppLayout";
import MediaPanel from "@/components/media/MediaPanel";
import PlayerPanel from "@/components/player/PlayerPanel";
import ChatPanel from "@/components/chat/ChatPanel";

export default function Home() {
  return (
    <AppLayout>
      <MediaPanel />
      <PlayerPanel />
      <ChatPanel />
    </AppLayout>
  );
}
