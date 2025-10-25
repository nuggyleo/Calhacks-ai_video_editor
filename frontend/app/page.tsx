'use client';

// This is the main page component that assembles the entire application layout.
// It will import and arrange the three main panels: Media, Player, and Chat.

import AppLayout from "@/components/layout/AppLayout";
import MediaPanel from "@/components/media/MediaPanel";
import PlayerPanel from "@/components/player/PlayerPanel";
import ChatPanel from "@/components/chat/ChatPanel";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { useAppStore } from "@/lib/store";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function Home() {
  const { authStatus } = useAppStore();
  const router = useRouter();

  useEffect(() => {
    if (authStatus === 'unauthenticated') {
      router.push('/login');
    }
  }, [authStatus, router]);

  if (authStatus === 'loading' || authStatus === 'unauthenticated') {
    return (
      <div className="w-screen h-screen bg-black flex items-center justify-center">
        <p className="text-white">Loading...</p>
      </div>
    );
  }

  return (
    <AppLayout>
      <PanelGroup direction="horizontal" className="w-full h-full">
        {/* Left Column: Media Panel */}
        <Panel defaultSize={25} minSize={15}>
          <div className="h-full bg-gray-900 p-2">
            <MediaPanel />
          </div>
        </Panel>
        
        <PanelResizeHandle className="w-2 bg-gray-800 hover:bg-blue-600 transition-colors" />

        {/* Center Column: Player Panel */}
        <Panel defaultSize={50} minSize={30}>
          <div className="h-full bg-black flex items-center justify-center">
            <PlayerPanel />
          </div>
        </Panel>

        <PanelResizeHandle className="w-2 bg-gray-800 hover:bg-blue-600 transition-colors" />
        
        {/* Right Column: Chat Panel */}
        <Panel defaultSize={25} minSize={15}>
          <div className="h-full bg-gray-900">
            <ChatPanel />
          </div>
        </Panel>
      </PanelGroup>
    </AppLayout>
  );
}
